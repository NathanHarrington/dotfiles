#!/usr/bin/env python3
"""Unattended recovery from NetworkManager's saved-password/no-secrets stall.

Install:   sudo python3 wifi_saved_password_recovery.py install
Inspect:   sudo python3 wifi_saved_password_recovery.py status
Remove:    sudo python3 wifi_saved_password_recovery.py uninstall

Python standard library only. Requires NetworkManager, systemd and journalctl.
Installation discovers this machine's working Wi-Fi and existing profiles.
The installed copy embeds only interface/UUID/SSID metadata, never passwords.
No profile edits, package changes, service restarts, radio resets or reboots.
"""

import argparse
import ast
import fcntl
import json
import math
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import time
import uuid as uuid_module


VERSION = "2.0"
MARKER = "Managed by wifi_saved_password_recovery.py"
NAME = "wifi-saved-password-recovery"
SCRIPT = Path("/usr/local/libexec") / (NAME + ".py")
UNIT_DIR = Path("/etc/systemd/system")
RUNTIME = Path("/run") / NAME
STATE_FILE = RUNTIME / "state.json"
TRUSTED_SSIDS = {"MisplacedNoodle", "Thrive Members"}
STALL_SECONDS = 120
COOLDOWN_SECONDS = 300
JOURNAL_BATCH = 2000
INSTALL_CONFIG = None  # Replaced with local metadata in the installed copy.

NMCLI = "/usr/bin/nmcli"
SYSTEMCTL = "/usr/bin/systemctl"
JOURNALCTL = "/usr/bin/journalctl"
PROFILE_FIELDS = (
    "connection.type", "connection.interface-name", "connection.autoconnect",
    "connection.permissions", "connection.timestamp", "802-11-wireless.ssid",
    "802-11-wireless-security.key-mgmt", "802-11-wireless-security.psk-flags",
)
DEVICE_FIELDS = (
    "GENERAL.TYPE", "GENERAL.STATE", "GENERAL.AUTOCONNECT", "GENERAL.CON-UUID",
)
START_RE = re.compile(r"Activation: starting connection .* \(([0-9a-fA-F-]{36})\)")
CHANGE_RE = re.compile(r"state change: (\S+) -> (\S+) \(reason '([^']+)'")


class RecoveryError(Exception):
    pass


def log(message):
    print(f"{NAME}: {message}", flush=True)


def blank(value):
    return value in ("", "--")


def valid_uuid(value):
    try:
        return str(uuid_module.UUID(value)) == value.lower()
    except (ValueError, TypeError, AttributeError):
        return False


def boot_id():
    return Path("/proc/sys/kernel/random/boot_id").read_text().strip().replace("-", "")


class Runner:
    def __init__(self, seconds=100):
        self.deadline = time.monotonic() + seconds

    def remaining(self):
        return self.deadline - time.monotonic()

    def run(self, argv, timeout=8, accepted=(0,)):
        remaining = self.remaining()
        if remaining < 1:
            raise RecoveryError("Check time budget exhausted; deferred")
        try:
            result = subprocess.run(
                argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True,
                timeout=min(timeout, remaining),
                env={**os.environ, "LC_ALL": "C", "LANG": "C", "SYSTEMD_COLORS": "0"},
            )
        except subprocess.TimeoutExpired:
            raise RecoveryError(f"{Path(argv[0]).name} timed out; deferred") from None
        # Never include stdout/stderr here: a query can contain a saved secret.
        if result.returncode not in accepted:
            raise RecoveryError(f"{Path(argv[0]).name} failed (exit {result.returncode}); deferred")
        return result


