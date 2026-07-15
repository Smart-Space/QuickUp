"""
Plugin error isolation helpers
"""
import traceback


def format_plugin_error(err:Exception) -> str:
    return f"{err}\n{traceback.format_exc()}"
