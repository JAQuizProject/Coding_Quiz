"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getQuizData, submitQuizScore } from "../../api/quiz";
import { verifyToken } from "../../api/auth";
import { useAlert } from "../../context/AlertContext";
import QuizCard from "../../components/quizcard";
import CategorySelector from "../../components/categorySelector";
import { Container, Card, Button, Spinner } from "react-bootstrap";
import styles from "./page.module.css";

// localStorage 값을 안전하게 가져오는 함수
const getInitialState = (key, defaultValue) => {
  if (typeof window === "undefined") return defaultValue;
  return JSON.parse(localStorage.getItem(key)) || defaultValue;
};

export default function QuizPage() {
  const [quizzes, setQuizzes] = useState([]);
  const [answers, setAnswers] = useState({});
  const [results, setResults] = useState({});
  const [selectedCategory, setSelectedCategory] = useState("");

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const quizzesPerPage = 5;
  const router = useRouter();
  const showAlert = useAlert();

  useEffect(() => {
    checkLoginStatus();
  }, []);

  useEffect(() => {
    fetchQuizData(selectedCategory);
  }, [selectedCategory]);

  // results 상태 변경 시 localStorage 업데이트
  useEffect(() => {
    if (typeof window !== "undefined") {
      setAnswers(getInitialState("quizAnswers", {}));
      setResults(getInitialState("quizResults", {}));
    }
  }, []);

  const handleCategoryChange = (category) => {
    setCurrentPage(1);
    setSelectedCategory(category);
  };

  const checkLoginStatus = async () => {
    const result = await verifyToken();
    if (result && !result.error) {
      setIsLoggedIn(true);
    } else {
      setIsLoggedIn(false);
      showAlert("warning", "로그인 필요", "퀴즈를 풀려면 먼저 로그인해야 합니다.").then(() => {
        router.push("/login");
      });
    }
  };

  const fetchQuizData = async (category) => {
    setIsLoading(true);
    try {
      const result = await getQuizData(category === "전체" ? "" : category);
      setQuizzes(result?.data || []);
    } catch (error) {
      console.error("퀴즈 데이터를 불러오는데 실패했습니다.", error);
      setQuizzes([]);
    } finally {
      setIsLoading(false);
    }
  };

  const indexOfLastQuiz = currentPage * quizzesPerPage;
  const indexOfFirstQuiz = indexOfLastQuiz - quizzesPerPage;
  const currentQuizzes = quizzes.slice(indexOfFirstQuiz, indexOfLastQuiz);
  const isLastPage = indexOfLastQuiz >= quizzes.length;

  const handleAnswerChange = (quizId, value) => {
    setAnswers((prev) => {
      const updatedAnswers = { ...prev, [quizId]: value };
      localStorage.setItem("quizAnswers", JSON.stringify(updatedAnswers));
      return updatedAnswers;
    });
  };

  const handleCheckAnswer = (quizId) => {
    const userAnswer = answers[quizId]?.trim().toLowerCase();
    const correctAnswers = quizzes.find((quiz) => quiz.id === quizId)?.answer.split("/").map((ans) => ans.trim().toLowerCase());

    const isCorrect = correctAnswers?.includes(userAnswer);

    setResults((prev) => ({
      ...prev,
      [quizId]: isCorrect ? "correct" : "incorrect",
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (isSubmitting) return;

    setIsSubmitting(true);
    try {
      let totalCorrect = 0;
      let incorrectList = [];

      quizzes.forEach((quiz) => {
        const userAnswer = answers[quiz.id]?.trim().toLowerCase();
        const correctAnswers = quiz.answer.split("/").map((ans) => ans.trim().toLowerCase());

        const isCorrect = correctAnswers.includes(userAnswer);

        if (isCorrect) {
          totalCorrect++;
        } else {
          incorrectList.push({
            question: quiz.question,
            userAnswer: answers[quiz.id] || "(미입력)",
            correctAnswer: quiz.answer,
          });
        }
      });

      const totalQuestions = quizzes.length;
      const scoreData = { correct: totalCorrect, total: totalQuestions, score: (totalCorrect / totalQuestions) * 100 };

      localStorage.setItem("quizScore", JSON.stringify(scoreData));
      localStorage.setItem("quizResults", JSON.stringify(incorrectList));

      const result = await submitQuizScore(scoreData);

      if (!result.error) {
        router.push("/result");
      } else {
        showAlert("danger", "오류 발생", "점수 저장 실패");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Container className={`${styles.container} py-4`}>
      <Card className="shadow p-4">
        <Card.Title className="text-center fs-2 fw-bold text-primary">
          코딩 퀴즈 ({selectedCategory || "전체"})
        </Card.Title>
        <CategorySelector
          onSelectCategory={handleCategoryChange}
          selectedCategory={selectedCategory}
        />
        {isLoading ? (
          <div className="text-center py-3">
            <Spinner animation="border" variant="primary" />
            <p className="mt-2">로딩 중...</p>
          </div>
        ) : quizzes.length === 0 ? (
          <p className="text-center text-muted">퀴즈가 없습니다.</p>
        ) : (
          <>
            {currentQuizzes.map((quiz) => (
              <QuizCard
                key={quiz.id}
                quiz={quiz}
                value={answers[quiz.id] || ""}
                onChange={handleAnswerChange}
                onCheckAnswer={handleCheckAnswer}
                isCorrect={results[quiz.id]}
              />
            ))}

            <div className="text-center mt-4">
              <Button onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))} disabled={currentPage === 1} className="me-2">
                이전
              </Button>
              <span> {currentPage} 페이지 </span>
              <Button onClick={() => setCurrentPage((prev) => prev + 1)} disabled={isLastPage} className="ms-2">
                다음
              </Button>
            </div>

            {isLastPage && (
              <div className="text-center mt-4">
                <Button type="submit" className="w-50" variant="success" onClick={handleSubmit} disabled={isSubmitting}>
                  {isSubmitting ? "제출 중..." : "최종 제출하기"}
                </Button>
              </div>
            )}
          </>
        )}
      </Card>
    </Container>
  );
}
