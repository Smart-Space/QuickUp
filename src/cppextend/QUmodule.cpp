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


static PyObject* quick_fuzz(PyObject* self, PyObject* args) {
    PyObject* list;
    char* name;
    int acc;
    int num;
    int flag = PyArg_ParseTuple(args, "Osii:quick_fuzz_list", &list, &name, &acc, &num);
    if (!flag) {
        return NULL;
    }
    PyObject* result = PyList_New(0);
    int length = PyList_Size(list);
    int nownum = 0;
    for (int i = 0; i < length; i++) {
        PyObject* item = PyList_GetItem(list, i);
        std::string itemstr = (std::string)PyUnicode_AsUTF8(item);
        std::transform(itemstr.begin(), itemstr.end(), itemstr.begin(), ::tolower);
        int score = calculateSimilarity(name, itemstr);
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
    PyObject* pytooltip;
    PyObject* pyleft_callback;
    PyObject* pyright_callback;
    int flag = PyArg_ParseTuple(args, "OOO:init_tray", &pytooltip, &pyleft_callback, &pyright_callback);
    if (!flag) {
        return NULL;
    }
    wchar_t* tooltip = PyUnicode_AsWideCharString(pytooltip, NULL);
    if (init_ui_tray(tooltip, pyleft_callback, pyright_callback)) {
        return Py_BuildValue("i", 0);
    }
    return Py_BuildValue("i", -1);
}

static PyObject* remove_tray(PyObject* self, PyObject* args) {
    remove_ui_tray();
    return Py_None;
}


static PyMethodDef QUModuleMethods[] = {
    {"quick_fuzz", (PyCFunction)quick_fuzz, METH_VARARGS, PyDoc_STR("quick_fuzz(list:list, name:str, acc:int, num:int) -> list")},
    {"register_start", (PyCFunction)register_start, METH_VARARGS, PyDoc_STR("register_start(value:str, path:str) -> int")},
    {"unregister_start", (PyCFunction)unregister_start, METH_VARARGS, PyDoc_STR("unregister_start(value:str) -> int")},
    {"have_start_value", (PyCFunction)have_start_value, METH_VARARGS, PyDoc_STR("have_start_value(value:str) -> int")},
    {"create_link", (PyCFunction)create_link, METH_VARARGS, PyDoc_STR("create_link(app:str, cmd:str, lnkpath:str, icopath:str) -> bool")},
    {"init_tray", (PyCFunction)init_tray, METH_VARARGS, PyDoc_STR("init_tray(tooltip:str, left_callback:function, right_callback:function) -> int")},
    {"remove_tray", (PyCFunction)remove_tray, METH_VARARGS, PyDoc_STR("remove_tray() -> None")},
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
