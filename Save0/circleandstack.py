from __builtins__ import *
from circle_helper import helper_function

# =====================================
# 成就1: 循环导入 (Import Cycle)
# =====================================
def achieve_import_cycle():
    # """触发循环导入成就"""
    clear()
    # 这个文件导入 circle_helper.py
    # circle_helper.py 又导入 circleandstack.py
    # 形成循环导入
    import circle_helper
    
    # 做一些简单任务证明代码运行
    plant(Entities.Bush)
    harvest()

# =====================================
# 成就2: 栈溢出 (Stack Overflow)
# =====================================
def recursive_function(depth):
    # """无限递归函数,触发栈溢出"""
    # 种植一个灌木来显示进度
    if depth % 100 == 0:
        plant(Entities.Bush)
    
    # 递归调用自己,不设置终止条件
    return recursive_function(depth + 1)

def achieve_stack_overflow():
    # """触发栈溢出成就"""
    clear()
    till()
    
    # 开始无限递归
    recursive_function(0)

# =====================================
# 主程序
# =====================================
def main():
    # 选择要实现的成就
    achievement_mode = 1  # 1=循环导入, 2=栈溢出
    
    if achievement_mode == 1:
        achieve_import_cycle()
    elif achievement_mode == 2:
        achieve_stack_overflow()

if __name__ == "__main__":
    main()
