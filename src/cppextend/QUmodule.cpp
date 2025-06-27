/*
Quickup C++ module
- quick_fuzz 模糊匹配
- register_start 注册开机自启动
- unregister_start 取消注册开机自启动
- have_start_value 判断是否存在开机自启动项
*/
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "quickfuzz.h"
#include "regrun.h"


static PyObject* quick_fuzz(PyObject* self, PyObject* args) {
    char* a;
    char* b;
    int result;
    int flag = PyArg_ParseTuple(args, "ss:quick_fuzz", &a, &b);
    if (!flag) {
        return NULL;
    }
    std::string a_str(a);
    std::string b_str(b);
    result = calculateSimilarity(a_str, b_str);
    return Py_BuildValue("i", result);
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

static PyMethodDef QUModuleMethods[] = {
    {"quick_fuzz", (PyCFunction)quick_fuzz, METH_VARARGS, PyDoc_STR("quick_fuzz(a:str, b:str) -> int")},
    {"register_start", (PyCFunction)register_start, METH_VARARGS, PyDoc_STR("register_start(value:str, path:str) -> int")},
    {"unregister_start", (PyCFunction)unregister_start, METH_VARARGS, PyDoc_STR("unregister_start(value:str) -> int")},
    {"have_start_value", (PyCFunction)have_start_value, METH_VARARGS, PyDoc_STR("have_start_value(value:str) -> int")},
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
