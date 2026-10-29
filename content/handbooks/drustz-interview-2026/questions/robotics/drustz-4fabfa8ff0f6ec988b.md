---
id: drustz-4fabfa8ff0f6ec988b
section: robotics
order: 66
level: A
title: 08 · 个人故事与提问清单（Stories & Asks） · TL;DR — 只有 20 分钟就看这段
quick: 作者文档章节 · 08 · 个人故事与提问清单（Stories & Asks） · TL;DR — 只有 20 分钟就看这段
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/08_stories_and_asks.md
    type: primary
---
> 下文的个人经历、时间安排与复习状态属于原作者 DrustZ；可用作组织自己材料的参考。

## TL;DR — 只有 20 分钟就看这段

1. **一句话定位**：*"I've owned the exact loop they're hiring for — data mixtures, RL post-training, eval — just on LLM agents instead of robots. Robot learning is adopting the LLM playbook, and I bring the playbook."*
2. **自我介绍严格 60–90 秒**（你在 Decagon 讲了 11 分钟被打断——这次开场就说 "I'll do 60 seconds, we can go deep later"）。逐字稿见 §1。
3. **主打故事只有一个**：Reflection 的 RL 数据难度筛选（S1）——「以为是质量问题→被数据证伪→改成在线难度探测→12% 算力花在筛选上→能说出自己方案的失效条件」。这正中 JD 原话 *"diagnosing failure modes, improving data mixtures"*。
4. **第二故事**：Anthropic take-home 的 grader vs ROUGE（S3）——全数字可公开（AUROC 0.569 vs 0.838），对口 robotics 公认未解的 evaluation 难题。
5. **失误故事必备**（S5，Decagon 项目）：指标与天花板一位不差→逐字复现训练目标→教训「指标好得反常先看原始输出」。真实、有数字、有后续断言化动作。
6. **弱点预案核心句**：*"What's not missing is the training loop; what's missing is physical intuition — and I've closed a similar gap before at Meta Reality Labs, working one layer above raw EMG sensors."*
7. **Why Bot Company 三条**：HCI PhD → 家用机器人是 HRI 终极场景；no-teleop 立场逼出真正的 fleet data engine（正是你的专长的 hard mode）；<100 人全 IC、飞轮最早期 = 你这种「数据→模型改进」角色杠杆最大。
8. **反问的总原则**：每个问题都应暴露你已经想过 data engine / eval / product cadence 的具体细节，而不是要信息。最强的一问：*"Given you've ruled out in-home teleop, what does the intervention signal look like — and who closes the loop on a failure clip today?"*
9. **地雷**：别提 Airbnb 诉讼和合同工集体诉讼；别逼问产品形态（stealth）；别问 remote（全员 SF onsite）；Reflection 细节讲方法不讲绝对数字。
10. **每轮都是生死轮**（单轮否决制，见 02）——所以 S1 + 弱点预案 + founder 轮的 Why 必须练到脱口而出，其余按需调用。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/08_stories_and_asks.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/08_stories_and_asks.md)。作者整理资料；许可和第三方来源范围见阅读指南。
