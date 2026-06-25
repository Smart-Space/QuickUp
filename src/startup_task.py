import subprocess


def _run_schtasks(args):
    try:
        result = subprocess.run(["schtasks", *args], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def has_task(task_name):
    if not task_name:
        return False
    return _run_schtasks(["/Query", "/TN", task_name])


def set_task(task_name, app_path):
    if not task_name or not app_path:
        return False
    return _run_schtasks([
        "/Create",
        "/F",
        "/RL",
        "HIGHEST",
        "/TN",
        task_name,
        "/TR",
        app_path,
        "/SC",
        "ONLOGON",
    ])


def remove_task(task_name):
    if not task_name:
        return False
    return _run_schtasks(["/Delete", "/F", "/TN", task_name])
