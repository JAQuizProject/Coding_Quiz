const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// 퀴즈 데이터 가져오기 (카테고리별 필터링 지원)
export const getQuizData = async (category = "") => {
  const token = localStorage.getItem("token");
  if (!token) return { error: "로그인이 필요합니다." };

  try {
    const url = category ? `${BASE_URL}/quiz/get?category=${category}` : `${BASE_URL}/quiz/get`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
    });

    const data = await response.json();
    if (!response.ok) throw new Error("퀴즈 데이터를 불러오지 못했습니다.");

    return data;
  } catch (error) {
    console.error("Quiz Data Fetch Error:", error);
    return { error: "서버 오류 발생" };
  }
};

export const getCategories = async () => {
  try {
    const response = await fetch(`${BASE_URL}/quiz/categories`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();
    if (!response.ok) throw new Error("카테고리를 불러오지 못했습니다.");

    return data;
  } catch (error) {
    console.error("Category Fetch Error:", error);
    return { error: "서버 오류 발생" };
  }
};

// 점수 제출 API
export const submitQuizScore = async (scoreData) => {
  try {
    const token = localStorage.getItem("token");
    if (!token) return { error: "로그인이 필요합니다." };

    const response = await fetch(`${BASE_URL}/quiz/submit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify(scoreData),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error("점수 저장 실패");
    }

    return data;
  } catch (error) {
    console.error("점수 제출 오류:", error);
    return { error: "서버 오류 발생" };
  }
};

