const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function getRanking(category = "전체") {
  try {
    // FastAPI 서버 주소로 요청 보내기
    const response = await fetch(`${BASE_URL}/ranking/get?category=${encodeURIComponent(category)}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error("랭킹 데이터를 가져오는 데 실패했습니다.");
    }

    return await response.json();
  } catch (error) {
    console.error("❌ 랭킹 API 호출 중 오류 발생:", error);
    return { ranking: [] }; // 오류 발생 시 빈 배열 반환
  }
}
