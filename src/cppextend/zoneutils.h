#pragma once

#include <windows.h>
#include <winternl.h>
#include <appmodel.h>
#include <dwmapi.h>
#include <VersionHelpers.h>

#include <algorithm>
#include <atomic>
#include <cmath>
#include <cwchar>
#include <cwctype>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_map>
#include <vector>


typedef NTSTATUS (NTAPI *pNtQueryInformationProcess)(
    HANDLE ProcessHandle,
    ULONG ProcessInformationClass,
    PVOID ProcessInformation,
    ULONG ProcessInformationLength,
    PULONG ReturnLength
);

constexpr ULONG ProcessCommandLineInformation = 60;

static void CloseHandleIfNeeded(HANDLE handle) {
    if (handle) {
        CloseHandle(handle);
    }
}

static HANDLE OpenQueryLimitedProcess(DWORD pid) {
    if (pid == 0) {
        return nullptr;
    }
    return OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid);
}

static std::wstring GetFileNameFromPath(const std::wstring& path) {
    size_t pos = path.find_last_of(L"\\/");
    if (pos == std::wstring::npos) {
        return path;
    }
    return path.substr(pos + 1);
}

static std::wstring ToLowerCopy(std::wstring value) {
    std::transform(value.begin(), value.end(), value.begin(), [](wchar_t ch) {
        return static_cast<wchar_t>(std::towlower(ch));
    });
    return value;
}

static std::wstring GetProcessImagePath(DWORD pid) {
    HANDLE hProc = OpenQueryLimitedProcess(pid);
    if (!hProc) {
        return L"";
    }

    wchar_t exePath[MAX_PATH];
    DWORD size = MAX_PATH;
    std::wstring result;
    if (QueryFullProcessImageNameW(hProc, 0, exePath, &size)) {
        result.assign(exePath, size);
    }
    CloseHandleIfNeeded(hProc);
    return result;
}

static bool TryGetPackageFullName(DWORD pid, std::wstring& packageFullName) {
    packageFullName.clear();

    HANDLE hProc = OpenQueryLimitedProcess(pid);
    if (!hProc) {
        return false;
    }

    wchar_t pkgFullName[PACKAGE_FULL_NAME_MAX_LENGTH + 1] = { 0 };
    UINT32 len = PACKAGE_FULL_NAME_MAX_LENGTH;
    bool ok = (GetPackageFullName(hProc, &len, pkgFullName) == ERROR_SUCCESS);
    if (ok) {
        packageFullName.assign(pkgFullName);
    }
    CloseHandleIfNeeded(hProc);
    return ok;
}

static std::wstring GetWindowExecutablePath(HWND hwnd) {
    DWORD pid = 0;
    GetWindowThreadProcessId(hwnd, &pid);
    return GetProcessImagePath(pid);
}

std::wstring GetExistingProcessCommandLine(DWORD pid) {
    // 动态获取 ntdll!NtQueryInformationProcess
    static const auto NtQueryInfo = reinterpret_cast<pNtQueryInformationProcess>(GetProcAddress(GetModuleHandleW(L"ntdll.dll"), "NtQueryInformationProcess"));
    if (!NtQueryInfo) return L"";

    HANDLE hProc = OpenQueryLimitedProcess(pid);
    if (!hProc) {
        return L"";
    }

    // 第一次调用获取所需缓冲区大小
    ULONG returnLength = 0;
    NTSTATUS status = NtQueryInfo(hProc, ProcessCommandLineInformation, nullptr, 0, &returnLength);
    
    if (returnLength == 0) {
        CloseHandleIfNeeded(hProc);
        return L"";
    }

    // 分配缓冲区并正式读取
    std::vector<BYTE> buffer(returnLength);
    status = NtQueryInfo(hProc, ProcessCommandLineInformation, buffer.data(), returnLength, &returnLength);
    CloseHandleIfNeeded(hProc);

    if (status != 0) { // STATUS_SUCCESS = 0
        return L"";
    }

    // 解析 UNICODE_STRING
    auto* ustr = reinterpret_cast<UNICODE_STRING*>(buffer.data());
    if (ustr->Length == 0 || ustr->Buffer == nullptr || ustr->Length < sizeof(WCHAR)) {
        return L""; // 进程可能无命令行参数
    }
    // 获取启动参数
    std::wstring cmdLine(ustr->Buffer, ustr->Length / sizeof(WCHAR));
    size_t i = 0;
    size_t len = cmdLine.length();
    while (i < len && cmdLine[i] == L' ') ++i; // 去除开头空格
    if (i >= len) {
        return L"";
    }
    if (cmdLine[i] == L'"') { // 去除双引号
        ++i;
        while (i < len && cmdLine[i]!= L'"') ++i;
        ++i;
    } else { // 没有双引号，取到第一个空格
        while (i < len && cmdLine[i] != L' ') ++i;
    }
    while (i < len && cmdLine[i] == L' ') ++i; // 去除参数之间空格
    return cmdLine.substr(i);
}

