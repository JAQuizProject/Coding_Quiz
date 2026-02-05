"use client";

import { useState } from "react";
import { signup } from "../../api/auth";
import { useAlert } from "../../context/AlertContext";
import { Container, Form, Button, Card, Row, Col } from "react-bootstrap";
import styles from "./page.module.css";

export default function Signup() {
  const showAlert = useAlert();
  const [formData, setFormData] = useState({ username: "", email: "", password: "" });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await signup(formData);

    if (result.error) {
      showAlert("error", "회원가입 실패", result.error);
    } else {
      showAlert("success", "회원가입 성공!", `환영합니다, ${result.user.username}!`);
      setTimeout(() => {
        window.location.href = "/login";
      }, 2000);
    }
  };

  return (
    <Container className={`${styles.authContainer} d-flex justify-content-center align-items-center`}>
      <Row className="w-100">
        <Col md={6} className="mx-auto">
          <Card className="shadow p-4 rounded">
            <Card.Title className="text-center fs-3 fw-bold text-success">📝 회원가입</Card.Title>
            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-3">
                <Form.Label>사용자명</Form.Label>
                <Form.Control type="text" name="username" placeholder="사용자명 입력" onChange={handleChange} required />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>이메일</Form.Label>
                <Form.Control type="email" name="email" placeholder="이메일 입력" onChange={handleChange} required />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>비밀번호</Form.Label>
                <Form.Control type="password" name="password" placeholder="비밀번호 입력" onChange={handleChange} required />
              </Form.Group>

              <Button type="submit" className={`${styles.authButton} w-100 btn-success`}>
                회원가입
              </Button>
            </Form>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}
