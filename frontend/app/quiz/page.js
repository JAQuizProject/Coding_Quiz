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
  const [quizzes, setQuizzes] = useState([]);  // 퀴즈 리스트
  const [answers, setAnswers] = useState({});  // 사용자가 입력한 정답
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [results, setResults] = useState({});  // 정답 여부 저장
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

  // 정답 제출 함수 개선
  const handleSubmit = (event) => {
    event.preventDefault();
    let correctCount = 0;
    let newResults = {};

    quizzes.forEach((quiz) => {
      if (answers[quiz.id]) {
        const userAnswer = answers[quiz.id]
          .trim() // 앞뒤 공백 제거
          .replace(/\s+/g, " ") // 여러 개의 공백을 하나로
          .replace(/[^a-zA-Z0-9ㄱ-ㅎㅏ-ㅣ가-힣 ]/g, "") // 특수 문자 제거
          .toLowerCase(); // 대소문자 무시

        const correctAnswers = quiz.answer
          .split("/") // 여러 정답 허용 (예: "Spring/스프링")
          .map(ans => ans.trim().replace(/\s+/g, " ").replace(/[^a-zA-Z0-9ㄱ-ㅎㅏ-ㅣ가-힣 ]/g, "").toLowerCase()); // 대소문자 무시

        const isCorrect = correctAnswers.includes(userAnswer); // 정답 여부 체크

        newResults[quiz.id] = isCorrect ? "correct" : "incorrect"; // 결과 저장

        if (isCorrect) correctCount++;
      }
    });

    setResults(newResults); // 정답 결과 저장
    showAlert("success", "퀴즈 결과", `🎉 ${correctCount}개의 정답을 맞췄습니다!`);
  };

  return (
    <Container className={`${styles.container} py-4`}>
      <Card className="shadow p-4">
        <Card.Title className="text-center fs-2 fw-bold text-primary">코딩 퀴즈</Card.Title>
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
                isCorrect={results[quiz.id]}
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
