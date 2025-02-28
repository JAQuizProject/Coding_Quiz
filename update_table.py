import sqlite3

DATABASE_PATH = "backend/quiz_app.db"


def reset_quiz_table():
    """기존 테이블 삭제 후 새 테이블 생성"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 기존 테이블 삭제
    cursor.execute("DROP TABLE IF EXISTS quizzes")

    # 새로운 테이블 생성
    cursor.execute('''
        CREATE TABLE quizzes (
            id INTEGER PRIMARY KEY,
            question TEXT NOT NULL,
            explanation TEXT,  -- 설명 필드 추가
            answer TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("quizzes 테이블 재생성 완료!")


if __name__ == "__main__":
    reset_quiz_table()