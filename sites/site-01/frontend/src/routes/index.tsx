import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { TempMailApp } from "@/components/tempmail/TempMailApp";
import { Toaster } from "@/components/ui/sonner";

const FAQ_ITEMS = [
  ["What is a temporary email?", "A temporary email is an auto-generated, short-lived email address that lets you receive verification emails, activation links, or signup confirmations without exposing your real inbox."],
  ["Is TempMails.top free?", "Completely free. No registration required, no personal data collected, no targeted ads."],
  ["How long does a temporary email last?", "Emails are automatically deleted after a few hours. The exact retention period is shown when you create your address."],
  ["Can I receive attachments with temporary email?", "Yes. The system displays emails with attachments and lets you view or download them."],
  ["Why am I not receiving emails?", "Some senders block disposable email domains. Try switching to a different available domain and retry."],
  ["Is temporary email safe?", "All connections are encrypted via HTTPS. Email content is not logged or used for analytics."],
  ["Can I send emails from temporary email?", "TempMails.top only supports receiving emails to prevent abuse."],
  ["Can I customize the email username?", "Yes. Click the edit button to enter a custom username prefix."],
  ["Can other people see my emails?", "Anyone who knows the temporary address can view its inbox. Avoid sharing sensitive addresses."],
  ["Why so many domains?", "To bypass blocks that some websites place on common disposable email domains."],
];

const faqJsonLd = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: FAQ_ITEMS.map(([q, a]) => ({
    "@type": "Question",
    name: q,
    acceptedAnswer: { "@type": "Answer", text: a },
  })),
};

const appJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebApplication",
  name: "TempMails.top",
  applicationCategory: "CommunicationApplication",
  operatingSystem: "Web, iOS, Android",
  offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
  description: "Free, instant, no-registration temporary email service. Get a disposable email address in seconds to protect your real inbox from spam.",
};

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "TempMails.top — Free Disposable Email | Protect Your Inbox from Spam" },
      { name: "description", content: "Get a free temporary email address in seconds. No registration, no tracking. Protect your real inbox from spam, data breaches, and unwanted emails." },
      { name: "keywords", content: "temporary email, disposable email, temp mail, burner email, anonymous email, throwaway email, privacy email, spam protection" },
      { name: "author", content: "TempMails.top" },
      { name: "robots", content: "index, follow" },
      { property: "og:type", content: "website" },
      { property: "og:title", content: "TempMails.top — Free Disposable Email" },
      { property: "og:description", content: "Get a free temporary email address in seconds. No registration, no tracking. Protect your real inbox from spam." },
      { property: "og:url", content: "https://tempmails.top/" },
      { property: "og:site_name", content: "TempMails.top" },
      { property: "og:image", content: "https://tempmails.top/og-image.png" },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "twitter:title", content: "TempMails.top — Free Disposable Email" },
      { name: "twitter:description", content: "Get a free temporary email address in seconds. No registration, no tracking." },
    ],
    links: [
      { rel: "canonical", href: "https://tempmails.top/" },
      { rel: "x-default", href: "https://tempmails.top/" },
    ],
    scripts: [
      { type: "application/ld+json", children: JSON.stringify(faqJsonLd) },
      { type: "application/ld+json", children: JSON.stringify(appJsonLd) },
    ],
  }),
  component: Index,
});

function Index() {
  const navigate = useNavigate();

  // Redirect ?lang=XX to main page (these are legacy URLs from old hreflang tags)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.has("lang")) {
      // Remove ?lang= parameter and redirect to clean URL
      params.delete("lang");
      const newSearch = params.toString();
      const newUrl = newSearch ? `/?${newSearch}` : "/";
      navigate({ to: newUrl, replace: true });
    }
  }, [navigate]);

  return (
    <>
      {/* Static SEO content visible to crawlers, hidden when app loads */}
      <div className="sr-only" aria-hidden="false">
        <h1>Free Temporary Email — Protect Your Inbox from Spam</h1>
        <p>
          TempMails.top is a free, instant, no-registration temporary email service.
          Get a disposable email address in seconds to protect your real inbox from spam,
          data breaches, and unwanted emails. No sign-up required, no tracking, completely anonymous.
        </p>
        <h2>How It Works</h2>
        <ol>
          <li>Visit TempMails.top — a temporary email address is generated instantly</li>
          <li>Use the address to sign up for services, download content, or verify accounts</li>
          <li>Receive emails in real-time without revealing your real address</li>
          <li>The email address expires automatically after a few hours</li>
        </ol>
        <h2>Why Use Temporary Email?</h2>
        <ul>
          <li>Protect your real inbox from spam and marketing emails</li>
          <li>Avoid data breaches — your real email is never exposed</li>
          <li>Test services without commitment</li>
          <li>Maintain your online privacy</li>
        </ul>
        <h2>Frequently Asked Questions</h2>
        <dl>
          {FAQ_ITEMS.map(([q, a], i) => (
            <div key={i}>
              <dt>{q}</dt>
              <dd>{a}</dd>
            </div>
          ))}
        </dl>
      </div>
      {/* App component */}
      <TempMailApp />
      <Toaster position="top-right" richColors />
    </>
  );
}
