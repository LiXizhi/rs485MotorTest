import tkinter as tk
from tkinter import ttk
import com  # 导入 com.py 中的代码
import serial
import sys

class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see(tk.END)  # 自动滚动到底部

def on_up_button_click():
    com.addMotorSpeed(ser, 32, 32)
    print("上按钮点击")

def on_down_button_click():
    com.addMotorSpeed(ser, -32, -32)
    print("下按钮点击")

def on_port_select(event):
    global ser
    selected_port = port_var.get()
    try:
        ser = serial.Serial(selected_port, 9600, timeout=1)
        if not ser.is_open:
            status_label.config(text="打开串口失败")
        else:
            status_label.config(text=f"已连接到 {selected_port}")
    except Exception as e:
        status_label.config(text=f"连接失败: {e}")
        print(f"连接失败: {e}")

def main():
    global port_var, status_label, ser
    root = tk.Tk()
    root.title("串口控制")

    # 创建下拉列表
    port_var = tk.StringVar()
    port_combobox = ttk.Combobox(root, textvariable=port_var)
    port_combobox['values'] = [f"{port.device}" for i, port in enumerate(com.list_serial_ports(), start=1)]
    port_combobox.bind('<<ComboboxSelected>>', on_port_select)
    port_combobox.grid(row=0, column=0, padx=10, pady=10)

    # 创建状态标签
    status_label = tk.Label(root, text="请选择一个串口")
    status_label.grid(row=1, column=0, padx=10, pady=10)

    # 创建按钮
    up_button = tk.Button(root, text="上(w)", command=on_up_button_click)
    up_button.grid(row=2, column=0, padx=10, pady=10)

    down_button = tk.Button(root, text="下(s)", command=on_down_button_click)
    down_button.grid(row=3, column=0, padx=10, pady=10)

    # 创建文本区域
    output_text = tk.Text(root, height=10, width=50)
    output_text.grid(row=4, column=0, padx=10, pady=10)

    # 重定向标准输出和标准错误
    sys.stdout = TextRedirector(output_text, "stdout")
    sys.stderr = TextRedirector(output_text, "stderr")

    # 绑定 W 和 S 键
    root.bind('w', lambda event: on_up_button_click())
    root.bind('s', lambda event: on_down_button_click())

    root.mainloop()

if __name__ == "__main__":
    main()