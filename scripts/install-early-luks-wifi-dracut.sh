#!/usr/bin/env bash
set -euo pipefail

module_dir=/usr/lib/dracut/modules.d/91wpa-supplicant-initrd
dracut_conf=/etc/dracut.conf.d/91-early-ssh-wifi.conf
nm_connection_dir=/etc/NetworkManager/system-connections

if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
  echo "Run with sudo: sudo $0" >&2
  exit 1
fi

for required in \
  /etc/wpa_supplicant/wpa_supplicant.conf \
  /etc/dbus-1/system.d/wpa_supplicant.conf \
  /usr/share/dbus-1/system-services/fi.w1.wpa_supplicant1.service; do
  if [[ ! -e "$required" ]]; then
    echo "Missing required wpa_supplicant file: $required" >&2
    exit 1
  fi
done

wifi_driver_modules="$(
  for iface in /sys/class/net/*; do
    [[ -d "$iface/wireless" ]] || continue
    module_path="$(readlink -f "$iface/device/driver/module" 2>/dev/null)" || continue
    module_name="$(basename "$module_path")"
    printf '%s\n' "$module_name"
    find "$module_path/holders" -mindepth 1 -maxdepth 1 -printf '%f\n' 2>/dev/null
  done | sort -u | xargs
)"

if [[ -z "$wifi_driver_modules" ]]; then
  echo "No Wi-Fi driver module found under /sys/class/net/*/wireless" >&2
  exit 1
fi

mapfile -t initrd_nmconnections < <(
  find "$nm_connection_dir" -maxdepth 1 -type f -name 'initrd-*.nmconnection' -print | sort
)

