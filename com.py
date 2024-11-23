import serial
import serial.tools.list_ports
import binascii
import keyboard
import time

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

def list_serial_ports():
    # 获取所有可用的串口
    ports = serial.tools.list_ports.comports()
    
    # 打印每个串口的信息
    for i, port in enumerate(ports, start=1):
        print(f"{i}: 设备: {port.device}, 描述: {port.description}, VID:PID {port.vid}:{port.pid}")
    return ports
def read_serial_data(serial_port):
    if serial_port.in_waiting > 0:
        data = serial_port.read(serial_port.in_waiting)
        return data.hex().upper() # 将二进制数据转换为十六进制字符串，并转换为大写
    return ""
def wait_and_read_serial_data(serial_port):
    for _ in range(50):
        data = read_serial_data(serial_port)
        if data:
            return data
        time.sleep(0.02)  # 等待一段时间后再次检查，避免 CPU 占用过高
def send_hexdata_string(serial_port, hex_string):
    data = binascii.unhexlify(hex_string)
    crc_checksum = crc16_modbus(data)
    crc_bytes = crc16_to_bytes(crc_checksum)
    hex_string = hex_string + crc_bytes.hex().upper()
    print(f"发送: {hex_string}")
    # 发送数据
    serial_port.write(binascii.unhexlify(hex_string))

    #response = read_serial_data(serial_port)
    response = wait_and_read_serial_data(serial_port)
    print(f"<<收到: {response}")
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

motor1Speed = 0
motor2Speed = 0

def updateMotors(serial_port):
    global motor1Speed, motor2Speed
    send_hexdata_string(serial_port, f"030309{int_to_hex_4_letters(motor1Speed)}00000000000000")
    time.sleep(0.1)
    send_hexdata_string(serial_port, f"010309{int_to_hex_4_letters(motor2Speed)}00000000000000")
def addMotorSpeed(serial_port, motor1Delta, motor2Delta):
    global motor1Speed, motor2Speed
    motor1Speed += motor1Delta
    motor2Speed += motor2Delta
    # 确保最小速度为 0，最大速度为 1024
    motor1Speed = max(0, min(1024, motor1Speed))
    motor2Speed = max(0, min(1024, motor2Speed))

    updateMotors(serial_port)

def setMotorSpeed(serial_port, motor1, motor2):
    global motor1Speed, motor2Speed
    motor1Speed = motor1
    motor2Speed = motor2
    updateMotors(serial_port)

def main():
    ports = list_serial_ports()
    if not ports:
        print("未发现任何串口设备")
        return

    while True:
        try:
            choice = int(input("请选择一个串口（输入编号）: "))
            if 1 <= choice <= len(ports):
                selected_port = ports[choice - 1].device
                break
            else:
                print("无效的选择，请重新输入。")
        except ValueError:
            print("无效的输入，请输入一个数字。")

    baudrate = 9600  # 根据实际情况设置波特率
    with serial.Serial(selected_port, baudrate, timeout=1) as ser:
        if not ser.is_open:
            print("打开串口失败")
            return

        print("w key 32; s key -32; q key 退出")
        while True:
            if keyboard.is_pressed('w'):
                addMotorSpeed(ser, 32, 32)
                time.sleep(0.05)  # 防止按键重复触发
            elif keyboard.is_pressed('s'):
                addMotorSpeed(ser, -32, -32)
                time.sleep(0.05)  # 防止按键重复触发
            elif keyboard.is_pressed('q'):
                break

if __name__ == "__main__":
    main()