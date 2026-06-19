import { createFileRoute } from "@tanstack/react-router";
import { TempMailApp } from "@/components/tempmail/TempMailApp";
import { Toaster } from "@/components/ui/sonner";

const FAQ_ITEMS = [
  ["什么是临时邮箱？", "临时邮箱是一种自动生成、有限时间内可用的电子邮件地址，用于在不暴露真实邮箱的前提下接收验证邮件、激活链接或注册确认。"],
  ["TempMail Pro 是免费的吗？", "完全免费。不要求注册，不收集个人信息，不投放定向广告。"],
  ["临时邮箱可以保留多久？", "默认数小时后自动销毁。Premium 用户可永久保留。"],
  ["可以用临时邮箱接收附件吗？", "可以。系统会显示带有附件的邮件，并允许你查看或下载。"],
  ["为什么我收不到邮件？", "部分发件方屏蔽一次性邮箱域名。可切换到其他可用域名重试。"],
  ["临时邮箱安全吗？", "所有连接均通过 HTTPS 加密，邮件内容不会被记录用于分析。"],
  ["能用它发送邮件吗？", "TempMail Pro 仅支持接收，不支持发送，以防止滥用。"],
  ["可以自定义邮箱用户名吗？", "可以。点击「改变」即可输入自定义用户名前缀。"],
  ["邮件会被其他人看到吗？", "任何知道临时地址的人都能查看其收件箱，请避免分享。"],
  ["为什么需要那么多域名？", "为了绕过某些网站对常见一次性邮箱域名的封锁。"],
  ["我可以在 iOS / Android / 浏览器上使用吗？", "iOS、Android 应用和 Chrome、Firefox、Edge 扩展即将推出，敬请期待。"],
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
  name: "TempMail Pro",
  applicationCategory: "CommunicationApplication",
  operatingSystem: "Web, iOS, Android",
  offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
  description: "免费、即时、零注册的临时邮箱与一次性匿名邮箱服务。",
};

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "TempMail Pro · 免费临时邮箱 / 一次性匿名邮箱" },
      { name: "description", content: "免费、即时、零注册的临时邮箱服务。生成一次性匿名邮箱地址，5 秒级实时接收验证邮件，远离垃圾邮件骚扰。" },
      { name: "keywords", content: "临时邮箱,一次性邮箱,匿名邮箱,10分钟邮箱,burner mail,disposable email,temp mail,验证码邮箱" },
      { name: "author", content: "TempMail Pro" },
      { name: "robots", content: "index, follow" },
      { property: "og:type", content: "website" },
      { property: "og:title", content: "TempMail Pro · 免费临时邮箱 / 一次性匿名邮箱" },
      { property: "og:description", content: "零注册的临时邮箱，5 秒级实时收信，保护你的真实邮箱不被骚扰。" },
      { property: "og:url", content: "https://tempmails.top/" },
      { property: "og:site_name", content: "TempMail Pro" },
      { property: "og:image", content: "https://tempmails.top/og-image.svg" },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "twitter:title", content: "TempMail Pro · 免费临时邮箱" },
      { name: "twitter:description", content: "零注册、即时收信的一次性匿名邮箱。" },
    ],
    links: [
      { rel: "canonical", href: "https://tempmails.top/" },
      { rel: "alternate", hreflang: "en", href: "https://tempmails.top/" },
      { rel: "alternate", hreflang: "zh", href: "https://tempmails.top/?lang=zh" },
      { rel: "alternate", hreflang: "ja", href: "https://tempmails.top/?lang=ja" },
      { rel: "alternate", hreflang: "ko", href: "https://tempmails.top/?lang=ko" },
      { rel: "alternate", hreflang: "es", href: "https://tempmails.top/?lang=es" },
      { rel: "alternate", hreflang: "fr", href: "https://tempmails.top/?lang=fr" },
      { rel: "alternate", hreflang: "de", href: "https://tempmails.top/?lang=de" },
      { rel: "alternate", hreflang: "x-default", href: "https://tempmails.top/" },
    ],
    scripts: [
      { type: "application/ld+json", children: JSON.stringify(faqJsonLd) },
      { type: "application/ld+json", children: JSON.stringify(appJsonLd) },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <>
      <TempMailApp />
      <Toaster position="top-right" richColors />
    </>
  );
}
