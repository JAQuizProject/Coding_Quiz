"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getQuizData, submitQuizScore } from "../../api/quiz";
import { verifyToken } from "../../api/auth";
import { useAlert } from "../../context/AlertContext";
import QuizCard from "../../components/quizcard";
import CategorySelector from "../../components/categorySelector";
import { Container, Card, Button, Spinner, Pagination } from "react-bootstrap";
import styles from "./page.module.css";

// localStorage 값을 안전하게 가져오는 함수
const getInitialState = (key, defaultValue) => {
  if (typeof window === "undefined") return defaultValue;
  return JSON.parse(localStorage.getItem(key)) || defaultValue;
};

const STORAGE_KEYS = {
  answers: "quizAnswers",
  checkResults: "quizCheckResults",
  score: "quizScore",
  incorrectList: "quizResults",
};

export default function QuizPage() {
  const [quizzes, setQuizzes] = useState([]);
  const [answers, setAnswers] = useState({});
  const [results, setResults] = useState({});
  const [selectedCategory, setSelectedCategory] = useState("전체");

  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const quizzesPerPage = 10;
  const pageNumberBlockSize = 10;
  const router = useRouter();
  const showAlert = useAlert();

  useEffect(() => {
    checkLoginStatus();
  }, []);

  useEffect(() => {
    fetchQuizData(selectedCategory);
  }, [selectedCategory]);

  // localStorage에서 답안/채점 결과 불러오기
  useEffect(() => {
    if (typeof window !== "undefined") {
      setAnswers(getInitialState(STORAGE_KEYS.answers, {}));
      setResults(getInitialState(STORAGE_KEYS.checkResults, {}));
    }
  }, []);

  const handleCategoryChange = (category) => {
    setCurrentPage(1);
    setSelectedCategory(category);
  };

  const checkLoginStatus = async () => {
    const result = await verifyToken();
    if (!result || result.error) {
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

  const totalQuizzes = quizzes.length;
  const totalPages = Math.ceil(totalQuizzes / quizzesPerPage);
  const indexOfLastQuiz = currentPage * quizzesPerPage;
  const indexOfFirstQuiz = indexOfLastQuiz - quizzesPerPage;
  const currentQuizzes = quizzes.slice(indexOfFirstQuiz, indexOfLastQuiz);
  const currentPageBlock = Math.floor((currentPage - 1) / pageNumberBlockSize);
  const startPage = currentPageBlock * pageNumberBlockSize + 1;
  const endPage = Math.min(startPage + pageNumberBlockSize - 1, totalPages);
  const visiblePages = Array.from(
    { length: Math.max(0, endPage - startPage + 1) },
    (_, index) => startPage + index
  );

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const handleAnswerChange = (quizId, value) => {
    setAnswers((prev) => {
      const updatedAnswers = { ...prev, [quizId]: value };
      localStorage.setItem(STORAGE_KEYS.answers, JSON.stringify(updatedAnswers));
      return updatedAnswers;
    });
  };

  const handleCheckAnswer = (quizId) => {
    const userAnswer = answers[quizId]?.trim().toLowerCase();
    const correctAnswers = quizzes.find((quiz) => quiz.id === quizId)?.answer.split("/").map((ans) => ans.trim().toLowerCase());

    const isCorrect = correctAnswers?.includes(userAnswer);

    setResults((prev) => {
      const updated = { ...prev, [quizId]: isCorrect ? "correct" : "incorrect" };
      localStorage.setItem(STORAGE_KEYS.checkResults, JSON.stringify(updated));
      return updated;
    });
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
      const scoreData = {
        correct: totalCorrect,
        total: totalQuestions,
        score: (totalCorrect / totalQuestions) * 100,
        category: selectedCategory || "전체"
      };

      localStorage.setItem(STORAGE_KEYS.score, JSON.stringify(scoreData));
      localStorage.setItem(STORAGE_KEYS.incorrectList, JSON.stringify(incorrectList));

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

  const checkedCount = quizzes.filter((q) => results[q.id]).length;
  const correctCount = quizzes.filter((q) => results[q.id] === "correct").length;

  return (
    <Container className={`cq-container ${styles.container}`}>
      <Card className={styles.panel}>
        <Card.Body className={styles.panelBody}>
          <div className={styles.panelHeader}>
            <div>
              <h1 className={styles.panelTitle}>코딩 퀴즈</h1>
              <p className={`mb-0 ${styles.panelSubtitle}`}>
                카테고리 <span className={styles.metaChip}>{selectedCategory || "전체"}</span>
                <span className={styles.metaDivider} aria-hidden />
                진행 {checkedCount}/{totalQuizzes} 채점, 정답 {correctCount}
              </p>
            </div>
            <div className={styles.panelMeta}>
              <span className={styles.metaChip}>
                Page {currentPage}/{totalPages || 1}
              </span>
              <span className={styles.metaChip}>문항 {totalQuizzes}</span>
            </div>
          </div>

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
            <div className={styles.quizList}>
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
            </div>

            {currentPage === totalPages && (
              <div className={styles.submitRow}>
                <Button type="submit" variant="success" size="sm" onClick={handleSubmit} disabled={isSubmitting}>
                  {isSubmitting ? "제출 중..." : "제출하기"}
                </Button>
              </div>
            )}

            {/* 페이지네이션 */}
            <div className={styles.paginationRow}>
              <Pagination>
                {/* 이전 버튼 */}
                <Pagination.Prev
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                />

                {/* 페이지 숫자 버튼 */}
                {visiblePages.map((pageNo) => (
                  <Pagination.Item
                    key={pageNo}
                    active={pageNo === currentPage}
                    onClick={() => handlePageChange(pageNo)}
                  >
                    {pageNo}
                  </Pagination.Item>
                ))}

                {/* 다음 버튼 */}
                <Pagination.Next
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                />
              </Pagination>
            </div>
          </>
        )}
        </Card.Body>
      </Card>
    </Container>
  );
}
