---
id: drustz-0c3a500000ece351ce
section: robotics
order: 3
level: A
title: 01 — The Bot Company 公司情报（Company Brief） · TL;DR — 只有 20 分钟就看这段
quick: 作者文档章节 · 01 — The Bot Company 公司情报（Company Brief） · TL;DR — 只有 20 分钟就看这段
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/01_company_brief.md
    type: primary
---
## TL;DR — 只有 20 分钟就看这段

1. **一句话**：The Bot Company（bot.co，下称 Botco）在做「a helpful robot for every home」——**非人形、轮式/履带底盘 + 机械臂**的家用机器人，至今 **0 产品、0 收入、0 公开 demo**，估值 **&#36;4B+**（⚠️ 最后一轮 close 未见正式 PR）。
2. **三个数字**：累计融资 **~$552M**（$150M@$550M → $150M@$2B Greenoaks → $250M@&#36;4B+ Eclipse）；团队 **~79–94 人**（目标永远 <100 人、95% 工程师）；在招 **9 个岗位**，全部 SF onsite，&#36;200K–&#36;350K。
3. **创始人**：Kyle Vogt（CEO，Twitch + Cruise 创始人，2023/11 因 Cruise 拖行事故后离职）；Paril Jain（CTO，Tesla FSD **Planning, Imitation Learning & RL** tech lead）；Luke Holoubek（前 Cruise 工程师）。
4. **技术路线（有证据）**：端到端神经网络 + imitation learning，抛弃经典 CV/规划栈；**明确拒绝入户 teleoperation**（隐私 + 不可扩展）；靠 in-home 部署 + fleet learning + OTA 回灌数据——Cruise/Tesla 的 fleet 思路直接移植。
5. **三层技术栈（JD 确证）**：VLA 式 **Multimodal Foundation Models**（text/image/video/kinematics 统一，含 post-training/RL）+ **World Models**（视频生成神经模拟器）+ **Whole-Body Control**（sim-to-real RL）。
6. **你面的 "MLO" 岗**：公开 JD 里**不存在**这个名字（⚠️ 内部叫法/未公开岗）。最对口的公开 JD = **Multimodal Foundation Models**（唯一写明 post-training 的岗）+ **ML Infra - Data Infrastructure**。备考按这两份 JD 的并集准备。
7. **产品哲学**：捆绑「一千件小事」（捡玩具、收包裹、清桌面，容错 90–99%），刻意回避洗碗/洗衣等高风险任务；"Most robots will be specialized, not humanoids"。
8. **数据侧的现实**（对 data collection 方向最重要）：加州合同工集体诉讼（2026-06 获集体地位，估计 "hundreds of employees"）+ Airbnb 秘密测试事件（~6 英尺原型、30+ 人轮班）⚠️ 强烈暗示存在**大规模线下人工数据采集/演示 operator 队伍**——「不做 teleop」指的是不进用户家，不等于不用人类演示数据。
9. **文化关键词**（JD 原文）：extreme sharpness、mental acuity、engineering curiosity、high performance mindset；全员 IC、radical ownership、「工程师离可部署机器人不超过 10 英尺」。
10. **面试策略一句话**：把自己讲成「能 own 整条 data → post-training → eval 链路的人」，用 LLM post-training 经验类比到 VLA，主动谈 data engine 和 fleet learning——这正好打在他们 JD 的 "Own the Training Loop End-to-End" 上。
11. **别主动提**：Cruise 拖行事故细节、Airbnb 诉讼、合同工诉讼——知道即可，问到再得体回应。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/01_company_brief.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/01_company_brief.md)。作者整理资料；许可和第三方来源范围见阅读指南。
