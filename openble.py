from bleak import BleakScanner, BleakClient
import asyncio
import binascii
import keyboard
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

async def list_ble_devices():
    devices = await BleakScanner.discover()
    for i, d in enumerate(devices):
        print(f"{i + 1}: {d}")
    return devices

async def select_device(devices):
    while True:
        try:
            choice = int(input("请选择一个设备（输入编号）: "))
            if 1 <= choice <= len(devices):
                return devices[choice - 1]
            else:
                print("无效的选择，请重新输入。")
        except ValueError:
            print("无效的输入，请输入一个数字。")

async def send_hexdata_string(client, hex_string):
    data = binascii.unhexlify(hex_string)
    crc_checksum = crc16_modbus(data)
    crc_bytes = crc16_to_bytes(crc_checksum)
    hex_string = hex_string + crc_bytes.hex().upper()
    print(hex_string)
    # send by concatenating the data and CRC bytes
    await send_hex_string(client, hex_string)
async def send_hex_string(client, hex_string):
    try:
        data = bytes.fromhex(hex_string)
        # 假设我们有一个特定的特征（UUID）用于发送数据
        # 请根据实际情况修改特征的 UUID
        characteristic_uuid = "FFE2"  # 示例特征 UUID
        await client.write_gatt_char(characteristic_uuid, data)
        print("数据发送成功")
    except Exception as e:
        print(f"数据发送失败: {e}")

motor1Speed = 0
motor2Speed = 0

def int_to_hex_4_letters(num):
    # 确保输入是一个整数
    if not isinstance(num, int):
        raise ValueError("Input must be an integer")
    
    # 将整数转换为 4 位的十六进制字符串
    hex_str = f"{num:04x}"
    
    # 交换高低字节
    low_bytes = hex_str[2:4]
    high_bytes = hex_str[0:2]
    result = low_bytes + high_bytes
    
    return result
async def updateMotors(client):
    global motor1Speed, motor2Speed
    await send_hexdata_string(client, f"030309{int_to_hex_4_letters(motor1Speed)}00000000000000")
    await send_hexdata_string(client, f"010309{int_to_hex_4_letters(motor2Speed)}00000000000000")
async def addMotorSpeed(client, motor1Delta, motor2Delta):
    global motor1Speed, motor2Speed
    motor1Speed += motor1Delta
    motor2Speed += motor2Delta
    # ensure min speed is 0, max speed is 1024
    motor1Speed = max(0, min(1024, motor1Speed))
    motor2Speed = max(0, min(1024, motor2Speed))

    await updateMotors(client)
async def setMotorSpeed(client, motor1, motor2):
    global motor1Speed, motor2Speed
    motor1Speed = motor1
    motor2Speed = motor2
    await updateMotors(client)
async def main():
    devices = await list_ble_devices()
    if not devices:
        print("未发现任何设备")
        return

    selected_device = await select_device(devices)
    print(f"连接到设备: {selected_device}")

    async with BleakClient(selected_device) as client:
        if not client.is_connected:
            print("连接失败")
            return

        print("w key 32; s key -32; q key 退出")
        while True:
            if keyboard.is_pressed('w'):
                await addMotorSpeed(client, 32, 32)
                await asyncio.sleep(0.1)  # 防止按键重复触发
            elif keyboard.is_pressed('s'):
                await addMotorSpeed(client, -32, -32)
                await asyncio.sleep(0.1)  # 防止按键重复触发
            elif keyboard.is_pressed('q'):
                break

        #while True:
        #    hex_string = input("请输入十六进制字符串 (输入 'q' 退出): ")
        #    if hex_string.lower() == 'q':
        #        break
        #    await send_hexdata_string(client, hex_string)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())