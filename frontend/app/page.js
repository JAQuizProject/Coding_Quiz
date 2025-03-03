"use client";
import Link from "next/link";
import styles from "./page.module.css";
import { Container, Button, Row, Col } from "react-bootstrap";

export default function Home() {
  return (
    <div className={styles.pageContainer}>
      <div className={styles.background}></div>

      <Container className="text-center mt-5">
        <Row className="justify-content-center">
          <Col md={8} lg={6} className={`${styles.contentBox} p-4`}>
            <h1 className="fw-bold text-dark">🚀 코딩 면접 대비 퀴즈</h1>
            <p className="mt-3">
              자바스크립트, 자바, 파이썬 관련된 문제들이 무작위로 출제됩니다!
            </p>
            <p>⚡ 기술 면접을 대비하는 문제로 구성되어 있어 실전 감각을 키울 수 있어요.</p>

            <Link href="/quiz">
              <Button variant="primary" size="lg" className="mt-3">
                퀴즈 시작하기 →
              </Button>
            </Link>
          </Col>
        </Row>
      </Container>
    </div>
  );
}
