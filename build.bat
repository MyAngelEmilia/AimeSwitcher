@echo off
chcp 65001 >nul
echo ========================================
echo   Aime 卡号快切 - 一键编译
echo ========================================
echo.

pip install keyboard pyinstaller >nul 2>&1

echo [1/2] 正在编译...
pyinstaller --noconfirm --onefile --windowed --name "Aime卡号快切" --uac-admin main.py

if %errorlevel% neq 0 (
    echo.
    echo [失败] 编译出错，请检查上方日志。
    pause
    exit /b 1
)

echo [2/2] 清理临时文件...
rmdir /s /q build 2>nul
del /q "Aime卡号快切.spec" 2>nul

echo.
echo ========================================
echo   编译完成!
echo   输出: dist\Aime卡号快切.exe
echo ========================================
echo.
pause
