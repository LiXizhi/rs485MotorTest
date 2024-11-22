import sys
import binascii

def crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def crc16_to_bytes(crc: int) -> bytes:
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

def main():
    if len(sys.argv) > 1:
        hex_string = sys.argv[1]
    else:
        hex_string = input("请输入十六进制字符串: ")
    try:
        data = binascii.unhexlify(hex_string)
        crc_checksum = crc16_modbus(data)
        crc_bytes = crc16_to_bytes(crc_checksum)
        print(f"CRC16-Modbus校验和: {crc_checksum:04X}")
        print(f"CRC16-Modbus校验和字节: {hex_string.upper()}{crc_bytes.hex().upper()}")
    except binascii.Error:
        print("输入的十六进制字符串无效，请重新输入。")

if __name__ == "__main__":
    main()