# SoC specific quirks
QUIRK_USB_DROP = 1 << 0

# SoC data
SOC_DATA = {
    "Exynos9840\00": {
        "rx_address": 0x02022000,
        "usb_struct_offset": 0x0480,
        "quirks": 0
    },

    "Exynos9830\00": {
        "rx_address": 0x02022000,
        "usb_struct_offset": 0x0480,
        "quirks": 0
    },

    "Exynos3830\00": {
        "rx_address": 0x02022000,
        "usb_struct_offset": 0x0480,
        "quirks": 0
    },

    "Exynos9810\00": {
        "rx_address": 0x02021800,
        "usb_struct_offset": 0x0280,
        "quirks": 0
    },

    "Exynos9610\00": {
        "rx_address": 0x02021800,
        "usb_struct_offset": 0x0280,
        "quirks": 0
    },

    "Exynos8890\00": {
        "rx_address": 0x02021800,
        "usb_struct_offset": 0x0460,
        "quirks": QUIRK_USB_DROP
    },

    "Exynos7885\00": {
        "rx_address": 0x02021800,
        "usb_struct_offset": 0x0280,
        "quirks": 0
    },

    "Exynos7870\00": {
        "rx_address": 0x02021800,
        "usb_struct_offset": 0x0350,
        "quirks": 0
    },
}
