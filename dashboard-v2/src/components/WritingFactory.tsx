"use client";

import { useState } from "react";
import { SoldierAnimation } from "./SoldierAnimation";

interface Character {
  id: string;
  name: string;
  role: string;
  icon: string;
  desk: string;
  status: "working" | "error" | "stopped" | "done" | "resting";
  progress: number;
}

const characters: Character[] = [
  {
    id: "songhuizong",
    name: "宋徽宗",
    role: "总管/审批",
    icon: "👑",
    desk: "龙椅 + 朱笔 + 竹简堆",
    status: "working",
    progress: 75,
  },
  {
    id: "liqingzhao",
    name: "李清照",
    role: "写作",
    icon: "✍️",
    desk: "书桌 + 毛笔 + 墨砚 + 纸张",
    status: "working",
    progress: 60,
  },
  {
    id: "yuefei",
    name: "岳飞",
    role: "质检",
    icon: "🔍",
    desk: "帅案 + 放大镜 + 精忠报国旗帜",
    status: "done",
    progress: 100,
  },
  {
    id: "zhangzeduan",
    name: "张择端",
    role: "大纲/研究",
    icon: "🎨",
    desk: "画架 + 画卷 + 毛笔",
    status: "working",
    progress: 45,
  },
  {
    id: "ligang",
    name: "李纲",
    role: "策略/规划",
    icon: "🗺️",
    desk: "沙盘 + 地图 + 令旗",
    status: "resting",
    progress: 0,
  },
  {
    id: "hanshizhong",
    name: "韩世忠",
    role: "部署/发布",
    icon: "🐎",
    desk: "战马 + 号角 + 令箭",
    status: "resting",
    progress: 0,
  },
  {
    id: "zongze",
    name: "宗泽",
    role: "监控/运维",
    icon: "🏰",
    desk: "城墙 + 望远镜 + 警钟",
    status: "error",
    progress: 30,
  },
];

const statusColors = {
  working: "bg-jade-green",
  error: "bg-vermillion",
  stopped: "bg-ash-gray",
  done: "bg-imperial-gold",
  resting: "bg-ink-blue",
};

const statusLabels = {
  working: "执行中",
  error: "报错",
  stopped: "终止",
  done: "完成",
  resting: "休息",
};

const statusAnimations = {
  working: "animate-pulse",
  error: "animate-blink",
  stopped: "",
  done: "",
  resting: "",
};

export function WritingFactory() {
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);

  return (
    <div className="space-y-6">
      {/* 标题 */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-parchment">宋徽宗写作工厂</h2>
        <p className="text-sm text-ash-gray">编制内内容生产 · 7阶段流水线</p>
      </div>

      {/* 场景：宋代书房 */}
      <div className="relative bg-gradient-to-b from-ink-blue/20 to-ink-black/40 rounded-xl p-6 min-h-[500px]">
        {/* 背景装饰 */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-4 left-4 text-6xl">📜</div>
          <div className="absolute top-4 right-4 text-6xl">🏛️</div>
          <div className="absolute bottom-4 left-4 text-6xl">🎋</div>
          <div className="absolute bottom-4 right-4 text-6xl">🏮</div>
        </div>

        {/* 7张长桌 */}
        <div className="relative grid grid-cols-4 gap-6">
          {characters.map((char, index) => (
            <div
              key={char.id}
              onClick={() => setSelectedCharacter(char)}
              className={`guofeng-card p-4 cursor-pointer transition-all hover:scale-105 ${
                selectedCharacter?.id === char.id ? "ring-2 ring-imperial-gold" : ""
              } ${index === 0 ? "col-span-4" : ""}`}
            >
              {/* 角色信息 */}
              <div className="flex items-center gap-3 mb-3">
                <span className="text-3xl">{char.icon}</span>
                <div>
                  <h3 className="font-bold text-parchment">{char.name}</h3>
                  <p className="text-xs text-ash-gray">{char.role}</p>
                </div>
                <div className="ml-auto">
                  <div className={`status-light ${char.status === "working" ? "green" : char.status === "error" ? "red" : ""}`} />
                </div>
              </div>

              {/* 桌上道具 */}
              <p className="text-xs text-ash-gray mb-3">桌上：{char.desk}</p>

              {/* 状态和进度 */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className={`text-xs px-2 py-0.5 rounded ${statusColors[char.status]} text-white`}>
                    {statusLabels[char.status]}
                  </span>
                  <span className="text-xs text-ash-gray">{char.progress}%</span>
                </div>
                
                {/* 墨条进度条 */}
                <div className="ink-progress h-2">
                  <div
                    className="h-full bg-gradient-to-r from-imperial-gold to-vermillion transition-all duration-500"
                    style={{ width: `${char.progress}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 小兵（驿卒）动画 */}
        <div className="mt-4">
          <SoldierAnimation width={800} height={200} />
        </div>
      </div>

      {/* 选中角色详情 */}
      {selectedCharacter && (
        <div className="guofeng-card p-4">
          <h3 className="font-bold text-imperial-gold mb-2">
            {selectedCharacter.name} - {selectedCharacter.role}
          </h3>
          <p className="text-sm text-ash-gray">
            当前状态：{statusLabels[selectedCharacter.status]}
          </p>
          <p className="text-sm text-ash-gray">
            完成进度：{selectedCharacter.progress}%
          </p>
        </div>
      )}
    </div>
  );
}
