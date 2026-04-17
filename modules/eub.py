import struct
import logging
import sys

from modules.usb_helper import query_and_save_response

logger  = logging.getLogger(__name__)

def write_u32(value):
    return struct.pack('<I', value)

def write_header(data, size):
    data[4:8] = write_u32(size)

def calculate_checksum(data):
    checksum = sum(data[8:-2]) & 0xFFFF
    data[-2:] = struct.pack('<H', checksum)
    return checksum

def load_file(file_input):
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

def send_file(device, file_path, output_folder_path, console_output):
    logger.warning("Uploading file.")
    file = load_file(file_path)
    file_size = len(file)

    write_header(file, file_size)
    calculate_checksum(file)

    ret = device.write(2, file, timeout=50000)

    query_and_save_response(device, output_folder_path, console_output)

    if ret != file_size:
        logger.critical(f"=> Houston, we have a problem, the file was rejected.")
        sys.exit(-1)
    else:
        logger.info(f"=> File sent sucessfully!")
