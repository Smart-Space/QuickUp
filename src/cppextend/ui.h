#include <windows.h>
#include <Python.h>

#define WM_TRAYICON (WM_USER + 100)
#define ID_SHOW 10
#define ID_ABOUT 11
#define ID_EXIT 12

NOTIFYICONDATAW nid = {};
// PyObject* py_callback_left = nullptr;
// PyObject* py_callback_right = nullptr;
PyObject* show_callback = nullptr;
PyObject* about_callback = nullptr;
PyObject* exit_callback = nullptr;

HMENU hmenu;//菜单句柄

LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam) {
    UINT WM_TASKBARCREATED = RegisterWindowMessage(TEXT("TaskbarCreated"));
    if (message == WM_TRAYICON) {
        PyGILState_STATE gstate = PyGILState_Ensure();
        switch (lParam) {
            case WM_LBUTTONDOWN:
                PyObject_CallObject(show_callback, NULL);
                break;
            case WM_RBUTTONDOWN:
                // 获取鼠标坐标
                POINT pt;
                GetCursorPos(&pt);
                SetForegroundWindow(hWnd);
                int res = TrackPopupMenu(hmenu, TPM_RETURNCMD, pt.x, pt.y, 0, hWnd, NULL);
                if (res == ID_SHOW) {
                    PyObject_CallObject(show_callback, NULL);
                } else if (res == ID_ABOUT) {
                    PyObject_CallObject(about_callback, NULL);
                } else if (res == ID_EXIT) {
                    PyObject_CallObject(exit_callback, NULL);
                    PostQuitMessage(0);
                }
                break;
        }
        PyGILState_Release(gstate);
    } else if (message == WM_TASKBARCREATED) {
        // 防止explora.exe重启后，原有的托盘图标消失
        Shell_NotifyIconW(NIM_ADD, &nid);
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

bool init_ui_tray(const wchar_t* tooltip, PyObject* _show_callback, PyObject* _about_callback, PyObject* _exit_callback) {
    Py_XINCREF(_show_callback);
    Py_XINCREF(_about_callback);
    Py_XINCREF(_exit_callback);
    show_callback = _show_callback;
    about_callback = _about_callback;
    exit_callback = _exit_callback;

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

    hmenu = CreatePopupMenu();
    AppendMenuW(hmenu, MF_STRING, ID_SHOW, L"显示");
    AppendMenuW(hmenu, MF_STRING, ID_ABOUT, L"关于");
    AppendMenuW(hmenu, MF_STRING, ID_EXIT, L"退出");

    return true;
}

void remove_ui_tray() {
    Shell_NotifyIconW(NIM_DELETE, &nid);
    ZeroMemory(&nid, sizeof(nid));

    Py_XDECREF(show_callback);
    Py_XDECREF(about_callback);
    Py_XDECREF(exit_callback);
    show_callback = about_callback = exit_callback = nullptr;
}
