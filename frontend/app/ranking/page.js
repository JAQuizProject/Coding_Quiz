"use client";
import { useState, useEffect } from "react";
import { getRanking } from "../../api/ranking";
import { getCategories } from "../../api/quiz";
import { Badge, Card, Container, Table, Spinner, Form } from "react-bootstrap";

export default function RankingPage() {
  const [ranking, setRanking] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [category, setCategory] = useState("전체");
  const [categories, setCategories] = useState(["전체"]);

  useEffect(() => {
    fetchRanking(category);
  }, [category]);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchRanking = async (selectedCategory) => {
    setIsLoading(true);
    try {
      const result = await getRanking(selectedCategory);
      if (result && result.ranking) {
        setRanking(result.ranking);
      }
    } catch (error) {
      console.error("랭킹 데이터를 불러오는 중 오류 발생:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const medalForRank = (rankNo) => {
    if (rankNo === 1) return "🥇";
    if (rankNo === 2) return "🥈";
    if (rankNo === 3) return "🥉";
    return "•";
  };

  const fetchCategories = async () => {
    try {
      const result = await getCategories();
      if (result && result.data) {
        setCategories(["전체", ...result.data.filter((cat) => cat !== "전체")]);
      }
    } catch (error) {
      console.error("카테고리 데이터를 불러오는 중 오류 발생:", error);
    }
  };

  return (
    <Container className="cq-container py-4">
      <Card className="p-3 p-md-4">
        <div className="d-flex flex-wrap align-items-end justify-content-between gap-3 mb-3">
          <div>
            <h1 className="mb-1 fw-bold">랭킹</h1>
            <p className="mb-0 cq-muted">
              카테고리별 최고 점수를 확인하고 기록에 도전해 보세요.
            </p>
          </div>

          <Form.Group style={{ minWidth: 220 }}>
            <Form.Label className="fw-bold mb-1">카테고리</Form.Label>
            <Form.Select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </Form.Select>
          </Form.Group>
        </div>

        {isLoading ? (
          <div className="text-center py-4">
            <Spinner animation="border" variant="primary" />
            <p className="mt-2 mb-0 cq-muted">랭킹 불러오는 중...</p>
          </div>
        ) : ranking.length === 0 ? (
          <p className="text-center text-muted mb-0">랭킹 데이터가 없습니다.</p>
        ) : (
          <Table responsive hover className="align-middle mb-0">
            <thead>
              <tr className="text-center">
                <th style={{ width: 110 }}>순위</th>
                <th>유저</th>
                <th style={{ width: 140 }}>점수</th>
                <th style={{ width: 160 }}>카테고리</th>
                <th style={{ width: 160 }}>날짜</th>
              </tr>
            </thead>
            <tbody>
              {ranking.map((rank, index) => {
                const rankNo = Number(rank.rank ?? index + 1);
                return (
                  <tr
                    key={`${rank.username}-${rankNo}-${index}`}
                    className={`text-center ${rankNo <= 3 ? "table-active" : ""}`}
                  >
                    <td className="fw-bold">
                      {medalForRank(rankNo)} {rankNo}
                    </td>
                    <td className="text-start fw-bold">{rank.username}</td>
                    <td>
                      <Badge bg="primary" className="px-3 py-2">
                        {rank.score}
                      </Badge>
                    </td>
                    <td>
                      <Badge bg="light" text="dark" className="px-3 py-2 border">
                        {rank.category}
                      </Badge>
                    </td>
                    <td className="cq-muted">{rank.date}</td>
                  </tr>
                );
              })}
            </tbody>
          </Table>
        )}
      </Card>
    </Container>
  );
}