class NetworkManager:
    def __init__(self, runner, interface):
        self.runner = runner
        self.interface = interface

    def query(self, *args, timeout=8, secret=False):
        options = [NMCLI, "--colors", "no", "--terse", "--escape", "no"]
        if secret:
            options.append("--show-secrets")
        # Remove the record terminator, preserving empty trailing field values.
        return self.runner.run(options + list(args), timeout).stdout.removesuffix("\n")

    def snapshot(self):
        values = self.query("-g", ",".join(DEVICE_FIELDS), "device", "show", self.interface).split("\n")
        if len(values) != len(DEVICE_FIELDS):
            raise RecoveryError("Cannot determine Wi-Fi device state")
        try:
            number = int(values[1].split()[0])
        except (ValueError, IndexError):
            raise RecoveryError("Unrecognized Wi-Fi device state") from None
        return {"type": values[0], "state": number, "autoconnect": values[2],
                "uuid": None if blank(values[3]) else values[3].lower(),
                "radio": self.query("radio", "wifi")}

    def profile(self, profile_uuid):
        values = self.query("-g", ",".join(PROFILE_FIELDS), "connection", "show", "uuid", profile_uuid).split("\n")
        if len(values) != len(PROFILE_FIELDS):
            raise RecoveryError("Cannot determine saved profile settings")
        return dict(zip(PROFILE_FIELDS, values))

    def has_saved_password(self, profile_uuid):
        value = self.query("-g", "802-11-wireless-security.psk", "connection", "show",
                           "uuid", profile_uuid, secret=True)
        return value not in ("", "--", "<hidden>")

    def ssids(self, refresh=False):
        return set(self.query("--wait", "10", "-g", "SSID", "device", "wifi", "list",
                              "ifname", self.interface, "--rescan", "yes" if refresh else "no",
                              timeout=15 if refresh else 8).splitlines())

    def activate(self, profile_uuid):
        result = self.runner.run(
            [NMCLI, "--colors", "no", "--wait", "45", "connection", "up", "uuid",
             profile_uuid, "ifname", self.interface], timeout=50, accepted=tuple(range(256)),
        )
        return result.returncode


def validate_profile(profile, interface, expected_ssid=None, active=False):
    if profile["connection.type"] != "802-11-wireless":
        raise RecoveryError("Profile is not Wi-Fi")
    ssid = profile["802-11-wireless.ssid"]
    if ssid not in TRUSTED_SSIDS or (expected_ssid is not None and ssid != expected_ssid):
        raise RecoveryError("Profile is not an allowed home/work network")
    if profile["connection.interface-name"] not in ("", "--", interface):
        raise RecoveryError("Profile belongs to another interface")
    if profile["connection.autoconnect"] != "yes":
        raise RecoveryError("Profile autoconnect is disabled")
    if not blank(profile["connection.permissions"]):
        raise RecoveryError("Profile is restricted to a user session")
    if profile["802-11-wireless-security.key-mgmt"] != "wpa-psk":
        raise RecoveryError("Only the existing WPA-PSK saved-password setup is supported")
    if profile["802-11-wireless-security.psk-flags"].split()[:1] != ["0"]:
        raise RecoveryError("Password is not system-managed")
    try:
        stamp = int(profile["connection.timestamp"])
    except ValueError:
        raise RecoveryError("Cannot verify a previous successful connection") from None
    if stamp < 0 or (stamp == 0 and not active):
        raise RecoveryError("Profile has no recorded successful connection")
    return ssid, stamp


def new_history():
    return {"cursor": None, "invocation": None, "attempt_uuid": None,
            "failures": {},
            "success_us": 0, "reset_us": 0}


def fresh_state(current_boot, now, damaged=False):
    return {"version": 2, "boot": current_boot, "history": new_history(),
            "watch_uuid": None, "first_seen": None,
            "last_attempt": now if damaged else None, "last_scan": None,
            "last_reason": None}


def reset_observation(state):
    state["watch_uuid"] = None
    state["first_seen"] = None
    # Deliberately preserve last_attempt and last_scan across every skip.


def clear_failure(history):
    history["failures"] = {}


