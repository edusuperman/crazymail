import type { Metadata } from "next";
import TempMailClient from "@/components/TempMailClient";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://tempmailpro.com";

export const metadata: Metadata = {
  title: "TempMail Pro — Free Disposable Email | Protect Your Privacy",
  description:
    "Generate instant disposable email addresses. No sign-up, no tracking. Protect your inbox from spam and stay anonymous online.",
  alternates: {
    canonical: siteUrl,
  },
  openGraph: {
    title: "TempMail Pro — Free Disposable Email",
    description:
      "Generate instant disposable email addresses. No sign-up, no tracking.",
    type: "website",
    url: siteUrl,
  },
};

export default function Home() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    name: "TempMail Pro",
    url: siteUrl,
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
