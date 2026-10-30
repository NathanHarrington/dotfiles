#!/usr/bin/env python3
"""
Collect and analyze kilo power-recovery state with a single SSH login.

By default this connects to the "kilo" SSH host once, runs a remote collector,
then analyzes the collected sections locally. Save the raw capture with
--raw-out and re-analyze it later with --analyze-raw.
"""

from __future__ import annotations

import argparse
import base64
import dataclasses
import pathlib
import re
import shutil
import subprocess
import sys
from typing import Iterable


REMOTE_COLLECTOR = r"""#!/usr/bin/env bash
set +e
export LC_ALL=C

b64_file() {
    if command -v base64 >/dev/null 2>&1; then
        base64 "$1" | tr -d '\n'
    elif command -v python3 >/dev/null 2>&1; then
        python3 - "$1" <<'PY'
import base64
import pathlib
import sys

sys.stdout.write(base64.b64encode(pathlib.Path(sys.argv[1]).read_bytes()).decode("ascii"))
PY
    else
        printf 'base64 unavailable'
    fi
}

run_here() {
    local name out err status script

    name="$1"
    script="$(cat)"
    out="$(mktemp "${TMPDIR:-/tmp}/kilo-audit-out.XXXXXX")" || exit 1
    err="$(mktemp "${TMPDIR:-/tmp}/kilo-audit-err.XXXXXX")" || exit 1

    bash -c "$script" >"$out" 2>"$err"
    status=$?

    printf '__KILO_AUDIT_BEGIN__ %s %s\n' "$name" "$status"
    printf '__KILO_AUDIT_STDOUT__\n'
    b64_file "$out"
    printf '\n__KILO_AUDIT_STDERR__\n'
    b64_file "$err"
    printf '\n__KILO_AUDIT_END__ %s\n' "$name"

    rm -f "$out" "$err"
}

run_here metadata <<'SECTION'
printf 'generated_at=%s\n' "$(date -Is 2>/dev/null || date)"
printf 'hostname=%s\n' "$(hostname 2>/dev/null)"
printf 'hostname_short=%s\n' "$(hostname -s 2>/dev/null || hostname 2>/dev/null)"
printf 'user=%s\n' "$(id 2>/dev/null)"
printf '\n-- hostnamectl --\n'
hostnamectl 2>/dev/null || true
SECTION

run_here command_presence <<'SECTION'
for cmd in \
    xidlehook xautolock xset xss-lock i3lock i3-msg jq pactl \
    systemctl loginctl upower journalctl swapon free rpm fwupdmgr \
    sudo grep find awk sed timeout base64 python3
do
    if command -v "$cmd" >/dev/null 2>&1; then
        printf '%s=%s\n' "$cmd" "$(command -v "$cmd")"
    else
        printf '%s=MISSING\n' "$cmd"
    fi
done
SECTION

run_here list_power_settings <<'SECTION'
helper="$HOME/projects/dotfiles/scripts/list-power-settings.sh"
if [ -x "$helper" ]; then
    "$helper"
else
    printf 'missing_helper=%s\n' "$helper"
fi
SECTION

run_here idle_runtime <<'SECTION'
printf '== idle processes ==\n'
pgrep -af 'xautolock|xidlehook|suspend-on-battery-idle|xss-lock|i3lock' 2>/dev/null || true

printf '\n== i3 config idle lines: ~/.config/i3/config ==\n'
grep -nE 'suspend-on-battery-idle|xss-lock|i3lock|xautolock|xidlehook' "$HOME/.config/i3/config" 2>/dev/null || true

printf '\n== i3 config idle lines: repo i3/config ==\n'
grep -nE 'suspend-on-battery-idle|xss-lock|i3lock|xautolock|xidlehook' "$HOME/projects/dotfiles/i3/config" 2>/dev/null || true
SECTION

run_here hibernate_kernel <<'SECTION'
printf 'state='
cat /sys/power/state 2>/dev/null || true
printf 'disk='
cat /sys/power/disk 2>/dev/null || true
printf 'resume='
cat /sys/power/resume 2>/dev/null || true

printf '\n== swap ==\n'
swapon --show --output NAME,TYPE,SIZE,USED,PRIO 2>/dev/null || true
free -h 2>/dev/null | sed -n '1,3p'

printf '\n== cmdline resume bits ==\n'
tr ' ' '\n' </proc/cmdline 2>/dev/null | grep -E '^(resume|resume_offset|root|rd\.luks)=' || true

printf '\n== sleep config ==\n'
systemd-analyze cat-config systemd/sleep.conf 2>/dev/null | grep -E '^[#[:space:]]*(Allow|Hibernate|Suspend|MemorySleep|HibernateMode|HibernateState|Resume)' || true
SECTION

run_here logind_config <<'SECTION'
systemd-analyze cat-config systemd/logind.conf 2>/dev/null || true
SECTION

run_here power_supply <<'SECTION'
for d in /sys/class/power_supply/*; do
    [ -d "$d" ] || continue
    printf '\n-- %s --\n' "${d##*/}"
    for f in type online status capacity model_name manufacturer; do
        [ -r "$d/$f" ] && printf '%s=%s\n' "$f" "$(cat "$d/$f" 2>/dev/null)"
    done
done

printf '\n== upower dump ==\n'
upower -d 2>/dev/null || true
SECTION

run_here journals <<'SECTION'
printf '== suspend-on-battery-idle journal ==\n'
journalctl -b -t suspend-on-battery-idle --no-pager -n 160 2>/dev/null || true

printf '\n== hibernate journal ==\n'
journalctl -b -u systemd-hibernate.service -u hibernate.target --no-pager -n 120 2>/dev/null || true

printf '\n== wake/resume journal hints ==\n'
journalctl -b --no-pager 2>/dev/null |
    grep -Ei 'hibernate|sleep operation|waking up from system sleep state S4|wake requested|OnByAc|AC attach|ACPI: PM|PM: hibernation|HibernateLocation' |
    tail -220 || true
SECTION

run_here firmware_sysfs <<'SECTION'
printf '== firmware attributes ==\n'
if [ -d /sys/class/firmware-attributes ]; then
    find /sys/class/firmware-attributes -maxdepth 5 -type f 2>/dev/null | sed -n '1,240p'
    printf '\n== current values matching power/ac/wake ==\n'
    for f in /sys/class/firmware-attributes/*/attributes/*/current_value; do
        [ -r "$f" ] || continue
        attr=${f%/current_value}
        name=${attr##*/}
        case "$name" in
            *[Pp]ower*|*[Aa][Cc]*|*[Ww]ake*|*[Bb]oot*|*[Ll]id*)
                printf '%s=%s\n' "$name" "$(cat "$f" 2>/dev/null)"
                ;;
        esac
    done
else
    printf 'firmware-attributes not present\n'
fi

printf '\n== thinkpad modules ==\n'
lsmod 2>/dev/null | grep -E 'think_lmi|thinkpad_acpi|firmware_attributes' || true

printf '\n== dmi ==\n'
for f in sys_vendor product_name product_version product_family bios_version bios_date; do
    printf '%s=' "$f"
    cat "/sys/class/dmi/id/$f" 2>/dev/null || true
done
SECTION

run_here firmware_bios_settings <<'SECTION'
if command -v fwupdmgr >/dev/null 2>&1; then
    if command -v timeout >/dev/null 2>&1; then
        timeout 20 fwupdmgr get-bios-settings 2>&1
    else
        fwupdmgr get-bios-settings 2>&1
    fi
else
    printf 'fwupdmgr=MISSING\n'
fi
SECTION

run_here firmware_bios_settings_sudo <<'SECTION'
if ! command -v fwupdmgr >/dev/null 2>&1; then
    printf 'fwupdmgr=MISSING\n'
elif ! command -v sudo >/dev/null 2>&1; then
    printf 'sudo=MISSING\n'
elif sudo -n true 2>/dev/null; then
    if command -v timeout >/dev/null 2>&1; then
        timeout 20 sudo -n fwupdmgr get-bios-settings 2>&1
    else
        sudo -n fwupdmgr get-bios-settings 2>&1
    fi
else
    printf 'sudo_nopasswd=no\n'
fi
SECTION

run_here early_luks <<'SECTION'
printf '== dracut conf files ==\n'
for d in /etc/dracut.conf.d /etc/cmdline.d; do
    [ -d "$d" ] || continue
    printf '\n-- %s --\n' "$d"
    find "$d" -maxdepth 1 -type f -print 2>/dev/null | sort | while IFS= read -r f; do
        printf '\n### %s ###\n' "$f"
        sed -n '1,160p' "$f" 2>/dev/null || true
    done
done

printf '\n== early ssh/network grep ==\n'
grep -RInE 'sshd|dropbear|authorized_keys|rd\.neednet|ip=|ifname=|bootdev=|network-manager|NetworkManager|iwd|wpa' \
    /etc/dracut.conf.d /etc/cmdline.d /etc/default/grub 2>/dev/null || true

printf '\n== dracut packages ==\n'
printf 'rpm_dracut_network='
rpm -q dracut-network 2>/dev/null || true
printf 'rpm_dracut_sshd='
rpm -q dracut-sshd 2>/dev/null || true

printf '\n== kernel cmdline network/ssh bits ==\n'
tr ' ' '\n' </proc/cmdline 2>/dev/null | grep -Ei 'ip=|rd\.neednet|ssh|sshd|dropbear|ifname|bootdev|wifi|wpa|iwd|network' || true

printf '\n== initramfs files ==\n'
ls -1 /boot/initramfs-* 2>/dev/null | tail -8 || true
SECTION

run_here wake_sources <<'SECTION'
for f in /sys/devices/platform/thinkpad_acpi/wakeup_reason \
         /sys/devices/platform/thinkpad_acpi/wakeup_hotunplug_complete \
         /proc/acpi/wakeup
do
    [ -r "$f" ] || continue
    printf '\n-- %s --\n' "$f"
    cat "$f" 2>/dev/null || true
done
SECTION
"""


