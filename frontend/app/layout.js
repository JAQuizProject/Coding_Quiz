import { IBM_Plex_Mono, IBM_Plex_Sans_KR } from "next/font/google";
import Providers from "./providers";
import styles from "./layout.module.css";
import "./globals.css";

const sans = IBM_Plex_Sans_KR({
  weight: ["400", "500", "600", "700"],
  subsets: ["latin"],
  display: "swap",
  variable: "--font-sans",
});

const mono = IBM_Plex_Mono({
  weight: ["400", "500", "600"],
  subsets: ["latin"],
  display: "swap",
  variable: "--font-mono",
});

export default function RootLayout({ children }) {
  return (
    <html lang="ko" className={`${sans.variable} ${mono.variable}`}>
      <body className={styles.body}>
        <Providers>
          <main className={styles.main}>{children}</main>
        </Providers>
      </body>
    </html>
  );
}
