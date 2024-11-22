import serial.tools.list_ports

def list_serial_ports():
    # 获取所有可用的串口
    ports = serial.tools.list_ports.comports()
    
    # 打印每个串口的信息
    for port in ports:
        print(f"设备: {port.device}, 描述: {port.description}, VID:PID {port.vid}:{port.pid}")

if __name__ == "__main__":
    list_serial_ports()