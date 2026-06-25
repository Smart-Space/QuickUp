# ./config.py
"""
QuickUp configuration file.
"""
import os
import json
from copy import deepcopy

from cppextend.QUmodule import detect_app_theme

# 默认设置
def _normalize_shortcut_list(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = [value]
    if isinstance(value, (list, tuple)):
        normalized = []
        for item in value:
            if isinstance(item, str) and item:
                normalized.append(item)
        return normalized
    return None

def merge_shortcuts(defaults, overrides):
    result = {}
    if not isinstance(overrides, dict):
        overrides = {}
    for scope, actions in defaults.items():
        result[scope] = {}
        override_actions = overrides.get(scope, {})
        if not isinstance(override_actions, dict):
            override_actions = {}
        for action, sequences in actions.items():
            override_val = override_actions.get(action, None)
            normalized = _normalize_shortcut_list(override_val)
            if normalized is None:
                result[scope][action] = list(sequences)
            else:
                result[scope][action] = normalized
        for action, override_val in override_actions.items():
            if action in result[scope]:
                continue
            normalized = _normalize_shortcut_list(override_val)
            if normalized is not None:
                result[scope][action] = normalized
    for scope, override_actions in overrides.items():
        if scope in result or not isinstance(override_actions, dict):
            continue
        result[scope] = {}
        for action, override_val in override_actions.items():
            normalized = _normalize_shortcut_list(override_val)
            if normalized is not None:
                result[scope][action] = normalized
    return result

DEFAULT_SHORTCUTS = {
    'editor': {
        'close': ['<Control-w>'],
        'save': ['<Control-s>'],
        'run': ['<Control-r>'],
        'set_cwd': ['<Control-e>'],
        'toggle_priority': ['<Alt-a>'],
        'open_local': ['<Alt-f>'],
        'add_cmd': ['<Alt-c>'],
        'add_cmds': ['<Alt-s>'],
        'add_task': ['<Alt-t>'],
        'add_workspace': ['<Alt-w>'],
        'add_tip': ['<Alt-i>'],
        'copy_task': ['<Control-Shift-C>'],
        'paste_task': ['<Control-Shift-V>'],
    },
    'setting': {
        'page_general': ['<Alt-KeyPress-1>'],
        'page_advanced': ['<Alt-KeyPress-2>'],
        'page_storage': ['<Alt-KeyPress-3>'],
        'page_shortcut': ['<Alt-KeyPress-4>'],
        'check_update': ['<Control-u>'],
        'close': ['<Control-w>'],
    },
    'select': {
        'next': ['<Down>'],
        'prev': ['<Up>'],
        'confirm': ['<Return>'],
        'close': ['<Escape>'],
    }
}
settings = {
    'general': {
        'theme': 'light',# light dark system
        'accentColorL': '#0067c0',
        'accentColorD': '#4cc2ff',
        'accentBorder': False,
        'patternRank': 75,
        'maxSearchCount': 5,
        'showHidden': False,
        'topMost': False,
        'checkUpdate': True,
        'closeToTray': True,
        'transparency': 0,
    },
    'advanced': {
        'runWhenStart': False,
        'disAdmin': False,
        'autoSave': False,
        'callUp': [0x0001, 0x51],
        'zoneRetryTimes': 20,
        'startOnAdmin': False,
        'shortcuts': deepcopy(DEFAULT_SHORTCUTS),
    },
    'storage': {}
}

theme_original = 'light'

def init_config():
    """
    初始化配置文件
    """
    global theme_original
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
            theme_original = settings['general']['theme']
            if theme_original == 'system':
                settings['general']['theme'] = detect_app_theme()
        with open(os.path.join(os.path.expanduser('~'), '.QuickUp', 'config-advanced.json'), 'r', encoding='utf-8') as f:
            advanced_data = json.load(f)
            settings['advanced'].update(advanced_data)
            settings['advanced']['shortcuts'] = merge_shortcuts(
                DEFAULT_SHORTCUTS,
                advanced_data.get('shortcuts', {})
            )
        with open(os.path.join(os.path.expanduser('~'), '.QuickUp', 'config-storage.json'), 'r', encoding='utf-8') as f:
            settings['storage'].update(json.load(f))

def get_shortcuts(scope, defaults):
    shortcuts = settings['advanced'].get('shortcuts', {})
    merged = merge_shortcuts({scope: defaults}, {scope: shortcuts.get(scope, {})})
    return merged.get(scope, defaults)

def save_config():
    """
    保存配置文件
    """
    with open(os.path.join(os.path.expanduser('~'), '.QuickUp', 'config-general.json'), 'w', encoding='utf-8') as f:
        settings['general']['theme'] = theme_original
        json.dump(settings['general'], f, indent=4)
        if theme_original == 'system':
            settings['general']['theme'] = detect_app_theme()
    with open(os.path.join(os.path.expanduser('~'), '.QuickUp', 'config-advanced.json'), 'w', encoding='utf-8') as f:
        json.dump(settings['advanced'], f, indent=4)
    with open(os.path.join(os.path.expanduser('~'), '.QuickUp', 'config-storage.json'), 'w', encoding='utf-8') as f:
        json.dump(settings['storage'], f, indent=4)
