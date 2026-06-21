import { createFileRoute, Link, Outlet } from "@tanstack/react-router";

export const Route = createFileRoute("/blog")({
  head: () => ({
    meta: [
      { title: "Blog - TempMails.top | Temporary Email Tips & Guides" },
      { name: "description", content: "Learn about temporary email, privacy protection, and online security. Tips, guides, and best practices for using disposable email addresses." },
      { name: "robots", content: "index, follow" },
      { property: "og:type", content: "blog" },
      { property: "og:title", content: "Blog - TempMails.top" },
      { property: "og:description", content: "Learn about temporary email, privacy protection, and online security." },
    ],
    links: [
      { rel: "canonical", href: "https://tempmails.top/blog" },
    ],
  }),
  component: BlogPage,
});

const blogPosts = [
  {
    slug: "best-temporary-email-services-2026",
    title: "Best Temporary Email Services in 2026 (Comparison)",
    excerpt: "We tested the top temporary email services so you don't have to. Compare features, speed, privacy, and pricing to find the best disposable email for your needs.",
    date: "2026-06-20",
    readTime: "8 min read",
    category: "Comparison",
  },
  {
    slug: "protect-privacy-with-temporary-email",
    title: "How to Protect Your Privacy with Temporary Email",
    excerpt: "Learn how disposable email addresses can protect your real inbox from spam, data breaches, and unwanted tracking. Complete privacy guide.",
    date: "2026-06-20",
    readTime: "6 min read",
    category: "Privacy",
  },
  {
    slug: "temporary-email-for-verification",
    title: "Temporary Email for Account Verification: Complete Guide",
    excerpt: "Step-by-step guide on using temporary email for account verification on websites, apps, and services without exposing your real email.",
    date: "2026-06-20",
    readTime: "7 min read",
    category: "Guide",
  },
  {
    slug: "disposable-email-statistics-2026",
    title: "Disposable Email Statistics 2026: What You Need to Know",
    excerpt: "The latest statistics on temporary email usage, market growth, and user behavior. Data-driven insights for marketers and developers.",
    date: "2026-06-20",
    readTime: "5 min read",
    category: "Data",
  },
  {
    slug: "is-temporary-email-safe",
    title: "Is Temporary Email Safe? Security Guide",
    excerpt: "Addressing common security concerns about temporary email services. Learn about encryption, data retention, and best practices.",
    date: "2026-06-20",
    readTime: "6 min read",
    category: "Security",
  },
  {
    slug: "6-billion-emails-leaked-2026",
    title: "6.8 Billion Emails Leaked: Why Your Real Inbox Is Now a Liability",
    excerpt: "A massive data leak exposed 6.8 billion email records in February 2026.",
    date: "2026-06-21",
    readTime: "6 min read",
    category: "Data Breach",
  },
  {
    slug: "12-percent-signups-use-temp-email",
    title: "12% of All Signups Use Temp Email",
    excerpt: "Verified.email 2026 report reveals 12% of all online signups use disposable email.",
    date: "2026-06-21",
    readTime: "5 min read",
    category: "Data",
  },
  {
    slug: "platforms-blocking-temp-email-2026",
    title: "Platforms Fighting Back: Blocking Temp Emails in 2026",
    excerpt: "Major platforms are cracking down on disposable email addresses.",
    date: "2026-06-21",
    readTime: "7 min read",
    category: "Industry",
  },
  {
    slug: "temp-email-chatgpt-claude-codex",
    title: "Temp Email for ChatGPT, Claude & Codex",
    excerpt: "I tested temporary email on ChatGPT, Claude, and Codex.",
    date: "2026-06-21",
    readTime: "6 min read",
    category: "AI Tools",
  },
  {
    slug: "temp-email-tiktok-instagram-reddit",
    title: "Temp Email for TikTok, Instagram & Reddit",
    excerpt: "I tested temporary email on TikTok, Instagram, and Reddit.",
    date: "2026-06-21",
    readTime: "7 min read",
    category: "Social Media",
  },
];

function BlogPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-16">
      <div className="mb-12 text-center">
        <h1 className="text-4xl font-bold tracking-tight">Blog</h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Tips, guides, and insights about temporary email and online privacy
        </p>
      </div>

      <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        {blogPosts.map((post) => (
          <article
            key={post.slug}
            className="group rounded-lg border border-border bg-card p-6 transition-colors hover:border-primary/50"
          >
            <div className="mb-4 flex items-center gap-2">
              <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                {post.category}
              </span>
              <span className="text-xs text-muted-foreground">{post.readTime}</span>
            </div>
            <h2 className="mb-2 text-xl font-semibold tracking-tight group-hover:text-primary">
              <Link to={`/blog/${post.slug}`}>{post.title}</Link>
            </h2>
            <p className="mb-4 text-sm text-muted-foreground">{post.excerpt}</p>
            <div className="flex items-center justify-between">
              <time className="text-xs text-muted-foreground">{post.date}</time>
              <Link
                to={`/blog/${post.slug}`}
                className="text-sm font-medium text-primary hover:underline"
              >
                Read more →
              </Link>
            </div>
          </article>
        ))}
      </div>
      <Outlet />
    </div>
  );
}
