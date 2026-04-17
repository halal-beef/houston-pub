import os
from time import sleep

import usb.core
import usb.backend.libusb1

import logging

from modules.hexdump import hexdump

logger  = logging.getLogger(__name__)

response_cnt = 0

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

            if os.name != "nt":
                if device.is_kernel_driver_active(0):
                    device.detach_kernel_driver(0)

            usb.util.claim_interface(device, 0)

            return device
        
def query_and_save_response(device, output_folder_path, console_output):
    output_data = []

    if not output_folder_path and not console_output:
        return

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

    if output_folder_path:
        logger.debug(f"Saving device response {response_cnt} to {output_folder_path}/response_{response_cnt}.bin")
        output = open(f"{output_folder_path}/responnse_{response_cnt}", "wb")
        output.write(output_bytes)
        output.close()
        logger.info("Saved")
