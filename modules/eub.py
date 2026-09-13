import struct
import logging
import sys

from modules.usb_helper import query_and_save_response, read_bytes

logger  = logging.getLogger(__name__)

def write_u32(value):
    return struct.pack('<I', value)

def write_header(data, size):
    data[0:4] = b"\x1BDNW"
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

def send_file(device, file_path, output_folder_path, console_output, debug_mode):
    logger.warning(f"Uploading file {file_path}")
    file = load_file(file_path)
    file_size = len(file)

    write_header(file, file_size)
    calculate_checksum(file)

    is_new_dnw = device.idProduct == 0x1100
    if is_new_dnw:
        while True:
            req = read_bytes(device)
            if len(req) == 0:
                continue
            if req.startswith(b'\neub:req:'):
                logger.warning(f"=> Device requested {req.decode()[18:-1]}")
                while True:
                    chunk = read_bytes(device)
                    req += chunk
                    if len(chunk) == 1:
                        break
                query_and_save_response(device, output_folder_path, console_output, debug_mode, req)
                break
            query_and_save_response(device, output_folder_path, console_output, debug_mode, req)
    ret = device.write(2, file, timeout=5000)

    if is_new_dnw:
        res = read_bytes(device)
        query_and_save_response(device, output_folder_path, console_output, debug_mode, res)
    else:
        query_and_save_response(device, output_folder_path, console_output, debug_mode)

    if ret != file_size or (is_new_dnw and res.startswith(b'\neub:nak:')):
        logger.critical(f"=> Houston, we have a problem, the file was rejected.")
        sys.exit(-1)
    else:
        logger.info(f"=> File sent sucessfully!")
