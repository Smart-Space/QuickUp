/*
Quickup C++ module
- quick_fuzz 模糊匹配
- register_start 注册开机自启动
- unregister_start 取消注册开机自启动
- have_start_value 判断是否存在开机自启动项
*/
#include <algorithm>

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "quickfuzz.h"
#include "regrun.h"
#include "shortcut.h"
#include "ui.h"
#include "hotkey.h"
#include "zone.h"

#include <dwmapi.h>


static PyObject* get_parent(PyObject* self, PyObject* args) {
    long hwnd;
    int flag = PyArg_ParseTuple(args, "i:get_parent", &hwnd);
    if (!flag) {
        return NULL;
    }
    HWND parent = GetParent((HWND)hwnd);
    return Py_BuildValue("i", parent);
}

static PyObject* get_windowtext(PyObject* self, PyObject* args) {
    long hwnd;
    int flag = PyArg_ParseTuple(args, "i:get_windowtext", &hwnd);
    if (!flag) {
        return NULL;
    }
    if (!IsWindow((HWND)hwnd)) {
        return Py_False;
    }
    int len = GetWindowTextLengthW((HWND)hwnd);
    wchar_t* buffer = new wchar_t[len + 1];
    GetWindowTextW((HWND)hwnd, buffer, len + 1);
    PyObject* result = PyUnicode_FromWideChar(buffer, len);
    delete[] buffer;
    return result;
}

static PyObject* priority_window(PyObject* self, PyObject* args) {
    PyObject* name;
    int flag = PyArg_ParseTuple(args, "O:priority_window", &name);
    if (!flag) {
        return NULL;
    }
    HWND hwnd;
    // 判断是str还是int
    if (PyLong_Check(name)) { // int
        hwnd = (HWND)PyLong_AsLong(name);
    } else { // str
        wchar_t* wname = PyUnicode_AsWideCharString(name, NULL);
        hwnd = FindWindowW(nullptr, wname);
        PyMem_Free(wname);
    }
    if (hwnd) {
        ShowWindow(hwnd, SW_SHOW);
        SetForegroundWindow(hwnd);
        return Py_True;
    }
    return Py_False;
}

using FuncGetCurrentPackageFullName = LONG(WINAPI*)(UINT32*, PWSTR);
static PyObject* is_msix(PyObject* self, PyObject* args) {
    HMODULE hKernel32 = GetModuleHandleW(L"kernel32.dll");
    auto pGetCurrentPackageFullName = (FuncGetCurrentPackageFullName)
        GetProcAddress(hKernel32, "GetCurrentPackageFullName");
    if (!pGetCurrentPackageFullName) {
        return Py_False;
    }
    UINT32 len = 0;
    LONG result = pGetCurrentPackageFullName(&len, nullptr);
    if (result != ERROR_INSUFFICIENT_BUFFER) {
        return Py_False;
    }
    return Py_True;
}

static PyObject* window_no_icon(PyObject* self, PyObject* args) {
    long hwnd;
    int flag = PyArg_ParseTuple(args, "i:window_no_icon", &hwnd);
    if (!flag) {
        return NULL;
    }
    HWND root = GetParent((HWND)hwnd);
    LONG windowlong = GetWindowLongW(root, GWL_STYLE);
    windowlong &= ~WS_SYSMENU;
    SetWindowLongW(root, GWL_STYLE, windowlong);
    return Py_None;
}

#ifndef DWMWA_USE_IMMERSIVE_DARK_MODE
#define DWMWA_USE_IMMERSIVE_DARK_MODE 20
#endif
static PyObject* set_window_dark(PyObject* self, PyObject* args) {
    long hwnd;
    int flag = PyArg_ParseTuple(args, "i:set_window_dark", &hwnd);
    if (!flag) {
        return NULL;
    }
    HWND root = GetParent((HWND)hwnd);
    int dark = 1;
    DwmSetWindowAttribute(
        root,
        DWMWA_USE_IMMERSIVE_DARK_MODE,
        &dark,
        sizeof(dark)
    );
    return Py_None;
}

