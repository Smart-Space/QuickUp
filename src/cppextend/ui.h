#include <windows.h>
#include <Python.h>
#include <thread>

#define WM_TRAYICON (WM_USER + 100)
#define ID_SHOW 10
#define ID_ABOUT 11
#define ID_EXIT 12

NOTIFYICONDATAW nid = {};
PyObject* about_callback = nullptr;
PyObject* exit_callback = nullptr;

HWND quickup_window;// QuickUp主窗口句柄
HMENU hmenu;// 菜单句柄

void ShowWindow() {
    ShowWindow(quickup_window, SW_SHOW);
    SetForegroundWindow(quickup_window);
}
void AboutWindow() {
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject_CallObject(about_callback, NULL);
    PyGILState_Release(gstate);
}
void ExitWindow() {
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject_CallObject(exit_callback, NULL);
    PyGILState_Release(gstate);
}
LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam) {
    static UINT WM_TASKBARCREATED = RegisterWindowMessage(TEXT("TaskbarCreated"));
    if (message == WM_TRAYICON) {
        switch (lParam) {
            case WM_LBUTTONDOWN:
                ShowWindow();
                break;
            case WM_RBUTTONDOWN:
                // 获取鼠标坐标
                POINT pt;
                GetCursorPos(&pt);
                SetForegroundWindow(hWnd);
                if (IsWindowVisible(quickup_window) || IsIconic(quickup_window)) {
                    ShowWindow();
                }
                int res = TrackPopupMenu(hmenu, TPM_RETURNCMD, pt.x, pt.y, 0, hWnd, NULL);
                if (res == ID_SHOW) {
                    ShowWindow();
                } else if (res == ID_ABOUT) {
                    std::thread([]{ AboutWindow(); }).detach();
                } else if (res == ID_EXIT) {
                    ExitWindow();
                    PostQuitMessage(0);
                }
                break;
        }
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

bool init_ui_tray(HWND quhwnd, const wchar_t* tooltip, PyObject* _about_callback, PyObject* _exit_callback) {
    Py_XINCREF(_about_callback);
    Py_XINCREF(_exit_callback);
    about_callback = _about_callback;
    exit_callback = _exit_callback;

    quickup_window = GetParent(quhwnd);

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

    Py_XDECREF(about_callback);
    Py_XDECREF(exit_callback);
    about_callback = exit_callback = nullptr;
}


class DropTarget {
public:
    DropTarget(HWND _hwnd, PyObject* _callback) : hwnd(_hwnd), callback(_callback) {
        Py_INCREF(callback);
    }

    ~DropTarget() {
        Py_DECREF(callback);
        callback = nullptr;
        RemoveWindowSubclass(hwnd, StaticDropProc, 0);
        DragAcceptFiles(hwnd, FALSE);
        hwnd = nullptr;
    }

    void enable_drop() {
        DragAcceptFiles(hwnd, TRUE);
        SetWindowSubclass(hwnd, StaticDropProc, 0, reinterpret_cast<DWORD_PTR>(this));
    }
private:
    HWND hwnd;
    PyObject* callback;

    static LRESULT CALLBACK StaticDropProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam, UINT_PTR uIdSubclass, DWORD_PTR dwRefData) {
        DropTarget* target = reinterpret_cast<DropTarget*>(dwRefData);
        if (message == WM_DROPFILES) {
            PyGILState_STATE gstate = PyGILState_Ensure();
            wchar_t filename[MAX_PATH];
            DragQueryFileW(reinterpret_cast<HDROP>(wParam), 0, filename, MAX_PATH);
            PyObject* pyfilename = PyUnicode_FromWideChar(filename, -1);
            PyObject* arg = PyTuple_Pack(1, pyfilename);
            PyObject_CallObject(target->callback, arg);
            Py_DECREF(arg);
            Py_DECREF(pyfilename);
            DragFinish(reinterpret_cast<HDROP>(wParam));
            PyGILState_Release(gstate);
        }
        return DefSubclassProc(hWnd, message, wParam, lParam);
    }
};

int detect_theme() {
    HKEY hKey;
    DWORD value = 1; // 默认明亮
    DWORD size = sizeof(DWORD);
    LONG result = RegOpenKeyExW(HKEY_CURRENT_USER,
        L"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
        0, KEY_READ, &hKey);
    if (result == ERROR_SUCCESS) {
        RegQueryValueExW(hKey, L"AppsUseLightTheme", nullptr, nullptr, (LPBYTE)&value, &size);
        RegCloseKey(hKey);
    } else {
        return 1;
    }
    return value;
}
