import { createFileRoute } from "@tanstack/react-router";
import { Shield, Mail } from "lucide-react";

import { MailWorkspace, trustItems } from "@/components/mail-workspace";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const SITE_TITLE = "TempMail Pro — Free Disposable Email, Instant Inbox";
const SITE_DESC =
  "Generate a free temporary email address in one click. Receive verification codes and one-time mail in real time. No signup, no tracking — disposable by design.";
const SITE_URL = "https://tempmail.pro";

const faqs = [
  {
    q: "What is a temporary email (disposable email)?",
    a: "A temporary email is a short-lived inbox you can use to sign up for websites, receive verification codes, or test forms without exposing your real address. TempMail Pro generates a fresh address instantly and lets it expire whenever you're done.",
  },
  {
    q: "Is TempMail Pro safe to use?",
    a: "Yes. We do not require signup, do not store passwords, and never link the inbox to your identity. Messages are kept only as long as needed for you to read them. Avoid using disposable inboxes for accounts you care about long-term — they are designed to be ephemeral.",
  },
  {
    q: "How long are messages kept?",
    a: "Messages live in the temporary inbox for a short retention window (typically hours, depending on volume) and are then permanently deleted. You can also delete any individual message manually at any time.",
  },
  {
    q: "How does a temporary email protect my privacy?",
    a: "By using a disposable address instead of your real email, you stop services from cross-referencing your identity, you keep marketing spam out of your real inbox, and you minimize damage if a third-party database is leaked.",
  },
  {
    q: "Can I pick my own username and domain?",
    a: "Yes. Type a custom username prefix and pick any available domain from the dropdown, then hit Generate. Leave the username blank to get a randomly generated, harder-to-guess address.",
  },
];

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebApplication",
      name: "TempMail Pro",
      url: SITE_URL,
      applicationCategory: "CommunicationApplication",
      operatingSystem: "Any",
      description: SITE_DESC,
      offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
      featureList: [
        "One-click disposable email generation",
        "Custom username and domain selection",
        "Realtime inbox with 5-second polling",
        "Message delete and read tracking",
      ],
    },
    {
      "@type": "FAQPage",
      mainEntity: faqs.map((f) => ({
        "@type": "Question",
        name: f.q,
        acceptedAnswer: { "@type": "Answer", text: f.a },
      })),
    },
  ],
};

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: SITE_TITLE },
      { name: "description", content: SITE_DESC },
      {
        name: "keywords",
        content:
          "temp mail, temporary email, disposable email, anonymous email, 临时邮箱, 一次性邮箱, 匿名邮箱, throwaway email, fake email, 10 minute mail",
      },
      { name: "author", content: "TempMail Pro" },
      { property: "og:type", content: "website" },
      { property: "og:title", content: SITE_TITLE },
      { property: "og:description", content: SITE_DESC },
      { property: "og:url", content: SITE_URL },
      { property: "og:site_name", content: "TempMail Pro" },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "twitter:title", content: SITE_TITLE },
      { name: "twitter:description", content: SITE_DESC },
    ],
    links: [{ rel: "canonical", href: SITE_URL }],
    scripts: [
      {
        type: "application/ld+json",
        children: JSON.stringify(jsonLd),
      },
    ],
  }),
  component: HomePage,
});

