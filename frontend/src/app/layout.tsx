import type { Metadata } from "next";
import React from "react";
import { Space_Grotesk, Inter, IBM_Plex_Sans, VT323 } from "next/font/google";
import "./globals.css";
import "./glassmorphism.css";
import '@rainbow-me/rainbowkit/styles.css';
import { MainLayout } from "@/components/layout";
import { Web3Provider } from "@/lib/wagmi";

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const ibmPlex = IBM_Plex_Sans({
  variable: "--font-ibm-plex",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const vt323 = VT323({
  variable: "--font-vt323",
  subsets: ["latin"],
  weight: ["400"],
});

export const metadata: Metadata = {
  title: "Fluxo - Private Intelligence Agent",
  description: "Private intelligence agent for Web3. Autonomous portfolio tracking, risk analysis, yield optimization, and strategic execution.",
  keywords: ["DeFi", "Web3", "Crypto", "Intelligence", "Privacy", "Autonomous"],
};

import { FluxoProvider } from "@/providers/FluxoProvider";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${spaceGrotesk.variable} ${inter.variable} ${ibmPlex.variable} ${vt323.variable} antialiased`}
      >
        <Web3Provider>
          <FluxoProvider>
            <MainLayout>{children}</MainLayout>
          </FluxoProvider>
        </Web3Provider>
      </body>
    </html>
  );
}