def consume_event(history, entry, interface, current_boot):
    if entry.get("_BOOT_ID") != current_boot:
        raise RecoveryError("Journal entry belongs to another boot; deferred")
    try:
        at = int(entry["__MONOTONIC_TIMESTAMP"])
        real = int(entry["__REALTIME_TIMESTAMP"])
        cursor, message = entry["__CURSOR"], entry["MESSAGE"]
        if at < 0 or real < 0 or not isinstance(cursor, str) or not isinstance(message, str):
            raise ValueError
    except (KeyError, ValueError, TypeError):
        raise RecoveryError("Unrecognized journal metadata; deferred") from None
    history["cursor"] = cursor
    prefix = f"device ({interface}): "
    if prefix not in message or at <= history["success_us"]:
        return
    message = message.split(prefix, 1)[1]
    started = START_RE.search(message)
    if started:
        history["attempt_uuid"] = started.group(1).lower()
        history["reset_us"] = at
        history["failures"].pop(history["attempt_uuid"], None)
        return
    change = CHANGE_RE.search(message)
    if not change:
        if "Activation: successful, device activated" in message:
            clear_failure(history)
            history["success_us"] = at
            history["reset_us"] = at
        return
    old, new, reason = change.groups()
    if new == "activated":
        # A success through ANY profile invalidates ALL previous failures.
        clear_failure(history)
        history["success_us"] = at
        history["reset_us"] = at
    elif new == "failed" and reason == "no-secrets":
        if history["attempt_uuid"]:
            history["failures"][history["attempt_uuid"]] = {"at_us": at, "real_us": real}
    elif old == "failed" and new == "disconnected" and reason == "none":
        pass  # Preserve the preceding no-secrets failure after the brief failed state.
    elif new == "need-auth":
        pass  # Live state and UUID provide independent evidence of a pending prompt.
    else:
        history["failures"].pop(history["attempt_uuid"], None)
        history["reset_us"] = at
        if new in ("unmanaged", "unavailable") or reason in ("user-requested", "sleeping", "connection-removed"):
            clear_failure(history)
            history["attempt_uuid"] = None


def update_history(runner, state, interface):
    invocation = runner.run([SYSTEMCTL, "show", "-p", "InvocationID", "--value",
                             "NetworkManager.service"]).stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{32}", invocation):
        raise RecoveryError("Cannot identify the running NetworkManager instance")
    history = state["history"]
    if history["invocation"] != invocation:
        state["history"] = history = new_history()
        history["invocation"] = invocation
        reset_observation(state)
    args = [JOURNALCTL, "--boot=" + state["boot"], "--no-pager", "--quiet", "--output=json",
            "--output-fields=MESSAGE,_BOOT_ID,__CURSOR,__MONOTONIC_TIMESTAMP,__REALTIME_TIMESTAMP",
            "--lines=+" + str(JOURNAL_BATCH), "--case-sensitive=yes",
            "--grep=device \\(" + re.escape(interface) + r"\):",
            "_SYSTEMD_UNIT=NetworkManager.service", "_SYSTEMD_INVOCATION_ID=" + invocation]
    if history["cursor"]:
        args.append("--after-cursor=" + history["cursor"])
    try:
        result = runner.run(args, timeout=12, accepted=(0, 1))
        # journalctl returns 1 for no matching messages. Actual errors have stderr.
        if result.returncode == 1 and result.stderr.strip():
            raise RecoveryError("Journal query failed; deferred")
        lines = result.stdout.splitlines()
        for line in lines:
            consume_event(history, json.loads(line), interface, state["boot"])
    except (RecoveryError, json.JSONDecodeError):
        # An expired cursor or unreadable journal cannot authorize a reconnect.
        # Rebuild from this boot on the next tick, retaining the retry cooldown.
        state["history"] = new_history()
        reset_observation(state)
        raise RecoveryError("Journal evidence unavailable; will rebuild it next check") from None
    return len(lines) < JOURNAL_BATCH


def candidate(snapshot, history, allowed):
    if snapshot["type"] != "wifi" or snapshot["radio"] != "enabled":
        return None, "Wi-Fi disabled or unavailable"
    if snapshot["autoconnect"] != "yes":
        return None, "Device autoconnect disabled"
    state, current = snapshot["state"], snapshot["uuid"]
    if state == 100:
        return None, "Wi-Fi connected"
    if current is not None and current not in allowed:
        return None, "Another profile is active or connecting"
    if state == 60 and current in allowed:
        return current, "Saved profile waiting for authentication"
    if state not in (30, 120):
        return None, "Normal connection attempt or unavailable device"
    failures = [(key, value) for key, value in history["failures"].items()
                if key in allowed and current in (None, key)
                and value["at_us"] > history["success_us"]]
    if failures:
        selected = max(failures, key=lambda item: item[1]["at_us"])[0]
        return selected, "Unresolved no-secrets failure"
    return None, "No confirmed credential stall"


def record_reason(state, reason):
    if state.get("last_reason") != reason:
        log(reason)
        state["last_reason"] = reason


