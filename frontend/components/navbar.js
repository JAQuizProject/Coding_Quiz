"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { verifyToken, logout } from "../api/auth";
import { Navbar, Nav, Container, Button } from "react-bootstrap";
import styles from "./navbar.module.css";

export default function CustomNavbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");
  const pathname = usePathname();

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

  const isActive = (href) => {
    if (!pathname) return false;
    if (href === "/") return pathname === "/";
    return pathname === href || pathname.startsWith(`${href}/`);
  };

  const navLinkClass = (href) =>
    `${styles.navLink} ${isActive(href) ? styles.active : ""}`;

  return (
    <Navbar expand="lg" variant="light" className={styles.navbar}>
      <Container>
        <Navbar.Brand as={Link} href="/" className={styles.brand}>
          <span className={styles.brandMark}>CQ</span>
          <span className={styles.brandText}>Coding Quiz Master</span>
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="navbar-nav" className={styles.toggle} />
        <Navbar.Collapse id="navbar-nav">
          <Nav className="ms-auto">
            <Nav.Link as={Link} href="/" className={navLinkClass("/")}>
              Home
            </Nav.Link>
            <Nav.Link as={Link} href="/quiz" className={navLinkClass("/quiz")}>
              Quiz
            </Nav.Link>
            <Nav.Link
              as={Link}
              href="/ranking"
              className={navLinkClass("/ranking")}
            >
              Ranking
            </Nav.Link>
            {isLoggedIn ? (
              <>
                <Nav.Link disabled className={styles.username}>👤 {username}</Nav.Link>
                <Button variant="outline-danger" onClick={handleLogout} className={styles.logoutBtn}>
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Nav.Link as={Link} href="/login" className={navLinkClass("/login")}>
                  Login
                </Nav.Link>
                <Nav.Link as={Link} href="/signup" className={navLinkClass("/signup")}>
                  SignUp
                </Nav.Link>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}
