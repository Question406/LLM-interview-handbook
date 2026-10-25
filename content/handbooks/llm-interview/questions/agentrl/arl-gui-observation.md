---
id: arl-gui-observation
section: agentrl
order: 15
level: A
title: Browser / GUI Agent 的 Observation 应怎么表示？
quick: "混合截图、DOM 或无障碍树、结构化元素信息和动作历史。截图看得到遮挡和弹层，但定位不稳、成本高；DOM 便宜好检索，却会漏掉 canvas、图标和弹层，混用能兼顾语义与几何。树、图和元素 ID 要对应同一次观察，动态加载、弹窗遮挡这些场景都要进评测。"
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

我会混合四路信号：截图、DOM 或无障碍信息（a11y）树、结构化元素信息、动作历史。截图看得到视觉状态，但定位不稳、token 成本高；DOM 便宜好检索，却会漏掉 canvas、图标和弹层。混起来能兼顾语义和几何，前提是树、图和元素 ID 对应的是同一次观察。

比如页面上弹出一个 cookie 同意框，正好挡住「提交」按钮。DOM 树里提交按钮好好的，模型照着点，点到的是弹层，截图里却看得见遮挡。反过来，一个只有图标、没有文字的按钮，在截图里模型未必认得出，a11y 树里却可能写着它的角色和名字。所以观测结果（observation）别理解成「把网页塞进上下文」。SeeClick 一类工作说明视觉 grounding 要单独训，不能假设模型看着截图自己就会找按钮。定位怎么融合，见 `cu-dom-a11y-visual-grounding`。

## 表征权衡：成本、可定位、动态一致性

四路信号各管一块。截图跨站点泛化强，能看见 CSS 绘制、遮挡、弹窗，但坐标会随分辨率和设备像素比（DPR）漂，整屏的视觉 token 也贵。DOM / a11y 树里的角色、名字、`disabled`、层次都便宜、可检索，可虚拟列表、iframe、自定义绘制经常缺节点，或者目标框为 0。结构化元数据包括稳定的 element id、可见 bbox、可聚焦性、当前 URL / frame；id 要是每次重绘都变，action grounding 就会漂。动作历史记的是上次点了什么、滚了多少，没有它，模型看不到自己造成的状态差。

工程上，element id 要在同一次观察内稳定，或者改用角色 + 名字 + 相对几何来指认，别用「第 17 个 div」这种说法。动态加载时 observation 要带上「仍在加载」的标记，否则模型会在空白树上瞎点。预算上，对树做可见节点过滤，对截图做局部裁剪，别把整棵 HTML 和 4K 图都喂进去，那会把长上下文问题伪装成 Agent 能力问题。观测还要能回放，存截图哈希、树序列化、id 映射和动作，不然失败了只能说一句「模型不会用浏览器」。训练时 environment observation 不进 policy 损失（loss）：视觉 encoder 冻结时，图只是 $s_t$；端到端训，也只在策略 token 上反传，别对 DOM 文本算语言模型似然。

## 评测要覆盖单模态会翻车的场景

评测别只测静态桌面点选，至少要有动态加载、弹窗挡点击、要 scroll 才出现的目标、纯视觉信息（图标无文本）、a11y 树缺失或滞后、Retina 坐标翻倍、iframe 偏移。这些正是 `cu-failure-taxonomy` 里 grounding 层失败的来源。报告也要拆开：树能不能召回目标、视觉点有没有命中、冲突时有没有换通道，一个端到端成功率看不出这些。

## 追问

**为什么不把整页 HTML 当 observation？**
Token 会爆炸，而且大量节点不可见，模型会去拟合标记顺序，学不到可见的 UI。先过滤可见 / 可聚焦节点，再按需截图确认。

**Set-of-Mark 编号每次都变怎么办？**
编号只是当步观察的局部坐标，别跨步当稳定 id。下一步要按新树重新标，否则会点到别的元素。

**Observation 要不要进监督微调（SFT）的 loss？**
不要当目标 token，它是状态，不属于策略输出。对它算交叉熵损失（CE），等于让模型背页面。

**和 computer-use 定位那题是什么关系？**
这题管 $s_t$ 怎么表示，`cu-dom-a11y-visual-grounding` 管树和视觉怎么融合成点击点。观测不稳定，融合管道就没法评。
