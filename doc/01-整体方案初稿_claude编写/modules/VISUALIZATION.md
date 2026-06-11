# 动态可视化设计：活的清明上河图

## 设计哲学

参考抖音博主「混子哥」风格：
- 简笔画线条，黑色勾线 + 少量国风配色（朱红/墨绿/金黄）
- 动作夸张、有记忆点，让非技术人员看3分钟就能理解系统在干什么
- 场景化叙事：每个技术事件都映射成一个可见的「故事」

---

## 主视觉：横向滚动城镇全景

```
← 向左滚动（查看更多驿站）                  向右滚动 →
┌───────────────────────────────────────────────────────────────────┐
│                    宋代城镇全景（清明上河图风格）                    │
│  🏯汴京总督府    🏪驿站01    🏪驿站02  ···  🏪驿站20   🌐好汉地图  │
│  [宋徽宗批折]   [李纲研究]  [张择端]         [飞鸽进港]  [世界版图] │
│                                                                   │
│  ～～～运河～～～  🕊→→→  🕊→→→  🕊→→→  ～～～～～～～～～～     │
│                                                                   │
│  📊今日产出:47篇  ⚠3站异常  💰收益$234  🎯任务队列:12           │
└───────────────────────────────────────────────────────────────────┘
```

---

## PixiJS 场景层级结构

```typescript
// frontend/src/pixi/scenes/MainScene.ts

class MainScene extends Container {
  layers = {
    background:  new Container(),  // 城镇背景图（静态 + 微动）
    buildings:   new Container(),  // 20个驿站建筑
    river:       new Container(),  // 运河（流水动效）
    pigeons:     new Container(),  // 飞鸽（最活跃层）
    characters:  new Container(),  // 官员/好汉人物
    effects:     new Container(),  // 粒子特效（箭矢/烟雾/金光）
    ui_overlay:  new Container(),  // 数据标签浮层
    darkdoor:    new Container(),  // 皇城司暗门（最高层）
  }
}
```

---

## 核心动效清单

### 1. 飞鸽传书（最常见动效）
**触发**：内容任务从一个阶段进入下一阶段
```typescript
// 飞鸽飞行路径：贝塞尔曲线
const pigeon = new PigeonSprite();
pigeon.flyFrom(ligang_pos).to(zhangzeduan_pos)
      .withPayload(task.word_count > 2000 ? 'heavy_bag' : 'letter')
      .duration(1200); // ms
```

**飞鸽形态**：
- 普通信件：小白鸽，携带卷轴
- 重要稿件（>2000字）：大白鸽，背着大包裹
- 紧急任务：红色飞鸽，飞行轨迹留火花

### 2. 飞鸽中箭（质检失败）
**触发**：QA分数低于打回阈值
```typescript
// 中箭后粒子爆炸，羽毛散落
pigeon.hitByArrow()
      .particleExplosion(feather_texture)
      .fallAnimation()
      .onComplete(() => showRetryBubble(task_id));
```
**动效细节**：箭从岳飞营帐方向射出，命中飞鸽，羽毛飘散，卷轴落地

### 3. 官员动作帧动画
每位官员有4组循环动画：

| 官员 | 空闲动画 | 工作动画 | 通过动画 | 失败动画 |
|------|---------|---------|---------|---------|
| 李纲 | 捋胡须 | 翻阅竹简 | 点头满意 | 拍桌子 |
| 张择端 | 看向窗外 | 挥毫绘图 | 举起画卷 | 撕稿纸 |
| 李清照 | 望月沉思 | 疾书挥毫 | 吟诗微笑 | 蹙眉摇头 |
| 岳飞 | 负手踱步 | 红笔审阅 | 大力打勾 | 抛出卷轴（打回）|
| 宋徽宗 | 把玩印章 | 批阅奏折 | 盖章通过 | 站立发金牌 |

### 4. 金牌触发动效
```typescript
// 每道金牌对应不同程度的视觉变化
switch(medalLevel) {
  case 1: site.addWarningFlag();                    // 驿站旗帜变黄
  case 4: pipeline.pauseAllPigeons();               // 飞鸽全部停飞
  case 7: scene.partialGrayscale(['database']);     // 数据库区域变灰
  case 12:
    scene.fullGrayscale();                          // 全图黑白
    bgm.fadeOut(2000);                              // 古琴声渐弱
    songhuizong.standUp().walkToCenter();           // 宋徽宗走到中央
    showOverlay('奉旨停机', calligraphy_style);     // 书法字幕
    break;
}
```

### 5. 好汉升级动效
**触发**：某好汉 XP 达到下一等级阈值
- 金光从人物头顶升起
- 滚动字幕：「[好汉名] 晋升为 [新等级]」
- 梁山大旗在世界地图对应位置插旗

### 6. 收益里程碑动效
**触发**：单站月收益突破设定目标
- 铜钱从屋顶飞出
- 宋徽宗双手合十点头
- 数字跳动动效

---

## React Flow：流水线可视化

```typescript
// frontend/src/flows/ContentPipelineFlow.tsx
// 点击某个驿站，右侧展开该站流水线状态图

const nodes = [
  { id: 'stage1', label: '李纲\n关键词研究', type: 'official',
    data: { status: 'running', progress: 0.7 }},
  { id: 'stage2', label: '张择端\nSERP+大纲', type: 'official',
    data: { status: 'waiting' }},
  // ...
];
// 节点颜色：running=青绿 / waiting=米黄 / done=朱红 / failed=墨灰
```

---

## WebSocket 实时驱动

```typescript
// frontend/src/lib/ws-client.ts

wsClient.on('pigeon_fly', (data) => {
  pixiScene.triggerPigeonFly(data.from, data.to, data.payload_size);
  flowChart.updateNodeStatus(data.task_id, data.to_stage, 'running');
});

wsClient.on('pigeon_shot', (data) => {
  pixiScene.triggerPigeonShot(data.task_id);
  notifications.push({ type: 'warning', msg: `任务 ${data.task_id} 质检失败，打回重写` });
});

wsClient.on('gold_medal', (data) => {
  pixiScene.triggerGoldMedalEffect(data.level);
  goldMedalPanel.show(data);
});
```

---

## 国风配色方案

```css
:root {
  --ink-black:     #1a1a1a;   /* 墨黑（主线条）*/
  --vermillion:    #c0392b;   /* 朱红（强调/告警）*/
  --imperial-gold: #d4a017;   /* 帝金（重要节点）*/
  --jade-green:    #2e7d5e;   /* 玉绿（正常运行）*/
  --parchment:     #f5f0e8;   /* 宣纸色（背景）*/
  --ink-blue:      #2c4a6e;   /* 靛蓝（数据图表）*/
  --warning-amber: #e67e22;   /* 琥珀（警告）*/
  --ash-gray:      #bdc3c7;   /* 灰（停运/禁用）*/
}
```

---

## 美术资源生成指引

所有角色使用 **Grok Imagine + Midjourney** 生成，风格 Prompt 模板：

```
Song Dynasty official cartoon character, [角色名], simple ink brush style,
minimalist line art, black outlines with minimal color (vermillion and gold accents),
chibi proportions, expressive face, [该角色标志性动作/道具],
white background, vector-style, consistent with "混子哥" (Chinese history comic) aesthetic
```

输出格式：SVG（用于 PixiJS Sprite），分辨率 256x256 per frame，
每个角色最少 4 组动画（idle/work/pass/fail），每组 8-12 帧。
