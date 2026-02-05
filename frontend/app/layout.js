"use client";
import Navbar from "../components/navbar";
import { AlertProvider } from "../context/AlertContext";
import styles from "./layout.module.css";
import "./globals.css";

export default function RootLayout({ children }) {
  return (
      <AlertProvider>
        <html lang="ko">
          <head />
          <body className="bg-light">
            <Navbar />
            <main className={styles.main}>{children}</main>
          </body>
        </html>
      </AlertProvider>
  );
}
