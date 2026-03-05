#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Study - 主入口文件
支持多种智能代理的命令行交互界面
"""

import sys
import argparse
from agents.travel_agent import run_travel_agent


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔════════════════════════════════════════╗
║         Agent Study - 智能助手系统        ║
╚════════════════════════════════════════╝
"""
    print(banner)


def print_menu():
    """打印功能菜单"""
    menu = """
请选择一个智能代理:
[1] 旅行助手 - 查询天气和推荐旅游景点
[0] 退出程序
"""
    print(menu)


def run_travel_agent_interactive():
    """运行旅行助手代理"""
    print("\n=== 旅行助手 ===")
    print("你可以查询城市天气和获取旅游景点推荐")
    print("输入示例:")
    print("  - 查询今天北京的天气")
    print("  - 北京有什么好玩的景点")
    print("  - 根据上海的天气推荐景点\n")
    
    while True:
        try:
            user_input = input("请输入你的问题 (输入 'q' 返回主菜单): ").strip()
            if user_input.lower() in ['q', 'quit', 'exit']:
                print("返回主菜单...\n")
                break
            
            if not user_input:
                print("输入不能为空，请重新输入。\n")
                continue
            
            # 调用旅行代理
            from agents.travel_agent import run_travel_agent
            run_travel_agent(user_prompt=user_input)
            print()
            
        except KeyboardInterrupt:
            print("\n\n检测到中断，返回主菜单...\n")
            break
        except Exception as e:
            print(f"\n发生错误: {e}\n")


def main():
    """主函数"""
    print_banner()
    
    # 支持命令行参数模式
    parser = argparse.ArgumentParser(description='Agent Study - 智能助手系统')
    parser.add_argument('--agent', type=str, help='指定要运行的代理类型 (travel)')
    parser.add_argument('--query', type=str, help='直接执行查询，不进入交互模式')
    
    args = parser.parse_args()
    
    # 命令行直接执行模式
    if args.agent:
        if args.agent == 'travel':
            if args.query:
                print(f"执行查询: {args.query}\n")
                run_travel_agent(user_prompt=args.query)
            else:
                run_travel_agent_interactive()
        else:
            print(f"未知的代理类型: {args.agent}")
            sys.exit(1)
        return
    
    # 交互式菜单模式
    while True:
        print_menu()
        try:
            choice = input("请输入选项编号: ").strip()
            
            if choice == '1':
                run_travel_agent_interactive()
            elif choice == '0':
                print("感谢使用 Agent Study，再见！")
                break
            else:
                print("无效的选项，请重新选择。\n")
                
        except KeyboardInterrupt:
            print("\n\n程序已退出。")
            sys.exit(0)
        except Exception as e:
            print(f"\n发生错误: {e}\n")


if __name__ == "__main__":
    main()
