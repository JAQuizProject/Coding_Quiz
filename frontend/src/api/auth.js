const BASE_URL = "http://127.0.0.1:8000"; // FastAPI 주소

export const signup = async (userData) => {
  try {
    const response = await fetch("http://127.0.0.1:8000/auth/signup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
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

    return await response.json();
  } catch (error) {
    console.error("Login Error:", error);
    return { error: "서버와 연결할 수 없습니다." };
  }
};
