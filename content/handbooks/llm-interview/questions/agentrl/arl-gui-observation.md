---
id: arl-gui-observation
section: agentrl
order: 15
level: A
title: Browser / GUI Agent 的 Observation 应怎么表示？
quick: >-
  通常组合 screenshot/vision、DOM/accessibility tree、structured element metadata 与
  action history。纯截图泛化强但定位难；纯 DOM 高效但可能缺视觉状态；混合表示更实用。
tags:
  - GUI Agent
  - Observation
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: SeeClick
    url: https://arxiv.org/abs/2401.10935
    type: primary
---

GUI Agent 的 observation 不是「把网页塞进上下文」。这块容易直接答成二选一：只截图，定位漂、token 贵；只 DOM，canvas / 图标 / 弹层视觉状态全丢。实用做法是混合：screenshot + DOM / a11y 树 + 元素元数据 + action history。SeeClick 一类工作说明视觉 grounding 要单独训，不能假设截图里「模型自己会找按钮」。定位融合细节见 `cu-dom-a11y-visual-grounding`。

## 表征权衡：成本、可定位、动态一致性

四路信号各管一块：

- **截图：** 跨站点泛化强，能看见 CSS 绘制、遮挡、弹窗；坐标随分辨率 / DPR 漂，整屏视觉 token 贵。
- **DOM / a11y 树：** 角色、名、`disabled`、层次便宜且可检索；虚拟列表、iframe、自定义绘制常缺节点或 bbox 为 0。
- **结构化元数据：** 稳定 element id、可见 bbox、可聚焦性、当前 URL / frame。id 每次重绘都变，action grounding 会漂。
- **Action history：** 上次点了什么、滚动了多少。没有它，模型看不到自己造成的状态差。

关键工程约束：element id 必须在同一次观察内稳定，或改用角色 + 名 + 相对几何，而不是「第 17 个 div」。动态加载时 observation 要带「仍在加载」标记，否则模型会在空白树上瞎点。训练时 environment observation 不属于 policy loss：视觉 encoder 若冻结，图只是 $s_t$；若端到端训，也只在策略 token 上反传，不要对 DOM 文本做语言模型似然。

## 评测必须覆盖单模态会翻车的场景

Eval 不要只测静态桌面点选。至少包括：动态加载、弹窗挡点击、需要 scroll 才出现的目标、纯视觉信息（图标无文本）、a11y 树缺失或滞后、Retina 坐标翻倍、iframe 偏移。这些正是 `cu-failure-taxonomy` 里 grounding 层的来源。报告应拆开：树能否召回目标、视觉点是否命中、冲突时是否改通道，而不是一个端到端成功率。

观测还要可回放：存截图哈希、树序列化、id 映射和动作。没有这些，失败只能叫「模型不会用浏览器」。预算上应对树做可见节点过滤，对截图做局部裁剪，避免把整棵 HTML 和 4K 图都喂进去。那会把长上下文问题伪装成 Agent 能力问题。

最后我会补一句：混合观测是默认，不是折中。树管语义候选，图管几何与视觉-only 状态，历史管「我刚做了什么」。id 不稳、树图冲突、动态加载，都必须进评测。

## 追问

- **为什么不把整页 HTML 当 observation？** Token 爆炸，且大量不可见节点；模型会拟合标记顺序而不是可见 UI。过滤可见 / 可聚焦节点，再按需截图确认。
- **Set-of-Mark 编号每次变怎么办？** 编号是当步观察的局部坐标，不要跨步当稳定 id。下一步必须按新树重标，否则会点到别人。
- **Observation 要不要进 SFT loss？** 不要当目标 token。它是状态，不是策略输出。对它算 CE 等于让模型背页面。
- **和 computer-use 定位题？** 本题管 $s_t$ 怎么表示；`cu-dom-a11y-visual-grounding` 管树与视觉如何融合成点击点。没有稳定观测，融合管道无从评。
