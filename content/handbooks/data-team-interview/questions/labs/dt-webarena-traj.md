---
id: dt-webarena-traj
section: labs
order: 38
level: A
title: WebArena：812 道网页任务，动作序列对了就能进 SFT 吗？
quick: >-
  不能。同一任务有多条合法路径，判断标准是最终功能 assertion 是否通过，再查过程中有没有改了不该改的状态，逐次点击不必和人类一致。失败 replay
  可作负例或恢复材料，不能直接当成功示范。训练实例还要和评测模板 deduplication。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'WebArena: A Realistic Web Environment for Building Autonomous Agents'
    url: 'https://arxiv.org/abs/2307.13854'
    type: primary
  - title: 'OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks'
    url: 'https://arxiv.org/abs/2404.07972'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

不能。动作序列对上某一次人类点击，既不必要也不充分：同一任务可以有多条合法路径，逐个比较动作判断不了任务有没有完成。进 SFT 的标准是环境里的功能 assertion 通过，同时过程中没有改动不该改的状态。

比如一个「把某件商品加进购物车」的任务，人类是先搜索再点进商品页，模型是从分类页一路点进去，两条路都对。要求复现人类那一次的点击顺序，模型这条就被判错了。反过来，模型自己说「我完成了」也不算数，最终要由环境 assertion 来判断。

WebArena 用的是真实网站的镜像，共 812 道长程任务；人类成功率大约 78.24%，当时最好的 GPT-4 agent 大约 14.41%。他们还放出了 179 道题的人类 trajectories（Playwright trace）。模型和人类差距这么大，失败 replay 直接拿去做 SFT，就是在教失败行为。

筛的时候，每一步动作先对上当时的 DOM 或无障碍树，基于过期画面的动作不要。网页 observation 当上下文，训练 loss 只计算助手动作，HTML 全文不做 cross-entropy 目标。终局看环境 assertion。过程上，功能对了但点过无关页，终局可以算过；多余的写操作要看有没有改了不该改的状态；只读的闲逛当噪声，不一定算失败。来源上人类 trajectories 优先。

## 追问

**失败 replay 就完全没用了吗？**
有用，标成被放弃的尝试或负例，可以当恢复材料，只是不能当成功示范，见 `dt-swe-success-noise`。

**训练实例会不会和评测撞？**
会。WebArena 的题由模板实例化，模型会背模板，训练用的实例要和 evaluation gate 模板 deduplication，见 `dt-contamination`。

**这和 GUI trajectories 那题有什么区别？**
`dt-gui-traj` 讲的是桌面和手机，截图加无障碍树，点偏了就脏；这张卡讲浏览器，DOM 和无障碍树，加功能 assertion。

**只要无障碍树、不要截图行不行？**
纯文本站点够用；图标按钮、验证码、视觉货架就需要图，见 `dt-gui-traj`、`dt-multimodal-data`。
