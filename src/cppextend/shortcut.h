#include <windows.h>
#include <shellapi.h>
#include <shlobj.h>
#include <wchar.h>


bool CreateLinkFile(LPCWSTR appPath, LPCWSTR cmdLine, LPCOLESTR lnkPath, LPCWSTR iconPath) {
    HRESULT hr = CoInitialize(NULL);
    if (FAILED(hr)) {
        return false;
    }
    IShellLinkW* pShellLink = NULL;
    hr = CoCreateInstance(CLSID_ShellLink, NULL, CLSCTX_INPROC_SERVER, IID_IShellLinkW, (LPVOID*)&pShellLink);
    if (SUCCEEDED(hr)) {
        pShellLink->SetPath(appPath);
        std::wstring strTmp = appPath;
        size_t start = strTmp.find_last_of(L"/\\");
        pShellLink->SetWorkingDirectory((LPCWSTR)(strTmp.substr(0, start).c_str()));
        pShellLink->SetArguments(cmdLine);
        if (iconPath) {
            pShellLink->SetIconLocation(iconPath, 0);
        }
        IPersistFile* pPersistFile = NULL;
        hr = pShellLink->QueryInterface(IID_IPersistFile, (LPVOID*)&pPersistFile);
        if (SUCCEEDED(hr)) {
            hr = pPersistFile->Save(lnkPath, FALSE);
            pPersistFile->Release();
        }
        pShellLink->Release();
    }
    CoUninitialize();
    return SUCCEEDED(hr);
}