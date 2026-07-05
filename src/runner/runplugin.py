"""
执行插件任务
"""
import ast
import inspect

from runner import Task
import datas
from plugin.manager import plugin_manager


class RunPlugin(Task):

    def __init__(self, name:str, task:dict, cwd:str='', deamon:bool=True):
        super().__init__(name, 'plugin')
        self.task = task
        self.cwd = cwd
        self.deamon = deamon

    @staticmethod
    def __parse_plugin_args(args_text:str):
        args_text = (args_text or '').strip()
        if not args_text:
            return [], {}

        call_expr = ast.parse(f"__quickup_plugin_args__({args_text})", mode='eval')
        if not isinstance(call_expr.body, ast.Call):
            raise ValueError("插件参数格式错误")

        positional_args = []
        keyword_args = {}

        for arg in call_expr.body.args:
            if isinstance(arg, ast.Starred):
                expanded = ast.literal_eval(arg.value)
                if not isinstance(expanded, (list, tuple)):
                    raise ValueError("*args 必须解析为列表或元组")
                positional_args.extend(expanded)
            else:
                positional_args.append(ast.literal_eval(arg))

        for keyword in call_expr.body.keywords:
            if keyword.arg is None:
                expanded = ast.literal_eval(keyword.value)
                if not isinstance(expanded, dict):
                    raise ValueError("**kwargs 必须解析为字典")
                keyword_args.update(expanded)
            else:
                keyword_args[keyword.arg] = ast.literal_eval(keyword.value)

        return positional_args, keyword_args

    @staticmethod
    def __handler_accepts_args(handler, positional_args:list, keyword_args:dict) -> bool:
        """
        分析插件任务处理器的签名，判断其是否接受额外的参数。
        如果处理器的签名中包含 *args 或 **kwargs，或者能够绑定传递的参数，返回 True。
        """
        if not positional_args and not keyword_args:
            return False

        try:
            signature = inspect.signature(handler)
        except (TypeError, ValueError):
            return True

        try:
            signature.bind_partial(object(), object(), *positional_args, **keyword_args)
        except TypeError:
            return False
        return True

    def run(self):
        handler = plugin_manager.get_task_handler(self.task.get('name'))
        if handler is None:
            datas.root_error_message = f"任务: {self.name}\n\n"\
            f"插件任务类型: {self.task.get('name', '')}\n\n"\
            f"错误: {plugin_manager.errors.get(self.task.get('name', ''), '未知错误')}"
            if datas.root:
                datas.root.event_generate('<<RunCmdError>>')
            return False

        task_payload = dict(self.task)
        try:
            positional_args, keyword_args = self.__parse_plugin_args(task_payload.get('args', ''))
        except Exception as e:
            datas.root_error_message = f"任务: {self.name}\n\n"\
            f"插件任务类型: {self.task.get('name', '')}\n\n"\
            f"插件参数解析失败: \n{e}"
            if datas.root:
                datas.root.event_generate('<<RunCmdError>>')
            return False

        task_payload['args'] = {
            'args': positional_args,
            'kwargs': keyword_args,
        }
        runtime = {
            'name': self.name,
            'cwd': self.cwd,
            'deamon': self.deamon,
        }
        try:
            if self.__handler_accepts_args(handler, positional_args, keyword_args):
                res = handler(task_payload, runtime, *positional_args, **keyword_args)
            else:
                res = handler(task_payload, runtime)
        except Exception as e:
            datas.root_error_message = f"任务: {self.name}\n\n"\
            f"插件任务类型: {self.task.get('name', '')}\n\n"\
            f"错误: {e}"
            if datas.root:
                datas.root.event_generate('<<RunCmdError>>')
            return False

        if res is False:
            return False
        return True


def run_plugin(name:str, task:dict, cwd:str='', deamon:bool=True):
    plugin_task = RunPlugin(name, task, cwd, deamon)
    return plugin_task.run()
