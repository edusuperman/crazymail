import type { Metadata } from "next";
import TempMailClient from "@/components/TempMailClient";

export const metadata: Metadata = {
  title: "TempMail Pro — Free Disposable Email | Protect Your Privacy",
  description:
    "Generate instant disposable email addresses. No sign-up, no tracking. Protect your inbox from spam and stay anonymous online.",
  openGraph: {
    title: "TempMail Pro — Free Disposable Email",
    description:
      "Generate instant disposable email addresses. No sign-up, no tracking.",
    type: "website",
  },
};

export default function Home() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    name: "TempMail Pro",
    description: "Free temporary email service for privacy protection",
    applicationCategory: "UtilitiesApplication",
    operatingSystem: "Web",
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "USD",
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <TempMailClient />
    </>
  );
}
