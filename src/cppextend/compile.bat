@echo off
REM Build the QuickUp C++ extension module via setup.py

setlocal
pushd "%~dp0"

python setup.py build_ext --inplace

set EXITCODE=%ERRORLEVEL%
popd

@REM rename cppextend\QUmodule.*.pyd to QUmodule.pyd
if exist QUmodule.*.pyd (
    ren QUmodule.*.pyd QUmodule.pyd
)

endlocal & exit /b %EXITCODE%
