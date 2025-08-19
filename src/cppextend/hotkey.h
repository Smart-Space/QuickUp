#include <windows.h>
#include <Python.h>
#include <thread>
#include <chrono>

int modifers;
int key;
PyObject* callback;
MSG msg;
int hotkey_id;
bool running;


void stop_hotkey_listener(){
    running = false;
    UnregisterHotKey(NULL, hotkey_id);
    GlobalDeleteAtom(hotkey_id + 0xC000);
    Py_XDECREF(callback);
}

void create_hotkey_listener(){
    RegisterHotKey(NULL, hotkey_id, modifers, key);
    while(running){
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        if (PeekMessageW(&msg, NULL, 0, 0, PM_REMOVE)){
            if (msg.message == WM_HOTKEY && msg.wParam == hotkey_id){
                PyGILState_STATE gstate = PyGILState_Ensure();
                PyObject_CallObject(callback, NULL);
                PyGILState_Release(gstate);
            }
        }
    }
}

void start_hotkey_listener(int _modifers, int _key, PyObject* _callback){
    Py_XINCREF(_callback);
    modifers = _modifers;
    key = _key;
    callback = _callback;
    hotkey_id = GlobalAddAtomW(L"QuickUpHotkey") - 0xC000;
    running = true;
    std::thread listener_thread(create_hotkey_listener);
    listener_thread.detach();
}
