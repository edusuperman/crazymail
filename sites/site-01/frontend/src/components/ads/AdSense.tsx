import { useEffect } from "react";

declare global {
  interface Window {
    adsbygoogle: unknown[];
  }
}

const ADSENSE_CLIENT_ID = "ca-pub-XXXXXXXXXXXXXXXX"; // TODO: 替换为真实 ID

/**
 * AdSense 广告单元组件
 * 在博客文章和主页面中显示广告
 */
export function AdUnit({
  slot,
  format = "auto",
  responsive = true,
  className = "",
}: {
  slot: string;
  format?: string;
  responsive?: boolean;
  className?: string;
}) {
  useEffect(() => {
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch (e) {
      console.warn("AdSense push failed:", e);
    }
  }, []);

  return (
    <div className={`ad-container my-6 ${className}`}>
      <ins
        className="adsbygoogle"
        style={{ display: "block" }}
        data-ad-client={ADSENSE_CLIENT_ID}
        data-ad-slot={slot}
        data-ad-format={format}
        data-full-width-responsive={responsive ? "true" : "false"}
      />
    </div>
  );
}

/**
 * AdSense 脚本加载组件
 * 放在 layout 或 _app 中
 */
export function AdSenseScript() {
  return (
    <script
      async
      src={`https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADSENSE_CLIENT_ID}`}
      crossOrigin="anonymous"
    />
  );
}

/**
 * 博客文章内广告位
 * 在文章中间插入
 */
export function BlogInArticleAd() {
  return (
    <AdUnit
      slot="XXXXXXXXXX" // TODO: 替换为真实 slot ID
      format="fluid"
      className="my-8 rounded-lg border border-border/30 bg-muted/30 p-4"
    />
  );
}

/**
 * 博客文章底部广告位
 */
export function BlogBottomAd() {
  return (
    <AdUnit
      slot="XXXXXXXXXX" // TODO: 替换为真实 slot ID
      format="auto"
      className="mt-8"
    />
  );
}

/**
 * 侧边栏广告位
 */
export function SidebarAd() {
  return (
    <AdUnit
      slot="XXXXXXXXXX" // TODO: 替换为真实 slot ID
      format="auto"
      className="sticky top-4"
    />
  );
}
