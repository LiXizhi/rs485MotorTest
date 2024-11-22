import asyncio  
import logging  
from bleak import BleakScanner  

# Enable debug logging  
logging.basicConfig(level=logging.DEBUG)  

async def list_ble_devices():  
    print("Scanning for BLE devices...")  
    devices = await BleakScanner.discover(timeout=10)  
    if devices:  
        print("\nFound BLE devices:")  
        for i, device in enumerate(devices, 1):  
            print(f"{i}. Name: {device.name}, Address: {device.address}, RSSI: {device.rssi}")  
    else:  
        print("No BLE devices found.")  

if __name__ == "__main__":  
    asyncio.run(list_ble_devices())  