"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
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
    <Container className={`cq-container ${styles.page}`}>
      <Row className="align-items-stretch gy-4">
        <Col lg={6}>
          <Card className={styles.card}>
            <Card.Body className={styles.cardBody}>
              <div className={styles.header}>
                <h1 className={styles.title}>로그인</h1>
                <p className={styles.subtitle}>
                  퀴즈 기록과 점수를 저장하려면 로그인하세요.
                </p>
              </div>

              <Form onSubmit={handleSubmit} className={styles.form}>
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
                    autoComplete="current-password"
                    onChange={handleChange}
                    required
                  />
                </Form.Group>

                <Button type="submit" size="lg" className={`w-100 ${styles.submit}`}>
                  로그인
                </Button>
              </Form>

              <div className={styles.footer}>
                계정이 없나요?{" "}
                <Link href="/signup" className={styles.footerLink}>
                  회원가입
                </Link>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={6} className={styles.posterCol}>
          <div className={`${styles.poster} cq-surface`}>
            <div className={styles.posterBackdrop} aria-hidden />
            <div className={styles.posterHeader}>
              <span className={styles.posterBadge}>SCORE</span>
              <span className={styles.posterText}>
                로그인하면 퀴즈 점수가 자동 저장되고 랭킹에 반영돼요.
              </span>
            </div>
            <div className={styles.posterImage}>
              <Image
                src="/illustrations/login-score-save.svg"
                alt="점수 저장 및 랭킹 반영 안내"
                fill
                sizes="(max-width: 992px) 100vw, 520px"
                className={styles.posterImg}
              />
            </div>
            <div className={styles.posterMeta}>
              <span className={styles.metaPill}>제출 즉시 저장</span>
              <span className={styles.metaPill}>카테고리별 누적</span>
              <span className={styles.metaPill}>랭킹 자동 반영</span>
            </div>
          </div>
        </Col>
      </Row>
    </Container>
  );
}