BEGIN_RE = re.compile(r"^__KILO_AUDIT_BEGIN__ ([A-Za-z0-9_.-]+) (-?\d+)$")
END_RE = re.compile(r"^__KILO_AUDIT_END__ ([A-Za-z0-9_.-]+)$")


@dataclasses.dataclass
class Section:
    name: str
    status: int
    stdout: str
    stderr: str


@dataclasses.dataclass
class Check:
    status: str
    name: str
    detail: str


def decode_b64(payload: str) -> str:
    if not payload:
        return ""
    return base64.b64decode(payload.encode("ascii"), validate=False).decode(
        "utf-8", errors="replace"
    )


def parse_capture(raw: str) -> dict[str, Section]:
    sections: dict[str, Section] = {}
    lines = raw.splitlines()
    index = 0

    while index < len(lines):
        begin = BEGIN_RE.match(lines[index])
        if not begin:
            index += 1
            continue

        name = begin.group(1)
        status = int(begin.group(2))
        index += 1

        if index >= len(lines) or lines[index] != "__KILO_AUDIT_STDOUT__":
            raise ValueError(f"Malformed section {name}: missing stdout marker")
        index += 1

        stdout_lines: list[str] = []
        while index < len(lines) and lines[index] != "__KILO_AUDIT_STDERR__":
            stdout_lines.append(lines[index])
            index += 1

        if index >= len(lines):
            raise ValueError(f"Malformed section {name}: missing stderr marker")
        index += 1

        stderr_lines: list[str] = []
        while index < len(lines) and not END_RE.match(lines[index]):
            stderr_lines.append(lines[index])
            index += 1

        if index >= len(lines):
            raise ValueError(f"Malformed section {name}: missing end marker")

        end = END_RE.match(lines[index])
        assert end is not None
        if end.group(1) != name:
            raise ValueError(f"Malformed section {name}: ended as {end.group(1)}")

        sections[name] = Section(
            name=name,
            status=status,
            stdout=decode_b64("".join(stdout_lines)),
            stderr=decode_b64("".join(stderr_lines)),
        )
        index += 1

    if not sections:
        raise ValueError("No audit sections found in capture")

    return sections