std::wstring GetWindowPackageFeature(HWND hwnd) {
    DWORD pid = 0;
    GetWindowThreadProcessId(hwnd, &pid);
    if (pid == 0) return L"";

    std::wstring packageFullName;
    if (TryGetPackageFullName(pid, packageFullName)) {
        return packageFullName;
    }

    return GetProcessImagePath(pid);
}

struct WindowIdentity {
    HWND hwnd = nullptr;
    HWND identityHwnd = nullptr;
    std::wstring packageFullName;
    std::wstring exePath;
    bool isPackaged = false;
    std::wstring feature;
};

static BOOL CALLBACK FindCoreWindowChildProc(HWND child, LPARAM lParam) {
    HWND* found = reinterpret_cast<HWND*>(lParam);
    if (!found || *found) {
        return FALSE;
    }
    wchar_t className[256];
    if (GetClassNameW(child, className, 256)) {
        if (wcscmp(className, L"Windows.UI.Core.CoreWindow") == 0) {
            *found = child;
            return FALSE;
        }
    }
    return TRUE;
}

static HWND FindCoreWindowChild(HWND hwnd) {
    HWND found = nullptr;
    EnumChildWindows(hwnd, FindCoreWindowChildProc, reinterpret_cast<LPARAM>(&found));
    return found;
}

static WindowIdentity ResolveWindowIdentity(HWND hwnd) {
    WindowIdentity identity;
    identity.hwnd = hwnd;
    identity.identityHwnd = hwnd;

    wchar_t className[256];
    if (GetClassNameW(hwnd, className, 256)) {
        if (wcscmp(className, L"ApplicationFrameWindow") == 0) {
            HWND child = FindCoreWindowChild(hwnd);
            if (child) {
                identity.identityHwnd = child;
            }
        }
    }

    if (identity.identityHwnd == hwnd) {
        std::wstring hostExePath = GetWindowExecutablePath(hwnd);
        if (!hostExePath.empty()) {
            std::wstring hostFile = GetFileNameFromPath(hostExePath);
            if (_wcsicmp(hostFile.c_str(), L"ApplicationFrameHost.exe") == 0) {
                HWND child = FindCoreWindowChild(hwnd);
                if (child) {
                    identity.identityHwnd = child;
                }
            }
        }
    }

    DWORD pid = 0;
    GetWindowThreadProcessId(identity.identityHwnd, &pid);
    if (pid == 0) {
        return identity;
    }

    identity.isPackaged = TryGetPackageFullName(pid, identity.packageFullName);
    if (!identity.isPackaged) {
        identity.exePath = GetProcessImagePath(pid);
    }

    identity.feature = identity.isPackaged ? identity.packageFullName : identity.exePath;

    return identity;
}

namespace WindowMonitor {
    struct ManagedWindow {
        RECT originalRect;
        UINT lastState;
    };
    std::unordered_map<HWND, ManagedWindow> managedWindows;
    std::mutex managedMutex;

    HWINEVENTHOOK hLocationHook = nullptr;
    HWINEVENTHOOK hMoveSizeHook = nullptr;
    HWINEVENTHOOK hDestroyHook = nullptr;

    // 记录窗口被接管前的状态
    void RegisterManagedWindow(HWND hwnd) {
        std::lock_guard<std::mutex> lock(managedMutex);
        // 如果未被追踪过，才记录其最原始状态
        if (managedWindows.find(hwnd) == managedWindows.end()) {
            ManagedWindow mw;
            WINDOWPLACEMENT wp = { sizeof(wp) };
            if (GetWindowPlacement(hwnd, &wp)) {
                mw.lastState = wp.showCmd;
                if (wp.showCmd == SW_NORMAL || wp.showCmd == SW_SHOWNORMAL) {
                    GetWindowRect(hwnd, &mw.originalRect);
                } else {
                    mw.originalRect = wp.rcNormalPosition;
                }
                managedWindows[hwnd] = mw;
            }
        }
    }

