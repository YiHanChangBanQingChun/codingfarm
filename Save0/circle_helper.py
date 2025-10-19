# 循环导入辅助文件
from __builtins__ import *
from circleandstack import achieve_import_cycle

def helper_function():
    plant(Entities.Bush)
    # 调用主文件的函数,形成真正的循环依赖
    achieve_import_cycle()
    