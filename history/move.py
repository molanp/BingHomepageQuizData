#!/usr/bin/env python3
# move_all_json_pathlib.py

from pathlib import Path
import re

def move_date_json_files():
    """
    遍历指定目录，将所有 yyyy-mm-dd.json 格式的文件移动到 yyyy/mm/dd/dd.json
    
    Args:
        root_dir (str or Path): 要遍历的根目录，默认为当前目录
    """
    # 转换为 Path 对象
    root_path = Path(__file__).parent
    print(root_path)

    # 统计处理结果
    processed_count = 0
    error_count = 0

    # 遍历当前目录下的所有文件
    for file_path in root_path.iterdir():
        # 只处理文件，跳过目录
        if not file_path.is_file():
            continue

        # 获取文件名
        filename = file_path.name

        if match := re.match(r'^(\d{4})-(\d{2})-(\d{2})\.json$', filename):
            try:
                # 提取年月日
                year, month, day = match.groups()

                # 构建目标目录和文件路径
                target_dir = root_path / year / month
                target_file = target_dir / f"{day}.json"

                # 如果目标文件已存在，跳过
                if target_file.exists():
                    print(f"警告: 目标文件 {target_file} 已存在，跳过 {filename}")
                    error_count += 1
                    continue

                # 创建目标目录（包括中间路径）
                target_dir.mkdir(parents=True, exist_ok=True)

                # 移动文件
                file_path.rename(target_file)
                print(f"成功移动: {filename} -> {target_file}")
                processed_count += 1

            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")
                error_count += 1

    # 输出统计信息
    print("\n处理完成:")
    print(f"  成功移动: {processed_count} 个文件")
    print(f"  错误/跳过: {error_count} 个文件")

def main():
    """主函数"""
    print("开始遍历当前目录并移动符合条件的JSON文件...")
    move_date_json_files()
    print("操作完成!")

if __name__ == "__main__":
    main()