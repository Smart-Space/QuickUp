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
    int pyhwnd;
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
    int flag = PyArg_ParseTuple(args, "iO:enable_entry_drop", &pyhwnd, &pycallback);
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


static PyMethodDef QUModuleMethods[] = {
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
