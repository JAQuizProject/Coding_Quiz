import { Card, Form } from "react-bootstrap";
import styles from "./quizcard.module.css";

export default function QuizCard({ quiz, value, onChange }) {
  return (
    <Card className="mb-3 shadow-sm border-0 rounded-3">
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
          className="mt-2 p-2"
        />
      </Card.Body>
    </Card>
  );
}
