"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Accordion, Badge, Button, Card, Container } from "react-bootstrap";
import styles from "./page.module.css";

export default function QuizResultPage() {
  const [score, setScore] = useState(null);
  const [correctCount, setCorrectCount] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [incorrectQuestions, setIncorrectQuestions] = useState([]);
  const router = useRouter();

  useEffect(() => {
    const storedScore = localStorage.getItem("quizScore");
    if (storedScore) {
      const { correct, total, score } = JSON.parse(storedScore);
      setCorrectCount(correct);
      setTotalQuestions(total);
      setScore(score);
    } else {
      console.warn("quizScore 없음 (이미 삭제됨)");
    }

    const storedResults = localStorage.getItem("quizResults");
    if (storedResults) {
      setIncorrectQuestions(JSON.parse(storedResults));
    } else {
      console.warn("quizResults 없음 (이미 삭제됨)");
    }
  }, []);

  const handleRetry = () => {
    // 기존 데이터 삭제
    localStorage.removeItem("quizScore");
    localStorage.removeItem("quizResults");
    localStorage.removeItem("quizAnswers");
    localStorage.removeItem("quizCheckResults");

    // 퀴즈 페이지로 이동
    router.push("/quiz");
  };

  const scoreValue = score === null ? 0 : Number(score);
  const scoreText = score === null ? "-" : scoreValue.toFixed(0);

  return (
    <Container className={`cq-container ${styles.container}`}>
      <Card className={`p-3 p-md-4 ${styles.card}`}>
        <div className={styles.header}>
          <div>
            <h1 className={styles.title}>퀴즈 결과</h1>
            <p className={`mb-0 ${styles.subtitle}`}>
              틀린 문제는 아래에서 바로 복기할 수 있어요.
            </p>
          </div>
          <div className={styles.headerBadges}>
            <Badge bg="light" text="dark" className="px-3 py-2 border">
              {correctCount}/{totalQuestions} Correct
            </Badge>
          </div>
        </div>

        {score !== null ? (
          <>
            <div className={styles.summary}>
              <div className={styles.gaugeWrap}>
                <div
                  className={styles.gauge}
                  style={{ "--p": String(Math.max(0, Math.min(100, scoreValue))) }}
                  aria-label={`최종 점수 ${scoreText}점`}
                >
                  <div className={styles.gaugeInner}>
                    <div className={styles.gaugeValue}>{scoreText}</div>
                    <div className={styles.gaugeLabel}>점</div>
                  </div>
                </div>
              </div>

              <div className={styles.summaryText}>
                <div className={styles.summaryRow}>
                  <div className={styles.summaryItem}>
                    <div className={styles.summaryKey}>맞춘 개수</div>
                    <div className={styles.summaryVal}>
                      {correctCount} / {totalQuestions}
                    </div>
                  </div>
                  <div className={styles.summaryItem}>
                    <div className={styles.summaryKey}>최종 점수</div>
                    <div className={styles.summaryVal}>
                      <span className={styles.scoreStrong}>{scoreText}</span> / 100
                    </div>
                  </div>
                </div>
                <div className={styles.actions}>
                  <Button variant="primary" onClick={handleRetry}>
                    다시 풀기
                  </Button>
                  <Button as={Link} href="/ranking" variant="outline-primary">
                    랭킹 보기
                  </Button>
                </div>
              </div>
            </div>

            <div className={styles.incorrectSection}>
              <h2 className={styles.sectionTitle}>틀린 문제</h2>
              {incorrectQuestions.length > 0 ? (
                <Accordion alwaysOpen>
                  {incorrectQuestions.map((quiz, index) => (
                    <Accordion.Item key={index} eventKey={String(index)}>
                      <Accordion.Header>
                        <span className={styles.accordionQuestion}>
                          {index + 1}. {quiz.question}
                        </span>
                      </Accordion.Header>
                      <Accordion.Body>
                        <div className={styles.answerGrid}>
                          <div>
                            <div className={styles.answerLabel}>입력한 답</div>
                            <div className={styles.answerValueBad}>{quiz.userAnswer}</div>
                          </div>
                          <div>
                            <div className={styles.answerLabel}>정답</div>
                            <div className={styles.answerValueGood}>
                              <code>{quiz.correctAnswer}</code>
                            </div>
                          </div>
                        </div>
                      </Accordion.Body>
                    </Accordion.Item>
                  ))}
                </Accordion>
              ) : (
                <p className="mb-0 cq-muted">전부 정답입니다. 완벽해요.</p>
              )}
            </div>
          </>
        ) : (
          <p className="text-danger mb-0">❌ 결과를 불러올 수 없습니다.</p>
        )}
      </Card>
    </Container>
  );
}
