import { Card, Form } from "react-bootstrap";

export default function QuizCard({ quiz, value, onChange, isCorrect }) {
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
          className={`mt-2 p-2 ${isCorrect === "correct" ? "bg-light text-success" : isCorrect === "incorrect" ? "bg-light text-danger" : ""}`}
        />

        {/* 정답 여부 메시지 */}
        {isCorrect === "correct" && <p className="text-success mt-2">✅ 정답입니다!</p>}
        {isCorrect === "incorrect" && <p className="text-danger mt-2">❌ 오답입니다! 정답: {quiz.answer}</p>}
      </Card.Body>
    </Card>
  );
}
