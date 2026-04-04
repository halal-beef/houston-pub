#!/bin/bash

# Check for root
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root."
    exit 1
fi

RULES=/etc/udev/rules.d/51-android.rules
LINES=(
    "# Samsung Exynos USB Boot Mode"
    "SUBSYSTEM=="usb", ATTR{idVendor}=="04e8", ATTR{idProduct}=="1234", MODE="0660", GROUP="dialout""
)

# Create file if needed
if [ ! -f "$RULES" ]; then
    touch "$RULES"
fi

# Append lines if not present already
for LINE in "${LINES[@]}"; do
    if ! grep -Fxq "$LINE" "$RULES"; then
        echo "$LINE" >> "$RULES"
    fi
done

# Reload udev rules
udevadm control --reload
udevadm trigger
