#include <windows.h>
#include <appmodel.h>
#include <dwmapi.h>
#include <string>
#include <thread>
#include <vector>
#include <algorithm>
#include <mutex>

std::wstring GetWindowPackageFeature(HWND hwnd) {
    DWORD pid = 0;
    GetWindowThreadProcessId(hwnd, &pid);
    if (pid == 0) return L"";

    HANDLE hProc = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid);
    if (!hProc) return L"";

    wchar_t pkgFullName[PACKAGE_FULL_NAME_MAX_LENGTH + 1] = { 0 };
    UINT32 len = PACKAGE_FULL_NAME_MAX_LENGTH;
    if (GetPackageFullName(hProc, &len, pkgFullName) == ERROR_SUCCESS) {
        CloseHandle(hProc);
        return std::wstring(pkgFullName);
    }

    wchar_t exePath[MAX_PATH];
    DWORD size = MAX_PATH;
    if (QueryFullProcessImageNameW(hProc, 0, exePath, &size)) {
        CloseHandle(hProc);
        return std::wstring(exePath);
    }
    CloseHandle(hProc);
    return L"";
}

namespace WindowMonitor {
    // 带有时间戳的窗口记录
    struct WindowRecord {
        HWND hwnd;
        std::chrono::steady_clock::time_point showTime;

        bool operator==(const HWND& other) const {
            return hwnd == other;
        }
    };

    std::vector<WindowRecord> recentWindows;
    std::mutex rwMutex;
    
    std::thread monitorThread;
    std::atomic<bool> isListening{false};
    DWORD threadId = 0;
    HWINEVENTHOOK hEventHook = nullptr;

    const size_t MAX_RECENT_WINDOWS = 30;

    // WinEvent 回调函数
    void CALLBACK WinEventProc(
        HWINEVENTHOOK hWinEventHook,
        DWORD event,
        HWND hwnd,
        LONG idObject,
        LONG idChild,
        DWORD dwEventThread,
        DWORD dwmsEventTime
    ) {
        // 只关心顶层窗口本身的事件
        if (idObject != OBJID_WINDOW || idChild != CHILDID_SELF || hwnd == nullptr) {
            return;
        }

        // 过滤掉非顶层窗口
        if (GetParent(hwnd) != NULL) {
            return;
        }

        // 过滤掉明显的非主窗口 (例如没有所有者的弹出窗口)
        if (GetWindow(hwnd, GW_OWNER) != NULL) {
            return;
        }

        // 跳过不含标题栏的某些阴影或辅助窗口
        long style = GetWindowLong(hwnd, GWL_STYLE);
        if (!(style & WS_CAPTION)) {
            return;
        }

        auto now = std::chrono::steady_clock::now();

        std::lock_guard<std::mutex> lock(rwMutex);
        
        // 避免重复添加相同的 HWND
        std::erase_if(recentWindows, [hwnd](const WindowRecord& r) {
            return r.hwnd == hwnd;
        });
        
        // 最新的在最后
        recentWindows.push_back({hwnd, now});

        // 维持 vector 大小
        if (recentWindows.size() > MAX_RECENT_WINDOWS) {
            recentWindows.erase(recentWindows.begin());
        }
    }

    // 线程执行的监听循环
    void MessageLoop() {
        // 记录当前线程ID
        threadId = GetCurrentThreadId();

        hEventHook = SetWinEventHook(
            EVENT_OBJECT_SHOW, EVENT_OBJECT_SHOW,
            NULL,
            WinEventProc,
            0, 0, // 监听所有进程和线程
            WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS // 进程外回调，跳过自己
        );

        if (!hEventHook) {
            // std::wcerr << L"Failed to set WinEventHook!" << std::endl;
            return;
        }

        MSG msg;
        while (GetMessage(&msg, NULL, 0, 0)) {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }

        // 退出前清理
        if (hEventHook) {
            UnhookWinEvent(hEventHook);
            hEventHook = nullptr;
        }
    }