def recover_once(nm, state, config, save, history_reader=update_history, clock=time.monotonic):
    def skip(reason):
        reset_observation(state)
        record_reason(state, reason)
        save(state)
        return "skipped"

    snapshot = nm.snapshot()
    now = clock()
    if snapshot["state"] == 100:
        clear_failure(state["history"])
        state["history"]["success_us"] = int(now * 1_000_000)
        state["history"]["attempt_uuid"] = snapshot["uuid"]
        return skip("Wi-Fi connected")
    if snapshot["radio"] != "enabled" or snapshot["autoconnect"] != "yes":
        return skip("Wi-Fi or device autoconnect disabled")
    if not history_reader(nm.runner, state, nm.interface):
        return skip("Reading remaining journal history; no recovery attempted")
    snapshot = nm.snapshot()
    selected, reason = candidate(snapshot, state["history"], config["profiles"])
    if selected is None:
        return skip(reason)
    profile = nm.profile(selected)
    ssid, stamp = validate_profile(profile, nm.interface, config["profiles"][selected])
    if snapshot["state"] != 60 and state["history"]["failures"][selected]["real_us"] <= stamp * 1_000_000:
        state["history"]["failures"].pop(selected, None)
        return skip("Failure predates the profile's last successful connection")

    visible = nm.ssids()
    now = clock()
    if ssid not in visible and (state["last_scan"] is None or now - state["last_scan"] >= COOLDOWN_SECONDS):
        again, _ = candidate(nm.snapshot(), state["history"], config["profiles"])
        if again != selected:
            return skip("State changed before scan; deferred")
        state["last_scan"] = now
        save(state)
        visible = nm.ssids(refresh=True)
    if ssid not in visible:
        return skip("Stalled profile's network is not in range")

    now = clock()
    first = state["first_seen"]
    if (state["watch_uuid"] != selected or first is None
            or state["history"]["reset_us"] > first * 1_000_000):
        state["watch_uuid"], state["first_seen"] = selected, now
    if now - state["first_seen"] < STALL_SECONDS:
        record_reason(state, f"Credential stall observed for {selected}; waiting two minutes")
        save(state)
        return "waiting"
    if state["last_attempt"] is not None and now - state["last_attempt"] < COOLDOWN_SECONDS:
        record_reason(state, "Recovery cooldown active")
        save(state)
        return "backoff"
    if not history_reader(nm.runner, state, nm.interface):
        return skip("Journal changed; deferred")
    again, _ = candidate(nm.snapshot(), state["history"], config["profiles"])
    if (again != selected or state["first_seen"] is None
            or state["history"]["reset_us"] > state["first_seen"] * 1_000_000):
        return skip("Connection state changed; deferred")
    validate_profile(nm.profile(selected), nm.interface, config["profiles"][selected])
    if ssid not in nm.ssids() or not nm.has_saved_password(selected):
        return skip("Saved password or network unavailable; deferred")
    if nm.runner.remaining() < 55:
        return skip("Insufficient time for bounded activation; deferred")
    # Last read immediately before activation; never compete with another profile.
    again, _ = candidate(nm.snapshot(), state["history"], config["profiles"])
    if again != selected:
        return skip("Connection state changed immediately before recovery")
    state["last_attempt"] = clock()
    reset_observation(state)
    save(state)  # Persist BEFORE invoking nmcli, even if it fails or is killed.
    log(f"Retrying saved profile {selected} on {nm.interface}")
    result = nm.activate(selected)
    after = nm.snapshot()
    if after["state"] == 100:
        clear_failure(state["history"])
        state["history"]["success_us"] = int(clock() * 1_000_000)
        state["history"]["attempt_uuid"] = after["uuid"]
        message = "Recovered using the existing saved profile" if after["uuid"] == selected else "Wi-Fi connected through another profile"
        record_reason(state, message)
        save(state)
        return "recovered" if after["uuid"] == selected else "connected"
    record_reason(state, f"Activation returned {result}; further eligible retries at least five minutes apart")
    save(state)
    return "attempted"


