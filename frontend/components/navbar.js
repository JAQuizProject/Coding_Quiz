"use client";
import Link from "next/link";
import { useState, useEffect } from "react";
import { verifyToken, logout } from "../api/auth";
import { Navbar, Nav, Container, Button } from "react-bootstrap";
import styles from "./navbar.module.css";

export default function CustomNavbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");

  useEffect(() => {
    checkLoginStatus();
  }, []);

  const checkLoginStatus = async () => {
    const result = await verifyToken();
    if (result && !result.error) {
      setIsLoggedIn(true);
      setUsername(result.user);
    } else {
      setIsLoggedIn(false);
      setUsername("");
    }
  };

  const handleLogout = async () => {
    await logout();
    setIsLoggedIn(false);
    setUsername("");
    window.location.href = "/";
  };

  return (
    <Navbar expand="lg" className={styles.navbar}>
      <Container>
        <Navbar.Brand as={Link} href="/" className={styles.brand}>
          🚀 Coding Quiz Master
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="navbar-nav" className={styles.toggle} />
        <Navbar.Collapse id="navbar-nav">
          <Nav className="ms-auto">
            <Nav.Link as={Link} href="/" className={styles.navLink}>Home</Nav.Link>
            <Nav.Link as={Link} href="/quiz" className={styles.navLink}>Quiz</Nav.Link>
            <Nav.Link as={Link} href="/ranking" className={styles.navLink}>Ranking</Nav.Link>
            {isLoggedIn ? (
              <>
                <Nav.Link disabled className={styles.username}>👤 {username}</Nav.Link>
                <Button variant="outline-danger" onClick={handleLogout} className={styles.logoutBtn}>
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Nav.Link as={Link} href="/login" className={styles.navLink}>Login</Nav.Link>
                <Nav.Link as={Link} href="/signup" className={styles.navLink}>SignUp</Nav.Link>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}
