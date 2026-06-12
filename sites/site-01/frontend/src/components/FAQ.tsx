"use client";

const faqItems = [
  {
    question: "What is a temporary email?",
    answer: [
      "A temporary email, also known as a disposable email or throwaway email, is a short-lived email address that you can use without revealing your real email. It works just like a regular email — you can receive messages, read content, and even get verification codes — but it expires automatically after a set period.",
      "Temporary email services like CrazyMail generate a random email address for you instantly. There is no sign-up process, no password to remember, and no personal information required. You simply visit the website, get an address, and start receiving emails right away.",
      "This type of service is perfect for one-time registrations, downloading free resources, testing apps, or any situation where you need an email address but don't want to expose your permanent inbox to potential spam or data breaches.",
    ],
  },
  {
    question: "Is temporary email safe?",
    answer: [
      "Yes, using a temporary email is one of the safest ways to protect your online privacy. Since the address is not linked to your real identity, personal data, or existing accounts, it creates a protective barrier between you and potential data collectors, spammers, or hackers.",
      "Unlike your primary email, a disposable address cannot be used to trace back to you. If the temporary email gets compromised in a data breach, your real accounts and personal information remain completely untouched. This isolation is a key privacy advantage.",
      "However, it's important to understand that temporary emails are best suited for non-sensitive communications. Avoid using them for banking, government services, or any account where you need long-term access and strong security guarantees.",
    ],
  },
  {
    question: "How long are emails stored?",
    answer: [
      "Email storage duration depends on the service provider. At CrazyMail, emails are stored for a limited time — typically between 10 minutes and a few hours — after which they are permanently deleted from our servers. This auto-expiry is a core privacy feature.",
      "The short storage window means your data doesn't linger on our systems. Once an email expires, it is gone forever — no backups, no archives, no recovery. This approach minimizes the risk of data exposure and aligns with our privacy-first philosophy.",
      "If you need to keep any information from a received email, make sure to save or screenshot it before the expiration time. We recommend acting quickly on verification emails or time-sensitive content.",
    ],
  },
  {
    question: "Can I send emails?",
    answer: [
      "No, temporary email services are designed for receiving emails only. You cannot send emails from a disposable address. This is by design — it prevents misuse such as spam, phishing, or other abusive activities that could harm the service and its users.",
      "The receive-only model keeps the service free, fast, and reliable. It also means there is no outgoing mail server to configure, no SMTP credentials to manage, and no risk of your temporary address being used to impersonate someone else.",
      "If you need to send emails, we recommend using a full-featured email provider like Gmail, Outlook, or ProtonMail. Temporary emails complement these services by handling the incoming side — especially for sign-ups and one-time communications.",
    ],
  },
  {
    question: "Why use a temp email?",
    answer: [
      "The biggest reason to use a temp email is privacy protection. Every time you sign up for a website, download a freebie, or register for a service, your email address often ends up in marketing databases. A disposable email shields your real inbox from this inevitable spam.",
      "Temp emails are also invaluable for testing and development. Developers can use them to test email flows, verify registration processes, or check email templates without cluttering their personal or work inboxes. It's a clean, isolated testing environment.",
      "Beyond privacy and testing, disposable emails save time. There's no account creation, no password management, and no unsubscribe hassle. You get an address, use it, and walk away. For quick, one-off interactions with websites, nothing is faster or more convenient.",
    ],
  },
];

export default function FAQ() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqItems.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer.join(" "),
      },
    })),
  };

  return (
    <section className="max-w-3xl mx-auto px-4 py-12">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <h2 className="text-2xl sm:text-3xl font-bold text-center mb-8 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
        Frequently Asked Questions
      </h2>

      <div className="flex flex-col gap-3">
        {faqItems.map((item, idx) => (
          <details
            key={idx}
            className="group rounded-xl glass border border-slate-700/50 overflow-hidden transition-all duration-300 open:border-cyan-500/30 open:shadow-glass-lg"
          >
            <summary className="flex items-center justify-between gap-4 px-5 py-4 cursor-pointer select-none list-none text-slate-200 font-medium hover:text-cyan-300 transition-colors">
              <span>{item.question}</span>
              <svg
                className="w-5 h-5 shrink-0 text-slate-500 transition-transform duration-300 group-open:rotate-180 group-open:text-cyan-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </summary>
            <div className="px-5 pb-5 text-sm text-slate-400 leading-relaxed flex flex-col gap-3">
              {item.answer.map((para, pIdx) => (
                <p key={pIdx}>{para}</p>
              ))}
            </div>
          </details>
        ))}
      </div>
    </section>
  );
}
