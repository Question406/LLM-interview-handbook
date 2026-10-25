---
id: vlm-screenshot-coordinate
section: multimodal
order: 2
level: S
title: Screenshot-only GUI Agent 的 click 坐标为什么会失效？如何处理 resize、DPI、scroll、crop、overlay 与 stale screenshot？
quick: "截图像素没有稳定语义，DPR、缩放、滚动、弹窗都会让同一个按钮换位置。坐标要绑定当前 viewport、缩放和截图版本，每次高风险动作前重观察，点击后验证状态。我会优先用 element、目标框或归一化坐标，并对滚动、遮罩和窗口变化做 recovery。"
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

点击坐标会失效，是因为截图上的绝对像素没有稳定语义。同一个逻辑按钮，碰上设备像素比（DPR）、浏览器缩放、窗口 resize、页面 scroll、响应式断点、动画或弹窗，下一帧就会落到完全不同的 $(x, y)$。所以坐标要绑定具体是哪张截图，执行前比对有没有过期，高风险动作前重观察，点完再验证状态。

比如离线标注时点的是「确认」，执行时页面已经往下滚了一段，或者弹出一个广告，同一个点就落到了广告或「取消」上。SeeAct 一类工作把「看」和「点」拆开，正是因为像素观察很容易过期。

Action 的表示里要有 screenshot ID、当前 viewport、缩放 / DPR、目标语义或目标框，以及归一化坐标（相对截图宽高，不用屏幕物理像素）。优先用 element ID 或无障碍树节点，其次 bbox，最后才是点。Crop 过的局部图要记录 crop 原点，不然局部坐标会错位到整屏。实现上把截图、viewport、DPR 放进同一个结构体，执行器不接受裸的两个整数。归一化只挡得住分辨率变化，滚动、overlay 和页面结构变化它管不了，所以它是必要项，单靠它不够。

执行器发点击之前，比较计划时的 screenshot hash 和当前帧，不一致就当 stale，禁止沿用旧点。这要做成执行器的硬错误，只报警告不行。日志记下 hash 是否匹配、是否触发了重观察，不然 stale 点击会被算成 grounding 差。

典型的失效有这几种：滚动后还点旧坐标；overlay 或 toast 挡住目标，模型看不到 z-order；Retina 下逻辑像素和设备像素混用；iframe 或虚拟列表只渲染可见行。提交、支付、删除这类高风险动作前强制重观察，这一步不能为了速度关掉。发现遮挡或滚动，先 scroll-into-view 或关掉 overlay，再重新 grounding，别把误差当成「再点一次」。点完检查 URL、焦点、DOM 断言或业务 oracle，OS 级的 click 成功回执不代表业务完成。连续 stale 或验证失败要设预算，超了就停下升级人工，免得在错误的像素上死循环。

评测要故意注入漂移。microbench 对同一任务做 resize、改 DPR、中途滚动、弹出 modal、延迟截图，指标分开报静止帧 grounding 命中率、漂移后恢复成功率、stale 点击率；漂移 microbench 和端到端任务也分开报，免得静帧高分掩盖滚动失败。评测里常见的误导是只在固定分辨率的静帧上评测；不测 overlay；把 click API 成功当成任务成功。不注入漂移，测到的是标注质量，测不到运行时可靠性。stale 点击率可以做成 SLO，高风险动作上应该接近 0。面试时能讲清 DPR、滚动、overlay 各会让点落到哪里，以及点完怎么验证，这题就答到了。

## 追问

**bbox 比点更稳吗？**
通常是，因为可以算交并比（IoU，即两个区域的交集与并集之比）、做中心校正。但它同样要绑当前帧。

**和 DOM / a11y 融合题是什么关系？**
结构树提供候选，视觉确认几何。纯截图的路径没有结构树兜底，stale 检测得自己做。

**动画过程中能不能点？**
等稳定帧，或者等目标 bbox 连续两帧重合再点，否则一定 stale。
