"use client";

import { useState, useEffect } from "react";

export function Header() {
  const [currentTime, setCurrentTime] = useState("");
  const [systemStatus, setSystemStatus] = useState<"online" | "warning" | "error">("online");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const timeStr = now.toLocaleString("zh-CN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
      setCurrentTime(timeStr);
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="flex items-center justify-between px-6 py-3 border-b border-card-border bg-card-bg backdrop-blur-sm">
      {/* 左侧：标题 */}
      <div className="flex items-center gap-3">
        <span className="text-2xl">🏛️</span>
        <div>
          <h1 className="text-xl font-bold text-parchment">大宋宣和驿站</h1>
          <p className="text-xs text-ash-gray">临时邮箱矩阵 · 智能运营中枢</p>
        </div>
      </div>

      {/* 中间：系统状态 */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className={`status-light ${systemStatus === "online" ? "green" : "red"}`} />
          <span className="text-sm text-parchment">
            {systemStatus === "online" ? "系统正常" : systemStatus === "warning" ? "系统警告" : "系统异常"}
          </span>
        </div>
        
        {/* 心跳线 */}
        <svg width="100" height="20" viewBox="0 0 100 20">
          <polyline
            className="heartbeat-line"
            points="0,10 20,10 25,5 30,15 35,5 40,15 45,10 60,10 65,3 70,17 75,3 80,17 85,10 100,10"
          />
        </svg>
      </div>

      {/* 右侧：时间 */}
      <div className="text-right">
        <p className="text-sm text-parchment">{currentTime}</p>
        <p className="text-xs text-ash-gray">大宋宣和历</p>
      </div>
    </header>
  );
}
