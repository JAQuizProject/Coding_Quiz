"use client";
import { createContext, useContext } from "react";
import Swal from "sweetalert2";
import "sweetalert2/dist/sweetalert2.min.css"; // 스타일 적용

const AlertContext = createContext();

export function AlertProvider({ children }) {
  const showAlert = (type, title, text) => {
    return Swal.fire({
      icon: type, // "success", "error", "warning", "info"
      title: title,
      text: text,
      confirmButtonColor: type === "error" ? "#d33" : "#3085d6",
    });
  };

  return <AlertContext.Provider value={showAlert}>{children}</AlertContext.Provider>;
}

// 사용하기 쉽게 `useAlert` 훅 만들기
export function useAlert() {
  return useContext(AlertContext);
}
