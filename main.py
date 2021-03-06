# 작성자 : Redwing

# 실행 파일 생성 명령어 : 콘솔 창에 아래 명령이 입력
# pyinstaller -F -i=redwing.ico -n AutoSaveRestore main.py

import os
import datetime
import threading
import shutil
from enum import Enum


# 열거형 자료. C의 enum 과 유사.
class Result(Enum):
    NOFILE = 0  # 파일이 존재하지 않음(처음부터 없음)
    UPDATE = 1  # 파일이 변경됨
    STAY = 2  # 파일의 상태가 유지됨
    REMOVED = 3  # 파일이 있었는데 사라짐


# 파일 이름 및 경로. 현재는 내 로컬 경로.
route_path = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\LostRuins\\Saves"
save_file_name = "hardcore.sav"
backup_file_name = "hardcore_back.sav"

last_save_time = 0
run_flag = True  # 스레드 반복 플래그
previous_state = Result.NOFILE  #이전 상태를 저장하는 변수


# 세이브 파일이 변화되었는지 확인하는 함수.
def check_save_file_update():
    global last_save_time

    file_path = os.path.join(route_path, save_file_name)
    if not os.path.exists(file_path):
        if last_save_time == 0:  # 초기 상태, 즉 처음부터 세이브 파일이 없음

            print("no save file {0} founded.".format(save_file_name))
            return Result.NOFILE  # 파일이 없음
        else:
            print("save file is removed.")
            return Result.REMOVED  # 파일이 삭제됨

    else:
        mtime = os.path.getmtime(file_path)

        if last_save_time != mtime:
            if last_save_time == 0:  # 초기값
                print('save file found.')

            else:
                old_time = datetime.datetime.fromtimestamp(last_save_time)
                new_time = datetime.datetime.fromtimestamp(mtime)
                print('save file is updated. {0} -> {1}'.format(old_time, new_time))

            last_save_time = mtime

            # print(datetime.datetime.fromtimestamp(mtime))
            return Result.UPDATE
        else:
            return Result.STAY


# 세이브 파일을 백업
def backup_save_file():
    print("backup start.")
    file_path = os.path.join(route_path, save_file_name)
    backup_path = os.path.join(route_path, backup_file_name)
    shutil.copyfile(file_path, backup_path)
    print("backup complete.")


# 백업된 파일을 복구
def restore_save_file():
    print("save file restore start.")
    file_path = os.path.join(route_path, save_file_name)
    backup_path = os.path.join(route_path, backup_file_name)
    shutil.copyfile(backup_path, file_path)

    # 백업 파일을 복구한 시간을 적용
    global last_save_time
    mtime = os.path.getmtime(file_path)
    last_save_time = mtime
    print("restore complete.")


# 작업 함수
def worker():
    global previous_state
    res = check_save_file_update()  # 실제 작업 처리 부분

    if res != previous_state:  # 상태에 변화가 일어났을 때에만 로그 출력
        previous_state = res
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("[{1}] state : {0}".format(res, now))

    if res == Result.UPDATE:
        backup_save_file()  # 변경된 파일을 백업.

    elif res == Result.REMOVED:
        restore_save_file()  # 백업된 파일을 복구

    elif res == Result.NOFILE:  # 세이브 파일이 없음
        global run_flag   # 스레드 종료
        run_flag = False


# 작업 실행 스레드
def thread_run():
    global run_flag
    if run_flag:  # run_flag 가 true 일 때에만 실행
        worker()  # 실제 작업
        threading.Timer(3, thread_run).start()  # 3초 후 다음 작업 시작


# 세이브 파일이 있는지 확인하고, 없다면 경로 입력받기
def input_path():
    global route_path
    file_path = os.path.join(route_path, save_file_name)
    if not os.path.exists(file_path):
        print("{0} 에 세이브 파일(harcore.sav)가 없습니다.".format(route_path))
        print("다른 경로에 저장되어있다면 해당 경로를 입력해 주세요.")
        print("아직 하드코어 저장 파일이 생성되지 않았다면, 프로그램을 종료하고 세이브 파일 생성 후 재실행해 주시기 바랍니다.")
        route_path = input()


# 실행 부분
input_path()
thread_run()

