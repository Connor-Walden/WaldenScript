@echo off
echo.
call ./scripts/Windows/install.bat
call ./scripts/Windows/wdscript.bat ./src/ScriptTest
echo.