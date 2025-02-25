import { useState } from "react";
import { signup } from "../api/auth"; // signup 함수 가져오기

export default function Signup() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await signup(formData);

    if (result.error) {
      alert(`회원가입 실패: ${result.error}`);
    } else {
      alert("회원가입 성공! 🎉");
    }
  };

  return (
    <div>
      <h1>회원가입</h1>
      <form onSubmit={handleSubmit}>
        <input type="text" name="username" placeholder="사용자명" onChange={handleChange} required />
        <input type="email" name="email" placeholder="이메일" onChange={handleChange} required />
        <input type="password" name="password" placeholder="비밀번호" onChange={handleChange} required />
        <button type="submit">회원가입</button>
      </form>
    </div>
  );
}
