# ./config.py
"""
QuickUp configuration file.
"""
import os
import json

# 默认设置
settings = {
    'general': {
        'theme': 'light',# light dark
        'patternRank': 75,
        'maxSearchCount': 5,
        'topMost': False,
        'checkUpdate': True,
        'closeToTray': True,
    },
    'advanced': {
        'runWhenStart': False,
        'disAdmin': False,
        'autoSave': False,
        'callUp': [0x0001, 0x51],
    },
    'storage': {}
}


def init_config():
    """
    初始化配置文件
    """
    if not os.path.exists(os.path.join(os.path.expanduser('~'), '.QuickUp')):
        os.makedirs(os.path.join(os.path.expanduser('~'), '.QuickUp'))
        with open(os.path.join(os.path.expanduser('~'), '.QuickUp', 'config-general.json'), 'w', encoding='utf-8') as f:
            json.dump(settings['general'], f, indent=4)
        with open(os.path.join(os.path.expanduser('~'), '.QuickUp', 'config-advanced.json'), 'w', encoding='utf-8') as f:
            json.dump(settings['advanced'], f, indent=4)
        with open(os.path.join(os.path.expanduser('~'), '.QuickUp', 'config-storage.json'), 'w', encoding='utf-8') as f:
            json.dump(settings['storage'], f, indent=4)
    else:
        with open(os.path.join(os.path.expanduser('~'), '.QuickUp', 'config-general.json'), 'r', encoding='utf-8') as f:
            settings['general'].update(json.load(f))
        with open(os.path.join(os.path.expanduser('~'), '.QuickUp', 'config-advanced.json'), 'r', encoding='utf-8') as f:
            settings['advanced'].update(json.load(f))
        with open(os.path.join(os.path.expanduser('~'), '.QuickUp', 'config-storage.json'), 'r', encoding='utf-8') as f:
            settings['storage'].update(json.load(f))

def save_config():
    """
    保存配置文件
    """
    with open(os.path.join(os.path.expanduser('~'), '.QuickUp', 'config-general.json'), 'w', encoding='utf-8') as f:
        json.dump(settings['general'], f, indent=4)
    with open(os.path.join(os.path.expanduser('~'), '.QuickUp', 'config-advanced.json'), 'w', encoding='utf-8') as f:
        json.dump(settings['advanced'], f, indent=4)
    with open(os.path.join(os.path.expanduser('~'), '.QuickUp', 'config-storage.json'), 'w', encoding='utf-8') as f:
        json.dump(settings['storage'], f, indent=4)
