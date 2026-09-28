---
id: vlm-screenshot-coordinate
section: multimodal
order: 2
level: S
title: Screenshot-only GUI Agent 的 click 坐标为什么会失效？如何处理 resize、DPI、scroll、crop、overlay 与 stale screenshot？
quick: 像素不是稳定语义。坐标要绑定当前 viewport、缩放和截图版本；每次高风险动作前重观察，点击后验证状态。我会优先用 element / bbox / normalized coordinate，并对滚动、遮罩和窗口变化做 recovery。
tags:
  - GUI Agent
  - Visual Grounding
  - Reliability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: SeeAct
    url: https://arxiv.org/abs/2401.10935
    type: primary
---

截图上的绝对像素不是稳定语义。同一个逻辑按钮会因 DPR、浏览器缩放、窗口 resize、页面 scroll、响应式断点、动画或弹窗，在下一帧落到完全不同的 $(x, y)$。离线标注的点击点，执行时可能已经点到广告或「取消」。坐标合同要绑哪一张图、何时重观察、点完如何验证。SeeAct 一类工作把「看」和「点」拆开，正是因为像素观察很容易过期。

## 坐标必须绑定观察版本

Action 表示应包含 screenshot ID、当前 viewport、缩放 / DPR、目标语义或 bbox、以及归一化坐标（相对截图宽高，而不是屏幕物理像素）。优先 element ID / a11y 节点，其次 bbox，最后才是点。Crop 过的局部图必须记录 crop 原点，否则局部坐标会错位到整屏。执行器在发出点击前比较「计划时的 screenshot hash」与「当前帧」；不一致就视为 stale，禁止沿用旧点。归一化只挡分辨率变化，挡不住滚动和 overlay，所以它是必要项不是充分项。日志记下 hash 是否匹配、是否触发了重观察，否则 stale 点击会被算成 grounding 差。

## 失效模式与 recovery

典型失效：滚动后仍点旧坐标；overlay / toast 挡住目标但模型看不见 z-order；Retina 下逻辑像素与设备像素混用；iframe 或虚拟列表只渲染可见行。高风险动作（提交、支付、删除）前强制重观察。发现遮挡或滚动，先 scroll-into-view 或关 overlay，再 grounding，而不是把误差当「再点一次」。点击后检查 URL、焦点、DOM 断言或业务 oracle；只有 OS 级 click 成功回执，不代表业务完成。连续 stale 或验证失败要设预算，超限停并升级人工，避免在错误像素上死循环。

## 评测应故意注入漂移

microbench 要对同一任务做 resize、改 DPR、中途滚动、弹出 modal、延迟截图。指标拆开：静止帧 grounding 命中率、漂移后恢复成功率、stale 点击率。能刷的点：只在固定分辨率静帧评测；不测 overlay；把 click API 成功当任务成功。执行器合同：无 screenshot hash 匹配则拒绝点击；高风险动作强制重观察；验证失败走 recovery 而不是连点。评测若不注入漂移，测的是标注质量，不是运行时可靠性。把 stale 点击率做成 SLO：高风险动作上应接近 0。实现上截图、viewport、DPR 进同一结构体，禁止执行器接受裸的两个整数。

把 screenshot hash 不匹配做成执行器硬错误，而不是警告。高风险动作的重观察不可被「为了速度」关掉。漂移 microbench 与端到端任务分开报，避免静帧高分掩盖滚动失败。

坐标绑当前截图版本，stale 就禁止点击。能讲清 DPR、滚动、overlay 各会让点落到哪里，以及点后如何验证。

## 追问

- **为什么归一化还不够？** 归一化不管滚动和 overlay；它只挡分辨率变化，挡不住页面结构变。
- **bbox 比点更稳吗？** 通常是，因为可做 IoU 与中心校正；但仍要绑当前帧。
- **和 DOM/a11y 融合题的关系？** 结构树提供候选，视觉确认几何；纯截图路径必须自己承担 stale 检测。
- **动画过程中能不能点？** 等稳定帧或等目标 bbox 连续两帧重合，否则必 stale。
