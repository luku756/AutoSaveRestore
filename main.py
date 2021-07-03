# 작성자 : Redwing

import os
import datetime
import threading
from enum import Enum


# 열거형 자료. C의 enum 과 유사.
class Result(Enum):
    NOFILE = 0  # 파일이 존재하지 않음(처음부터 없음)
    UPDATE = 1  # 파일이 변경됨
    STAY = 2  # 파일의 상태가 유지됨
    REMOVED = 3  # 파일이 있었는데 사라짐


route_path = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\LostRuins\\Saves"
save_file_name = "1.sav"
backup_file_name = "hardcore_back.sav"

last_save_time = 0
run_flag = False  # 스레드 반복 플래그


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
        print("save file exist")
        mtime = os.path.getmtime(file_path)

        if last_save_time != mtime:
            print('save file updated. {0} -> {1}'.format(last_save_time, mtime))

            last_save_time = mtime

            print(datetime.datetime.fromtimestamp(mtime))
            return Result.UPDATE
        else:
            return Result.STAY


def backup_save_file():
    print("backup start.")


def restore_save_file():
    print("save file restore start.")


def worker():
    res = check_save_file_update()  # 실제 작업 처리 부분
    print("res : {0}".format(res))

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
        worker() # 실제 작업
        threading.Timer(2, thread_run).start()  # 3초 후 다음 작업 시작


check_save_file_update()
run_flag = True
thread_run()