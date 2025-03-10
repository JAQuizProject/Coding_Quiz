"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getQuizData, submitQuizScore } from "../../api/quiz";
import { verifyToken } from "../../api/auth";
import { useAlert } from "../../context/AlertContext";
import QuizCard from "../../components/quizcard";
import { Container, Card, Button, Spinner } from "react-bootstrap";
import styles from "./page.module.css";

export default function QuizPage() {
  const [quizzes, setQuizzes] = useState([]);
  const [answers, setAnswers] = useState(() => JSON.parse(localStorage.getItem("quizAnswers")) || {});
  const [results, setResults] = useState(() => JSON.parse(localStorage.getItem("quizResults")) || {});
  const [correctCount, setCorrectCount] = useState(() => JSON.parse(localStorage.getItem("quizCorrectCount")) || 0);

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const quizzesPerPage = 5;
  const router = useRouter();
  const showAlert = useAlert();

  useEffect(() => {
    const init = async () => {
      await checkLoginStatus();
      await fetchQuizData();
    };
    init();
  }, []);

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

  const fetchQuizData = async () => {
    try {
      const result = await getQuizData();
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
    const userAnswer = answers[quizId]?.trim()
      .replace(/\s+/g, " ")
      .replace(/[^a-zA-Z0-9ㄱ-ㅎㅏ-ㅣ가-힣 ]/g, "")
      .toLowerCase();

    const correctAnswers = quizzes
      .find((quiz) => quiz.id === quizId)
      ?.answer.split("/")
      .map((ans) => ans.trim().replace(/\s+/g, " ").replace(/[^a-zA-Z0-9ㄱ-ㅎㅏ-ㅣ가-힣 ]/g, "").toLowerCase());

    const isCorrect = correctAnswers?.includes(userAnswer);

    setResults((prev) => {
      const updatedResults = { ...prev, [quizId]: isCorrect ? "correct" : "incorrect" };
      localStorage.setItem("quizResults", JSON.stringify(updatedResults));
      return updatedResults;
    });

    setCorrectCount((prev) => {
      const newCount = isCorrect ? prev + 1 : Math.max(prev - 1, 0);
      localStorage.setItem("quizCorrectCount", JSON.stringify(newCount));
      return newCount;
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    let totalCorrect = 0;
    let finalResults = {};
    let incorrectList = [];

    quizzes.forEach((quiz) => {
      const userAnswer = answers[quiz.id]?.trim()
        .replace(/\s+/g, " ")
        .replace(/[^a-zA-Z0-9ㄱ-ㅎㅏ-ㅣ가-힣 ]/g, "")
        .toLowerCase();

      const correctAnswers = quiz.answer.split("/")
        .map((ans) => ans.trim().replace(/\s+/g, " ").replace(/[^a-zA-Z0-9ㄱ-ㅎㅏ-ㅣ가-힣 ]/g, "").toLowerCase());

      const isCorrect = correctAnswers.includes(userAnswer);
      finalResults[quiz.id] = isCorrect ? "correct" : "incorrect";

      if (isCorrect) {
        totalCorrect++;
      } else {
        incorrectList.push({
          question: quiz.question,
          userAnswer: answers[quiz.id] || "(미입력)",
          correctAnswer: quiz.answer
        });
      }
    });

    const totalQuestions = quizzes.length;
    const scoreData = { correct: totalCorrect, total: totalQuestions, score: (totalCorrect / totalQuestions) * 100 };

    // 점수 저장 후 콘솔 확인
    localStorage.setItem("quizScore", JSON.stringify(scoreData));
    localStorage.setItem("quizResults", JSON.stringify(incorrectList));

    const result = await submitQuizScore(scoreData);

    if (!result.error) {
      router.push("/result");
    } else {
      showAlert("danger", "오류 발생", "점수 저장 실패");
    }
  };


  const nextPage = () => setCurrentPage((prev) => prev + 1);
  const prevPage = () => setCurrentPage((prev) => Math.max(prev - 1, 1));

  return (
    <Container className={`${styles.container} py-4`}>
      <Card className="shadow p-4">
        <Card.Title className="text-center fs-2 fw-bold text-primary">코딩 퀴즈</Card.Title>
        {isLoading ? (
          <div className="text-center py-3">
            <Spinner animation="border" variant="primary" />
            <p className="mt-2">로딩 중...</p>
          </div>
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

            {/* 페이지네이션 버튼 */}
            <div className="text-center mt-4">
              <Button onClick={prevPage} disabled={currentPage === 1} className="me-2">
                이전
              </Button>
              <span> {currentPage} 페이지 </span>
              <Button onClick={nextPage} disabled={indexOfLastQuiz >= quizzes.length} className="ms-2">
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