static PyObject* shell_execute_ex_wrapper(PyObject* self, PyObject* args) {
    // 参数顺序: cmd, args, cwd, maximize, minimize, admin, wait, pos
    PyObject* cmd_obj = nullptr;
    PyObject* args_obj = nullptr;
    PyObject* cwd_obj = nullptr;
    int maximize = 0;
    int minimize = 0;
    int admin = 0;
    int wait = 0;
    PyObject* pos = nullptr;
    bool zone_round = false;
    if (!PyArg_ParseTuple(args, "OOOiiiiOp",
                          &cmd_obj, &args_obj, &cwd_obj,
                          &maximize, &minimize, &admin, &wait, &pos, &zone_round)) {
        return nullptr;
    }
    wchar_t* wcmd = PyUnicode_AsWideCharString(cmd_obj, NULL);
    wchar_t* wargs = PyUnicode_AsWideCharString(args_obj, NULL);
    wchar_t* wcwd = PyUnicode_AsWideCharString(cwd_obj, NULL);
    SHELLEXECUTEINFOW sei = { 0 };
    sei.cbSize = sizeof(SHELLEXECUTEINFOW);
    sei.fMask = SEE_MASK_NOCLOSEPROCESS;
    sei.hwnd = nullptr;
    sei.lpFile = wcmd;
    sei.lpParameters = wargs;
    sei.lpDirectory = wcwd;
    sei.nShow = maximize ? SW_MAXIMIZE : (minimize ? SW_MINIMIZE : SW_SHOW);
    sei.lpVerb = admin ? L"runas" : L"open";
    std::wstring message = L"";
    std::vector<int> pos_vec;
    pos_vec.reserve(4);
    if (PyList_Size(pos)) {
        int x = PyLong_AsInt(PyList_GET_ITEM(pos, 0));
        int y = PyLong_AsInt(PyList_GET_ITEM(pos, 1));
        int w = PyLong_AsInt(PyList_GET_ITEM(pos, 2));
        int h = PyLong_AsInt(PyList_GET_ITEM(pos, 3));
        pos_vec.push_back(x);
        pos_vec.push_back(y);
        pos_vec.push_back(w);
        pos_vec.push_back(h);
    }
    Py_BEGIN_ALLOW_THREADS
    auto launchTime = std::chrono::steady_clock::now();
    if (ShellExecuteExW(&sei)) {
        if (pos_vec.size() == 4) {
            modify_window_position(sei, wcmd, launchTime, pos_vec[0], pos_vec[1], pos_vec[2], pos_vec[3], zone_round);
        }
        if (wait) {
            WaitForSingleObject(sei.hProcess, INFINITE);
        }
    } else {
        LPWSTR buffer = nullptr;
        DWORD error_code = GetLastError();
        DWORD len = FormatMessageW(
            FORMAT_MESSAGE_ALLOCATE_BUFFER |
            FORMAT_MESSAGE_FROM_SYSTEM |
            FORMAT_MESSAGE_IGNORE_INSERTS,
            nullptr,
            error_code,
            MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
            (LPWSTR)&buffer,
            0,
            nullptr
        );
        if (len > 0 && buffer) {
            message = buffer;
            LocalFree(buffer);
        }
    }
    CloseHandle(sei.hProcess);
    Py_END_ALLOW_THREADS
    PyMem_Free(wcmd);
    PyMem_Free(wargs);
    PyMem_Free(wcwd);
    return PyUnicode_FromWideChar(message.c_str(), message.length());
}

