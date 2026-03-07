import time
import sys

def infinite_while_loop():
    """
    这是一个会导致无限死循环的while循环程序
    
    警告：运行此程序将创建一个永不停止的循环
    可以通过以下方式中断程序：
    1. 在终端中按 Ctrl+C
    2. 通过任务管理器强制结束进程
    """
    
    print("警告：这是一个无限循环程序！")
    print("程序将在3秒后开始运行...")
    print("如需停止，请按 Ctrl+C")
    print("-" * 40)
    
    # 3秒倒计时
    for i in range(3, 0, -1):
        print(f"倒计时: {i}秒")
        time.sleep(1)
    
    print("\n无限循环开始！")
    print("按 Ctrl+C 停止程序")
    print("-" * 40)
    
    # 计数器，用于显示循环次数
    counter = 0
    
    try:
        # 无限while循环 - 这是危险的核心代码
        # 条件永远为True，所以循环永远不会停止
        while True:
            counter += 1
            # 每隔1000次循环输出一次，避免过多输出
            if counter % 1000 == 0:
                print(f"循环次数: {counter:,} 次")
                # 短暂暂停，避免过度占用CPU
                time.sleep(0.01)
            
    except KeyboardInterrupt:
        # 捕获Ctrl+C中断信号
        print(f"\n\n程序被用户中断！")
        print(f"总循环次数: {counter:,} 次")
        return
    
    except Exception as e:
        print(f"\n程序异常: {e}")
        return

# 安全运行函数
def safe_run():
    """
    安全地运行无限循环程序
    """
    try:
        infinite_while_loop()
    except KeyboardInterrupt:
        print("程序已安全终止")
    finally:
        print("程序执行完毕")

# 主程序入口
if __name__ == "__main__":
    print("=" * 50)
    print("无限死循环演示程序")
    print("=" * 50)
    
    # 添加一个确认步骤，增加安全性
    response = input("是否要运行无限循环程序？(yes/no): ").strip().lower()
    
    if response == 'yes' or response == 'y':
        safe_run()
    else:
        print("程序已取消运行")
        sys.exit(0)