def atomic_write(path, content, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as output:
            os.fchmod(output.fileno(), mode)
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def load_state(path, current_boot, now):
    if not path.exists():
        return fresh_state(current_boot, now)
    try:
        state = json.loads(path.read_text())
        if state["boot"] != current_boot:
            return fresh_state(current_boot, now)
        if state["version"] != 2:
            raise ValueError
        for key in ("first_seen", "last_attempt", "last_scan"):
            value = state[key]
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= now):
                raise ValueError
        for key in ("watch_uuid",):
            if state[key] is not None and not valid_uuid(state[key]):
                raise ValueError
        history = state["history"]
        for key in new_history():
            value = history[key]
            if key.endswith("_us") and (type(value) is not int or value < 0):
                raise ValueError
            if key.endswith("uuid") and value is not None and not valid_uuid(value):
                raise ValueError
            if key in ("cursor", "invocation") and value is not None and not isinstance(value, str):
                raise ValueError
        if not isinstance(history["failures"], dict):
            raise ValueError
        for profile_uuid, failure in history["failures"].items():
            if not valid_uuid(profile_uuid) or not isinstance(failure, dict):
                raise ValueError
            for key in ("at_us", "real_us"):
                if type(failure.get(key)) is not int or failure[key] < 0:
                    raise ValueError
        return state
    except (OSError, ValueError, TypeError, KeyError):
        log("Runtime state unreadable; rebuilding evidence with a five-minute cooldown")
        return fresh_state(current_boot, now, damaged=True)


def require_root():
    if os.geteuid() != 0:
        raise RecoveryError("Run this command with sudo python3")


def owned(path):
    if path.is_symlink() or (path.exists() and (not path.is_file() or MARKER not in path.read_text())):
        raise RecoveryError(f"Refusing to replace or remove unrelated path: {path}")


def validate_config(config):
    if (not isinstance(config, dict) or config.get("version") != 2
            or not re.fullmatch(r"[A-Za-z0-9_.-]{1,15}", config.get("interface", ""))
            or not isinstance(config.get("profiles"), dict) or not config["profiles"]):
        raise RecoveryError("Invalid installed configuration")
    for key, value in config["profiles"].items():
        if not valid_uuid(key) or value not in TRUSTED_SSIDS:
            raise RecoveryError("Invalid allowed profile configuration")
    return config


def installed_config():
    owned(SCRIPT)
    if not SCRIPT.exists():
        raise RecoveryError("Recovery checker is not installed")
    lines = [line for line in SCRIPT.read_text().splitlines() if line.startswith("INSTALL_CONFIG = ")]
    if len(lines) != 1:
        raise RecoveryError("Cannot read installed configuration")
    return validate_config(ast.literal_eval(lines[0].split("=", 1)[1].strip()))


def check():
    require_root()
    config = validate_config(INSTALL_CONFIG)
    if RUNTIME.is_symlink():
        raise RecoveryError("Unsafe runtime directory")
    RUNTIME.mkdir(mode=0o700, parents=True, exist_ok=True)
    if RUNTIME.stat().st_uid != 0 or RUNTIME.stat().st_mode & 0o077:
        raise RecoveryError("Runtime directory must be private to root")
    fd = os.open(RUNTIME / "lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        state = load_state(STATE_FILE, boot_id(), time.monotonic())
        def save(value):
            atomic_write(STATE_FILE, json.dumps(value) + "\n", 0o600)
        try:
            recover_once(NetworkManager(Runner(), config["interface"]), state, config, save)
        except RecoveryError as error:
            reset_observation(state)
            record_reason(state, str(error))
            save(state)


def discover(runner, interface=None, selected_profiles=None):
    discovery = NetworkManager(runner, "")
    if not interface:
        listing = discovery.query("-f", "DEVICE,TYPE,STATE", "device", "status")
        interfaces = []
        for line in listing.splitlines():
            parts = line.split(":")
            if len(parts) == 3 and parts[1] == "wifi" and parts[2] in ("connected", "connected (externally)"):
                interfaces.append(parts[0])
        if len(interfaces) != 1:
            raise RecoveryError("Connect to the trusted Wi-Fi first; if multiple adapters are connected, add --interface NAME")
        interface = interfaces[0]
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,15}", interface):
        raise RecoveryError("Unsupported interface name")
    nm = NetworkManager(runner, interface)
    current = nm.snapshot()
    if (current["type"] != "wifi" or current["state"] != 100 or current["radio"] != "enabled"
            or current["autoconnect"] != "yes" or not valid_uuid(current["uuid"])):
        raise RecoveryError("Install while the intended Wi-Fi adapter is connected with autoconnect enabled")
    active_profile = nm.profile(current["uuid"])
    active_ssid, _ = validate_profile(active_profile, interface, active=True)
    if not nm.has_saved_password(current["uuid"]):
        raise RecoveryError("The working connection has no system-managed saved password")
    if selected_profiles:
        candidates = list(dict.fromkeys(value.lower() for value in selected_profiles))
        if current["uuid"] not in candidates:
            raise RecoveryError("Explicit --profile list must include the currently working profile UUID")
    else:
        listing = nm.query("-f", "UUID,TYPE", "connection", "show")
        candidates = [line.split(":")[0].lower() for line in listing.splitlines()
                      if line.endswith(":802-11-wireless")]
    profiles = {}
    for profile_uuid in candidates:
        if not valid_uuid(profile_uuid):
            raise RecoveryError("Invalid profile UUID")
        try:
            profile = nm.profile(profile_uuid)
            ssid, _ = validate_profile(profile, interface, active=profile_uuid == current["uuid"])
            # Default enrollment covers this currently verified SSID and duplicates.
            # Other networks require explicit --profile selection while connected.
            if not selected_profiles and ssid != active_ssid:
                continue
            if not nm.has_saved_password(profile_uuid):
                raise RecoveryError("No system-managed saved password")
            profiles[profile_uuid] = ssid
        except RecoveryError as error:
            if selected_profiles or profile_uuid == current["uuid"]:
                raise
            log(f"Excluded saved profile {profile_uuid}: {error}")
    if current["uuid"] not in profiles:
        raise RecoveryError("Could not verify the working profile")
    return validate_config({"version": 2, "host": socket.gethostname(),
                            "interface": interface, "profiles": profiles})


