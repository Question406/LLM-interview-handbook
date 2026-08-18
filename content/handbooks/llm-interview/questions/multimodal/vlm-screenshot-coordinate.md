---
id: vlm-screenshot-coordinate
section: multimodal
order: 2
level: S
title: Screenshot-only GUI Agent 的 click 坐标为什么会失效？如何处理 resize、DPI、scroll、crop、overlay 与 stale screenshot？
quick: 像素不是稳定语义。坐标要绑定当前 viewport、缩放和截图版本；每次高风险动作前重观察，点击后验证状态。优先使用 element / bbox / normalized coordinate，并对滚动、遮罩和窗口变化做 recovery。
tags:
  - GUI Agent
  - Visual Grounding
  - Reliability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: SeeAct
    url: https://arxiv.org/abs/2401.10935
    type: primary
---

同一个逻辑按钮会因 device pixel ratio、浏览器缩放、窗口 resize、页面 scroll、响应式布局、动画或弹窗改变像素位置。离线截图上的绝对 `(x, y)` 在实际执行时可能已经点击到别的元素。

action 表示应包含 screenshot/version ID、当前 viewport、目标 bbox 或元素语义、归一化坐标和 precondition。执行器发现 observation 已过期、目标被遮挡或页面滚动后，必须重新观察而不是沿用旧坐标。

点击后检查 URL、DOM、截图差异或业务状态；失败时可重新定位、回退 checkpoint 或请求澄清。只有点击成功的 API 回执不代表业务 action 正确完成。
