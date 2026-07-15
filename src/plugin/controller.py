"""
App controller
"""
import datas


class AppController:
    """
    应用控制接口
    """
    def hide(self):
        datas.root.withdraw()

    def show(self):
        datas.root.deiconify()
