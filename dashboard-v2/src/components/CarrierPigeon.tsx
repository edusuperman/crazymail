"use client";

import { useEffect, useRef, useState } from "react";
import * as PIXI from "pixi.js";

interface CarrierPigeonProps {
  width?: number;
  height?: number;
  onStart?: () => void;
  onComplete?: () => void;
}

interface PigeonState {
  x: number;
  y: number;
  angle: number;
  speed: number;
  wingAngle: number;
  wingDirection: number;
}

interface TrailPoint {
  x: number;
  y: number;
  alpha: number;
}

export function CarrierPigeon({
  width = 800,
  height = 600,
  onStart,
  onComplete,
}: CarrierPigeonProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const appRef = useRef<PIXI.Application | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (!canvasRef.current) return;
    let destroyed = false;

    // 创建 PixiJS 应用
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

  const startAnimation = () => {
    if (!appRef.current || isAnimating) return;

    setIsAnimating(true);
    onStart?.();

    const app = appRef.current;
    const stage = app.stage;

    // 清除现有内容
    stage.removeChildren();

    // 创建背景（宋代书房风格）
    const bg = new PIXI.Graphics();
    bg.rect(0, 0, width, height);
    bg.fill(0x1a1a2e);
    stage.addChild(bg);

    // 创建目标平台图标（内圈）
    const platformContainer = new PIXI.Container();
    stage.addChild(platformContainer);

    const platforms = [
      { name: "Reddit", x: width / 2 + 200, y: height / 2 },
      { name: "Twitter", x: width / 2, y: height / 2 - 200 },
      { name: "GitHub", x: width / 2 - 200, y: height / 2 },
      { name: "YouTube", x: width / 2, y: height / 2 + 200 },
    ];

    platforms.forEach((p) => {
      const circle = new PIXI.Graphics();
      circle.circle(0, 0, 30);
      circle.fill(0x2e7d5e);
      circle.stroke({ color: 0xd4a017, width: 2 });
      circle.position.set(p.x, p.y);
      platformContainer.addChild(circle);

      const text = new PIXI.Text({
        text: p.name,
        style: {
          fontFamily: "Arial",
          fontSize: 12,
          fill: 0xffffff,
          align: "center",
        },
      });
      text.anchor.set(0.5);
      text.position.set(p.x, p.y);
      platformContainer.addChild(text);
    });

    // 创建起点（好汉位置）
    const startX = 100;
    const startY = height / 2;

    const heroCircle = new PIXI.Graphics();
    heroCircle.circle(0, 0, 40);
    heroCircle.fill(0xc0392b);
    heroCircle.stroke({ color: 0xd4a017, width: 3 });
    heroCircle.position.set(startX, startY);
    stage.addChild(heroCircle);

    const heroText = new PIXI.Text({
      text: "好汉",
      style: {
        fontFamily: "Arial",
        fontSize: 14,
        fill: 0xffffff,
        align: "center",
      },
    });
    heroText.anchor.set(0.5);
    heroText.position.set(startX, startY);
    stage.addChild(heroText);

    // 创建信鸽
    const pigeon = new PIXI.Container();
    stage.addChild(pigeon);

    // 信鸽身体
    const body = new PIXI.Graphics();
    body.ellipse(0, 0, 20, 12);
    body.fill(0xffffff);
    pigeon.addChild(body);

    // 信鸽头部
    const head = new PIXI.Graphics();
    head.circle(15, -5, 8);
    head.fill(0xffffff);
    pigeon.addChild(head);

    // 信鸽嘴巴
    const beak = new PIXI.Graphics();
    beak.moveTo(23, -5);
    beak.lineTo(28, -3);
    beak.lineTo(23, -1);
    beak.closePath();
    beak.fill(0xd4a017);
    pigeon.addChild(beak);

    // 信鸽眼睛
    const eye = new PIXI.Graphics();
    eye.circle(18, -7, 2);
    eye.fill(0x000000);
    pigeon.addChild(eye);

    // 信鸽翅膀（左右各一个）
    const leftWing = new PIXI.Graphics();
    leftWing.moveTo(-5, -8);
    leftWing.lineTo(-20, -25);
    leftWing.lineTo(5, -12);
    leftWing.closePath();
    leftWing.fill(0xe0e0e0);
    pigeon.addChild(leftWing);

    const rightWing = new PIXI.Graphics();
    rightWing.moveTo(-5, 8);
    rightWing.lineTo(-20, 25);
    rightWing.lineTo(5, 12);
    rightWing.closePath();
    rightWing.fill(0xe0e0e0);
    pigeon.addChild(rightWing);

    // 信鸽尾巴
    const tail = new PIXI.Graphics();
    tail.moveTo(-20, 0);
    tail.lineTo(-35, -8);
    tail.lineTo(-35, 8);
    tail.closePath();
    tail.fill(0xd0d0d0);
    pigeon.addChild(tail);

    // 竹简（信鸽携带的物品）
    const scroll = new PIXI.Graphics();
    scroll.roundRect(-10, -3, 20, 6, 3);
    scroll.fill(0x8b4513);
    pigeon.addChild(scroll);

    // 初始化信鸽状态
    const pigeonState: PigeonState = {
      x: startX,
      y: startY,
      angle: 0,
      speed: 2,
      wingAngle: 0,
      wingDirection: 1,
    };

    // 尾迹点
    const trail: TrailPoint[] = [];
    const maxTrailLength = 50;

    // 目标平台
    let currentTargetIndex = 0;
    const target = platforms[currentTargetIndex];

    // 计算螺旋路径
    const centerX = width / 2;
    const centerY = height / 2;
    const spiralRadius = 200;
    let spiralAngle = 0;
    const spiralSpeed = 0.02;

    // 动画循环
    const animate = () => {
      if (!isAnimating) return;

      // 计算到目标的角度
      const dx = target.x - pigeonState.x;
      const dy = target.y - pigeonState.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < 5) {
        // 到达目标
        currentTargetIndex = (currentTargetIndex + 1) % platforms.length;
        if (currentTargetIndex === 0) {
          // 完成一圈
          setIsAnimating(false);
          onComplete?.();
          return;
        }
      }

      // 计算螺旋路径点
      const angleToTarget = Math.atan2(dy, dx);
      const spiralOffset = Math.sin(spiralAngle) * 50;

      // 移动信鸽
      pigeonState.x += Math.cos(angleToTarget) * pigeonState.speed;
      pigeonState.y += Math.sin(angleToTarget) * pigeonState.speed;

      // 添加螺旋效果
      pigeonState.x += Math.cos(spiralAngle + Math.PI / 2) * spiralOffset * 0.01;
      pigeonState.y += Math.sin(spiralAngle + Math.PI / 2) * spiralOffset * 0.01;

      // 更新信鸽位置和角度
      pigeon.position.set(pigeonState.x, pigeonState.y);
      pigeon.rotation = angleToTarget;

      // 翅膀动画
      pigeonState.wingAngle += 0.1 * pigeonState.wingDirection;
      if (pigeonState.wingAngle > 0.5 || pigeonState.wingAngle < -0.5) {
        pigeonState.wingDirection *= -1;
      }
      leftWing.rotation = pigeonState.wingAngle;
      rightWing.rotation = -pigeonState.wingAngle;

      // 添加尾迹点
      trail.push({
        x: pigeonState.x,
        y: pigeonState.y,
        alpha: 0.8,
      });

      // 限制尾迹长度
      if (trail.length > maxTrailLength) {
        trail.shift();
      }

      // 更新尾迹透明度
      trail.forEach((point, index) => {
        point.alpha = (index / trail.length) * 0.8;
      });

      // 绘制尾迹
      const trailGraphics = new PIXI.Graphics();
      if (trail.length > 1) {
        trailGraphics.moveTo(trail[0].x, trail[0].y);
        for (let i = 1; i < trail.length; i++) {
          trailGraphics.lineTo(trail[i].x, trail[i].y);
        }
        trailGraphics.stroke({ color: 0x95a5a6, width: 3, alpha: 0.5 });
      }
      stage.addChild(trailGraphics);

      // 更新螺旋角度
      spiralAngle += spiralSpeed;
    };

    // 添加动画到 ticker
    app.ticker.add(animate);
  };

  return (
    <div className="relative">
      <div ref={canvasRef} className="rounded-lg overflow-hidden" />
      <button
        onClick={startAnimation}
        disabled={isAnimating}
        className="absolute bottom-4 right-4 px-4 py-2 bg-imperial-gold text-ink-black rounded-lg font-bold disabled:opacity-50"
      >
        {isAnimating ? "飞行中..." : "放飞信鸽"}
      </button>
    </div>
  );
}