if ((${#initrd_nmconnections[@]} == 0)); then
  echo "No initrd NetworkManager profiles found in $nm_connection_dir" >&2
  exit 1
fi

install_items=()

for profile in "${initrd_nmconnections[@]}"; do
  if [[ "$profile" =~ [[:space:]] ]]; then
    echo "Initrd profile paths must not contain whitespace: $profile" >&2
    echo "Reclone it with a simple name like initrd-home before rebuilding initramfs." >&2
    exit 1
  fi
  uuid="$(sed -n 's/^uuid=//p' "$profile" | sed -n '1p')"
  if [[ -z "$uuid" ]]; then
    echo "Could not find connection UUID in $profile" >&2
    exit 1
  fi
  nmcli connection load "$profile" >/dev/null 2>&1 || true
  nmcli connection modify uuid "$uuid" \
    connection.autoconnect yes \
    connection.permissions "" \
    connection.interface-name "" \
    wifi.cloned-mac-address permanent
  install_items+=("$profile")
done

install_items_line=
for item in "${install_items[@]}"; do
  install_items_line+=" $item"
done

install -d -m 755 "$module_dir"

cat >"$module_dir/module-setup.sh" <<'EOF'
#!/usr/bin/bash

check() {
    require_binaries wpa_supplicant || return 1
    return 255
}

depends() {
    echo network-manager dbus systemd
    return 0
}

install() {
    local _nm_version

    _nm_version=${NM_VERSION:-$(NetworkManager --version)}

    inst_multiple -o /usr/bin/wpa_supplicant /usr/sbin/wpa_supplicant
    inst_multiple -o \
        /etc/sysconfig/wpa_supplicant \
        /etc/wpa_supplicant/wpa_supplicant.conf \
        /etc/dbus-1/system.d/wpa_supplicant.conf \
        /usr/share/dbus-1/system-services/fi.w1.wpa_supplicant1.service
    inst_libdir_file "NetworkManager/$_nm_version/libnm-device-plugin-wifi.so"
    inst_simple "$moddir/wpa_supplicant.service" "$systemdsystemunitdir/wpa_supplicant.service"
    inst_simple "$moddir/early-luks-wifi-activate.service" "$systemdsystemunitdir/early-luks-wifi-activate.service"
    inst_script "$moddir/early-luks-wifi-activate.sh" /usr/libexec/early-luks-wifi-activate
    $SYSTEMCTL -q --root "$initdir" enable wpa_supplicant.service
    $SYSTEMCTL -q --root "$initdir" enable early-luks-wifi-activate.service
}
EOF

cat >"$module_dir/wpa_supplicant.service" <<'EOF'
[Unit]
Description=WPA supplicant for NetworkManager in initrd
DefaultDependencies=no
Wants=dbus.service
After=dracut-cmdline.service dbus.service
Before=nm-initrd.service network.target
ConditionPathExists=/run/NetworkManager/initrd/neednet

[Service]
Type=dbus
BusName=fi.w1.wpa_supplicant1
EnvironmentFile=-/etc/sysconfig/wpa_supplicant
ExecStart=/usr/sbin/wpa_supplicant -c /etc/wpa_supplicant/wpa_supplicant.conf -u $INTERFACES $DRIVERS $OTHER_ARGS
Restart=on-failure

[Install]
WantedBy=initrd.target
EOF

cat >"$module_dir/early-luks-wifi-activate.service" <<'EOF'
[Unit]
Description=Activate initrd Wi-Fi profiles for early LUKS unlock
DefaultDependencies=no
Requires=nm-initrd.service
Wants=wpa_supplicant.service
After=wpa_supplicant.service nm-initrd.service
Before=nm-wait-online-initrd.service dracut-initqueue.service network-online.target
ConditionPathExists=/run/NetworkManager/initrd/neednet

[Service]
Type=oneshot
ExecStart=/usr/libexec/early-luks-wifi-activate

[Install]
WantedBy=initrd.target
EOF

cat >"$module_dir/early-luks-wifi-activate.sh" <<'EOF'
#!/usr/bin/bash
set -u

echo "early-luks-wifi: reloading initrd NetworkManager profiles"

for profile in /etc/NetworkManager/system-connections/initrd-*.nmconnection; do
    [ -f "$profile" ] || continue
    nmcli connection load "$profile" || true
done

nmcli connection reload || true
nmcli radio wifi on || true

echo "early-luks-wifi: devices visible to NetworkManager"
nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device status || true

connections="$(
    nmcli -t -f NAME,TYPE connection show 2>/dev/null |
        while IFS=: read -r name type; do
            case "$name:$type" in
                initrd-*:802-11-wireless) printf '%s\n' "$name" ;;
            esac
        done
)"

if [ -z "$connections" ]; then
    echo "early-luks-wifi: no initrd Wi-Fi connections are visible to NetworkManager"
    nmcli -t -f NAME,TYPE,AUTOCONNECT connection show || true
    exit 1
fi

for attempt in 1 2 3; do
    echo "early-luks-wifi: activation attempt $attempt"
    for connection in $connections; do
        echo "early-luks-wifi: trying $connection"
        if nmcli --wait 30 connection up id "$connection"; then
            echo "early-luks-wifi: activated $connection"
            nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device status || true
            exit 0
        fi
    done
    sleep 3
done

echo "early-luks-wifi: failed to activate any initrd Wi-Fi connection"
nmcli -t -f NAME,TYPE,AUTOCONNECT connection show || true
nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device status || true
exit 1
EOF

chmod 755 "$module_dir/module-setup.sh"
chmod 644 "$module_dir/wpa_supplicant.service"
chmod 644 "$module_dir/early-luks-wifi-activate.service"
chmod 755 "$module_dir/early-luks-wifi-activate.sh"

install -d -m 755 "$(dirname "$dracut_conf")"
{
  printf '%s\n' 'add_dracutmodules+=" network network-manager wpa-supplicant-initrd "'
  printf 'force_drivers+=" %s "\n' "$wifi_driver_modules"
  printf 'install_items+="%s "\n' "$install_items_line"
} >"$dracut_conf"
chmod 644 "$dracut_conf"

if command -v restorecon >/dev/null 2>&1; then
  restorecon -Rv "$module_dir" "$dracut_conf" "$nm_connection_dir"
fi

echo "Installed dracut module: $module_dir"
echo "Wrote dracut config: $dracut_conf"
echo "Wi-Fi driver modules: $wifi_driver_modules"
echo "Initrd NetworkManager profiles:"
printf '  %s\n' "${initrd_nmconnections[@]}"
