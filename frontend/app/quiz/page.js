"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getQuizData } from "../../api/quiz";
import { verifyToken } from "../../api/auth";
import { useAlert } from "../../context/AlertContext";
import QuizCard from "../../components/quizcard";
import { Container, Card, Button, Spinner } from "react-bootstrap";
import styles from "./page.module.css";

export default function QuizPage() {
  const [quizzes, setQuizzes] = useState([]);
  const [answers, setAnswers] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();
  const showAlert = useAlert();

  useEffect(() => {
    checkLoginStatus();
    fetchQuizData();
  }, []);

  // 로그인 상태 확인
  const checkLoginStatus = async () => {
    const result = await verifyToken();
    console.log("verifyToken 응답:", result);

    if (result && !result.error) {
      setIsLoggedIn(true);
    } else {
      setIsLoggedIn(false);
      showAlert("warning", "로그인 필요", "퀴즈를 풀려면 먼저 로그인해야 합니다.").then(() => {
        router.push("/login"); // 로그인 페이지로 이동
      });
    }
  };

  // 퀴즈 데이터 불러오기
  const fetchQuizData = async () => {
    try {
      const result = await getQuizData();
      console.log("getQuizData 응답:", result);
      if (result && result.data) {
        setQuizzes(result.data);
      } else {
        setError("퀴즈를 불러오지 못했습니다.");
      }
    } catch (err) {
      setError("서버 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  // 사용자 입력 업데이트
  const handleAnswerChange = (quizId, value) => {
    setAnswers({ ...answers, [quizId]: value });
  };

  // 정답 제출 (검증)
  const handleSubmit = (event) => {
    event.preventDefault();
    let correctCount = 0;
    quizzes.forEach((quiz) => {
      if (answers[quiz.id] && answers[quiz.id].toLowerCase() === quiz.answer.toLowerCase()) {
        correctCount++;
      }
    });
    showAlert("success", "퀴즈 결과", `🎉 ${correctCount}개의 정답을 맞췄습니다!`);
  };

  return (
    <Container className={`${styles.container} py-4`}>
      <Card className="shadow p-4">
        <Card.Title className="text-center fs-2 fw-bold text-primary">🚀 퀴즈 페이지</Card.Title>
        {isLoading ? (
          <div className="text-center py-3">
            <Spinner animation="border" variant="primary" />
            <p className="mt-2">로딩 중...</p>
          </div>
        ) : error ? (
          <p className="text-danger text-center">{error}</p>
        ) : (
          <form onSubmit={handleSubmit}>
            {quizzes.map((quiz) => (
              <QuizCard
                key={quiz.id}
                quiz={quiz}
                value={answers[quiz.id] || ""}
                onChange={handleAnswerChange}
              />
            ))}
            <div className="text-center mt-4">
              <Button type="submit" className="w-50" variant="success">
                제출하기
              </Button>
            </div>
          </form>
        )}
      </Card>
    </Container>
  );
}
