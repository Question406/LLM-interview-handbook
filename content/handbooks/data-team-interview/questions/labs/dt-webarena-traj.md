---
id: dt-webarena-traj
section: labs
order: 38
level: A
title: WebArena：812 道网页任务，动作序列对了就能进 SFT 吗？
quick: "不能。同一任务有多条合法路径，判断标准是最终功能断言是否通过，再查过程中有没有改了不该改的状态；逐次点击不必和人类一致。失败回放可作负例或恢复材料，不能直接当成功示范。训练实例还要和评测模板去重。"
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

不能。动作序列对上某一次人类点击，既不必要也不充分：同一任务可以有多条合法路径，逐字比较动作判断不了任务是否完成。进 SFT 的标准应该是环境里的功能断言通过，同时过程中没有改动不该改的状态。

## 为什么这样判

WebArena 用的是真实网站的镜像，共 812 道长程任务；人类成功率大约 78.24%，当时最好的 GPT-4 agent 大约 14.41%。他们还放出了 179 道题的人类轨迹（Playwright trace）。模型轨迹和人类轨迹差距这么大，失败回放如果直接拿去做监督微调（SFT），就是在教失败行为；要求模型复现某一次点击顺序，又会把合法的其他路径判成错。

模型自己说「我完成了」也不算数，最终要由环境断言来判断。

## 怎么筛

1. 对齐观察：每一步动作要对应当时的 DOM 或无障碍树，不能基于过期画面。
2. 定 loss：网页 observation 作为上下文，训练 loss 只计算助手动作，不把 HTML 全文作为交叉熵目标。
3. 终局用断言：环境断言通过才算完成。
4. 看过程：功能对了但点过无关页，终局可以算过；多余的写操作要看有没有改了不该改的状态；只读的闲逛当噪声，不一定算失败。
5. 定来源：人类轨迹优先；失败回放标成被放弃的尝试或负例，见 `dt-swe-success-noise`。
6. 去重：WebArena 的题由模板实例化，模型会背模板，训练用的实例要和门禁模板去重，见 `dt-contamination`。

`dt-gui-traj` 讲的是桌面和手机（截图加无障碍树，点偏了就脏），这张卡讲浏览器：DOM 和无障碍树，加功能断言。

## 追问

- **只要无障碍树、不要截图行不行？** 纯文本站点够用；图标按钮、验证码、视觉货架就需要图，见 `dt-gui-traj`、`dt-multimodal-data`。
