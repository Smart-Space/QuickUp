#include <windows.h>
#include <Python.h>
#include <thread>

int modifers;
int key;
PyObject* callback;

MSG msg;
int hotkey_id;
DWORD listener_thread_id;

void stop_hotkey_listener(){
    PostThreadMessageW(listener_thread_id, WM_QUIT, 0, 0);
    UnregisterHotKey(NULL, hotkey_id);
    GlobalDeleteAtom(hotkey_id + 0xC000);
    Py_XDECREF(callback);
}

void create_hotkey_listener(){
    listener_thread_id = GetCurrentThreadId();
    RegisterHotKey(NULL, hotkey_id, modifers, key);
    while(GetMessageW(&msg, (HWND)-1, 0, 0)){
        if (msg.message == WM_HOTKEY && msg.wParam == hotkey_id){
            PyGILState_STATE gstate = PyGILState_Ensure();
            PyObject_CallObject(callback, NULL);
            PyGILState_Release(gstate);
        }
    }
}

void start_hotkey_listener(int _modifers, int _key, PyObject* _callback){
    Py_XINCREF(_callback);
    modifers = _modifers;
    key = _key;
    callback = _callback;
    hotkey_id = GlobalAddAtomW(L"QuickUpHotkey") - 0xC000;
    std::thread listener_thread(create_hotkey_listener);
    listener_thread.detach();
}