static PyObject* run_console_commands(PyObject* self, PyObject* args) {
    // 参数顺序: cmd (str), cmds (list of str/bytes), cwd (str or None), wait (bool)
    PyObject* cmd_obj;
    PyObject* cmds_list;
    PyObject* cwd_obj;
    int wait_flag = 0;
    if (!PyArg_ParseTuple(args, "OOOi", &cmd_obj, &cmds_list, &cwd_obj, &wait_flag)) {
        return nullptr;
    }
    wchar_t* cmd_str = PyUnicode_AsWideCharString(cmd_obj, nullptr);
    wchar_t* cwd_str = PyUnicode_AsWideCharString(cwd_obj, nullptr);
    std::vector<std::string> cmds_strings;
    std::string item_str;
    for (Py_ssize_t i = 0; i < PyList_Size(cmds_list); ++i) {
        PyObject* item = PyList_GetItem(cmds_list, i);
        item_str = (std::string)PyUnicode_AsUTF8(item);
        item_str += "\n";
        cmds_strings.push_back(item_str);
    }
    Py_BEGIN_ALLOW_THREADS
    AllocConsole();
    SECURITY_ATTRIBUTES sa = { sizeof(sa), nullptr, TRUE };
    HANDLE hStdinRead = nullptr, hStdinWrite = nullptr;
    if (!CreatePipe(&hStdinRead, &hStdinWrite, &sa, 0)) {
        FreeConsole();
        PyMem_Free(cmd_str);
        PyMem_Free(cwd_str);
        return nullptr;
    }
    // 设置子进程 STARTUPINFO
    STARTUPINFOW si = {0};
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESTDHANDLES;
    si.hStdInput = hStdinRead;
    si.hStdOutput = GetStdHandle(STD_OUTPUT_HANDLE);
    si.hStdError = GetStdHandle(STD_ERROR_HANDLE);
    PROCESS_INFORMATION pi = {0};
    if (cwd_str[0] == '\0') {
        cwd_str = nullptr;
    }
    // 启动进程
    CreateProcessW(
        nullptr,                    // lpApplicationName
        cmd_str,                    // lpCommandLine
        nullptr,                    // lpProcessAttributes
        nullptr,                    // lpThreadAttributes
        TRUE,                       // bInheritHandles
        0,                          // dwCreationFlags
        nullptr,                    // lpEnvironment
        cwd_str,                    // lpCurrentDirectory
        &si,
        &pi
    );
    CloseHandle(hStdinRead);
    hStdinRead = nullptr;
    // 向子进程 stdin 写入命令
    DWORD written;
    for (auto cmd : cmds_strings) {
        WriteFile(hStdinWrite, cmd.c_str(), (DWORD)cmd.size(), &written, nullptr);
    }
    std::string exit_cmd = "exit\n";
    WriteFile(hStdinWrite, exit_cmd.c_str(), (DWORD)exit_cmd.size(), &written, nullptr);
    CloseHandle(hStdinWrite);
    // 等待或不等待
    if (wait_flag) {
        WaitForSingleObject(pi.hProcess, INFINITE);
    }
    // 清理
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    FreeConsole();
    Py_END_ALLOW_THREADS
    PyMem_Free(cmd_str);
    PyMem_Free(cwd_str);
    Py_RETURN_NONE;
}

static PyObject* quick_fuzz(PyObject* self, PyObject* args) {
    PyObject* list;
    char* name;
    int acc;
    int num;
    int flag = PyArg_ParseTuple(args, "Osii:quick_fuzz_list", &list, &name, &acc, &num);
    if (!flag) {
        return NULL;
    }
    setTargetChars((std::string)name);
    PyObject* result = PyList_New(0);
    int length = PyList_Size(list);
    int nownum = 0;
    for (int i = 0; i < length; i++) {
        PyObject* item = PyList_GetItem(list, i);
        std::string itemstr = (std::string)PyUnicode_AsUTF8(item);
        std::transform(itemstr.begin(), itemstr.end(), itemstr.begin(), ::tolower);
        int score = calculateSimilarity(itemstr);
        if (score >= acc) {
            PyList_Append(result, item);
            nownum++;
            if (nownum >= num) {
                break;
            }
        }
    }
    return result;
}

static PyObject* register_start(PyObject* self, PyObject* args) {
    char* value;
    char* path;
    int flag = PyArg_ParseTuple(args, "ss:register_start", &value, &path);
    if (!flag) {
        return NULL;
    }
    // char* -> wstring
    std::string value_str(value);
    std::wstring wvalue = std::wstring(value_str.begin(), value_str.end());
    std::string path_str(path);
    std::wstring wpath = std::wstring(path_str.begin(), path_str.end());
    if (!set_startup_registry(wvalue, wpath)) {
        return Py_BuildValue("i", -1);
    }
    return Py_BuildValue("i", 0);
}

static PyObject* unregister_start(PyObject* self, PyObject* args) {
    char* value;
    int flag = PyArg_ParseTuple(args, "s:unregister_start", &value);
    if (!flag) {
        return NULL;
    }
    // char* -> wstring
    std::string value_str(value);
    std::wstring wvalue = std::wstring(value_str.begin(), value_str.end());
    if (!delete_startup_registry(wvalue)) {
        return Py_BuildValue("i", -1);
    }
    return Py_BuildValue("i", 0);
}

static PyObject* have_start_value(PyObject* self, PyObject* args) {
    char* value;
    int flag = PyArg_ParseTuple(args, "s:have_start_value", &value);
    if (!flag) {
        return NULL;
    }
    // char* -> wstring
    std::string value_str(value);
    std::wstring wvalue = std::wstring(value_str.begin(), value_str.end());
    if (have_value(wvalue)) {
        return Py_BuildValue("i", 1);
    }
    return Py_BuildValue("i", 0);
}

