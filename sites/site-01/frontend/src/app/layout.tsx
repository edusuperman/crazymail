import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "TempMail Pro — Free Disposable Email",
    template: "%s | TempMail Pro",
  },
  description:
    "Generate instant disposable email addresses to protect your privacy. No sign-up required.",
  keywords: [
    "temporary email",
    "disposable email",
    "temp mail",
    "fake email",
    "email generator",
    "privacy protection",
    "spam protection",
    "anonymous email",
  ],
  openGraph: {
    title: "TempMail Pro — Free Disposable Email",
    description:
      "Generate instant disposable email addresses to protect your privacy. No sign-up required.",
    type: "website",
    siteName: "TempMail Pro",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "TempMail Pro — Free Disposable Email",
    description:
      "Generate instant disposable email addresses to protect your privacy. No sign-up required.",
  },
  robots: "index, follow",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://tempmailpro.com";

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "TempMail Pro",
    url: siteUrl,
    description:
      "Free temporary email service for privacy protection. Generate instant disposable email addresses.",
    inLanguage: "en",
    potentialAction: {
      "@type": "SearchAction",
      target: `${siteUrl}/?q={search_term_string}`,
      "query-input": "required name=search_term_string",
    },
  };

  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
