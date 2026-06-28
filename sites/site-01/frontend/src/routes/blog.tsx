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
    title: "How to Choose a Temporary Email Service in 2026",
    excerpt: "A practical guide to choosing a temporary email service. We break down what matters — speed, privacy, ads, and real-time updates.",
    date: "2026-06-20",
    readTime: "8 min read",
    category: "Guide",
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
  {
    slug: "is-temporary-email-safe-guide",
    title: "Is Temporary Email Safe? A Comprehensive Guide for Users",
    excerpt: "Learn if temporary email is safe to use. This guide covers security, privacy benefits, and best practices for using temp...",
    date: "2026-06-23",
    readTime: "9 min read",
    category: "Privacy",
  },
  {
    slug: "temporary-email-for-developers-guide",
    title: "How to Use Temporary Email for Developers: A Comprehensive Guide",
    excerpt: "Discover how temporary email for developers can enhance your workflow, protect privacy, and streamline testing. Get star...",
    date: "2026-06-24",
    readTime: "9 min read",
    category: "Guide",
  },
  {
    slug: "disposable-email-for-spam-protection-guide",
    title: "Disposable Email for Spam Protection: A Complete Guide",
    excerpt: "Protect your primary email from spam with disposable emails. Learn how tempmails.top offers a secure temporary email ser...",
    date: "2026-06-24",
    readTime: "9 min read",
    category: "Guide",
  },
  {
    slug: "email-privacy-for-small-businesses-guide",
    title: "Email Privacy for Small Businesses: Essential Strategies",
    excerpt: "Discover why email privacy is crucial for small businesses and how temporary emails from tempmails.top can provide robus...",
    date: "2026-06-24",
    readTime: "9 min read",
    category: "Privacy",
  },
  {
    slug: "temporary-email-for-verification-guide",
    title: "Temporary Email for Verification: Protect Your Privacy Online",
    excerpt: "Discover how to use temporary email for verification to protect your privacy. Avoid spam and secure your accounts with t...",
    date: "2026-06-24",
    readTime: "9 min read",
    category: "Guide",
  },
  {
    slug: "temporary-email-for-students-guide",
    title: "Temporary Email for Students: Protect Your Privacy Now",
    excerpt: "Learn how temporary email protects students from spam and data breaches. Use tempmails.top for secure academic communica...",
    date: "2026-06-24",
    readTime: "9 min read",
    category: "Guide",
  },
  {
    slug: "disposable-email-for-freelancers",
    title: "Disposable Email for Freelancers: Ultimate Privacy Guide",
    excerpt: "Discover how disposable email helps freelancers maintain privacy and avoid spam. Learn best practices and explore tools ...",
    date: "2026-06-24",
    readTime: "9 min read",
    category: "Guide",
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
