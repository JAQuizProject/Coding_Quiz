import os
import csv
import sqlite3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# SQLite DB 연결 경로
DATABASE_PATH = "quiz_app.db"
# 감시할 CSV 파일 경로
CSV_FILE_PATH = "csv_files/quiz_data.csv"

observer = None  # 감시 객체 전역 변수

# 데이터베이스가 비어 있는지 확인하는 함수
def is_db_empty():
    """데이터베이스에 데이터가 있는지 확인"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM quizzes")
            count = cursor.fetchone()[0]
            return count == 0  # 데이터가 없으면 True 반환
    except sqlite3.Error as e:
        print(f"DB 확인 중 오류 발생: {str(e)}")
        return True  # 오류 발생 시 데이터를 저장하도록 처리

# CSV 파일을 읽어 데이터베이스에 저장하는 함수
def store_csv_to_db(CSV_FILE_PATH):
    """CSV 파일을 읽어와 데이터베이스에 저장"""
    if not os.path.exists(CSV_FILE_PATH):
        print(f"CSV 파일을 찾을 수 없음: {CSV_FILE_PATH}")
        return

    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            with open(CSV_FILE_PATH, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                headers = next(csv_reader, None)

                if not headers or len(headers) < 4:
                    print(f"CSV 형식이 잘못됨: {CSV_FILE_PATH}")
                    return

                for row_number, row in enumerate(csv_reader, start=2):  # 2번째 줄부터 시작 (1번째는 헤더)
                    # 빈 행이면 건너뜀
                    if not any(row):
                        print(f"⚠ [행 {row_number}] 빈 행 건너뜀")
                        continue

                    if len(row) < 4:
                        print(f"⚠ [행 {row_number}] 잘못된 데이터 행 건너뜀: {row}")
                        continue

                    try:
                        quiz_id = int(row[0])  # ID는 정수로 변환
                        question = row[1]
                        explanation = row[2]
                        answer = str(row[3])  # answer를 문자열로 변환하여 저장

                        cursor.execute('''
                        REPLACE INTO quizzes (id, question, explanation, answer)
                        VALUES (?, ?, ?, ?)
                        ''', (quiz_id, question, explanation, answer))
                    except Exception as e:
                        print(f"❌ [행 {row_number}] 데이터 변환 오류: {row}, 오류: {str(e)}")
                        continue  # 오류 발생한 행은 건너뜀

            conn.commit()
        print(f"✅ CSV 파일 {CSV_FILE_PATH} 데이터 저장 완료!")
    except Exception as e:
        print(f"🚨 CSV 처리 중 오류 발생: {str(e)}")

# 리스너 클래스 정의
class CsvFileListener(FileSystemEventHandler):
    def __init__(self, CSV_FILE_PATH):
        self.CSV_FILE_PATH = os.path.abspath(CSV_FILE_PATH)

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path == self.CSV_FILE_PATH:
            print(f"CSV 파일 {event.src_path} 가 수정되었습니다.")
            print("DB에 저장을 시작합니다.")
            store_csv_to_db(event.src_path)

# CSV 감시 시작 함수
def start_csv_listener():
    global observer
    if observer is None or not observer.is_alive():
        watch_folder = os.path.dirname(CSV_FILE_PATH)
        os.makedirs(watch_folder, exist_ok=True)

        # 데이터베이스 확인 후 CSV 데이터 삽입 여부 결정
        if is_db_empty():
            print("데이터베이스가 비어 있습니다. CSV 데이터를 불러옵니다...")
            store_csv_to_db(CSV_FILE_PATH)
        else:
            print("데이터베이스에 기존 데이터가 존재합니다.")

        observer = Observer()
        event_handler = CsvFileListener(CSV_FILE_PATH)
        observer.schedule(event_handler, path=watch_folder, recursive=False)
        observer.start()
        print(f"CSV 감시 시작됨... ({CSV_FILE_PATH})")

# CSV 감시 중지 함수
def stop_csv_listener():
    global observer
    if observer:
        observer.stop()
        observer.join()
        print("CSV 감시가 중지되었습니다.")