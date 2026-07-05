#pragma once

#include <windows.h>

#include <array>
#include <chrono>
#include <string>
#include <thread>
#include <vector>

#include "zoneutils.h"

static std::array<int, 4> get_worker_size() {
    RECT rect;
    SystemParametersInfo(SPI_GETWORKAREA, 0, &rect, 0);
    return {rect.left, rect.top, rect.right, rect.bottom};
}

static int ZONE_TRY_TIMES = 20;
void set_zone_try_times(int times) {
    ZONE_TRY_TIMES = times;
}

// 查找目标窗口的真实HWND
// 通过特征名称匹配最近显示的主窗口，返回找到的窗口句柄，未找到返回NULL
HWND find_target_window(
    const std::wstring& exePath,
    std::chrono::steady_clock::time_point launchTime
) {
    std::wstring featureName = extractCoreName(exePath);
    if (featureName.empty()) {
        return NULL;
    }
    // std::wcout << L"featureName: " << featureName << std::endl;

    HWND targetHwnd = NULL;
    std::wstring normalizedFeatureName = ToLowerCopy(featureName);

    for (int i = 0; i < ZONE_TRY_TIMES; ++i) {
        // 获取线程安全的倒序列表（最新的在前）
        std::vector<WindowMonitor::WindowRecord> recentHwnds = WindowMonitor::GetRecentWindowsReversed();

        for (const auto& record : recentHwnds) {
            if (record.showTime < launchTime) {
                continue; // 过期的窗口不处理
            }

            HWND hwnd = record.hwnd;
            if (!IsWindow(hwnd) || !IsWindowVisible(hwnd)) continue;

            // 处理 UWP 架构
            WCHAR className[256];
            GetClassNameW(hwnd, className, 256);
            std::wstring wsClassName(className);

            // 如果不小心抓到了内层内容窗口，向上追溯找到最外层框架
            if (wsClassName == L"Windows.UI.Core.CoreWindow") {
                HWND rootHwnd = GetAncestor(hwnd, GA_ROOT);
                if (rootHwnd && rootHwnd != hwnd) {
                    hwnd = rootHwnd; // 把操作对象替换为外层框架
                } else {
                    continue; // 还没被框架托管，跳过等待下一次循环
                }
            }

            // UWP/WinUI3 Cloaked 检查
            int cloakedVal = 0;
            HRESULT hr = DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, &cloakedVal, sizeof(cloakedVal));
            if (SUCCEEDED(hr) && cloakedVal & DWM_CLOAKED_INHERITED) {
                continue;
            }

            WindowIdentity identity = ResolveWindowIdentity(hwnd);
            std::wstring feature = ToLowerCopy(identity.feature);
            
            // 倒叙匹配新窗口成功
            if (!feature.empty() && feature.find(normalizedFeatureName) != std::wstring::npos) {
                targetHwnd = hwnd;
                break; 
            }
        }

        if (targetHwnd) {
            break; // 找到，跳出重试循环
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    return targetHwnd;
}

bool modify_window_position(
    SHELLEXECUTEINFOW& sei,
    const std::wstring& exePath,
    std::chrono::steady_clock::time_point launchTime,
    int x, int y, int width, int height,
    bool zone_round
) {
    HWND targetHwnd = find_target_window(exePath, launchTime);
    if (targetHwnd) {
        // std::wcout << L"Window found. Applying layout..." << std::endl;
        WaitForInputIdle(sei.hProcess, 100);
        SmoothMoveWindow(targetHwnd, x, y, width, height, zone_round);
    } else {
        // std::wcerr << L"Timeout: Window not found." << std::endl;
    }

    return true;
}
