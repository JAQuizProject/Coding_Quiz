import { useState } from "react";
import { login } from "../api/auth"; // login 함수 가져오기

export default function Login() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await login(formData);

    if (result.error) {
      alert(`로그인 실패: ${result.error}`);
    } else {
      alert(`로그인 성공! 환영합니다, ${result.user.username}`);
    }
  };

  return (
    <div>
      <h1>로그인</h1>
      <form onSubmit={handleSubmit}>
        <input type="email" name="email" placeholder="이메일" onChange={handleChange} required />
        <input type="password" name="password" placeholder="비밀번호" onChange={handleChange} required />
        <button type="submit">로그인</button>
      </form>
    </div>
  );
}
