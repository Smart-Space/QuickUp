# ./ui/editor/base.py
"""
Shared state and initialization for editor modules
"""
from weakref import WeakValueDictionary
from tinui.theme.tinuidark import TinUIDark
from tinui.theme.tinuilight import TinUILight

import datas
import config

accent_color = None
theme = None
themename = ''
screen_rects = {}
screen_info = ''
task_editors = WeakValueDictionary()


class UsedMixin:
    """通用混入：删除按钮跳过(used)属性。右键删除按钮可在 使用/跳过 间切换，跳过的条目运行时不再执行，编辑时无法删除"""
    used_icon_del = '\uE74D'
    used_icon_skip = '\uE893'

    def init_used(self, used: bool = True):
        """初始化删除按钮跳过属性，需在 loadxml 之后调用"""
        self.used = True
        self.delbtn = self.uixml.tags['delbtn'][-1] # delete button uid
        self.delbtn_icon = f'{self.delbtn}icon' # delete button icon uid
        self.uixml.realui.tag_bind(self.delbtn, "<Button-3>", self.del_right_click)
        if not used:
            self.del_right_click(None) # true -> false for delete button
        self.used = used

    def del_right_click(self, _):
        self.used = not self.used
        self.uixml.realui.itemconfig(self.delbtn_icon, text=self.used_icon_del if self.used else self.used_icon_skip)
        if getattr(self, 'contentChanged', None):
            self.contentChanged(None)


def init_editor():
    global theme, themename, screen_rects, screen_info, accent_color
    if config.settings['general']['theme'] == 'dark':
        theme = TinUIDark
        themename = 'dark'
        accent_color = config.settings['general']['accentColorD']
    else:
        theme = TinUILight
        themename = 'light'
        accent_color = config.settings['general']['accentColorL']
    left, top, right, bottom = datas.worker_area
    screen_rects.clear()
    screen_rects['lrs'] = (
        (left, top, (right-left)//2, bottom),
        ((left+right)//2, top, (right-left)//2, bottom)
    )
    screen_rects['lcrs'] = (
        (left, top, (right-left)//3, bottom),
        ((left+right)//3, top, (right-left)//3, bottom),
        ((left+right)*2//3, top, (right-left)//3, bottom)
    )
    screen_rects['lr'] = (
        (left, top, (right-left)*2//3, bottom),
        (left, top, (right-left)//3, bottom),
        ((left+right)//3, top, (right-left)*2//3, bottom),
        ((left+right)*2//3, top, (right-left)//3, bottom)
    )
    screen_rects['quad'] = (
        (left, top, (right-left)//2, (bottom-top)//2),
        ((left+right)//2, top, (right-left)//2, (bottom-top)//2),
        (left, (top+bottom)//2, (right-left)//2, (bottom-top)//2),
        ((left+right)//2, (top+bottom)//2, (right-left)//2, (bottom-top)//2)
    )
    screen_info = '屏幕可用区域 '+', '.join(str(x) for x in datas.worker_area)
