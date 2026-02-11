import { Alert, Badge, Card, Form, Button } from "react-bootstrap";

export default function QuizCard({ quiz, value, onChange, isCorrect, onCheckAnswer }) {
  const isChecked = isCorrect === "correct" || isCorrect === "incorrect";
  const handleCheckAnswer = () => onCheckAnswer(quiz.id);

  return (
    <Card
      className={`mb-3 ${
        isCorrect === "correct"
          ? "border-success"
          : isCorrect === "incorrect"
            ? "border-danger"
            : ""
      }`}
    >
      <Card.Body>
        <div className="d-flex align-items-start justify-content-between gap-3">
          <Card.Text className="fs-5 fw-bold text-dark mb-2">
            {quiz.question}
          </Card.Text>
          {isChecked && isCorrect === "correct" && (
            <Badge bg="success" className="mt-1">
              Correct
            </Badge>
          )}
          {isChecked && isCorrect === "incorrect" && (
            <Badge bg="danger" className="mt-1">
              Incorrect
            </Badge>
          )}
        </div>

        <Card.Text className="text-muted mb-3">{quiz.explanation}</Card.Text>

        <Form.Control
          type="text"
          placeholder="정답 입력"
          value={value}
          onChange={(e) => onChange(quiz.id, e.target.value)}
          className={`p-2 ${
            isChecked && isCorrect === "correct"
              ? "bg-light text-success"
              : isChecked && isCorrect === "incorrect"
                ? "bg-light text-danger"
                : ""
          }`}
          disabled={isChecked}
        />

        {!isChecked && (
          <div className="d-flex justify-content-end mt-2">
            <Button variant="primary" size="sm" onClick={handleCheckAnswer}>
              정답 확인
            </Button>
          </div>
        )}

        {isChecked && isCorrect === "correct" && (
          <Alert variant="success" className="mt-3 mb-0 py-2">
            ✅ 정답입니다!
          </Alert>
        )}
        {isChecked && isCorrect === "incorrect" && (
          <Alert variant="danger" className="mt-3 mb-0 py-2">
            ❌ 오답입니다. 정답: <code>{quiz.answer}</code>
          </Alert>
        )}
      </Card.Body>
    </Card>
  );
}
