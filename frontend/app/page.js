"use client";
import Link from "next/link";
import Image from "next/image";
import styles from "./page.module.css";
import { Container, Button, Row, Col } from "react-bootstrap";

export default function Home() {
  return (
    <div className={styles.page}>
      <Container className="cq-container">
        <div className={`${styles.shell} cq-surface`}>
          <div className={styles.shellBackdrop} aria-hidden />

          <Row className="align-items-center gy-4">
            <Col lg={6} className={styles.copy}>
              <div className={styles.reveal1}>
                <div className={styles.kicker}>
                  <span className="cq-chip">Interview Ready</span>
                  <span className={styles.kickerDot} aria-hidden />
                  <span className={styles.kickerText}>매일 10분, 실전 감각</span>
                </div>
                <h1 className={styles.title}>
                  코딩 면접 대비
                  <span className={styles.titleAccent}> 퀴즈</span>
                </h1>
                <p className={styles.lead}>
                  자바스크립트, 자바, 파이썬 핵심 문제로 빠르게 점검하고, 틀린 문제는
                  결과 화면에서 다시 복기하세요.
                </p>
              </div>

              <div className={`${styles.ctaRow} ${styles.reveal2}`}>
                <Button
                  as={Link}
                  href="/quiz"
                  size="lg"
                  variant="primary"
                  className={styles.ctaPrimary}
                >
                  퀴즈 시작하기
                </Button>
                <Button
                  as={Link}
                  href="/ranking"
                  size="lg"
                  variant="outline-primary"
                  className={styles.ctaSecondary}
                >
                  랭킹 보기
                </Button>
              </div>

              <div className={`${styles.chips} ${styles.reveal3}`}>
                <span className="cq-chip">JavaScript</span>
                <span className="cq-chip">Java</span>
                <span className="cq-chip">Python</span>
              </div>

              <div className={`${styles.stats} ${styles.reveal3}`}>
                <div className={styles.statItem}>
                  <div className={styles.statValue}>즉시 채점</div>
                  <div className={styles.statLabel}>정답 확인 후 바로 피드백</div>
                </div>
                <div className={styles.statItem}>
                  <div className={styles.statValue}>자동 저장</div>
                  <div className={styles.statLabel}>중간에 나가도 답안 유지</div>
                </div>
              </div>

              <div className={`${styles.detailGrid} ${styles.reveal3}`}>
                <article className={styles.detailCard}>
                  <div className={styles.detailImageWrap}>
                    <Image
                      src="/illustrations/detail-random10.svg"
                      alt="전체 챕터 랜덤 10문제"
                      fill
                      sizes="(max-width: 992px) 100vw, 250px"
                      className={styles.detailImage}
                    />
                  </div>
                  <h3 className={styles.detailTitle}>전체 모드 랜덤 10문제</h3>
                  <p className={styles.detailBody}>
                    매번 다른 세트로 출제되어 반복 학습에 유리합니다.
                  </p>
                </article>

                <article className={styles.detailCard}>
                  <div className={styles.detailImageWrap}>
                    <Image
                      src="/illustrations/detail-admarket.svg"
                      alt="ADmarket 카테고리 묶음"
                      fill
                      sizes="(max-width: 992px) 100vw, 250px"
                      className={styles.detailImage}
                    />
                  </div>
                  <h3 className={styles.detailTitle}>ADmarket 통합 카테고리</h3>
                  <p className={styles.detailBody}>
                    Corp, Bidding, Message를 한 번에 학습할 수 있어요.
                  </p>
                </article>
              </div>
            </Col>

            <Col lg={6} className={styles.reveal2}>
              <div className={styles.preview}>
                <Image
                  src="/illustrations/hero-dashboard.svg"
                  alt="Coding Quiz 대시보드 일러스트"
                  fill
                  priority
                  sizes="(max-width: 992px) 100vw, 520px"
                  className={styles.previewImage}
                />
              </div>
              <div className={styles.previewCaption}>
                <span className={styles.captionCode}>CQ</span>
                <span className={styles.captionText}>단계별로 풀고, 끝에서 제출</span>
              </div>
            </Col>
          </Row>
        </div>
      </Container>
    </div>
  );
}
