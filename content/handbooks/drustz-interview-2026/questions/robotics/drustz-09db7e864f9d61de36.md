---
id: drustz-09db7e864f9d61de36
section: robotics
order: 12
level: A
title: '02 — 轮次形式与情报（The Bot Company Onsite, 13:00–17:00） · TL;DR — 只有 20 分钟就看这段'
quick: >-
  作者文档章节 · 02 — 轮次形式与情报（The Bot Company Onsite, 13:00–17:00） · TL;DR — 只有 20
  分钟就看这段
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/02_interview_rounds_intel.md
    type: primary
---
## TL;DR — 只有 20 分钟就看这段

1. **公开面经 = 零。** Glassdoor / Blind / Reddit / 一亩三分地 / X 全部交叉搜过，没有任何一篇 The Bot Company 面经。别再去搜了，时间花在下面的推断和练习上。
2. 但 JD 里有罕见的官方剧透："Throughout the process, we expect candidates to demonstrate: exceptional mental acuity / engineering curiosity / high performance mindset" —— **考快速思考、跨域推理、高压表现，不考背题**。预期节奏快、追问密、可能故意丢不熟悉领域的问题。
3. 最可能配置（概率 ~50%）：**实战 ML coding/debug（60–75min）→ 项目 deep-dive（60–75min）→ founder/开放设计（30–60min）**。4 小时 2–3 轮 ⇒ 每轮 60–90 分钟，全是深挖式；「常提前结束」最合理解释是**单轮否决制**（推断）——每一轮都是生死轮。
4. 面试官母体 = Cruise + Tesla 系。他们会用 **Tesla data engine 思维**（数据闭环、corner case 挖掘、eval 驱动迭代）审你的 post-training 经历。CTO Paril Jain 招聘推文单独点名 "scaling models **and evals**" —— **eval 方法论几乎必考**。
5. 同类公司（Skild）的评价哲学："**Hand-wave and you're done**"。说 domain randomization 会被追问随机化了哪些参数、什么范围。每个论断都要能落到参数、数字、具体实验。
6. 三大备战优先级：① 最硬的 post-training 项目按「failure mode → 诊断手段 → data/eval 改动 → 量化增益」四段式打磨到能被追问 30 分钟；② PyTorch 训练循环 debug + 向量化数值题（Skild 样题 + 手写 attention）；③ 一套「家用机器人 post-training 数据引擎 + eval 体系」开放设计答案。
7. Culture/founder 轮的正确姿势：聊 **high agency、IC ownership、in-person、愿意下场碰硬件**；**绝对不要聊晋升/带人/管理轨道**（公司明文 "Everyone is an IC"，Vogt 公开反层级）。
8. 「为什么是家用机器人、为什么是现在」要有真诚答案——Vogt 明言不卖公司、要长期做，founder 轮会测使命认同。
9. 判别信号：**如果 recruiter 提前让你准备任何材料（slides），Tesla 式 presentation 情景立刻升为第一**，当晚就做 30 分钟 slides。
10. 当天节奏：12:15 前吃完轻午餐 + 咖啡因，每轮间隙 2 分钟重置（水 + 深呼吸 + 翻一眼 cheat sheet），把「提前结束」当中性信号处理，最后一轮（16:00+）血糖低谷靠 snack 顶住。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/02_interview_rounds_intel.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/02_interview_rounds_intel.md)。作者整理资料；许可和第三方来源范围见阅读指南。
