import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NeuraFix School OS",
  description: "Production-grade AI School OS"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

