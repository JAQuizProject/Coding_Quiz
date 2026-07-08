"use client";

import Navbar from "../components/navbar";
import { AlertProvider } from "../context/AlertContext";

export default function Providers({ children }) {
  return (
    <AlertProvider>
      <Navbar />
      {children}
    </AlertProvider>
  );
}