def section_text(sections: dict[str, Section], name: str) -> str:
    section = sections.get(name)
    return section.stdout if section else ""


def kv_from_lines(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def command_present(sections: dict[str, Section], command: str) -> bool:
    commands = kv_from_lines(section_text(sections, "command_presence"))
    return commands.get(command, "MISSING") != "MISSING"


def extract_bios_setting(text: str, setting: str) -> tuple[bool, str | None, str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != f"{setting}:":
            continue

        block: list[str] = []
        for block_line in lines[index : index + 80]:
            if block and re.match(r"^\S[^:]*:$", block_line):
                break
            block.append(block_line)

        current_value = None
        for block_line in block:
            match = re.match(r"\s*Current Value:\s*(.*)$", block_line)
            if match:
                current_value = match.group(1).strip()
                break
        return True, current_value, "\n".join(block)

    return False, None, ""


def compact_lines(text: str, limit: int = 4) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""
    if len(lines) <= limit:
        return "; ".join(lines)
    return "; ".join(lines[:limit]) + f"; ... ({len(lines) - limit} more lines)"


def analyze(sections: dict[str, Section]) -> list[Check]:
    checks: list[Check] = []

    metadata = section_text(sections, "metadata")
    metadata_values = kv_from_lines(metadata)
    host = metadata_values.get("hostname_short") or metadata_values.get("hostname")
    if host == "kilo":
        checks.append(Check("PASS", "Connected host", "remote hostname is kilo"))
    else:
        checks.append(Check("WARN", "Connected host", f"remote hostname is {host or 'unknown'}"))

    list_power = section_text(sections, "list_power_settings")
    idle_runtime = section_text(sections, "idle_runtime")
    hibernate = section_text(sections, "hibernate_kernel")
    journals = section_text(sections, "journals")
    early_luks = section_text(sections, "early_luks")

    if re.search(r"^state=.*\bdisk\b", hibernate, re.MULTILINE):
        checks.append(Check("PASS", "Kernel hibernate support", "/sys/power/state includes disk"))
    else:
        checks.append(Check("FAIL", "Kernel hibernate support", "/sys/power/state does not include disk"))

    resume_has_device = re.search(r"^resume=(?!0:0\b).+", hibernate, re.MULTILINE)
    cmdline_has_resume = re.search(r"^resume=", hibernate, re.MULTILINE)
    cmdline_has_offset = re.search(r"^resume_offset=", hibernate, re.MULTILINE)
    swapfile = re.search(r"^/swapfile\s+file\s+", hibernate, re.MULTILINE)
    if resume_has_device and cmdline_has_resume and cmdline_has_offset and swapfile:
        checks.append(
            Check(
                "PASS",
                "Hibernate resume target",
                "resume device, resume_offset, and /swapfile are configured",
            )
        )
    else:
        missing = []
        if not resume_has_device:
            missing.append("/sys/power/resume")
        if not cmdline_has_resume:
            missing.append("kernel resume=")
        if not cmdline_has_offset:
            missing.append("kernel resume_offset=")
        if not swapfile:
            missing.append("/swapfile")
        checks.append(Check("FAIL", "Hibernate resume target", "missing " + ", ".join(missing)))

    helper_ready = all(
        needle in list_power
        for needle in [
            "Started from i3:                   yes",
            "Watcher process:                   running",
            "Battery sleep action:              hibernate after 10m",
        ]
    )
    watcher_named = re.search(r"Idle watcher:\s+(xautolock|xidlehook)", list_power)
    process_present = "xautolock" in idle_runtime or "xidlehook" in idle_runtime
    if helper_ready and watcher_named and process_present:
        checks.append(
            Check(
                "PASS",
                "Battery idle hibernate helper",
                f"{watcher_named.group(1)} is running and configured for hibernate after 10m",
            )
        )
    else:
        checks.append(
            Check(
                "FAIL",
                "Battery idle hibernate helper",
                "helper is not fully configured/running for 10-minute hibernate",
            )
        )

    if command_present(sections, "xautolock") or command_present(sections, "xidlehook"):
        checks.append(Check("PASS", "Idle watcher installed", "xautolock or xidlehook is installed"))
    else:
        checks.append(Check("FAIL", "Idle watcher installed", "install xautolock or xidlehook"))

    if command_present(sections, "xset"):
        checks.append(Check("PASS", "X DPMS helper", "xset is installed"))
    else:
        checks.append(
            Check(
                "WARN",
                "X DPMS helper",
                "xset is missing; 10-minute hibernate can still work, but helper-managed screen-off cannot",
            )
        )

    lid_hibernates = all(
        needle in list_power
        for needle in [
            "Lid close:                         hibernate (configured)",
            "Lid close on AC:                   hibernate (configured)",
            "Lid close while docked:            hibernate (configured)",
        ]
    )
    if lid_hibernates:
        checks.append(Check("PASS", "Lid hibernate policy", "all lid-close paths are configured for hibernate"))
    else:
        checks.append(Check("WARN", "Lid hibernate policy", "one or more lid-close paths are not hibernate"))

    ran_hibernate = "idle threshold reached on battery power; running hibernate" in journals
    returned_hibernate = "System returned from sleep operation 'hibernate'" in journals
    if ran_hibernate and returned_hibernate:
        checks.append(
            Check(
                "PASS",
                "Observed hibernate cycle",
                "journal shows idle-triggered hibernate and a later successful resume",
            )
        )
    elif ran_hibernate:
        checks.append(Check("WARN", "Observed hibernate cycle", "journal shows hibernate requested, but no resume confirmation"))
    else:
        checks.append(Check("WARN", "Observed hibernate cycle", "no idle-triggered hibernate in current boot journal"))

    firmware_text = "\n".join(
        [
            section_text(sections, "firmware_bios_settings_sudo"),
            section_text(sections, "firmware_bios_settings"),
            section_text(sections, "firmware_sysfs"),
        ]
    )
    found_on_ac, on_ac_value, on_ac_block = extract_bios_setting(firmware_text, "OnByAcAttach")
    if not found_on_ac:
        checks.append(
            Check(
                "UNKNOWN",
                "Power on when AC is attached",
                "OnByAcAttach was not exposed by the collected firmware interfaces",
            )
        )
    elif on_ac_value and on_ac_value.lower() in {"enable", "enabled", "1", "yes", "on"}:
        checks.append(Check("PASS", "Power on when AC is attached", f"OnByAcAttach current value is {on_ac_value}"))
    elif on_ac_value and on_ac_value.lower() in {"disable", "disabled", "0", "no", "off"}:
        checks.append(Check("FAIL", "Power on when AC is attached", f"OnByAcAttach current value is {on_ac_value}"))
    else:
        detail = on_ac_value or compact_lines(on_ac_block) or "current value unavailable"
        checks.append(
            Check(
                "UNKNOWN",
                "Power on when AC is attached",
                f"OnByAcAttach exists, but current value was not readable noninteractively: {detail}",
            )
        )

    early_indicators: list[str] = []
    if re.search(r"^rpm_dracut_sshd=dracut-sshd-", early_luks, re.MULTILINE):
        early_indicators.append("dracut-sshd installed")
    if re.search(r"\b(dropbear|authorized_keys|rd\.neednet|ifname=|bootdev=)\b", early_luks, re.IGNORECASE):
        early_indicators.append("early SSH/network config present")
    if re.search(r"^ip=", early_luks, re.MULTILINE):
        early_indicators.append("kernel cmdline ip= present")

    if early_indicators:
        checks.append(Check("FAIL", "Early-LUKS SSH", ", ".join(sorted(set(early_indicators)))))
    else:
        checks.append(Check("PASS", "Early-LUKS SSH", "no dracut SSH/network unlock indicators found"))

    ac_online = re.search(r"-- AC --.*?online=1", section_text(sections, "power_supply"), re.S)
    if ac_online:
        checks.append(Check("INFO", "Current AC state", "AC is currently online"))
    else:
        checks.append(Check("INFO", "Current AC state", "AC is not currently online or not reported"))

    return checks


def resolve_tailscale_ip(host: str) -> str | None:
    if not shutil.which("tailscale"):
        return None

    try:
        result = subprocess.run(
            ["tailscale", "ip", "-4", host],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    if result.returncode != 0:
        return None

    ip = result.stdout.strip().splitlines()
    return ip[0].strip() if ip and ip[0].strip() else None


def build_ssh_command(args: argparse.Namespace) -> list[str]:
    command = ["ssh"]

    if args.ssh_config:
        command.extend(["-F", str(pathlib.Path(args.ssh_config).expanduser())])

    if args.batch_mode:
        command.extend(["-o", "BatchMode=yes"])

    if args.strict_host_key_checking:
        command.extend(["-o", f"StrictHostKeyChecking={args.strict_host_key_checking}"])

    if args.known_hosts:
        command.extend(["-o", f"UserKnownHostsFile={args.known_hosts}"])

    host_name = args.host_name
    if not host_name and args.tailscale_resolve:
        host_name = resolve_tailscale_ip(args.host)

    if host_name:
        command.extend(["-o", f"HostName={host_name}"])

    if args.identity_file:
        command.extend(["-o", f"IdentityFile={pathlib.Path(args.identity_file).expanduser()}"])
        command.extend(["-o", "IdentitiesOnly=yes"])

    for ssh_option in args.ssh_option:
        command.extend(["-o", ssh_option])

    command.extend([args.host, "bash -s --"])
    return command


def collect(args: argparse.Namespace) -> str:
    ssh_command = build_ssh_command(args)
    result = subprocess.run(
        ssh_command,
        input=REMOTE_COLLECTOR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    if result.returncode != 0:
        print("SSH collection failed", file=sys.stderr)
        print("Command: " + " ".join(ssh_command), file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        raise SystemExit(result.returncode)

    return result.stdout


def print_report(sections: dict[str, Section], checks: Iterable[Check]) -> int:
    metadata_values = kv_from_lines(section_text(sections, "metadata"))
    generated_at = metadata_values.get("generated_at", "unknown")
    host = metadata_values.get("hostname_short") or metadata_values.get("hostname") or "unknown"

    print(f"Power recovery audit for {host}")
    print(f"Collected: {generated_at}")
    print(f"Sections: {len(sections)}")
    print()

    exit_code = 0
    for check in checks:
        print(f"{check.status:7} {check.name}: {check.detail}")
        if check.status == "FAIL":
            exit_code = 1

    section_errors = [
        section
        for section in sections.values()
        if section.status != 0 and section.name not in {"firmware_bios_settings_sudo"}
    ]
    if section_errors:
        print()
        print("Collection notes:")
        for section in section_errors:
            detail = compact_lines(section.stderr or section.stdout, limit=2)
            print(f"WARN    section {section.name} exited {section.status}: {detail}")

    return exit_code


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect and analyze kilo hibernate/power-recovery state with one SSH login."
    )
    parser.add_argument("--host", default="kilo", help="SSH host alias to connect to")
    parser.add_argument(
        "--host-name",
        help="Override SSH HostName, for example kilo's Tailscale IP",
    )
    parser.add_argument(
        "--ssh-config",
        default=str(pathlib.Path.home() / ".ssh" / "config"),
        help="SSH config file to use; pass '' to use ssh defaults",
    )
    parser.add_argument("--identity-file", help="Optional SSH private key")
    parser.add_argument(
        "--known-hosts",
        help="Optional UserKnownHostsFile path",
    )
    parser.add_argument(
        "--strict-host-key-checking",
        default="accept-new",
        help="Value for StrictHostKeyChecking, default: accept-new",
    )
    parser.add_argument(
        "--ssh-option",
        action="append",
        default=[],
        help="Additional ssh -o option; may be passed multiple times",
    )
    parser.add_argument(
        "--no-batch-mode",
        dest="batch_mode",
        action="store_false",
        help="Allow SSH to prompt for passwords/passphrases",
    )
    parser.set_defaults(batch_mode=True)
    parser.add_argument(
        "--no-tailscale-resolve",
        dest="tailscale_resolve",
        action="store_false",
        help="Do not resolve --host with local 'tailscale ip -4'",
    )
    parser.set_defaults(tailscale_resolve=True)
    parser.add_argument("--raw-out", help="Save raw sectioned capture to this file")
    parser.add_argument("--analyze-raw", help="Analyze a previously saved raw capture instead of SSH")
    parser.add_argument("--print-raw", action="store_true", help="Print raw capture after collection")

    args = parser.parse_args(argv)
    if args.ssh_config == "":
        args.ssh_config = None
    return args


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    if args.analyze_raw:
        raw = pathlib.Path(args.analyze_raw).read_text(encoding="utf-8", errors="replace")
    else:
        raw = collect(args)
        if args.raw_out:
            pathlib.Path(args.raw_out).write_text(raw, encoding="utf-8")
        if args.print_raw:
            print(raw)

    sections = parse_capture(raw)
    checks = analyze(sections)
    return print_report(sections, checks)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