def unit_texts(interface):
    service = f"""# {MARKER}
[Unit]
Description=Recover Wi-Fi saved-password authentication stalls
After=NetworkManager.service
ConditionPathExists=/sys/class/net/{interface}

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {SCRIPT} check
TimeoutStartSec=120
RuntimeDirectory={NAME}
RuntimeDirectoryMode=0700
RuntimeDirectoryPreserve=yes
UMask=0077
NoNewPrivileges=yes
PrivateTmp=yes
ProtectHome=yes
ProtectSystem=strict
ReadWritePaths={RUNTIME}
"""
    timer = f"""# {MARKER}
[Unit]
Description=Check for Wi-Fi authentication stalls every minute

[Timer]
OnActiveSec=30s
OnUnitInactiveSec=60s
AccuracySec=5s
Unit={NAME}.service

[Install]
WantedBy=timers.target
"""
    return service, timer


def control(runner, *args, accepted=(0,)):
    return runner.run([SYSTEMCTL, *args], timeout=20, accepted=accepted)


def install(interface=None, selected_profiles=None):
    require_root()
    for tool in (NMCLI, SYSTEMCTL, JOURNALCTL, "/usr/bin/python3"):
        if not Path(tool).is_file():
            raise RecoveryError(f"Required program unavailable: {tool}; no packages installed")
    legacy = UNIT_DIR / "puddlejumper-wifi-recovery.timer"
    if legacy.exists():
        raise RecoveryError("Earlier recovery timer found. First run: sudo python3 /usr/local/libexec/puddlejumper-wifi-recovery.py --uninstall")
    runner = Runner(240)
    config = discover(runner, interface, selected_profiles)
    for key, ssid in config["profiles"].items():
        print(f"Allowed: {config['interface']} / {ssid} / {key}")
    # Check journal access before writing files; never force a network outage.
    trial = fresh_state(boot_id(), time.monotonic())
    update_history(runner, trial, config["interface"])
    source_lines = Path(__file__).resolve().read_text().splitlines()
    replacements = 0
    for number, line in enumerate(source_lines):
        if line.startswith("INSTALL_CONFIG = "):
            source_lines[number] = "INSTALL_CONFIG = " + repr(config)
            replacements += 1
    if replacements != 1:
        raise RecoveryError("Installer source has an unexpected configuration layout")
    source = "\n".join(source_lines) + "\n"
    compile(source, str(SCRIPT), "exec")
    service, timer = unit_texts(config["interface"])
    files = {SCRIPT: (source, 0o755), UNIT_DIR / (NAME + ".service"): (service, 0o644),
             UNIT_DIR / (NAME + ".timer"): (timer, 0o644)}
    for path in files:
        owned(path)
    before = {path: (path.read_text(), path.stat().st_mode & 0o777) if path.exists() else None for path in files}
    was_enabled = control(runner, "is-enabled", NAME + ".timer", accepted=(0, 1, 3, 4)).returncode == 0
    was_active = control(runner, "is-active", NAME + ".timer", accepted=(0, 1, 3, 4)).returncode == 0
    try:
        if before[UNIT_DIR / (NAME + ".timer")] is not None:
            control(runner, "stop", NAME + ".timer")
            control(runner, "stop", NAME + ".service")
        for path, (content, mode) in files.items():
            atomic_write(path, content, mode)
        restorecon = Path("/usr/sbin/restorecon")
        if restorecon.is_file():
            runner.run([str(restorecon), *(str(path) for path in files)])
        control(runner, "daemon-reload")
        control(runner, "enable", "--now", NAME + ".timer")
        control(runner, "is-enabled", NAME + ".timer")
        control(runner, "is-active", NAME + ".timer")
    except Exception:
        rollback = Runner(120)
        for action in ("stop", "disable"):
            control(rollback, action, NAME + ".timer", accepted=tuple(range(256)))
        control(rollback, "stop", NAME + ".service", accepted=tuple(range(256)))
        for path, previous in before.items():
            if previous is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, *previous)
        control(rollback, "daemon-reload")
        if was_enabled:
            control(rollback, "enable", NAME + ".timer")
        if was_active:
            control(rollback, "start", NAME + ".timer")
        raise
    print("Installed. Timer enabled and active; no reboot needed.")
    print("Recovery during a real credential stall has not yet been verified on this machine.")
    print(f"Status: sudo python3 {SCRIPT} status")
    print(f"Logs:   sudo journalctl -u {NAME}.service --since today --no-pager")


