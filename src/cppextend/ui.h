#include <windows.h>
#include <Python.h>

NOTIFYICONDATAW nid = {};
PyObject* py_callback_left = nullptr;
PyObject* py_callback_right = nullptr;

#define WM_TRAYICON (WM_USER + 100)

LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam) {
    if (message == WM_TRAYICON) {
        switch (lParam) {
            PyGILState_STATE gstate;
            case WM_LBUTTONDOWN:
                gstate = PyGILState_Ensure();
                PyObject_CallObject(py_callback_left, NULL);
                PyGILState_Release(gstate);
                break;
            case WM_RBUTTONDOWN:
                // 获取鼠标坐标
                POINT pt;
                GetCursorPos(&pt);
                gstate = PyGILState_Ensure();
                PyObject* args = Py_BuildValue("(ii)", pt.x, pt.y);
                if (args) {
                    PyObject_CallObject(py_callback_right, args);
                    Py_DECREF(args);
                }
                PyGILState_Release(gstate);
                break;
        }
    }
    return DefWindowProc(hWnd, message, wParam, lParam);
}

// 创建隐藏窗口
HWND create_hidden_window() {
    HINSTANCE hInstance = GetModuleHandle(NULL);
    WNDCLASS wc = {};
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = (LPCTSTR)L"QuickUpTrayIconHiddenWindowClass";
    RegisterClass(&wc);
    return CreateWindow(
        wc.lpszClassName,
        (LPCTSTR)L"QuickUp Tray Icon Hidden Window",
        0,
        CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT,
        NULL,
        NULL,
        hInstance,
        NULL
    );
}

bool init_ui_tray(const wchar_t* tooltip, PyObject* left_callback, PyObject* right_callback) {
    Py_XINCREF(left_callback);
    Py_XINCREF(right_callback);
    py_callback_left = left_callback;
    py_callback_right = right_callback;

    // 创建隐藏窗口
    HWND hWnd = create_hidden_window();
    if (!hWnd) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create hidden window");
        return false;
    }

    HICON hIcon = (HICON)LoadImageW(
        NULL,
        L"./logo.ico",
        IMAGE_ICON,
        GetSystemMetrics(SM_CXICON),
        GetSystemMetrics(SM_CYICON),
        LR_LOADFROMFILE | LR_DEFAULTCOLOR
    );

    ZeroMemory(&nid, sizeof(nid));
    nid.cbSize = sizeof(NOTIFYICONDATAW);
    nid.hWnd = hWnd;
    nid.uID = 1;
    nid.uFlags = NIF_ICON | NIF_MESSAGE | NIF_TIP;
    nid.uCallbackMessage = WM_TRAYICON;
    nid.hIcon = hIcon;
    wcsncpy_s(nid.szTip, _countof(nid.szTip), tooltip, _TRUNCATE);

    Shell_NotifyIconW(NIM_ADD, &nid);
    return true;
}

void remove_ui_tray() {
    Shell_NotifyIconW(NIM_DELETE, &nid);
    ZeroMemory(&nid, sizeof(nid));

    Py_XDECREF(py_callback_left);
    Py_XDECREF(py_callback_right);
    py_callback_left = py_callback_right = nullptr;
}
