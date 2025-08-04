#include <windows.h>
#include <iostream>

bool set_startup_registry(const std::wstring value_name, const std::wstring app_path) {
    HKEY hKey;
    std::wstring sub_key = L"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run";
    if (RegCreateKeyExW(HKEY_CURRENT_USER, sub_key.c_str(), 0, NULL, 0, KEY_WRITE, NULL, &hKey, NULL) != ERROR_SUCCESS) {
        return false;
    }
    if (RegSetValueExW(hKey, value_name.c_str(), 0, REG_SZ, (const BYTE*)app_path.c_str(), (app_path.length() + 1)* sizeof(wchar_t)) != ERROR_SUCCESS) {
        RegCloseKey(hKey);
        return false;
    }
    RegCloseKey(hKey);
    return true;
}

bool delete_startup_registry(const std::wstring value_name) {
    HKEY hKey;
    std::wstring sub_key = L"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run";
    if (RegOpenKeyExW(HKEY_CURRENT_USER, sub_key.c_str(), 0, KEY_WRITE, &hKey) != ERROR_SUCCESS) {
        return false;
    }
    if (RegDeleteValueW(hKey, value_name.c_str()) != ERROR_SUCCESS) {
        RegCloseKey(hKey);
        return false;
    }
    RegCloseKey(hKey);
    return true;
}

bool have_value(const std::wstring value_name) {
    HKEY hKey;
    std::wstring sub_key = L"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run";
    if (RegOpenKeyExW(HKEY_CURRENT_USER, sub_key.c_str(), 0, KEY_READ, &hKey) != ERROR_SUCCESS) {
        return false;
    }
    bool have_value = false;
    if (RegQueryValueExW(hKey, value_name.c_str(), NULL, NULL, NULL, NULL) == ERROR_SUCCESS) {
        have_value = true;
    }
    RegCloseKey(hKey);
    return have_value;
}

std::wstring invalid_chars[] = {L"\\", L"/", L":", L"*", L"?", L"\"", L"<", L">", L"|"};
bool valid_windows_filename(const std::wstring filename) {
    for (auto invalid_char : invalid_chars) {
        if (filename.find(invalid_char) != std::wstring::npos) {
            return false;
        }
    }
    // 不以空格或.结尾
    if (filename.back() == L' ' || filename.back() == L'.') {
        return false;
    }
    return true;
}
