import os
from time import sleep

import usb.core
import usb.backend.libusb1

import logging

import threading

from modules.hexdump import hexdump

logger  = logging.getLogger(__name__)

response_cnt = 0

def usb_wait_msg(stop_event):
    attempts = 0

    while not stop_event.wait(timeout=1):
        print(".", end="", flush=True)
        attempts += 1

        if attempts % 15 == 0:
            print()
            logger.debug("Tip: Plug in your device with the power button pressed.")


def find_device():
    usb_backend = None
    if os.name == "nt":
        usb_backend = usb.backend.libusb1.get_backend(find_library=lambda x: libusb.dll._name)

    stop_msg = threading.Event()
    dot_thread = threading.Thread(target=usb_wait_msg, args=(stop_msg,), daemon=True)
    dot_thread.start()

    while True:
        device = usb.core.find(idVendor=0x04e8, idProduct=0x1234, backend=usb_backend)
        if device is not None:
            break

    stop_msg.set()
    dot_thread.join()
    print()

    if os.name != "nt":
        if device.is_kernel_driver_active(0):
            device.detach_kernel_driver(0)
        usb.util.claim_interface(device, 0)

    return device
 
def query_and_save_response(device, output_folder_path, console_output, debug_mode):
    output_data = []

    if not output_folder_path and not console_output:
        return

    while True:
        try:
            data = device.read(0x81, 512, timeout=25)
            output_data.append(data)
        except:
            break

    output_bytes = bytearray()
    for data in output_data:
        output_bytes.extend(data)

    if console_output == True:
        logger.info("Device Response:")
        if debug_mode:
            hexdump(output_bytes)
        else:
            for line in output_bytes.split(b'\x00'):
                if line:
                    logger.critical(line.decode('utf-8', errors='replace'))

    if output_folder_path:
        logger.debug(f"Saving device response {response_cnt} to {output_folder_path}/response_{response_cnt}.bin")
        output = open(f"{output_folder_path}/response_{response_cnt}.bin", "wb")
        output.write(output_bytes)
        output.close()
        logger.info("Saved")
