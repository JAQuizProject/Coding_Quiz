"use client";
import { useState, useEffect } from "react";
import { getRanking } from "../../api/ranking";
import { getCategories } from "../../api/quiz";
import { Container, Table, Spinner, Form } from "react-bootstrap";

export default function RankingPage() {
  const [ranking, setRanking] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [category, setCategory] = useState("전체"); // 기본값: 전체
  const [categories, setCategories] = useState(["전체"]); // 기본값: 전체

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

  const fetchCategories = async () => {
    try {
      const result = await getCategories();
      if (result && result.data) {
        setCategories(["전체", ...result.data]); // "전체" 추가
      }
    } catch (error) {
      console.error("카테고리 데이터를 불러오는 중 오류 발생:", error);
    }
  };

  return (
    <Container className="py-5">
      <h2 className="text-center text-primary mb-4">🏆 랭킹 페이지</h2>

      <Form.Select
        className="mb-4"
        value={category}
        onChange={(e) => setCategory(e.target.value)}
      >
        {categories.map((cat) => (
          <option key={cat} value={cat}>
            {cat}
          </option>
        ))}
      </Form.Select>

      {isLoading ? (
        <div className="text-center">
          <Spinner animation="border" variant="primary" />
          <p>랭킹 불러오는 중...</p>
        </div>
      ) : ranking.length === 0 ? (
        <p className="text-center text-muted">랭킹 데이터가 없습니다.</p>
      ) : (
        <Table striped bordered hover responsive>
          <thead>
            <tr className="text-center">
              <th>순위</th>
              <th>유저</th>
              <th>점수</th>
              <th>카테고리</th>
              <th>날짜</th>
            </tr>
          </thead>
          <tbody>
            {ranking.map((rank, index) => (
              <tr key={index} className="text-center">
                <td>🥇 {rank.rank}</td>
                <td>{rank.username}</td>
                <td>{rank.score}</td>
                <td>{rank.category}</td>
                <td>{rank.date}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </Container>
  );
}
