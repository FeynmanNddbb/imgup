@echo off
REM imgup Windows 图片上传工具启动脚本
REM 双击此文件即可打开图形界面

REM 尝试使用 pythonw（无控制台窗口）
where pythonw >nul 2>&1
if %errorlevel% == 0 (
    start "" pythonw "%~dp0upload_gui.py"
    exit
)

REM 如果没有 pythonw，使用 python
where python >nul 2>&1
if %errorlevel% == 0 (
    start "" python "%~dp0upload_gui.py"
    exit
)

REM 如果都没有，显示错误
echo 错误: 未找到 Python 环境
echo.
echo 请先安装 Python 3.x：
echo https://www.python.org/downloads/
echo.
pause
