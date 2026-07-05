# ./ui/editor/base.py
"""
Shared state and initialization for editor modules
"""
from tinui.theme.tinuidark import TinUIDark
from tinui.theme.tinuilight import TinUILight

import datas
import config

accent_color = None
theme = None
themename = ''
screen_rects = {}
screen_info = ''
task_editors = dict()


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
