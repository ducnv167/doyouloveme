@echo off
REM ================================
REM Step 1: Cài đặt thư viện
REM ================================
echo Installing requirements...
call pip install -r requirements.txt

REM ================================
REM Step 2: Mở 5 terminal chạy song song
REM ================================
REM Lấy thư mục hiện tại (nơi đặt file .bat)
set BASE_DIR=%~dp0

wt ^
new-tab cmd /k "cd /d %BASE_DIR% & doskey run=python main.py --file account1 & doskey reset=python reset_is_done.py --file account1 & python main.py --file account1" ^
; split-pane -H cmd /k "cd /d %BASE_DIR% & doskey run=python main.py --file account2 & doskey reset=python reset_is_done.py --file account2 & python main.py --file account2" ^
; split-pane -V cmd /k "cd /d %BASE_DIR% & doskey run=python main.py --file account3 & doskey reset=python reset_is_done.py --file account3 & python main.py --file account3" ^
; split-pane -H cmd /k "cd /d %BASE_DIR% & doskey run=python main.py --file account4 & doskey reset=python reset_is_done.py --file account4 & python main.py --file account4" ^
; split-pane -V cmd /k "cd /d %BASE_DIR% & doskey run=python main.py --file account5 & doskey reset=python reset_is_done.py --file account5 & python main.py --file account5"



echo All tasks started.