import { Alert, Badge, Card, Form, Button } from "react-bootstrap";

const formatPercent = (value) => `${Math.round((value || 0) * 100)}%`;

export default function QuizCard({ quiz, value, onChange, isCorrect, onCheckAnswer, evaluationDetail }) {
  const isChecked = isCorrect === "correct" || isCorrect === "incorrect";
  const handleCheckAnswer = () => onCheckAnswer(quiz.id);
  const userAnswerText = evaluationDetail?.userAnswer?.trim() ? evaluationDetail.userAnswer : "(미입력)";
  const matchedAnswerText = evaluationDetail?.matchedAnswer || quiz.answer;
  const criteriaText = evaluationDetail?.criteriaLabel || "정답 기준 미충족";
  const accuracyText = evaluationDetail ? formatPercent(evaluationDetail.similarity) : "-";
  const thresholdText =
    typeof evaluationDetail?.threshold === "number" ? formatPercent(evaluationDetail.threshold) : null;

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
            <div className="fw-semibold">✅ 정답입니다!</div>
            {evaluationDetail?.usedTolerance && (
              <div className="small mt-1">허용 범위 내 오타/표기 차이를 인정해 정답 처리했습니다.</div>
            )}
            <div className="small mt-2">
              <div>
                입력 답안: <code>{userAnswerText}</code>
              </div>
              <div>
                정답: <code>{matchedAnswerText}</code>
              </div>
              <div>판정 기준: {criteriaText}</div>
              <div>
                정확도: {accuracyText}
                {thresholdText ? ` (기준 ${thresholdText})` : ""}
              </div>
            </div>
          </Alert>
        )}
        {isChecked && isCorrect === "incorrect" && (
          <Alert variant="danger" className="mt-3 mb-0 py-2">
            <div className="fw-semibold">❌ 오답입니다.</div>
            <div className="small mt-2">
              <div>
                입력 답안: <code>{userAnswerText}</code>
              </div>
              <div>
                정답: <code>{quiz.answer}</code>
              </div>
              <div>판정 기준: {criteriaText}</div>
              <div>
                정확도: {accuracyText}
                {thresholdText ? ` (기준 ${thresholdText})` : ""}
              </div>
            </div>
          </Alert>
        )}
      </Card.Body>
    </Card>
  );
}
