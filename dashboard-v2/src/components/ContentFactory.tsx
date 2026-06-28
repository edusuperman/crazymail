"use client";

import { useState, useEffect, useCallback } from "react";

interface Stage {
  id: number;
  name: string;
  role: string;
  icon: string;
  status: "waiting" | "running" | "done" | "error";
  progress: number;
  output?: string;
}

interface ProgressMessage {
  task_id: string;
  stage_id: number;
  stage_name: string;
  status: "waiting" | "running" | "done" | "error";
  progress: number;
  message: string;
  output?: string;
  timestamp: string;
}

const INITIAL_STAGES: Stage[] = [
  { id: 1, name: "研究", role: "张择端", icon: "🎨", status: "waiting", progress: 0 },
  { id: 2, name: "大纲", role: "李纲", icon: "🗺️", status: "waiting", progress: 0 },
  { id: 3, name: "初稿", role: "李清照", icon: "✍️", status: "waiting", progress: 0 },
  { id: 4, name: "润色", role: "李清照", icon: "✍️", status: "waiting", progress: 0 },
  { id: 5, name: "质检", role: "岳飞", icon: "🔍", status: "waiting", progress: 0 },
  { id: 6, name: "部署", role: "韩世忠", icon: "🐎", status: "waiting", progress: 0 },
  { id: 7, name: "监控", role: "宗泽", icon: "🏰", status: "waiting", progress: 0 },
];

// API 基础 URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function ContentFactory() {
  const [stages, setStages] = useState<Stage[]>(INITIAL_STAGES);
  const [keyword, setKeyword] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [taskId, setTaskId] = useState<string | null>(null);

  const addLog = useCallback((msg: string) => {
    setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
  }, []);

  const updateStage = useCallback((id: number, updates: Partial<Stage>) => {
    setStages((prev) =>
      prev.map((s) => (s.id === id ? { ...s, ...updates } : s))
    );
  }, []);

  // SSE 连接
  useEffect(() => {
    if (!taskId || !isRunning) return;

    const eventSource = new EventSource(
      `${API_BASE}/api/v1/content-factory/progress/${taskId}`
    );

    eventSource.onmessage = (event) => {
      try {
        const data: ProgressMessage = JSON.parse(event.data);

        // 更新阶段状态
        if (data.stage_id > 0) {
          updateStage(data.stage_id, {
            status: data.status,
            progress: data.progress,
            output: data.output,
          });
        }

        // 添加日志
        addLog(data.message);

        // 检查是否完成
        if (data.status === "done" && data.stage_id === 7) {
          addLog("🎉 流水线完成！");
          setIsRunning(false);
          eventSource.close();
        } else if (data.status === "error") {
          addLog(`❌ 流水线失败: ${data.message}`);
          setIsRunning(false);
          eventSource.close();
        }
      } catch (error) {
        console.error("解析 SSE 消息失败:", error);
      }
    };

    eventSource.onerror = (error) => {
      console.error("SSE 连接错误:", error);
      addLog("❌ 连接中断");
      setIsRunning(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [taskId, isRunning, updateStage, addLog]);

  const runPipeline = async () => {
    if (!keyword.trim() || isRunning) return;

    setIsRunning(true);
    setStages(INITIAL_STAGES);
    setLogs([]);
    addLog(`开始流水线：关键词「${keyword}」`);

    try {
      // 调用后端 API 启动流水线
      const response = await fetch(`${API_BASE}/api/v1/content-factory/run`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          keyword: keyword,
          language: "en",
          word_count_min: 1500,
          word_count_max: 3000,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setTaskId(data.task_id);
      addLog(`任务已创建: ${data.task_id}`);
    } catch (error) {
      console.error("启动流水线失败:", error);
      addLog(`❌ 启动失败: ${error instanceof Error ? error.message : String(error)}`);
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 标题 */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-parchment">宋徽宗写作工厂</h2>
        <p className="text-sm text-ash-gray">7阶段内容生产流水线</p>
      </div>

      {/* 输入区 */}
      <div className="flex gap-4 items-center">
        <input
          type="text"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="输入关键词，如 'temporary email for privacy'"
          className="flex-1 px-4 py-2 bg-card-bg border border-card-border rounded-lg text-parchment placeholder-ash-gray"
          disabled={isRunning}
          onKeyDown={(e) => e.key === "Enter" && runPipeline()}
        />
        <button
          onClick={runPipeline}
          disabled={isRunning || !keyword.trim()}
          className="px-6 py-2 bg-imperial-gold text-ink-black rounded-lg font-bold disabled:opacity-50 hover:bg-imperial-gold/90 transition-colors"
        >
          {isRunning ? "运行中..." : "开始生产"}
        </button>
      </div>

      {/* 7阶段流水线 */}
      <div className="grid grid-cols-7 gap-2">
        {stages.map((stage, i) => (
          <div key={stage.id} className="text-center">
            {/* 连接线 */}
            {i > 0 && (
              <div className={`h-0.5 mb-2 ${
                stages[i - 1].status === "done" ? "bg-jade-green" : "bg-card-border"
              }`} />
            )}
            
            {/* 角色卡片 */}
            <div className={`guofeng-card p-3 ${
              stage.status === "running" ? "ring-2 ring-imperial-gold" :
              stage.status === "done" ? "ring-2 ring-jade-green" :
              stage.status === "error" ? "ring-2 ring-vermillion" : ""
            }`}>
              <span className="text-2xl">{stage.icon}</span>
              <p className="text-xs font-bold text-parchment mt-1">{stage.name}</p>
              <p className="text-xs text-ash-gray">{stage.role}</p>
              
              {/* 状态 */}
              <div className="mt-2">
                {stage.status === "waiting" && (
                  <span className="text-xs text-ash-gray">等待</span>
                )}
                {stage.status === "running" && (
                  <span className="text-xs text-imperial-gold animate-pulse">执行中...</span>
                )}
                {stage.status === "done" && (
                  <span className="text-xs text-jade-green">✓ 完成</span>
                )}
                {stage.status === "error" && (
                  <span className="text-xs text-vermillion">✗ 失败</span>
                )}
              </div>

              {/* 输出 */}
              {stage.output && (
                <p className="text-xs text-ash-gray mt-1 truncate" title={stage.output}>
                  {stage.output}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* 进度条 */}
      {isRunning && (
        <div className="w-full bg-card-bg rounded-full h-2">
          <div
            className="bg-imperial-gold h-2 rounded-full transition-all duration-500"
            style={{
              width: `${(stages.filter((s) => s.status === "done").length / 7) * 100}%`,
            }}
          />
        </div>
      )}

      {/* 日志 */}
      <div className="guofeng-card p-4 max-h-60 overflow-y-auto">
        <h3 className="text-sm font-bold text-imperial-gold mb-2">📋 运行日志</h3>
        {logs.length === 0 ? (
          <p className="text-xs text-ash-gray">等待启动...</p>
        ) : (
          <div className="space-y-1">
            {logs.map((log, i) => (
              <p key={i} className="text-xs text-parchment font-mono">{log}</p>
            ))}
          </div>
        )}
      </div>

      {/* 任务信息 */}
      {taskId && (
        <div className="guofeng-card p-3 text-center">
          <p className="text-xs text-ash-gray">
            任务 ID: <span className="text-parchment font-mono">{taskId}</span>
          </p>
        </div>
      )}
    </div>
  );
}
