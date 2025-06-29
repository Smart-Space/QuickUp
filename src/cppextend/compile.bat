@REM vs prompt x64:
cl /LD /I/python/include QUmodule.cpp E:/python/libs/python313.lib advapi32.lib /std:c++20 /O2 /DNDEBUG
del QUmodule.pyd
ren QUmodule.dll QUmodule.pyd
