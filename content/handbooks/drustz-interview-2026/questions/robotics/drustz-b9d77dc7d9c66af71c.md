---
id: drustz-b9d77dc7d9c66af71c
section: robotics
order: 63
level: A
title: 07 — 高概率题库与答案要点（Question Bank） · ⑦ Research 品味讨论（5 题）
quick: 作者文档章节 · 07 — 高概率题库与答案要点（Question Bank） · ⑦ Research 品味讨论（5 题）
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Robotics · Data、Learning 与 System Design
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/07_question_bank.md
    type: primary
---
## ⑦ Research 品味讨论（5 题）

> 考察点：engineering curiosity + 有立场的推理。结构：定义 → 论点 2–3 个 → 立场 → 主动给反方。**不要背结论，背论证。**

### ★ Q48. "What do you think is missing for home robots to have their GPT-3 moment?"（用户点名题）

- 先定义再答："Let me define the analogy: a GPT-3 moment means one generic pretrained model that handles unseen tasks with a tiny prompt or finetune — economically useful without per-task engineering. Robotics today is more like GPT-1: general within a lab, not general across homes."
- "**Missing piece one: the internet of robot data doesn't exist.** Text got trillions of tokens for free; robotics is hand-stitching a pyramid of teleop, human video, and sim — π0-class models train on the order of 10k hours. The data gap is many orders of magnitude."
- "**Missing piece two: evaluation.** There's no cheap, reproducible perplexity-equivalent. You can't run a scaling-law era without a measurement instrument — real-robot evals are expensive, high-variance, and unreproducible. I'd argue this is the most under-invested piece."
- "**Missing piece three: the error-tolerance asymmetry.** A bad text completion costs a re-prompt; a bad grasp costs a broken glass or worse. That caps how much autonomy you can deploy, which caps how fast the data flywheel spins."
- 表立场（顺便贴公司论点）："My bet: the unlock is **fleet-scale corrections** — deployment itself generating the data text got for free. Which is why starting with low-risk, high-tolerance tasks to get robots into homes early is, I think, the right wedge."（公司先做容错 90–99% 任务的路线，01 §4a）
- 主动给反方："The counter-argument: there may be no single 'moment' at all — capability might arrive tier by tier, because physical risk gates deployment per task class. I'd put maybe 40% on that world."

### ★ Q49. "We explicitly don't do in-home teleoperation. Do you agree with that call? How would you get correction data without it?"

- 先 steelman："I think it's the right product call, and I'd steelman it on both grounds: **privacy** — a stranger literally looking into your home is a trust-killer — and **unit economics** — an operator-hour per robot-hour doesn't amortize at fleet scale."（公司立场是事实，01 §4a；两条理由是他们公开说法）
- 再说代价，显示不是拍马屁："But let's be honest about the cost: you're giving up the richest label source in robot learning — on-policy interventions, the RLHF-equivalent. So the training loop has to replace that signal, not just skip it."
- 替代方案给一串："One: lightweight user feedback — a voice 'no, not that one', an app thumbs-down, physically nudging the robot — sparse but it scales with the fleet. Two: self-supervised success detection plus autonomous retry, so failures label themselves. Three: **offline RL on fleet logs** — RECAP-style, where failed episodes still teach. Four: replicate top fleet-failure clusters in sim for targeted practice."
- "Five: correction-grade teleop still happens — just in consented, staged environments, operated by staff, before deployment. My read is that's how they square the circle, given reports of a large contractor workforce doing collection."（后半句是推断——staged 采集属合理推测但未证实，口头要带 "my read is"）
- 收尾表忠诚但留脑子："So: agree with the constraint, and I find it generative — it forces the harder, more scalable version of the data engine. That's the problem I want to work on."

### Q50. "Will the home robot be one end-to-end model, or a modular stack?"
→ 立场题：公司押端到端（01 §4a），但答题别无脑站队——用 03 §3 双系统讲「end-to-end 学习 + 结构化延迟分层」不矛盾；safety layer 永远在学习模型外（06 万能原则）。

### Q51. "Humanoids are raising billions. This company went non-humanoid. Who's right?"
→ 01 §1：他们的原型是轮/履底盘+机械臂（Reuters/诉讼证实）。论证框架：form factor 应由任务分布+成本+可靠性反推，家庭地面多数任务不需要双足；反方（人形通吃人类环境+数据可迁移）也要说到。

### Q52. "What recent robotics result excited you most? Why?"
→ 03 §1 挑一个讲深：推荐 RECAP/π*0.6（贴自己 RL 背景，能讲 offline-to-online 细节）或 Helix 02 的 8 小时自主班次；讲「为什么它改变了我对瓶颈的判断」而不是复述摘要。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/07_question_bank.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/07_question_bank.md)。作者整理资料；许可和第三方来源范围见阅读指南。
