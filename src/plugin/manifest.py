"""
Plugin manifest parsing and validation
"""
from typing import Dict, Any
import os
import json


REQUIRED_FIELDS = [
    'name',
    'version',
    'entry',
]


def load_manifest(path:str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"manifest not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    _validate_manifest(data, path)
    return data


def _validate_manifest(data:Dict[str, Any], path:str):
    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ValueError(f"manifest missing field '{field}': {path}")
    if not isinstance(data.get('permissions', []), list):
        raise ValueError(f"manifest permissions must be list: {path}")
    if not isinstance(data.get('task_types', []), list):
        raise ValueError(f"manifest task_types must be list: {path}")
    if not isinstance(data.get('modules', []), list):
        raise ValueError(f"manifest modules must be list: {path}")
    for item in data.get('modules', []):
        if not isinstance(item, str) or not item:
            raise ValueError(f"manifest modules must contain non-empty strings: {path}")
