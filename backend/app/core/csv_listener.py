import os
import csv
import sqlite3
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# SQLite DB 연결 경로
DATABASE_PATH = "quiz_app.db"
# 감시할 CSV 파일 경로
CSV_FILE_PATH = "csv_files/quiz_data.csv"

# CSV 파일을 읽어 데이터베이스에 저장하는 함수
def store_csv_to_db(csv_file_path):
    """CSV 파일을 읽어와 데이터베이스에 저장"""
    if not os.path.exists(csv_file_path):
        print(f"CSV 파일을 찾을 수 없음: {csv_file_path}")
        return

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()

            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                # 첫 번째 줄(헤더) 읽기
                headers = next(csv_reader, None)

                if not headers or len(headers) < 4:
                    print(f"CSV 형식이 잘못됨: {csv_file_path}")
                    return

                for row in csv_reader:
                    if len(row) < 4:
                        print(f"잘못된 데이터 행 건너뜀: {row}")
                        continue

                    cursor.execute('''
                    REPLACE INTO quizzes (id, question, explanation, answer)
                    VALUES (?, ?, ?, ?)
                    ''', (row[0], row[1], row[2], row[3]))  # explanation 추가

            conn.commit()
            conn.close()
        print(f"CSV 파일 {csv_file_path} 데이터 저장 완료!")

    except Exception as e:
        print(f"CSV 처리 중 오류 발생: {str(e)}")


# 리스너 클래스 정의
class CsvFileListener(FileSystemEventHandler):
    def __init__(self, csv_file_path):
        self.csv_file_path = os.path.abspath(csv_file_path)

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
def start_csv_listener():
    watch_folder = os.path.dirname(CSV_FILE_PATH)  # 폴더 경로 추출
    os.makedirs(watch_folder, exist_ok=True)  # 폴더 없으면 생성

    observer = Observer()
    event_handler = CsvFileListener(CSV_FILE_PATH)
    observer.schedule(event_handler, path=watch_folder, recursive=False) # 현재 디렉토리에서만 감시
    # 리스너 시작
    observer.start()
    print(f"특정 CSV 파일 감시 중... ({CSV_FILE_PATH})")

    try:
        while True:
            time.sleep(1) # 파일 시스템 변경을 계속 감시
    except KeyboardInterrupt:
        print("\n CSV 감시 중지됨.")
        observer.stop() # 사용자가 종료하면 감시 종료
    observer.join()

if __name__ == "__main__":
    start_csv_listener()  # CSV 감시 시작