"use client";

import { useState } from "react";
import { login } from "../../api/auth";
import { useAlert } from "../../context/AlertContext";
import { Container, Form, Button, Card, Row, Col } from "react-bootstrap";
import styles from "./page.module.css";

export default function Login() {
  const showAlert = useAlert();
  const [formData, setFormData] = useState({ email: "", password: "" });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await login(formData);

    if (result.error) {
      showAlert("error", "로그인 실패", result.error);
    } else {
      showAlert("success", "로그인 성공!", `환영합니다, ${result.user.username}`).then(() => {
        window.location.href = "/";
      });
    }
  };

  return (
    <Container className={`${styles.authContainer} d-flex justify-content-center align-items-center`}>
      <Row className="w-100">
        <Col md={6} className="mx-auto">
          <Card className="shadow p-4 rounded">
            <Card.Title className="text-center fs-3 fw-bold text-primary">🔑 로그인</Card.Title>
            <Form onSubmit={handleSubmit}>
              <Form.Group className="mb-3">
                <Form.Label>이메일</Form.Label>
                <Form.Control type="email" name="email" placeholder="이메일 입력" onChange={handleChange} required />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>비밀번호</Form.Label>
                <Form.Control type="password" name="password" placeholder="비밀번호 입력" onChange={handleChange} required />
              </Form.Group>

              <Button type="submit" className={`${styles.authButton} w-100`}>
                로그인
              </Button>
            </Form>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}
