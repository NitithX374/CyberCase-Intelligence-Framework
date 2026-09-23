import type { Metadata } from "next";
import { Manrope, JetBrains_Mono, Noto_Sans_Thai } from "next/font/google";
import "./globals.css";
import "boxicons/css/boxicons.min.css";
import Providers from "./providers";

const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin"],
  display: "swap",
});

// Case material is mostly Thai. Without a Thai face it renders in whatever the
// operating system has, which never matches Manrope's size or weight.
const notoSansThai = Noto_Sans_Thai({
  variable: "--font-thai",
  subsets: ["thai"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "CyberCase",
  icons: {
    icon: "/cybercase-mark.png",
    apple: "/cybercase-mark.png",
  },
  description: "A source-bound workspace for case summarization, analysis, and guided follow-up.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${manrope.variable} ${notoSansThai.variable} ${jetbrainsMono.variable}`}
    >
      <body className="font-sans antialiased" suppressHydrationWarning>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
