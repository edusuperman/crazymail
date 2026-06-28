"use client";

import { useEffect, useRef, useState } from "react";
import * as PIXI from "pixi.js";

interface SoldierProps {
  width?: number;
  height?: number;
}

// 7张桌子的位置（对应7位历史名人）
const DESK_POSITIONS = [
  { name: "宋徽宗", x: 400, y: 100, role: "总管" },
  { name: "李清照", x: 200, y: 200, role: "写作" },
  { name: "岳飞", x: 600, y: 200, role: "质检" },
  { name: "张择端", x: 150, y: 350, role: "研究" },
  { name: "李纲", x: 400, y: 350, role: "策略" },
  { name: "韩世忠", x: 650, y: 350, role: "部署" },
  { name: "宗泽", x: 400, y: 500, role: "监控" },
];

// 任务类型
type TaskType = "carry" | "run" | "patrol";

interface Task {
  type: TaskType;
  from: number;
  to: number;
  progress: number;
}

export function SoldierAnimation({ width = 800, height = 600 }: SoldierProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const appRef = useRef<PIXI.Application | null>(null);
  const [currentTask, setCurrentTask] = useState<string>("巡逻中...");

  useEffect(() => {
    if (!canvasRef.current) return;
    let destroyed = false;

    const app = new PIXI.Application();
    app.init({
      width,
      height,
      backgroundColor: 0x1a1a2e,
      antialias: true,
    }).then(() => {
      if (!destroyed && canvasRef.current) {
        canvasRef.current.appendChild(app.canvas);
        appRef.current = app;
        initScene(app);
      }
    });

    return () => {
      destroyed = true;
      if (appRef.current) {
        try { appRef.current.destroy(true); } catch (e) {}
        appRef.current = null;
      }
    };
  }, [width, height]);

  const initScene = (app: PIXI.Application) => {
    const stage = app.stage;

    // 背景
    const bg = new PIXI.Graphics();
    bg.rect(0, 0, width, height);
    bg.fill(0x1a1a2e);
    stage.addChild(bg);

    // 绘制7张桌子
    DESK_POSITIONS.forEach((desk, index) => {
      // 桌子
      const table = new PIXI.Graphics();
      table.roundRect(-40, -20, 80, 40, 8);
      table.fill(0x8b4513);
      table.stroke({ color: 0xd4a017, width: 2 });
      table.position.set(desk.x, desk.y);
      stage.addChild(table);

      // 角色名
      const nameText = new PIXI.Text({
        text: desk.name,
        style: {
          fontFamily: "Arial",
          fontSize: 12,
          fill: 0xffffff,
          align: "center",
        },
      });
      nameText.anchor.set(0.5);
      nameText.position.set(desk.x, desk.y - 35);
      stage.addChild(nameText);

      // 角色图标（简化）
      const icon = new PIXI.Graphics();
      icon.circle(0, 0, 15);
      icon.fill(index === 0 ? 0xd4a017 : 0x2e7d5e);
      icon.position.set(desk.x, desk.y);
      stage.addChild(icon);
    });

    // 创建小兵
    const soldier = createSoldier();
    soldier.position.set(DESK_POSITIONS[0].x, DESK_POSITIONS[0].y + 60);
    stage.addChild(soldier);

    // 小兵状态
    let currentDeskIndex = 0;
    let targetDeskIndex = 1;
    let taskProgress = 0;
    let taskType: TaskType = "patrol";
    let speed = 1;
    let isCarrying = false;

    // 竹简（小兵携带的物品）
    const scroll = new PIXI.Graphics();
    scroll.roundRect(-8, -3, 16, 6, 3);
    scroll.fill(0x8b4513);
    scroll.visible = false;
    soldier.addChild(scroll);

    // 动画循环
    const animate = () => {
      const currentDesk = DESK_POSITIONS[currentDeskIndex];
      const targetDesk = DESK_POSITIONS[targetDeskIndex];

      // 计算方向
      const dx = targetDesk.x - soldier.x;
      const dy = (targetDesk.y + 60) - soldier.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < 5) {
        // 到达目标桌子
        if (taskType === "carry") {
          // 传递竹简完成
          scroll.visible = false;
          isCarrying = false;
          setCurrentTask(`已将竹简送到${targetDesk.name}处`);
        }

        // 切换到下一个任务
        currentDeskIndex = targetDeskIndex;
        targetDeskIndex = (targetDeskIndex + 1) % DESK_POSITIONS.length;

        // 随机决定下一个任务
        const rand = Math.random();
        if (rand < 0.4) {
          taskType = "carry";
          scroll.visible = true;
          isCarrying = true;
          setCurrentTask(`从${DESK_POSITIONS[currentDeskIndex].name}取竹简送往${DESK_POSITIONS[targetDeskIndex].name}`);
          speed = 1;
        } else if (rand < 0.7) {
          taskType = "run";
          setCurrentTask(`紧急报信：前往${DESK_POSITIONS[targetDeskIndex].name}处`);
          speed = 2;
        } else {
          taskType = "patrol";
          setCurrentTask("巡逻中...");
          speed = 0.5;
        }
      }

      // 移动小兵
      const moveX = (dx / distance) * speed;
      const moveY = (dy / distance) * speed;
      soldier.x += moveX;
      soldier.y += moveY;

      // 更新小兵朝向
      if (Math.abs(dx) > Math.abs(dy)) {
        soldier.scale.x = dx > 0 ? 1 : -1;
      }
    };

    app.ticker.add(animate);
  };

  const createSoldier = (): PIXI.Container => {
    const container = new PIXI.Container();

    // 身体
    const body = new PIXI.Graphics();
    body.ellipse(0, 0, 12, 16);
    body.fill(0x4a6741); // 军绿色
    container.addChild(body);

    // 头
    const head = new PIXI.Graphics();
    head.circle(0, -20, 10);
    head.fill(0xf5d0a9); // 肤色
    container.addChild(head);

    // 头盔
    const helmet = new PIXI.Graphics();
    helmet.arc(0, -22, 12, Math.PI, 0);
    helmet.fill(0x666666);
    container.addChild(helmet);

    // 眼睛
    const leftEye = new PIXI.Graphics();
    leftEye.circle(-3, -22, 2);
    leftEye.fill(0x000000);
    container.addChild(leftEye);

    const rightEye = new PIXI.Graphics();
    rightEye.circle(3, -22, 2);
    rightEye.fill(0x000000);
    container.addChild(rightEye);

    // 腿
    const leftLeg = new PIXI.Graphics();
    leftLeg.rect(-6, 12, 5, 12);
    leftLeg.fill(0x4a6741);
    container.addChild(leftLeg);

    const rightLeg = new PIXI.Graphics();
    rightLeg.rect(1, 12, 5, 12);
    rightLeg.fill(0x4a6741);
    container.addChild(rightLeg);

    return container;
  };

  return (
    <div className="relative">
      <div ref={canvasRef} className="rounded-lg overflow-hidden" />
      <div className="absolute top-4 left-4 bg-card-bg/80 px-3 py-2 rounded-lg">
        <p className="text-sm text-parchment">{currentTask}</p>
      </div>
    </div>
  );
}
