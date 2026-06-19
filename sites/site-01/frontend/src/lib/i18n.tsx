import { createContext, useContext, useState, type ReactNode } from "react";

export interface LangDef {
  code: string;
  label: string;
  flag: string;
}

export const LANGS: LangDef[] = [
  { code: "en", label: "English", flag: "🇺🇸" },
  { code: "zh", label: "中文", flag: "🇨🇳" },
  { code: "ja", label: "日本語", flag: "🇯🇵" },
  { code: "ko", label: "한국어", flag: "🇰🇷" },
  { code: "es", label: "Español", flag: "🇪🇸" },
  { code: "fr", label: "Français", flag: "🇫🇷" },
  { code: "de", label: "Deutsch", flag: "🇩🇪" },
];

export type Lang = (typeof LANGS)[number]["code"];

type TranslationValue = string | string[] | [string, string][] | { t: string; l: string[] }[];
type Translations = Record<string, Record<string, TranslationValue>>;

const translations: Translations = {
  en: {
    // Nav
    "nav.about": "About",
    "nav.apps": "Apps",
    "nav.faq": "FAQ",
    "nav.premium": "Premium",
    "nav.upgrade": "Upgrade",
    // Hero
    "hero.title1": "Disposable inbox,",
    "hero.title2": "zero trace.",
    "hero.subtitle": "Get a free temporary email address in seconds. No sign-up, no tracking, no spam.",
    "hero.yourMailbox": "YOUR MAILBOX",
    "hero.provider": "PROVIDER",
    "hero.badgeLive": "LIVE",
    "hero.badgeSecure": "HTTPS Secure",
    "hero.badgeBurn": "Auto-delete 10min",
    "hero.clickToCopy": "Click to copy",
    "hero.generating": "Generating...",
    // Actions
    "actions.copyAddress": "Copy address",
    "actions.copy": "Copy",
    "actions.random": "Random",
    "actions.change": "Change",
    "actions.delete": "Delete",
    "actions.more": "More",
    "actions.refreshNow": "Refresh now",
    "actions.upgradePremium": "Upgrade to Premium",
    // Inbox
    "inbox.messages": "Inbox",
    "inbox.saved": "Saved",
    "inbox.emptyInbox": "No messages yet",
    "inbox.emptySaved": "No saved messages",
    "inbox.newMail": "New mail received",
    "inbox.newMailbox": "New mailbox created",
    "inbox.deleted": "Message deleted",
    "inbox.deleteMail": "Delete",
    "inbox.copied": "Copied to clipboard",
    "inbox.refresh": "Refresh",
    "inbox.bookmark": "Save",
    "inbox.unbookmark": "Unsave",
    "inbox.savedToast": "Message saved",
    "inbox.unsavedToast": "Removed from saved",
    "inbox.switched": "Switched to mailbox",
    // Change dialog
    "change.title": "Change Email Address",
    "change.desc": "Customize your temporary email address.",
    "change.username": "Username",
    "change.placeholder": "Enter username",
    "change.domain": "Domain",
    "change.selectDomain": "Select domain",
    "change.randomize": "Randomize",
    "change.confirm": "Confirm",
    "change.cancel": "Cancel",
    "change.warning1": "Changing your email will generate a new address.",
    "change.warning2": "Messages sent to the old address will be lost.",
    // Features
    "features.instant": "Instant Setup",
    "features.instantD": "Get a working email in 2 seconds.",
    "features.private": "Privacy First",
    "features.privateD": "No signup, no tracking, no logs.",
    "features.fast": "Lightning Fast",
    "features.fastD": "Emails arrive in real-time.",
    "features.burn": "Auto-Burn",
    "features.burnD": "Everything deleted after 10 min.",
    "features.multi": "Multi-Domain",
    "features.multiD": "8 domains to bypass blocks.",
    // What is
    "whatis.kicker": "WHAT IS THIS?",
    "whatis.title1": "What is a",
    "whatis.title2": "temporary email?",
    "whatis.p1": "A disposable email protects your real inbox from spam, data breaches, and unwanted tracking.",
    "whatis.p2": "Use it for sign-ups, downloads, trials — anything you don't trust with your real address.",
    // Apps
    "apps.kicker": "COMING SOON",
    "apps.title": "Mobile Apps",
    "apps.desc": "Take disposable email everywhere. iOS, Android, and browser extensions are on the way.",
    // FAQ
    "faq.kicker": "FAQ",
    "faq.title1": "Got questions?",
    "faq.title2": "We've got answers.",
    "faq.contact": "Can't find what you're looking for? Contact us at",
    "faq.items": [
      ["What is a temporary email?", "A temporary email (also called a disposable email or temp mail) is a short-lived email address that you can use to sign up for services, download content, or verify accounts without exposing your real email address. It helps protect your privacy and keeps your primary inbox free from spam."],
      ["How long does a temporary email last?", "Our temporary emails are valid for 10 minutes by default. After that, the email address and all associated messages are permanently deleted. You can always generate a new temporary email address whenever you need one."],
      ["Is temporary email really free?", "Yes! TempMails.top is 100% free to use. There are no hidden fees, no premium tiers, and no credit card required. You can create and use as many temporary email addresses as you need."],
      ["Can I send emails with a temporary address?", "No, temporary emails are receive-only. This design choice helps prevent abuse and keeps the service free for everyone. If you need to send emails, we recommend using a traditional email service."],
      ["Is my privacy protected?", "Absolutely. We don't require any personal information to use our service. We don't track your IP address, don't use cookies for tracking, and all emails are automatically deleted after expiration. Your privacy is our top priority."],
      ["Can I use temporary email for account verification?", "Yes! Many users use temporary emails to verify accounts on websites, apps, and services. However, some services may block known temporary email domains. If you encounter this, simply generate a new email address."],
    ],
    // Premium
    "premium.kicker": "PREMIUM",
    "premium.title1": "Unlock more power",
    "premium.title2": "with Premium",
    "premium.desc": "Get access to extended email retention, custom domains, and priority support.",
    "premium.bullets": ["24-hour email retention", "Custom domain support", "Priority support", "No ads"],
    "premium.cta1": "Get Premium",
    "premium.cta2": "Learn more",
    "premium.comingSoon": "Coming soon!",
    // Footer
    "footer.privacy": "Privacy Policy",
    "footer.terms": "Terms of Service",
    "footer.about": "About",
    "footer.tagline": "Free disposable email for privacy protection.",
    "footer.tagline2": "Built with ♥ for privacy",
    "footer.copyright": "© 2026 TempMails.top. All rights reserved.",
    "footer.cols": [
      { t: "Product", l: ["Features", "How it Works", "Pricing", "Browser Extensions"] },
      { t: "Legal", l: ["Privacy Policy", "Terms of Service", "Cookie Policy"] },
      { t: "Support", l: ["FAQ", "Contact Us", "Status Page"] },
    ],
  },
  zh: {
    // Nav
    "nav.about": "关于",
    "nav.apps": "应用",
    "nav.faq": "常见问题",
    "nav.premium": "高级版",
    "nav.upgrade": "升级",
    // Hero
    "hero.title1": "一次性收件箱，",
    "hero.title2": "零痕迹。",
    "hero.subtitle": "几秒内获取免费临时邮箱地址。无需注册，无追踪，无垃圾邮件。",
    "hero.yourMailbox": "你的邮箱",
    "hero.provider": "服务商",
    "hero.badgeLive": "实时",
    "hero.badgeSecure": "HTTPS 安全",
    "hero.badgeBurn": "10分钟后自动删除",
    "hero.clickToCopy": "点击复制",
    "hero.generating": "生成中...",
    // Actions
    "actions.copyAddress": "复制地址",
    "actions.copy": "复制",
    "actions.random": "随机",
    "actions.change": "更换",
    "actions.delete": "删除",
    "actions.more": "更多",
    "actions.refreshNow": "立即刷新",
    "actions.upgradePremium": "升级到高级版",
    // Inbox
    "inbox.messages": "收件箱",
    "inbox.saved": "已保存",
    "inbox.emptyInbox": "暂无邮件",
    "inbox.emptySaved": "暂无保存的邮件",
    "inbox.newMail": "收到新邮件",
    "inbox.newMailbox": "新邮箱已创建",
    "inbox.deleted": "邮件已删除",
    "inbox.deleteMail": "删除",
    "inbox.copied": "已复制到剪贴板",
    "inbox.refresh": "刷新",
    "inbox.bookmark": "保存",
    "inbox.unbookmark": "取消保存",
    "inbox.savedToast": "邮件已保存",
    "inbox.unsavedToast": "已取消保存",
    "inbox.switched": "已切换到邮箱",
    // Change dialog
    "change.title": "更换邮箱地址",
    "change.desc": "自定义你的临时邮箱地址。",
    "change.username": "用户名",
    "change.placeholder": "输入用户名",
    "change.domain": "域名",
    "change.selectDomain": "选择域名",
    "change.randomize": "随机生成",
    "change.confirm": "确认",
    "change.cancel": "取消",
    "change.warning1": "更换邮箱将生成新地址。",
    "change.warning2": "发送到旧地址的邮件将丢失。",
    // Features
    "features.instant": "即时创建",
    "features.instantD": "2 秒内获取可用邮箱。",
    "features.private": "隐私优先",
    "features.privateD": "无注册，无追踪，无日志。",
    "features.fast": "极速体验",
    "features.fastD": "邮件实时到达。",
    "features.burn": "自动销毁",
    "features.burnD": "10 分钟后自动删除一切。",
    "features.multi": "多域名",
    "features.multiD": "8 个域名绕过屏蔽。",
    // What is
    "whatis.kicker": "这是什么？",
    "whatis.title1": "什么是",
    "whatis.title2": "临时邮箱？",
    "whatis.p1": "一次性邮箱保护你的真实收件箱免受垃圾邮件、数据泄露和 unwanted 追踪。",
    "whatis.p2": "用于注册、下载、试用——任何你不信任的场景。",
    // Apps
    "apps.kicker": "即将推出",
    "apps.title": "手机应用",
    "apps.desc": "随时随地使用一次性邮箱。iOS、Android 和浏览器扩展即将推出。",
    // FAQ
    "faq.kicker": "常见问题",
    "faq.title1": "有问题？",
    "faq.title2": "我们有答案。",
    "faq.contact": "找不到您要找的内容？请联系我们",
    "faq.items": [
      ["什么是临时邮箱？", "临时邮箱（也称为一次性邮箱或临时邮件）是一个短期有效的电子邮件地址，您可以使用它来注册服务、下载内容或验证账户，而无需暴露您的真实电子邮件地址。它有助于保护您的隐私，并保持您的主收件箱免受垃圾邮件的困扰。"],
      ["临时邮箱能用多久？", "我们的临时邮箱默认有效期为 10 分钟。之后，该电子邮件地址和所有关联的消息将被永久删除。您可以随时生成新的临时邮箱地址。"],
      ["临时邮箱真的免费吗？", "是的！TempMails.top 完全免费使用。没有隐藏费用，没有高级套餐，无需信用卡。您可以根据需要创建和使用任意数量的临时邮箱地址。"],
      ["我可以用临时邮箱发送邮件吗？", "不可以，临时邮箱只能接收邮件。这个设计选择有助于防止滥用，并保持服务对所有人免费。如果您需要发送邮件，我们建议使用传统的电子邮件服务。"],
      ["我的隐私受到保护吗？", "绝对受到保护。我们不需要任何个人信息即可使用我们的服务。我们不跟踪您的 IP 地址，不使用跟踪 Cookie，所有邮件在到期后自动删除。您的隐私是我们的首要任务。"],
      ["我可以用临时邮箱进行账户验证吗？", "可以！许多用户使用临时邮箱来验证网站、应用程序和服务上的账户。但是，某些服务可能会阻止已知的临时邮箱域名。如果您遇到这种情况，只需生成一个新的邮箱地址即可。"],
    ],
    // Premium
    "premium.kicker": "高级版",
    "premium.title1": "解锁更多功能",
    "premium.title2": "升级高级版",
    "premium.desc": "获取延长的邮箱保留时间、自定义域名和优先支持。",
    "premium.bullets": ["24 小时邮箱保留", "自定义域名支持", "优先支持", "无广告"],
    "premium.cta1": "获取高级版",
    "premium.cta2": "了解更多",
    "premium.comingSoon": "即将推出！",
    // Footer
    "footer.privacy": "隐私政策",
    "footer.terms": "服务条款",
    "footer.about": "关于我们",
    "footer.tagline": "免费一次性邮箱，保护您的隐私。",
    "footer.tagline2": "用 ♥ 为隐私而建",
    "footer.copyright": "© 2026 TempMails.top. 保留所有权利。",
    "footer.cols": [
      { t: "产品", l: ["功能", "工作原理", "定价", "浏览器扩展"] },
      { t: "法律", l: ["隐私政策", "服务条款", "Cookie 政策"] },
      { t: "支持", l: ["常见问题", "联系我们", "状态页面"] },
    ],
  },
};

function getTranslation(lang: Lang, key: string): TranslationValue {
  return translations[lang]?.[key] ?? translations.en[key] ?? key;
}

interface I18nContextValue {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: Record<string, Record<string, TranslationValue>>;
}

const I18nContext = createContext<I18nContextValue>({
  lang: "en",
  setLang: () => {},
  t: translations.en as unknown as Record<string, Record<string, TranslationValue>>,
});

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>("en");

  const t = new Proxy({} as Record<string, Record<string, TranslationValue>>, {
    get(_, section: string) {
      return new Proxy({} as Record<string, TranslationValue>, {
        get(_, key: string) {
          return getTranslation(lang, `${section}.${key}`);
        },
      });
    },
  });

  return (
    <I18nContext.Provider value={{ lang, setLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}
