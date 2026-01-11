@REM vs prompt x64:
cl /utf-8 /LD /I/python/include QUmodule.cpp E:/python/libs/python313.lib advapi32.lib Ole32.lib user32.lib Shell32.lib Comctl32.lib dwmapi.lib /std:c++20 /O2 /DNDEBUG /Fe:QUmodule.pyd
