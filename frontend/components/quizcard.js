import { useState } from "react";
import { Card, Form, Button } from "react-bootstrap";

export default function QuizCard({ quiz, value, onChange, isCorrect, onCheckAnswer }) {
  const [isChecked, setIsChecked] = useState(false);

  const handleCheckAnswer = () => {
    setIsChecked(true);
    onCheckAnswer(quiz.id);
  };

  return (
    <Card className={`mb-3 shadow-sm rounded-3 ${isCorrect === "correct" ? "border-success" : isCorrect === "incorrect" ? "border-danger" : ""}`}>
      <Card.Body>
        {/* 문제 제목 (질문) */}
        <Card.Text className="fs-5 fw-bold text-dark">{quiz.question}</Card.Text>

        {/* 문제 설명 */}
        <Card.Text className="text-muted">{quiz.explanation}</Card.Text>

        {/* 정답 입력 */}
        <Form.Control
          type="text"
          placeholder="정답 입력"
          value={value}
          onChange={(e) => onChange(quiz.id, e.target.value)}
          className={`mt-2 p-2 ${isChecked && isCorrect === "correct" ? "bg-light text-success" : isChecked && isCorrect === "incorrect" ? "bg-light text-danger" : ""}`}
          disabled={isChecked} // 정답 확인 후 입력 비활성화
        />

        {/* 정답 확인 버튼 */}
        {!isChecked && (
          <Button variant="primary" size="sm" className="mt-2" onClick={handleCheckAnswer}>
            정답 확인
          </Button>
        )}

        {/* 정답 여부 메시지 */}
        {isChecked && isCorrect === "correct" && <p className="text-success mt-2">✅ 정답입니다!</p>}
        {isChecked && isCorrect === "incorrect" && <p className="text-danger mt-2">❌ 오답입니다! 정답: {quiz.answer}</p>}
      </Card.Body>
    </Card>
  );
}