static PyObject* create_link(PyObject* self, PyObject* args) {
    PyObject* pyapp;
    PyObject* pycmd;
    PyObject* pylnkpath;
    PyObject* pyicopath;
    int flag = PyArg_ParseTuple(args, "OOOO:create_link", &pyapp, &pycmd, &pylnkpath, &pyicopath);
    if (!flag) {
        return NULL;
    }
    wchar_t* app = PyUnicode_AsWideCharString(pyapp, NULL);
    wchar_t* cmd = PyUnicode_AsWideCharString(pycmd, NULL);
    wchar_t* lnkpath = PyUnicode_AsWideCharString(pylnkpath, NULL);
    wchar_t* icopath = PyUnicode_AsWideCharString(pyicopath, NULL);
    bool result = CreateLinkFile((LPCWSTR)app, (LPCWSTR)cmd, (LPCOLESTR)lnkpath, (LPCWSTR)icopath);
    return PyBool_FromLong(result);
}

static PyObject* init_tray(PyObject* self, PyObject* args) {
    long pyhwnd;
    PyObject* pytooltip;
    PyObject* about_callback;
    PyObject* exit_callback;
    int flag = PyArg_ParseTuple(args, "iOOO:init_tray", &pyhwnd, &pytooltip, &about_callback, &exit_callback);
    if (!flag) {
        return NULL;
    }
    HWND hWnd = (HWND)pyhwnd;
    wchar_t* tooltip = PyUnicode_AsWideCharString(pytooltip, NULL);
    if (init_ui_tray(hWnd, tooltip, about_callback, exit_callback)) {
        return Py_BuildValue("i", 0);
    }
    return Py_BuildValue("i", -1);
}

static PyObject* remove_tray(PyObject* self, PyObject* args) {
    remove_ui_tray();
    return Py_None;
}

static PyObject* enable_entry_drop(PyObject* self, PyObject* args) {
    long long pyhwnd;
    PyObject* pycallback;
    int flag = PyArg_ParseTuple(args, "LO:enable_entry_drop", &pyhwnd, &pycallback);
    if (!flag) {
        return NULL;
    }
    HWND hwnd = (HWND)pyhwnd;
    DropTarget* dt = new DropTarget(hwnd, pycallback);
    dt->enable_drop();
    return PyCapsule_New(dt, NULL, NULL);;
}

static PyObject* disable_entry_drop(PyObject* self, PyObject* args) {
    PyObject* pydt;
    int flag = PyArg_ParseTuple(args, "O:disable_entry_drop", &pydt);
    if (!flag) {
        return NULL;
    }
    DropTarget* dt = (DropTarget*)PyCapsule_GetPointer(pydt, NULL);
    delete dt;
    Py_DecRef(pydt);
    return Py_None;
}

static PyObject* is_valid_windows_filename(PyObject* self, PyObject* args) {
    PyObject* pyfilename;
    int flag = PyArg_ParseTuple(args, "O:is_valid_windows_filename", &pyfilename);
    if (!flag) {
        return NULL;
    }
    wchar_t* filename = PyUnicode_AsWideCharString(pyfilename, NULL);
    bool result = valid_windows_filename(filename);
    return PyBool_FromLong(result);
}

static PyObject* start_hotkey(PyObject* self, PyObject* args) {
    int fsmodifier;
    int fskey;
    PyObject* pycallback;
    int flag = PyArg_ParseTuple(args, "iiO:create_hotkey", &fsmodifier, &fskey, &pycallback);
    if (!flag) {
        return NULL;
    }
    start_hotkey_listener(fsmodifier, fskey, pycallback);
    return Py_None;
}

static PyObject* stop_hotkey(PyObject* self, PyObject* args) {
    stop_hotkey_listener();
    return Py_None;
}

static PyObject* detect_app_theme(PyObject* self, PyObject* args) {
    int result = detect_theme();
    if (result == 0) {
        return PyUnicode_FromString("dark");
    } else {
        return PyUnicode_FromString("light");
    }
}

static PyObject* worker_size(PyObject* self, PyObject* args) {
    auto [top, left, bottom, right] = get_worker_size();
    return Py_BuildValue("iiii", top, left, bottom, right);
}

static PyObject* start_window_hook(PyObject* self, PyObject* args) {
    Py_BEGIN_ALLOW_THREADS
    WindowMonitor::Start();
    Py_END_ALLOW_THREADS
    return Py_None;
}

static PyObject* stop_window_hook(PyObject* self, PyObject* args) {
    Py_BEGIN_ALLOW_THREADS
    WindowMonitor::Stop();
    Py_END_ALLOW_THREADS
    return Py_None;
}

static PyObject* zone_try_times(PyObject* self, PyObject* args) {
    int times;
    int flag = PyArg_ParseTuple(args, "i:zone_try_times", &times);
    if (!flag) {
        return NULL;
    }
    set_zone_try_times(times);
    return Py_None;
}


