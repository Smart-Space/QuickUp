# ./ui/editor/__init__.py
"""
QuickUp 任务编辑器模块
"""
from . import base
from .cmdeditor import CmdEditor
from .cmdseditor import CmdsEditor
from .taskeditor import TaskEditor
from .wspeditor import WspEditor
from .tipeditor import TipEditor
from .editor import Editor, create_editor


def __getattr__(name):
    return getattr(base, name)