function HomePage() {
  return (
    <div className="min-h-screen ambient-bg">
      <header className="border-b border-border/60 backdrop-blur-md bg-background/60 sticky top-0 z-30">
        <div className="mx-auto max-w-6xl px-4 md:px-6 h-16 flex items-center justify-between">
          <a href="/" className="flex items-center gap-2 group" aria-label="TempMail Pro home">
            <span className="relative inline-flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-[var(--shadow-glow)]">
              <Mail className="size-5" />
            </span>
            <span className="font-semibold tracking-tight text-lg">
              TempMail<span className="text-primary">.Pro</span>
            </span>
          </a>
          <nav className="hidden md:flex items-center gap-7 text-sm text-muted-foreground">
            <a href="#mailbox" className="hover:text-foreground">Mailbox</a>
            <a href="#why" className="hover:text-foreground">Why disposable</a>
            <a href="#faq" className="hover:text-foreground">FAQ</a>
            <a href="#privacy" className="hover:text-foreground">Privacy</a>
          </nav>
          <a
            href="#mailbox"
            className="text-sm font-medium text-primary hover:underline underline-offset-4"
          >
            Open inbox →
          </a>
        </div>
      </header>

      <main>
        {/* Hero + workspace */}
        <section className="mx-auto max-w-6xl px-4 md:px-6 pt-12 md:pt-20 pb-10">
          <div className="grid lg:grid-cols-[1.1fr_1.4fr] gap-10 lg:gap-14 items-start">
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card/60 px-3 py-1 text-xs text-muted-foreground">
                <Shield className="size-3.5 text-primary" />
                Anonymous · No signup · Free forever
              </div>
              <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-[1.05]">
                A disposable inbox
                <br />
                you can <span className="text-primary">trust</span>.
              </h1>
              <p className="text-lg text-muted-foreground max-w-xl">
                TempMail Pro hands you a real, working email address in one click.
                Receive sign-up codes, test transactional flows, and keep your
                real inbox spam-free — no account required.
              </p>
              <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-muted-foreground">
                <span className="flex items-center gap-1.5"><span className="size-1.5 rounded-full bg-primary" /> Live in &lt;1s</span>
                <span className="flex items-center gap-1.5"><span className="size-1.5 rounded-full bg-primary" /> Custom usernames</span>
                <span className="flex items-center gap-1.5"><span className="size-1.5 rounded-full bg-primary" /> 5-second realtime</span>
              </div>
            </div>

            <div id="mailbox" className="lg:sticky lg:top-24">
              <MailWorkspace />
            </div>
          </div>
        </section>

        {/* Trust strip */}
        <section id="why" className="mx-auto max-w-6xl px-4 md:px-6 py-16">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {trustItems.map(({ icon: Icon, title, body }) => (
              <article
                key={title}
                className="rounded-xl border border-border bg-card/60 p-5 hover:border-primary/40 hover:bg-card transition-colors"
              >
                <div className="size-9 rounded-lg bg-accent text-accent-foreground flex items-center justify-center">
                  <Icon className="size-5" />
                </div>
                <h3 className="mt-3 font-semibold">{title}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{body}</p>
              </article>
            ))}
          </div>
        </section>

        {/* How */}
        <section className="mx-auto max-w-6xl px-4 md:px-6 py-12">
          <div className="grid lg:grid-cols-3 gap-6">
            {[
              {
                step: "01",
                title: "Generate",
                body: "Open the page and a fresh address is already waiting. Customize the prefix or domain if you like.",
              },
              {
                step: "02",
                title: "Use it anywhere",
                body: "Paste the address into any signup form, marketplace, newsletter, or sandbox test.",
              },
              {
                step: "03",
                title: "Read & burn",
                body: "Mail arrives within seconds. Read what you need, delete the rest, and walk away.",
              },
            ].map((s) => (
              <div key={s.step} className="rounded-2xl bg-surface/70 border border-border p-6">
                <div className="font-mono text-xs text-primary tracking-widest">{s.step}</div>
                <h3 className="mt-2 text-xl font-semibold">{s.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{s.body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* SEO content block */}
        <section className="mx-auto max-w-3xl px-4 md:px-6 py-16">
          <h2 className="text-3xl font-bold tracking-tight">
            Why use a temporary email address?
          </h2>
          <div className="mt-5 space-y-4 text-muted-foreground leading-relaxed">
            <p>
              Every time you hand your real email to a website, you risk
              marketing spam, profile cross-referencing, and exposure in the
              next data breach. A <strong className="text-foreground">temporary
              email</strong> — also called a <strong className="text-foreground">
              disposable email</strong>, <strong className="text-foreground">
              throwaway address</strong>, or <strong className="text-foreground">
              anonymous email</strong> — gives you a real working inbox that
              you can use once and forget.
            </p>
            <p>
              TempMail Pro is built for the moments when you just need to
              receive a verification code, claim a download, kick the tires on
              a new SaaS, or test your own product's signup flow. No account,
              no password, no link back to your identity.
            </p>
            <p>
              Need a long-lived inbox, family communication, or sensitive
              financial mail? Use your real provider for that. Disposable
              addresses are the right tool only for short-term, low-trust mail.
            </p>
          </div>
        </section>

        {/* FAQ */}
        <section id="faq" className="mx-auto max-w-3xl px-4 md:px-6 py-12">
          <h2 className="text-3xl font-bold tracking-tight">Frequently asked</h2>
          <p className="mt-2 text-muted-foreground">
            Short answers about disposable email, privacy, and how TempMail Pro works.
          </p>
          <Accordion type="single" collapsible className="mt-6">
            {faqs.map((f, i) => (
              <AccordionItem key={i} value={`faq-${i}`} className="border-border">
                <AccordionTrigger className="text-left text-base font-semibold">
                  {f.q}
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground leading-relaxed">
                  {f.a}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </section>
      </main>

      <footer id="privacy" className="border-t border-border/60 mt-10">
        <div className="mx-auto max-w-6xl px-4 md:px-6 py-10 grid md:grid-cols-3 gap-6 text-sm">
          <div>
            <div className="flex items-center gap-2 font-semibold">
              <Mail className="size-4 text-primary" /> TempMail.Pro
            </div>
            <p className="mt-2 text-muted-foreground max-w-sm">
              A free, anonymous, disposable mail service. Built for privacy,
              testing, and signups you don't want to commit to.
            </p>
          </div>
          <div>
            <div className="font-medium">Product</div>
            <ul className="mt-2 space-y-1 text-muted-foreground">
              <li><a href="#mailbox" className="hover:text-foreground">Open mailbox</a></li>
              <li><a href="#why" className="hover:text-foreground">Why disposable</a></li>
              <li><a href="#faq" className="hover:text-foreground">FAQ</a></li>
            </ul>
          </div>
          <div>
            <div className="font-medium">Privacy commitment</div>
            <p className="mt-2 text-muted-foreground">
              No signup, no tracking cookies, no ad networks. Mail is purged
              automatically and you can delete anything manually at any time.
            </p>
          </div>
        </div>
        <div className="border-t border-border/60">
          <div className="mx-auto max-w-6xl px-4 md:px-6 py-4 text-xs text-muted-foreground flex flex-wrap items-center justify-between gap-2">
            <span>© {new Date().getFullYear()} TempMail Pro. All addresses are disposable.</span>
            <span>Built with privacy first.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
