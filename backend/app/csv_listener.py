import csv
import sqlite3
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# CSV 파일을 읽어 데이터베이스에 저장하는 함수
def store_csv_to_db(csv_file_path):
    conn = sqlite3.connect('your_database.db')  # SQLite DB 연결
    cursor = conn.cursor()

    # CSV 파일을 읽어와서 데이터베이스에 저장
    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        # CSV 헤더 건너뛰기 (첫 번째 줄은 열 이름일 경우)
        next(csv_reader)

        for row in csv_reader:
            cursor.execute('''
            INSERT INTO quizzes (id, question, answer)
            VALUES (?, ?, ?)
            ''', (row[0], row[1], row[2]))  # 각 열에 맞는 값 넣기

    conn.commit()
    conn.close()
    print(f"CSV 파일 {csv_file_path} 내용을 DB에 저장 완료!")

# 리스너 클래스 정의
class CsvFileListener(FileSystemEventHandler):
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path == self.csv_file_path:  # 지정된 CSV 파일이 생성되었을 때
            print(f"CSV 파일 {event.src_path} 가 생성되었습니다. DB에 저장을 시작합니다.")
            store_csv_to_db(event.src_path)  # CSV 파일 읽어서 DB에 저장

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path == self.csv_file_path:  # 지정된 CSV 파일이 수정되었을 때
            print(f"CSV 파일 {event.src_path} 가 수정되었습니다. DB에 저장을 시작합니다.")
            store_csv_to_db(event.src_path)  # CSV 파일 읽어서 DB에 저장

# 모니터링할 CSV 파일 경로
csv_file_path = 'your_file.csv'  # 모니터링할 CSV 파일 경로

# Watchdog Observer 설정
observer = Observer()
event_handler = CsvFileListener(csv_file_path)
observer.schedule(event_handler, path='.', recursive=False)  # 현재 디렉토리에서만 감시

# 리스너 시작
observer.start()

try:
    while True:
        time.sleep(1)  # 파일 시스템 변경을 계속 감시
except KeyboardInterrupt:
    observer.stop()  # 사용자가 종료하면 감시 종료
observer.join()
