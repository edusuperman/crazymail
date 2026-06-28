import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "大宋宣和驿站 - CrazyMail Dashboard",
  description: "临时邮箱矩阵 · 智能运营中枢",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="day-night-bg night">
        {children}
      </body>
    </html>
  );
}
