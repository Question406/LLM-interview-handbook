---
id: dt-webarena-traj
section: labs
order: 38
level: A
title: WebArena：812 道网页任务，动作序列对了就能进 SFT 吗？
quick: "看最终功能断言是否通过，并检查过程有没有不该做的操作，不要求逐次点击与人类完全一致。失败回放可作为负例或恢复训练材料，不能直接当成功示范。产品数据来源使用 Applebot 和许可集，不能默认回灌用户浏览历史。"
companies:
  - apple
tags:
  - WebArena
  - Agent
  - Tool Use
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "WebArena: A Realistic Web Environment for Building Autonomous Agents"
    url: https://arxiv.org/abs/2307.13854
    type: primary
  - title: "OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks"
    url: https://arxiv.org/abs/2404.07972
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

网页 observation 作为上下文，训练 loss 只计算助手动作，不把 HTML 全文作为交叉熵目标。每一步动作要对应当时的 DOM 或无障碍树，不能基于过期画面。最后用环境断言判断任务完成，不能只相信模型的完成声明。人轨迹优先；失败回放标成被放弃的尝试或负例，见 `dt-swe-success-noise`。同一任务可以有多条合法路径，因此逐字比较动作序列不能判断任务是否正确。功能对了、点过无关页：终局可以过；多余写操作要看是否改了不该改的状态；只读闲逛当噪声，不一定当失败。训练用的实例要和门禁模板去重，见 `dt-contamination`。

不这么选的理由：把 agent 失败回放当 监督微调（SFT），或要求模型复现某一次点击顺序。`dt-gui-traj` 是桌面 / 手机（截图加无障碍树，点偏了就脏）。这张卡是浏览器：DOM / 无障碍信息 树加功能断言。

接到苹果：Safari / 邮件摘要在 AFM 是闭集工具加许可页，不是把用户浏览历史回灌，见 `dt-userlog-contrast`。研究环境可以自托管；产品通道仍是 Applebot 和许可集。纯文本站点只要 a11y 够用；图标按钮、验证码、视觉货架要图，见 `dt-gui-traj`、`dt-multimodal-data`。

公开锚点：WebArena 真实网站镜像，812 道长程任务；人大约 78.24%，当时最好的 GPT-4 agent 大约 14.41%。他们还放了 179 道题的人轨迹（Playwright trace）。

## 追问

- **功能对了、点过无关页？** 终局可以过。训练上多余写操作要看是否改了不该改的状态。只读闲逛，我当噪声，不一定当失败。
- **模板题会不会背？** 会。WebArena 题从模板实例化。训练用的实例要和门禁模板去重，见 `dt-contamination`。
- **只要 a11y、不要截图？** 纯文本站点够用。图标按钮、验证码、视觉货架要图，见 `dt-gui-traj`、`dt-multimodal-data`。
