"use client";
import { createContext, useContext } from "react";
import Swal from "sweetalert2";

const AlertContext = createContext();

export function AlertProvider({ children }) {
  const showAlert = (type, title, text) => {
    return Swal.fire({
      icon: type, // "success", "error", "warning", "info"
      title: title,
      text: text,
      confirmButtonColor: type === "error" ? "#dc2626" : "#0ea5e9",
    });
  };

  return <AlertContext.Provider value={showAlert}>{children}</AlertContext.Provider>;
}

// 사용하기 쉽게 `useAlert` 훅 만들기
export function useAlert() {
  return useContext(AlertContext);
}
