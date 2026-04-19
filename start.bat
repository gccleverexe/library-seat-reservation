@echo off
chcp 65001 >nul
title 校园图书馆座位预约系统

echo ================================================
echo   校园图书馆座位预约系统 - 一键启动
echo ================================================
echo.

:: 切换到脚本所在目录
cd /d "%~dp0"

:: 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

:: 安装依赖（首次运行或依赖缺失时）
echo [1/3] 检查并安装依赖...
python -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查 requirements.txt
    pause
    exit /b 1
)
echo       依赖检查完成
echo.

:: 启动后端（新窗口）
echo [2/3] 启动后端服务 (http://localhost:8000) ...
start "后端服务 - FastAPI" cmd /k "cd /d "%~dp0" && python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

:: 等待后端启动
echo       等待后端就绪...
timeout /t 3 /nobreak >nul

:: 启动前端静态服务器（新窗口）
echo [3/3] 启动前端服务 (http://localhost:3000) ...
start "前端服务 - Static" cmd /k "cd /d "%~dp0\frontend" && python -m http.server 3000"

:: 等待前端启动
timeout /t 2 /nobreak >nul

echo.
echo ================================================
echo   启动完成！
echo.
echo   前端地址：http://localhost:3000
echo   后端接口：http://localhost:8000
echo   API 文档：http://localhost:8000/docs
echo.
echo   默认管理员账号：admin / admin123
echo ================================================
echo.

:: 自动打开浏览器
echo 正在打开浏览器...
start "" "http://localhost:3000"

echo.
echo 关闭此窗口不会停止服务。
echo 如需停止服务，请关闭"后端服务"和"前端服务"两个窗口。
echo.
pause
