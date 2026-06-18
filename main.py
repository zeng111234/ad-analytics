#!/usr/bin/env python3
"""
智能广告效果分析与优化平台 - 主程序入口
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def main():
    """主函数"""
    print("=" * 60)
    print("智能广告效果分析与优化平台")
    print("=" * 60)
    print("\n欢迎使用广告效果分析工具！")
    print("\n主要功能：")
    print("1. 数据看板 - 查看广告效果数据")
    print("2. 效果预测 - 预测广告点击率、转化率")
    print("3. A/B测试 - 分析测试结果")
    print("4. 出价优化 - 获取出价建议")
    print("5. 素材分析 - 分析素材效果")
    print("\n请选择功能（1-5）或输入 'quit' 退出：")
    
    while True:
        try:
            choice = input("> ").strip().lower()
            
            if choice == 'quit' or choice == 'q':
                print("感谢使用，再见！")
                break
            elif choice == '1':
                print("\n启动数据看板...")
                print("请运行: streamlit run visualization/dashboard.py")
                break
            elif choice == '2':
                print("\n启动效果预测...")
                print("功能开发中...")
            elif choice == '3':
                print("\n启动A/B测试分析...")
                print("功能开发中...")
            elif choice == '4':
                print("\n启动出价优化...")
                print("功能开发中...")
            elif choice == '5':
                print("\n启动素材分析...")
                print("功能开发中...")
            else:
                print("无效选择，请输入1-5或'quit'退出")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    main()