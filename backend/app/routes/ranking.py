from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from datetime import datetime
from ..core.database import get_db

router = APIRouter()


@router.get("/get")
def get_ranking(category: str = None, db: Session = Depends(get_db)):
    """
    특정 카테고리의 상위 점수 랭킹을 조회 (카테고리 선택이 없으면 전체 랭킹 반환)
    """
    print(f"요청 받은 category: {category}")

    try:
        query = """
            SELECT u.username, s.score, s.category, s.created_at
            FROM scores s
            JOIN users u ON s.user_id = u.id
        """

        params = {}
        if category and category != "전체":
            query += " WHERE s.category = :category"
            params["category"] = category
        elif category == "전체":  # "전체" 문제를 푼 사용자만 조회
            query += " WHERE s.category = '전체'"

        query += " ORDER BY s.score DESC, s.created_at ASC LIMIT 10"

        rankings = db.execute(text(query), params).fetchall()

        ranking_list = []
        for i, r in enumerate(rankings):
            created_at = r[3]  # created_at 값

            # created_at이 문자열이면 datetime 객체로 변환
            if isinstance(created_at, str):
                try:
                    created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    created_at = None  # 변환 실패 시 None 처리

            ranking_list.append({
                "rank": i + 1,
                "username": r[0],
                "score": r[1],
                "category": r[2],  # 카테고리 값 올바르게 설정
                "date": created_at.strftime("%Y-%m-%d %H:%M") if created_at else "N/A"
            })

        print(f"반환되는 랭킹 데이터: {ranking_list}")

        return {"message": "랭킹 조회 성공", "ranking": ranking_list}

    except Exception as e:
        print(f"❌ 랭킹 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"랭킹 조회 오류: {str(e)}")
