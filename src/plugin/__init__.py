r"""
QuickUp Plugin System
插件系统

一、框架总览
1) 目录结构
- 插件目录: %APPDATA%\QuickUp\plugins\<plugin_id>\
- 清单文件: manifest.json
- 入口脚本: 由 manifest.json 的 entry 指定

2) 后端模块
- plugin.manager: 插件扫描、沙箱加载与生命周期管理
- plugin.registry: 任务类型与权限注册中心
- plugin.manifest: 清单解析与强校验
- plugin.api: 为插件提供的受限 API 接口
- plugin.controller: 应用控制
- plugin.errors: 错误格式化与隔离

3) 运行时挂载点
- 插件加载: 由 PluginManager 驱动，支持懒加载 (仅在任务触发时加载具体代码)
- 任务执行: RunTask 检索注册表中的 handler 并执行

二、运行逻辑
1) 启动与发现
- 扫描插件目录 -> 解析 manifest.json -> 将声明的 task_types 索引至注册表 (task_sources)
- 此时不执行插件代码，仅建立索引

2) 懒加载机制
- 当触发特定 task_type 任务时 -> 检查所属插件是否加载 -> 执行 _exec_sandbox() -> 调用 init()

3) 沙箱执行 (_exec_sandbox)
- 限制 __builtins__ (仅允许 ALLOWED_BUILTINS)
- 限制 import (仅允许 ALLOWED_IMPORTS)
- 通过自定义 __import__ 拦截非白名单模块

三、权限与安全
1) 强校验
- register_task_type 会校验该项是否在 manifest.json 中声明，未声明则抛出 ValueError

2) 隔离
- 插件代码在受限的全局环境中执行 (需要注意只能使用受限的库和内建变量与函数)
- 异常会被捕获并格式化，当拥有界面时，QuickUp会使用弹窗提示错误

四、扩展开发规范
1) manifest.json 格式
{
  "name": "my_plugin",
  "version": "1.0.0",
  "entry": "plugin.py",
  "permissions": ["task_exec", "ui_main"],
  "task_types": ["mytask"]
}

2) 入口脚本规范
- 必须提供 init(api, manifest)
- 注册拓展任务功能必须在 manifest 中预先声明

示例:
```
def init(api, manifest):
    def handler(task, runtime):
        # task 为当前任务条目 dict
        # runtime 包含 name/cwd/deamon
        # 可以有位置参数和关键字参数
        return True
    api.register_task_type("mytask", handler)
```


五、扩展使用方式
1) 安装: 放入 %APPDATA%\QuickUp\plugins\ 目录下
2) 启用: config.settings['storage']['plugins'][plugin_name]['enabled'] = True (by default)
3) 任务: 在任务 JSON 中使用 type="mytask"

六、API 能力
- register_task_type(name, handler)
- register_permission(name, description)
- hide() / show(): 控制主窗口
- get_config() / set_config(data): 读写插件私有存储设置

七、调用
1) QuickUp中使用插件栏目 -> 确定 task_type
2) 参数形式为Python风格参数 (位置参数 | 关键字参数)
3) 传递拓展能力与参数至插件接口
"""
