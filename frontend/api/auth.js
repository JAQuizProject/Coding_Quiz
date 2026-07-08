const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"; // 환경변수 적용

const getErrorMessage = async (response, fallbackMessage) => {
  try {
    const errorBody = await response.json();

    if (typeof errorBody?.detail === "string") {
      return errorBody.detail;
    }

    if (Array.isArray(errorBody?.detail) && errorBody.detail.length > 0) {
      const firstDetail = errorBody.detail[0];
      if (typeof firstDetail?.msg === "string") {
        return firstDetail.msg;
      }
    }
  } catch (parseError) {
    console.error("Error response parse failed:", parseError);
  }

  return fallbackMessage;
};

export const signup = async (userData) => {
  try {
    const response = await fetch(`${BASE_URL}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const errorMessage = await getErrorMessage(response, "회원가입에 실패했습니다.");
      return { error: errorMessage };
    }

    return await response.json();
  } catch (error) {
    console.error("Signup Error:", error);
    return { error: "서버와 연결할 수 없습니다." };
  }
};

export const login = async (userData) => {
  try {
    const response = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    localStorage.setItem("token", data.access_token); // JWT 토큰 저장
    return data;
  } catch (error) {
    console.error("Login Error:", error);
    return { error: "서버와 연결할 수 없습니다." };
  }
};

// 토큰 검증 API
export const verifyToken = async () => {
  const token = localStorage.getItem("token");
  if (!token) return { error: "토큰 없음" };

  try {
    const response = await fetch(`${BASE_URL}/auth/verify-token`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new Error("토큰이 유효하지 않음");
    }

    return await response.json();
  } catch (error) {
    console.error("Token Verify Error:", error);
    return { error: "토큰 검증 실패" };
  }
};

// 로그아웃 (프론트에서만 처리)
export const logout = async () => {
  localStorage.removeItem("token");
  return { message: "로그아웃 완료" };
};
