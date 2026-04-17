import logging

logger  = logging.getLogger(__name__)

def hexdump(data, length=16):
    for i in range(0, len(data), length):
        chunk = data[i:i+length]
        hex_str = ' '.join(f'{b:02X}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        logger.critical(f'{i:08X}  {hex_str:<{length*3}}  {ascii_str}')