    void DisableRoundCorners(HWND hwnd) {
        // 禁用圆角
        if (!IsWindows10OrGreater()) {
            return;
        }
        int cornerPreference = DWMWCP_DONOTROUND;
        DwmSetWindowAttribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, &cornerPreference, sizeof(cornerPreference));
    }

    void EnableRoundCorners(HWND hwnd) {
        // 启用圆角
        if (!IsWindows10OrGreater()) {
            return;
        }
        int cornerPreference = DWMWCP_ROUND;
        DwmSetWindowAttribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, &cornerPreference, sizeof(cornerPreference));
    }

    // 专门处理窗口移动、缩放、最大化还原
    void CALLBACK LocationWinEventProc(
        HWINEVENTHOOK hWinEventHook, DWORD event, HWND hwnd,
        LONG idObject, LONG idChild, DWORD dwEventThread, DWORD dwmsEventTime
    ) {
        // 只关心窗口自身
        if (idObject != OBJID_WINDOW || idChild != CHILDID_SELF || hwnd == nullptr) return;

        // 窗口销毁时清理内存
        if (event == EVENT_OBJECT_DESTROY) {
            std::lock_guard<std::mutex> lock(managedMutex);
            managedWindows.erase(hwnd);
            return;
        }

        std::lock_guard<std::mutex> lock(managedMutex);
        auto it = managedWindows.find(hwnd);
        if (it == managedWindows.end()) return;

        // 用户通过标题栏拖拽或边缘缩放
        if (event == EVENT_SYSTEM_MOVESIZESTART) {
            managedWindows.erase(it); // 用户介入，解除接管
            return;
        }

        // 状态变化（最大化/最小化/普通状态）
        if (event == EVENT_OBJECT_LOCATIONCHANGE) {
            WINDOWPLACEMENT wp = { sizeof(wp) };
            if (GetWindowPlacement(hwnd, &wp)) {
                if (wp.showCmd == SW_MAXIMIZE) {
                    // 将还原位置写回为原始窗口大小，避免还原时需要强制调整
                    WINDOWPLACEMENT newWp = wp;
                    newWp.rcNormalPosition = it->second.originalRect;
                    SetWindowPlacement(hwnd, &newWp);
                    it->second.lastState = SW_MAXIMIZE; // 记录已最大化
                    // 解除接管，恢复圆角
                    EnableRoundCorners(hwnd);
                    managedWindows.erase(it);
                } else if (wp.showCmd == SW_SHOWMINIMIZED || wp.showCmd == SW_MINIMIZE) {
                    it->second.lastState = SW_SHOWMINIMIZED;
                } else if (wp.showCmd == SW_NORMAL || wp.showCmd == SW_SHOWNORMAL) {
                    it->second.lastState = SW_NORMAL;
                }
            }
        }
    }

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

    // 判断是否为候选主窗口（过滤掉启动小窗、工具窗等）
    bool IsCandidateMainWindow(HWND hwnd, bool resizeableOnly = true) {
        if (!IsWindow(hwnd) || !IsWindowVisible(hwnd)) {
            return false;
        }

        LONG style = GetWindowLong(hwnd, GWL_STYLE);
        LONG exStyle = GetWindowLong(hwnd, GWL_EXSTYLE);

        // 必须有标题栏
        if (!(style & WS_CAPTION)) {
            return false;
        }

        // 过滤工具窗口/浮动小窗
        if (exStyle & WS_EX_TOOLWINDOW) {
            return false;
        }

        // 只保留可最大化/可调整大小的典型主窗口
        if (resizeableOnly && (style & WS_SIZEBOX) == 0 && (style & WS_MAXIMIZEBOX) == 0) {
            return false;
        }

        return true;
    }

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

        // 过滤掉明显的非主窗口 (例如有所有者的弹出窗口)
        if (GetWindow(hwnd, GW_OWNER) != NULL) {
            return;
        }

        // 进一步过滤（只保留典型主窗口，排除启动小窗等）
        if (!IsCandidateMainWindow(hwnd)) {
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

        // 监听拖拽开始
        hMoveSizeHook = SetWinEventHook(
            EVENT_SYSTEM_MOVESIZESTART, EVENT_SYSTEM_MOVESIZESTART,
            NULL, LocationWinEventProc,
            0, 0, WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS
        );

        // 监听位置及状态改变
        hLocationHook = SetWinEventHook(
            EVENT_OBJECT_LOCATIONCHANGE, EVENT_OBJECT_LOCATIONCHANGE,
            NULL, LocationWinEventProc,
            0, 0, WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS
        );

        // 监听销毁事件清理内存
        hDestroyHook = SetWinEventHook(
            EVENT_OBJECT_DESTROY, EVENT_OBJECT_DESTROY,
            NULL, LocationWinEventProc,
            0, 0, WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS
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

    bool IsCurrentContextDpiUnaware() {
        // 判断当前线程的 DPI 无感知
        DPI_AWARENESS_CONTEXT context = GetThreadDpiAwarenessContext();
        if (AreDpiAwarenessContextsEqual(context, DPI_AWARENESS_CONTEXT_UNAWARE)) {
            return true;
        }
#ifdef DPI_AWARENESS_CONTEXT_UNAWARE_GDISCALED
        if (AreDpiAwarenessContextsEqual(context, DPI_AWARENESS_CONTEXT_UNAWARE_GDISCALED)) {
            return true;
        }
#endif
        return false;
    }

    LONG ScaleCoord(LONG value, float factor) {
        return static_cast<LONG>(std::lround(static_cast<double>(value) * factor));
    }

    LONG UnscaleCoord(LONG value, float factor) {
        if (factor <= 0.0f) {
            return value;
        }
        return static_cast<LONG>(std::lround(static_cast<double>(value) / factor));
    }

    RECT AdjustRectForSizeWindowToRect(HWND hwnd, RECT logicalRect) {
        UINT dpi = GetDpiForWindow(hwnd);
        if (dpi == 0) {
            dpi = 96;
        }
        float dpiFactor = dpi / 96.0f;
        bool callerDpiUnaware = IsCurrentContextDpiUnaware();

        // 任务配置使用逻辑坐标，这里统一先转换到物理像素坐标进行计算。
        RECT newWindowRectPhysical = {
            ScaleCoord(logicalRect.left, dpiFactor),
            ScaleCoord(logicalRect.top, dpiFactor),
            ScaleCoord(logicalRect.right, dpiFactor),
            ScaleCoord(logicalRect.bottom, dpiFactor)
        };

        RECT windowRectCaller{};
        GetWindowRect(hwnd, &windowRectCaller);

        RECT windowRectPhysical = windowRectCaller;
        if (callerDpiUnaware) {
            windowRectPhysical.left = ScaleCoord(windowRectCaller.left, dpiFactor);
            windowRectPhysical.top = ScaleCoord(windowRectCaller.top, dpiFactor);
            windowRectPhysical.right = ScaleCoord(windowRectCaller.right, dpiFactor);
            windowRectPhysical.bottom = ScaleCoord(windowRectCaller.bottom, dpiFactor);
        }
        
        RECT frameRect{};
        // 获取窗口的可视化边框范围
        if (SUCCEEDED(DwmGetWindowAttribute(hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, &frameRect, sizeof(frameRect))))
        {
            // 计算逻辑边框与可视化边框的差值
            LONG leftMargin = frameRect.left - windowRectPhysical.left;
            LONG rightMargin = frameRect.right - windowRectPhysical.right;
            LONG bottomMargin = frameRect.bottom - windowRectPhysical.bottom;
            // 调整窗口理论大小
            newWindowRectPhysical.left -= leftMargin;
            newWindowRectPhysical.right -= rightMargin;
            newWindowRectPhysical.bottom -= bottomMargin;
        }

        // 不可调整大小的窗口
        if ((::GetWindowLong(hwnd, GWL_STYLE) & WS_SIZEBOX) == 0)
        {
            newWindowRectPhysical.right = newWindowRectPhysical.left + (windowRectPhysical.right - windowRectPhysical.left);
            newWindowRectPhysical.bottom = newWindowRectPhysical.top + (windowRectPhysical.bottom - windowRectPhysical.top);
        }

        if (!callerDpiUnaware) {
            return newWindowRectPhysical;
        }

        RECT callerRect = {
            UnscaleCoord(newWindowRectPhysical.left, dpiFactor),
            UnscaleCoord(newWindowRectPhysical.top, dpiFactor),
            UnscaleCoord(newWindowRectPhysical.right, dpiFactor),
            UnscaleCoord(newWindowRectPhysical.bottom, dpiFactor)
        };
        return callerRect;
    }

    
    // 窗口快照信息结构
    struct WindowSnapshot {
        HWND hwnd;
        std::wstring processName; // 进程文件名
        std::wstring commandArgs; // 启动参数
        RECT realRect;            // 真实位置和大小 (物理像素，不含阴影)
        bool isMinimized;         // 是否最小化
        bool isMaximized;         // 是否最大化
        bool isRoundCorner;        // 是否圆角
    };
    struct EnumData {
        std::vector<WindowSnapshot>* snapshots;
        std::vector<std::wstring>* minimizedNames;
    };

    inline bool ShouldIgnoreProcess(const std::wstring& processName) {
        if (processName.empty()) {
            return true;
        }
        std::wstring fileName = GetFileNameFromPath(processName);
        
        if (fileName == L"ApplicationFrameHost.exe") {
            return true;
        }
        
        return false;
    }

    BOOL CALLBACK EnumWindowsProc(HWND hwnd, LPARAM lParam) {
        EnumData* data = reinterpret_cast<EnumData*>(lParam);
        if (!data) return TRUE;

        // 只保留可改变大小的主窗口
        if (!IsCandidateMainWindow(hwnd, false)) {
            return TRUE;
        }

        WindowIdentity identity = ResolveWindowIdentity(hwnd);
        std::wstring processName = identity.feature;
        if (ShouldIgnoreProcess(processName)) {
            return TRUE;
        }

        RECT realRect = { 0 };
        if (FAILED(DwmGetWindowAttribute(hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, &realRect, sizeof(realRect)))) {
            GetWindowRect(hwnd, &realRect);
        }
        std::wstring exeFile = GetFileNameFromPath(identity.exePath);
        if (_wcsicmp(exeFile.c_str(), L"explorer.exe") == 0) {
            UINT dpi = GetDpiForWindow(hwnd);
            if (dpi == 0) {
                dpi = 96;
            }
            float dpiFactor = dpi / 96.0f;
            const int eps = static_cast<int>(20 * dpiFactor);
            RECT worker_size;
            SystemParametersInfo(SPI_GETWORKAREA, 0, &worker_size, 0);
            if (!IsZoomed(hwnd) &&
                std::abs((realRect.right - realRect.left) - (worker_size.right - worker_size.left)) <= eps &&
                std::abs((realRect.bottom - realRect.top) - (worker_size.bottom - worker_size.top)) <= eps) {
                // 可能是桌面窗口
                return TRUE;
            }
        } else if (_wcsicmp(exeFile.c_str(), L"QuickUp.exe") == 0) {
            // 过滤掉自己
            return TRUE;
        }

        DWORD processId = 0;
        GetWindowThreadProcessId(hwnd, &processId);
        std::wstring commandArgs = GetExistingProcessCommandLine(processId);

        bool isMinimized = IsIconic(hwnd) ? true : false;
        bool isMaximized = IsZoomed(hwnd) ? true : false;
        bool isRoundCorner = true; // 统一认为是圆角，考虑到无法识别Windows snap窗口

        if (data->snapshots) {
            data->snapshots->push_back({ hwnd, processName, commandArgs, realRect, isMinimized, isMaximized, isRoundCorner });
        }

        if (data->minimizedNames && isMinimized) {
            data->minimizedNames->push_back(processName);
        }

        return TRUE;
    }

    std::vector<WindowSnapshot> GetAllMainWindowSnapshots() {
        std::vector<WindowSnapshot> results;
        EnumData data = { &results, nullptr };
        EnumWindows(EnumWindowsProc, reinterpret_cast<LPARAM>(&data));
        return results;
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

        if (hEventHook) {
            UnhookWinEvent(hEventHook);
            hEventHook = nullptr;
        }
        if (hMoveSizeHook) {
            UnhookWinEvent(hMoveSizeHook);
            hMoveSizeHook = nullptr;
        }
        if (hLocationHook) {
            UnhookWinEvent(hLocationHook);
            hLocationHook = nullptr;
        }
        if (hDestroyHook) {
            UnhookWinEvent(hDestroyHook);
            hDestroyHook = nullptr;
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
}

void SmoothMoveWindow(HWND hwnd, int x, int y, int w, int h, bool zone_round) {
    WindowMonitor::RegisterManagedWindow(hwnd);

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
    std::wstring lowerInput = ToLowerCopy(input);
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
        std::wstring normalizedPath = input;
        std::replace(normalizedPath.begin(), normalizedPath.end(), L'\\', L'/');
        std::wstring fileName = GetFileNameFromPath(normalizedPath);
        if (fileName.empty()) {
            return input; // 即使可执行文件在Path，仍建议写全路径
        }
        return ToLowerCopy(fileName);
    }
}
