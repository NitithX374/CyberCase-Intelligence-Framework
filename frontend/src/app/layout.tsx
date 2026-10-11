import type { Metadata } from "next";
import { Manrope, JetBrains_Mono } from "next/font/google";
import localFont from "next/font/local";
import "./globals.css";
import "boxicons/css/boxicons.min.css";
import Providers from "./providers";

const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin"],
  display: "swap",
});

const plexSansThai = localFont({
  variable: "--font-thai",
  display: "swap",
  adjustFontFallback: false,
  declarations: [{ prop: "size-adjust", value: "115%" }],
  src: [
    { path: "./fonts/ibm-plex-sans-thai-thai-400-normal.woff2", weight: "400", style: "normal" },
    { path: "./fonts/ibm-plex-sans-thai-thai-500-normal.woff2", weight: "500", style: "normal" },
    { path: "./fonts/ibm-plex-sans-thai-thai-600-normal.woff2", weight: "600", style: "normal" },
    { path: "./fonts/ibm-plex-sans-thai-thai-700-normal.woff2", weight: "700", style: "normal" },
  ],
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
      className={`${manrope.variable} ${plexSansThai.variable} ${jetbrainsMono.variable}`}
    >
      <body className="font-sans antialiased" suppressHydrationWarning>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
