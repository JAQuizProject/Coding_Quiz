"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
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
    <Container className={`cq-container ${styles.page}`}>
      <Row className="align-items-stretch gy-4">
        <Col lg={6}>
          <Card className={styles.card}>
            <Card.Body className={styles.cardBody}>
              <div className={styles.header}>
                <h1 className={styles.title}>회원가입</h1>
                <p className={styles.subtitle}>
                  간단히 가입하고 퀴즈 점수와 랭킹에 도전해 보세요.
                </p>
              </div>

              <Form onSubmit={handleSubmit} className={styles.form}>
                <Form.Group className="mb-3">
                  <Form.Label className={styles.label}>사용자명</Form.Label>
                  <Form.Control
                    type="text"
                    name="username"
                    placeholder="표시될 이름"
                    autoComplete="username"
                    onChange={handleChange}
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label className={styles.label}>이메일</Form.Label>
                  <Form.Control
                    type="email"
                    name="email"
                    placeholder="name@example.com"
                    autoComplete="email"
                    onChange={handleChange}
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label className={styles.label}>비밀번호</Form.Label>
                  <Form.Control
                    type="password"
                    name="password"
                    placeholder="비밀번호 입력"
                    autoComplete="new-password"
                    onChange={handleChange}
                    required
                  />
                </Form.Group>

                <Button type="submit" size="lg" className={`w-100 ${styles.submit}`}>
                  회원가입
                </Button>
              </Form>

              <div className={styles.footer}>
                이미 계정이 있나요?{" "}
                <Link href="/login" className={styles.footerLink}>
                  로그인
                </Link>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={6} className={styles.posterCol}>
          <div className={`${styles.poster} cq-surface`}>
            <div className={styles.posterBackdrop} aria-hidden />
            <div className={styles.posterHeader}>
              <span className={styles.posterBadge}>NEW</span>
              <span className={styles.posterText}>
                가입 후 바로 퀴즈를 시작할 수 있어요.
              </span>
            </div>
            <div className={styles.posterImage}>
              <Image
                src="/signup.png"
                alt="회원가입 화면 예시"
                fill
                sizes="(max-width: 992px) 100vw, 520px"
                className={styles.posterImg}
              />
            </div>
          </div>
        </Col>
      </Row>
    </Container>
  );
}
