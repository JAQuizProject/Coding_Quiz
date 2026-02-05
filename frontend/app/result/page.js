"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Container, Card, Button } from "react-bootstrap";

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

    // 퀴즈 페이지로 이동
    router.push("/quiz");
  };

  return (
    <Container className="py-5">
      <Card className="shadow p-4 text-center">
        <Card.Title className="fs-2 fw-bold text-primary">퀴즈 결과</Card.Title>

        {/* 점수 표시 */}
        {score !== null ? (
          <>
            <p className="fs-4">✅ 맞춘 개수: {correctCount} / {totalQuestions} </p>
            <p className="fs-3 text-success">🎉 최종 점수: {score}점</p>

            {/* 틀린 문제 리스트 */}
            {incorrectQuestions.length > 0 && (
              <div className="mt-4">
                <h5 className="text-danger">❌ 틀린 문제 목록</h5>
                <ul className="list-group">
                  {incorrectQuestions.map((quiz, index) => (
                    <li key={index} className="list-group-item">
                      <strong>문제:</strong> {quiz.question} <br />
                      <strong className="text-danger">입력한 답:</strong> {quiz.userAnswer} <br />
                      <strong className="text-success">정답:</strong> {quiz.correctAnswer}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 다시 풀기 버튼 */}
            <div className="mt-4">
              <Button variant="primary" onClick={handleRetry}>
                다시 풀기
              </Button>
            </div>
          </>
        ) : (
          <p className="text-danger">❌ 결과를 불러올 수 없습니다.</p>
        )}
      </Card>
    </Container>
  );
}
