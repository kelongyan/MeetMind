import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MeetMind",
  description: "Trusted meeting intelligence workbench",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