static PyMethodDef QUModuleMethods[] = {
    {"get_parent", (PyCFunction)get_parent, METH_VARARGS, PyDoc_STR("get_parent(hwnd:int) -> int")},
    {"get_windowtext", (PyCFunction)get_windowtext, METH_VARARGS, PyDoc_STR("get_windowtext(hwnd:int) -> str")},
    {"priority_window", (PyCFunction)priority_window, METH_VARARGS, PyDoc_STR("priority_window(name:str|int) -> bool")},
    {"is_msix", (PyCFunction)is_msix, METH_VARARGS, PyDoc_STR("is_msix() -> bool")},
    {"window_no_icon", (PyCFunction)window_no_icon, METH_VARARGS, PyDoc_STR("window_no_icon(hwnd:int) -> None")},
    {"set_window_dark", (PyCFunction)set_window_dark, METH_VARARGS, PyDoc_STR("set_window_dark(hwnd:int) -> None")},
    {"shell_execute_ex_wrapper", (PyCFunction)shell_execute_ex_wrapper, METH_VARARGS, PyDoc_STR("shell_execute_ex_wrapper(cmd:str, args:str, cwd:str, maximize:int, minimize:int, admin:int, wait:int, pos:list, zone_round:bool) -> str")},
    {"run_console_commands", (PyCFunction)run_console_commands, METH_VARARGS, PyDoc_STR("run_console_commands(cmd:str, cmds:list, cwd:str, wait:bool) -> None")},
    {"quick_fuzz", (PyCFunction)quick_fuzz, METH_VARARGS, PyDoc_STR("quick_fuzz(list:list, name:str, acc:int, num:int) -> list")},
    {"register_start", (PyCFunction)register_start, METH_VARARGS, PyDoc_STR("register_start(value:str, path:str) -> int")},
    {"unregister_start", (PyCFunction)unregister_start, METH_VARARGS, PyDoc_STR("unregister_start(value:str) -> int")},
    {"have_start_value", (PyCFunction)have_start_value, METH_VARARGS, PyDoc_STR("have_start_value(value:str) -> int")},
    {"create_link", (PyCFunction)create_link, METH_VARARGS, PyDoc_STR("create_link(app:str, cmd:str, lnkpath:str, icopath:str) -> bool")},
    {"init_tray", (PyCFunction)init_tray, METH_VARARGS, PyDoc_STR("init_tray(window:int, tooltip:str, show_callback:function, about_callback:function, exit_callback:function) -> int")},
    {"remove_tray", (PyCFunction)remove_tray, METH_VARARGS, PyDoc_STR("remove_tray() -> None")},
    {"enable_entry_drop", (PyCFunction)enable_entry_drop, METH_VARARGS, PyDoc_STR("enable_entry_drop(hwnd:int, callback:function) -> DropTarget")},
    {"disable_entry_drop", (PyCFunction)disable_entry_drop, METH_VARARGS, PyDoc_STR("disable_entry_drop(dt:DropTarget) -> None")},
    {"is_valid_windows_filename", (PyCFunction)is_valid_windows_filename, METH_VARARGS, PyDoc_STR("is_valid_windows_filename(filename:str) -> bool")},
    {"start_hotkey", (PyCFunction)start_hotkey, METH_VARARGS, PyDoc_STR("start_hotkey(fsmodifier:int, fskey:int, callback:function) -> None")},
    {"stop_hotkey", (PyCFunction)stop_hotkey, METH_VARARGS, PyDoc_STR("stop_hotkey() -> None")},
    {"detect_app_theme", (PyCFunction)detect_app_theme, METH_VARARGS, PyDoc_STR("detect_app_theme() -> str")},
    {"worker_size", (PyCFunction)worker_size, METH_VARARGS, PyDoc_STR("worker_size() -> tuple")},
    {"start_window_hook", (PyCFunction)start_window_hook, METH_VARARGS, PyDoc_STR("start_window_hook() -> None")},
    {"stop_window_hook", (PyCFunction)stop_window_hook, METH_VARARGS, PyDoc_STR("stop_window_hook() -> None")},
    {"zone_try_times", (PyCFunction)zone_try_times, METH_VARARGS, PyDoc_STR("zone_try_times(times:int) -> None")},
    {NULL, NULL, 0, NULL}
};

PyDoc_STRVAR(module_doc, "Quickup C++ module");

static struct PyModuleDef QUmodule = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "QUmodule",
    .m_size = 0,  // non-negative
    .m_methods = QUModuleMethods,
};

PyMODINIT_FUNC PyInit_QUmodule(void) {
    return PyModuleDef_Init(&QUmodule);
}
