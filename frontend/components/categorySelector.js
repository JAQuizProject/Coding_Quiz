import { useState, useEffect } from "react";
import { getCategories } from "../api/quiz";
import styles from "./categorySelector.module.css";

export default function CategorySelector({ onSelectCategory, selectedCategory }) {
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    const fetchCategories = async () => {
      const result = await getCategories();
      if (result.data) {
        setCategories(["전체", ...result.data.filter((cat) => cat !== "전체")]);
      }
    };
    fetchCategories();
  }, []);

  return (
    <div className={styles.categoryContainer}>
      {categories.length > 0 ? (
        categories.map((category) => (
          <button
            key={category}
            onClick={() => onSelectCategory(category)}
            className={`${styles.categoryBtn} ${selectedCategory === category ? styles.selected : ""}`}
          >
            {category}
          </button>
        ))
      ) : (
        <p className="cq-muted mb-0">카테고리를 불러오는 중...</p>
      )}
    </div>
  );
}