def status():
    require_root()
    config = installed_config()
    runner = Runner(40)
    print(f"Version: {VERSION}; interface: {config['interface']}")
    for profile_uuid, ssid in config["profiles"].items():
        print(f"Allowed: {ssid} / {profile_uuid}")
    for operation in ("is-enabled", "is-active"):
        result = control(runner, operation, NAME + ".timer", accepted=(0, 1, 3, 4))
        print(f"Timer {operation}: {result.stdout.strip()}")
    current = NetworkManager(runner, config["interface"]).snapshot()
    print(f"Wi-Fi state: {current['state']}; active profile: {current['uuid'] or 'none'}")
    if STATE_FILE.exists():
        state = load_state(STATE_FILE, boot_id(), time.monotonic())
        print(f"Last check: {state.get('last_reason') or 'not recorded'}")
        if state["last_attempt"] is not None:
            print(f"Last recovery attempt: {int(time.monotonic() - state['last_attempt'])} seconds ago")
    print(f"Logs: sudo journalctl -u {NAME}.service --since today --no-pager")


def uninstall():
    require_root()
    files = [SCRIPT, UNIT_DIR / (NAME + ".service"), UNIT_DIR / (NAME + ".timer")]
    for path in files:
        owned(path)
    runner = Runner(90)
    if files[2].exists():
        control(runner, "disable", "--now", NAME + ".timer")
    if files[1].exists():
        control(runner, "stop", NAME + ".service")
    for path in files:
        path.unlink(missing_ok=True)
    if RUNTIME.is_symlink():
        raise RecoveryError("Unexpected runtime symlink; files removed but runtime cleanup stopped")
    for name in ("state.json", "lock"):
        (RUNTIME / name).unlink(missing_ok=True)
    if RUNTIME.exists():
        RUNTIME.rmdir()
    control(runner, "daemon-reload")
    print("Removed the checker, service, timer, and runtime state.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="action", required=True)
    installer = sub.add_parser("install", help="Install using this machine's existing working Wi-Fi")
    installer.add_argument("--interface", help="Wi-Fi interface; automatically detected if omitted")
    installer.add_argument("--profile", action="append", help="Allow an existing UUID; repeat to specify all allowed profiles")
    sub.add_parser("status", help="Show installed configuration and timer state")
    sub.add_parser("uninstall", help="Remove this addition")
    sub.add_parser("check", help="Internal timer entry point; use install for setup")
    args = parser.parse_args()
    try:
        if args.action == "install":
            install(args.interface, args.profile)
        else:
            globals()[args.action]()
        return 0
    except (RecoveryError, OSError, ValueError, SyntaxError) as error:
        log(str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
