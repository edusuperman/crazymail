"use client";

import { useState, useEffect } from "react";

interface DataPanelProps {
  activeTab: "writing" | "distribution" | "factory";
}

interface StatsData {
  timestamp: string;
  articles: { count: number; list: Array<{ title: string; date: string }> };
  heroes: { count: number; transparent_count: number };
  site: { url: string; status: string; code: string };
  api: { status: string; code: string };
}

export function DataPanel({ activeTab }: DataPanelProps) {
  const [currentTime, setCurrentTime] = useState("");
  const [stats, setStats] = useState<StatsData | null>(null);

  useEffect(() => {
    // 获取真实数据
    fetch("/api/stats")
      .then((res) => res.json())
      .then((data) => setStats(data))
      .catch((err) => console.error("Failed to fetch stats:", err));
  }, []);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString("zh-CN"));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <aside className="w-72 border-l border-card-border bg-card-bg backdrop-blur-sm overflow-y-auto">
      {/* 总数据看板 */}
      <div className="p-4 border-b border-card-border">
        <h3 className="text-sm font-bold text-imperial-gold mb-3">📊 总数据看板</h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="guofeng-card p-2 text-center">
            <p className="text-2xl font-bold text-parchment">
              {stats?.site.status === "online" ? "1" : "0"}
            </p>
            <p className="text-xs text-ash-gray">已上线站点</p>
          </div>
          <div className="guofeng-card p-2 text-center">
            <p className="text-2xl font-bold text-parchment">
              {stats?.articles.count ?? "..."}
            </p>
            <p className="text-xs text-ash-gray">已发布文章</p>
          </div>
          <div className="guofeng-card p-2 text-center">
            <p className="text-2xl font-bold text-imperial-gold">
              {stats?.heroes.count ?? "..."}
            </p>
            <p className="text-xs text-ash-gray">角色素材</p>
          </div>
          <div className="guofeng-card p-2 text-center">
            <p className="text-2xl font-bold text-parchment">
              {stats?.api.status === "online" ? "正常" : "异常"}
            </p>
            <p className="text-xs text-ash-gray">邮件API</p>
          </div>
        </div>
      </div>

      {/* 写作场景指标 */}
      {activeTab === "writing" && (
        <div className="p-4 border-b border-card-border">
          <h3 className="text-sm font-bold text-imperial-gold mb-3">📝 写作场景指标</h3>
          <div className="space-y-2 mb-4">
            {[
              { name: "研究", progress: 85, status: "done" },
              { name: "大纲", progress: 70, status: "working" },
              { name: "初稿", progress: 45, status: "working" },
              { name: "润色", progress: 30, status: "working" },
              { name: "质检", progress: 0, status: "waiting" },
              { name: "部署", progress: 0, status: "waiting" },
              { name: "监控", progress: 0, status: "waiting" },
            ].map((stage) => (
              <div key={stage.name} className="flex items-center gap-2">
                <span className="text-xs text-ash-gray w-12">{stage.name}</span>
                <div className="flex-1 ink-progress h-2">
                  <div
                    className="h-full bg-gradient-to-r from-jade-green to-imperial-gold transition-all"
                    style={{ width: `${stage.progress}%` }}
                  />
                </div>
                <span className="text-xs text-ash-gray w-10 text-right">{stage.progress}%</span>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="guofeng-card p-2 text-center">
              <p className="text-lg font-bold text-parchment">12分钟</p>
              <p className="text-xs text-ash-gray">平均耗时</p>
            </div>
            <div className="guofeng-card p-2 text-center">
              <p className="text-lg font-bold text-jade-green">92%</p>
              <p className="text-xs text-ash-gray">质检通过率</p>
            </div>
          </div>
        </div>
      )}

      {/* 推广场景指标 */}
      {activeTab === "distribution" && (
        <div className="p-4 border-b border-card-border">
          <h3 className="text-sm font-bold text-imperial-gold mb-3">⚔️ 推广场景指标</h3>
          <div className="space-y-2 mb-4">
            {[
              { name: "Reddit", count: 234, success: 95 },
              { name: "Twitter", count: 189, success: 88 },
              { name: "GitHub", count: 156, success: 92 },
              { name: "YouTube", count: 98, success: 78 },
            ].map((platform) => (
              <div key={platform.name} className="flex items-center justify-between">
                <span className="text-sm text-parchment">{platform.name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-ash-gray">{platform.count}篇</span>
                  <span className={`text-xs ${platform.success > 90 ? "text-jade-green" : "text-warning-amber"}`}>
                    {platform.success}%
                  </span>
                </div>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="guofeng-card p-2 text-center">
              <p className="text-lg font-bold text-parchment">45</p>
              <p className="text-xs text-ash-gray">活跃好汉</p>
            </div>
            <div className="guofeng-card p-2 text-center">
              <p className="text-lg font-bold text-warning-amber">3</p>
              <p className="text-xs text-ash-gray">异常预警</p>
            </div>
          </div>
        </div>
      )}

      {/* 风险雷达 */}
      <div className="p-4 border-b border-card-border">
        <h3 className="text-sm font-bold text-imperial-gold mb-3">🛡️ 风险雷达</h3>
        <div className="guofeng-card p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-parchment">站点状态</span>
            <span className={`text-sm font-bold ${stats?.site.status === "online" ? "text-jade-green" : "text-vermillion"}`}>
              {stats?.site.status === "online" ? "正常" : "异常"}
            </span>
          </div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-parchment">API 状态</span>
            <span className={`text-sm font-bold ${stats?.api.status === "online" ? "text-jade-green" : "text-vermillion"}`}>
              {stats?.api.status === "online" ? "正常" : "异常"}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-parchment">最后更新</span>
            <span className="text-sm text-ash-gray">
              {stats?.timestamp ? new Date(stats.timestamp).toLocaleTimeString("zh-CN") : "..."}
            </span>
          </div>
        </div>
      </div>

      {/* 系统健康度 */}
      <div className="p-4">
        <h3 className="text-sm font-bold text-imperial-gold mb-3">💓 系统健康度</h3>
        <div className="guofeng-card p-3">
          <svg width="100%" height="30" viewBox="0 0 200 30" className="mb-2">
            <polyline
              className="heartbeat-line"
              points="0,15 20,15 25,5 30,25 35,5 40,25 45,15 60,15 65,3 70,27 75,3 80,27 85,15 100,15 105,5 110,25 115,5 120,25 125,15 140,15 145,3 150,27 155,3 160,27 165,15 200,15"
            />
          </svg>
          <div className="flex items-center justify-between">
            <span className="text-sm text-parchment">状态</span>
            <span className="text-sm text-jade-green">正常运行</span>
          </div>
          <div className="flex items-center justify-between mt-1">
            <span className="text-sm text-parchment">运行时间</span>
            <span className="text-sm text-ash-gray">{currentTime}</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
