import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
from bleak import BleakClient, discover

class BLEApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BLE Client")
        
        self.device_var = tk.StringVar()
        self.device_list = ttk.Combobox(root, textvariable=self.device_var)
        self.device_list.pack(pady=10)
        
        self.refresh_button = tk.Button(root, text="Refresh", command=self.refresh_devices)
        self.refresh_button.pack(pady=5)
        
        self.connect_button = tk.Button(root, text="Connect", command=self.connect_device)
        self.connect_button.pack(pady=5)
        
        self.send_var = tk.StringVar()
        self.send_entry = tk.Entry(root, textvariable=self.send_var)
        self.send_entry.pack(pady=5)
        
        self.send_button = tk.Button(root, text="Send", command=self.send_data)
        self.send_button.pack(pady=5)
        
        self.receive_label = tk.Label(root, text="Received Data:")
        self.receive_label.pack(pady=5)
        
        self.receive_text = tk.Text(root, height=10, width=50)
        self.receive_text.pack(pady=5)
        
        self.client = None
        self.device_address = None
        
        # 使用 asyncio.create_task 来异步执行 scan_devices 方法
        self.root.after(0, lambda: asyncio.run(self.scan_devices()))

    async def scan_devices(self):
        devices = await discover()
        self.device_list['values'] = [f"{d.name} ({d.address})" for d in devices]

    def refresh_devices(self):
        asyncio.create_task(self.scan_devices())

    def connect_device(self):
        selected_device = self.device_var.get()
        if not selected_device:
            messagebox.showwarning("Warning", "Please select a device.")
            return
        
        self.device_address = selected_device.split(" ")[-1].strip("()")
        asyncio.create_task(self.connect_to_device())

    async def connect_to_device(self):
        try:
            self.client = BleakClient(self.device_address)
            await self.client.connect()
            messagebox.showinfo("Info", "Connected to device.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")

    def send_data(self):
        data = self.send_var.get()
        if not data:
            messagebox.showwarning("Warning", "Please enter data to send.")
            return
        
        try:
            data_bytes = bytes.fromhex(data)
            asyncio.create_task(self.send_to_device(data_bytes))
        except ValueError:
            messagebox.showerror("Error", "Invalid hex string.")

    async def send_to_device(self, data):
        try:
            await self.client.write_gatt_char("your_characteristic_uuid", data)
            messagebox.showinfo("Info", "Data sent successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send data: {e}")

    async def receive_data(self):
        while True:
            if self.client.is_connected:
                try:
                    data = await self.client.read_gatt_char("your_characteristic_uuid")
                    self.receive_text.insert(tk.END, data.hex() + "\n")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to receive data: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = BLEApp(root)
    root.mainloop()