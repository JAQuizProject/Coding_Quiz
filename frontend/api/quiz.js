const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export const getQuizData = async () => {
  const token = localStorage.getItem("token"); // 토큰 가져오기
  console.log("getQuizData 요청 토큰:", token);
  if (!token) return { error: "로그인이 필요합니다." };

  try {
    const response = await fetch(`${BASE_URL}/quiz/quiz`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`, // 인증 헤더 추가
      },
    });

    console.log("getQuizData 응답 상태 코드:", response.status);

    if (!response.ok) {
      throw new Error("퀴즈 데이터를 불러오지 못했습니다.");
    }

    return await response.json();
  } catch (error) {
    console.error("Quiz Data Fetch Error:", error);
    return { error: "서버 오류가 발생했습니다." };
  }
};
