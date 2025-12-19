import csv
import os
import sys

# 设置标准输出编码为 utf-8，防止 Windows 终端乱码
sys.stdout.reconfigure(encoding='utf-8')

# 定义输入和输出文件路径
input_file = r"D:\projects\WebCrawler\prosetting\output\cs2_prosettings.csv"
output_file = r"D:\projects\WebCrawler\prosetting\output\player_mouse_settings.csv"

# 需要提取的列名
target_columns = ["Player", "Mouse", "HZ", "DPI", "Sens", "eDPI", "Zoom Sens"]

try:
    if not os.path.exists(input_file):
        print(f"错误: 找不到输入文件 {input_file}")
        sys.exit(1)

    print(f"正在读取: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        
        # 检查 CSV 是否包含所有目标列
        missing_columns = [col for col in target_columns if col not in reader.fieldnames]
        if missing_columns:
            print(f"错误: 输入文件中缺少以下列: {missing_columns}")
            print(f"可用列: {reader.fieldnames}")
            sys.exit(1)
            
        # 提取数据
        extracted_data = []
        for row in reader:
            filtered_row = {col: row[col] for col in target_columns}
            extracted_data.append(filtered_row)
            
    print(f"已提取 {len(extracted_data)} 行数据。")

    # 写入新 CSV
    if extracted_data:
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=target_columns)
            writer.writeheader()
            writer.writerows(extracted_data)
        print(f"新文件已保存到: {output_file}")
    else:
        print("没有提取到任何数据。")

except Exception as e:
    print(f"发生错误: {e}")