    void DisableRoundCorners(HWND hwnd) {
        // 禁用圆角
        int cornerPreference = DWMWCP_DONOTROUND;
        DwmSetWindowAttribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, &cornerPreference, sizeof(cornerPreference));
    }

    RECT AdjustRectForSizeWindowToRect(HWND hwnd, RECT rect) {
        RECT newWindowRect = rect;
        RECT windowRect{};
        GetWindowRect(hwnd, &windowRect);
        float dpiFactor = GetDpiForWindow(hwnd) / 96.0; // QuickUp未开启DPI感知，这里需要乘以系统DPI因子，后面同理
        windowRect.left *= dpiFactor;
        windowRect.top *= dpiFactor;
        windowRect.right *= dpiFactor;
        windowRect.bottom *= dpiFactor;
        
        RECT frameRect{};
        // 获取窗口的可视化边框范围
        if (SUCCEEDED(DwmGetWindowAttribute(hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, &frameRect, sizeof(frameRect))))
        {
            // 计算逻辑边框与可视化边框的差值
            LONG leftMargin = frameRect.left - windowRect.left;
            LONG rightMargin = frameRect.right - windowRect.right;
            LONG bottomMargin = frameRect.bottom - windowRect.bottom;
            // 调整窗口理论大小
            newWindowRect.left -= leftMargin/dpiFactor;
            newWindowRect.right -= rightMargin/dpiFactor;
            newWindowRect.bottom -= bottomMargin/dpiFactor;
        }

        // 不可调整大小的窗口
        if ((::GetWindowLong(hwnd, GWL_STYLE) & WS_SIZEBOX) == 0)
        {
            newWindowRect.right = newWindowRect.left + (windowRect.right - windowRect.left)/dpiFactor;
            newWindowRect.bottom = newWindowRect.top + (windowRect.bottom - windowRect.top)/dpiFactor;
        }

        return newWindowRect;
    }

    //==========外部的接口==========

    void Start() {
        if (isListening) return;
        isListening = true;
        
        {
            std::lock_guard<std::mutex> lock(rwMutex);
            recentWindows.clear();
            recentWindows.reserve(MAX_RECENT_WINDOWS+1);// 预留一个位置
        }

        monitorThread = std::thread(MessageLoop);
    }

    void Stop() {
        if (!isListening) return;
        isListening = false;

        // 向子线程发送 WM_QUIT 消息
        if (threadId != 0) {
            PostThreadMessage(threadId, WM_QUIT, 0, 0);
        }

        if (monitorThread.joinable()) {
            monitorThread.join();
        }

        {
            std::lock_guard<std::mutex> lock(rwMutex);
            recentWindows.clear();
        }
        threadId = 0;
    }

    // 获取最近窗口的一份拷贝，以便主线程慢慢处理而不长时间占用锁
    std::vector<WindowRecord> GetRecentWindowsReversed() {
        std::lock_guard<std::mutex> lock(rwMutex);
        std::vector<WindowRecord> copy = recentWindows;
        std::reverse(copy.begin(), copy.end()); // 翻转，最新的在最前面
        return copy;
    }

    // 删除被处理过的 HWND
    void RemoveHandledWindow(HWND hwnd) {
        std::lock_guard<std::mutex> lock(rwMutex);
        auto it = std::find(recentWindows.begin(), recentWindows.end(), hwnd);
        if (it != recentWindows.end()) {
            recentWindows.erase(it);
        }
    }

    static bool ZONE_ROUND_CORNERS = false;
    void SetRoundCornersEnabled(bool enable) {
        ZONE_ROUND_CORNERS = enable;
    }
}

void SmoothMoveWindow(HWND hwnd, int x, int y, int w, int h, bool zone_round) {
    if (IsIconic(hwnd)) {
        ShowWindow(hwnd, SW_RESTORE);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    if (!zone_round) {
        WindowMonitor::DisableRoundCorners(hwnd);
    }

    RECT rect = { x, y, x + w, y + h };
    rect = WindowMonitor::AdjustRectForSizeWindowToRect(hwnd, rect);
    x = rect.left;
    y = rect.top;
    w = rect.right - x;
    h = rect.bottom - y;

    UINT flags = SWP_NOZORDER | SWP_NOACTIVATE | SWP_ASYNCWINDOWPOS;
    SetWindowPos(hwnd, NULL, x, y, w, h, flags);
}

// 分割字符串函数
std::vector<std::wstring> split(const std::wstring& s, char delimiter) {
    std::vector<std::wstring> tokens;
    std::wstring token;
    for (wchar_t c : s) {
        if (c == delimiter) {
            if (!token.empty()) {
                tokens.push_back(token);
                token.clear();
            }
        } else {
            token += c;
        }
    }
    if (!token.empty()) {
        tokens.push_back(token);
    }
    return tokens;
}

// 提取核心名称
std::wstring extractCoreName(const std::wstring& input) {
    if (input.empty()) {
        return L"";
    }

    // 判断是否是shell路径
    std::wstring lowerInput = input;
    std::transform(lowerInput.begin(), lowerInput.end(), lowerInput.begin(), ::tolower);
    if (lowerInput.starts_with(L"shell:")) {
        // 处理shell路径：shell:appsfolder\xxx_yyy!app
        std::vector<std::wstring> parts = split(lowerInput, L'\\');
        if (parts.empty()) {
            return input; // 不知道在写什么，返回原值
        }
        std::wstring lastPart = parts.back();
        
        // 按!分割取前面部分
        std::vector<std::wstring> nameParts = split(lastPart, L'_');
        if (nameParts.empty()) {
            return lastPart; // 没有_分割，返回最后一整部分
        }
        return nameParts[0];
    } else if (lowerInput.starts_with(L"http:") || lowerInput.starts_with(L"https:") || lowerInput.starts_with(L"ftp:") ||
               lowerInput.starts_with(L"mailto:") || lowerInput.starts_with(L"steam:")) {
        return L""; // 其他类型暂不处理
    } else {
        // 处理常规文件路径：d:/a/b.exe
        // 如果是单独打开能使用默认应用启动文件的话，无能为力。应当是使用应用+命令行
        std::wstring normalizedPath = lowerInput;
        std::replace(normalizedPath.begin(), normalizedPath.end(), L'\\', L'/');
        
        std::vector<std::wstring> parts = split(normalizedPath, L'/');
        if (parts.empty()) {
            return input; // 即使可执行文件在Path，仍建议写全路径
        }
        return parts.back();
    }
}