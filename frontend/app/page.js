"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/")
      .then((res) => res.json())
      .then((data) => setMessage(data.message))
      .catch((error) => console.error("Error fetching API:", error));
  }, []);

  return (
    <main>
      <h1>Coding Quiz</h1>
      <p>Backend says: {message}</p>
    </main>
  );
}
