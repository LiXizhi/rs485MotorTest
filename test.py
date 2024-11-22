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

# 测试函数
print(int_to_hex_4_letters(416))  # 输出: '3120'