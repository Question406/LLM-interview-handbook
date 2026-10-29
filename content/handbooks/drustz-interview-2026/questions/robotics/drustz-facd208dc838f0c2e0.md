---
id: drustz-facd208dc838f0c2e0
section: robotics
order: 27
level: A
title: 03 · Robot Learning 一天速成（写给 LLM post-training 背景的你） · 附：最后一晚补课清单（来自定位建议）
quick: >-
  作者文档章节 · 03 · Robot Learning 一天速成（写给 LLM post-training 背景的你） ·
  附：最后一晚补课清单（来自定位建议）
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/03_robot_learning_crash_course.md
    type: primary
---
## 附：最后一晚补课清单（来自定位建议）

1. **切入点选 post-training/RL**：RECAP → SimpleVLA-RL → LWD 这条线的方法论直接搬 LLM RL 骨架（advantage conditioning ≈ conditional SFT/RCSL、GRPO 变体、offline-to-online）。懂 RLHF 工程化的人在机器人公司是稀缺物种。
2. **第二切入点是 evaluation**：全行业没人满意现状，懂统计功效、A/B 基建、benchmark 设计的人可以直接建立话语权。
3. **常识底线名词**（能一句话解释即可，不会被深挖）：
   - **PD control**: "A feedback controller that corrects error proportionally to its magnitude and its rate of change—the workhorse of low-level joint control."
   - **MPC (model predictive control)**: "Replan a short-horizon optimal trajectory at every timestep using a dynamics model, execute the first action, repeat."
   - **Inverse kinematics**: "Solving for the joint angles that put the end-effector at a desired pose—the inverse of the forward geometry."
   - 「数据比算法值钱」的行业文化——面试里表现出你理解这一点。
4. 若有半天空档：跑一次 LeRobot/SmolVLA 或 openpi 的上手教程，面试里能说 "I've run openpi locally" 价值很大。

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/03_robot_learning_crash_course.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/03_robot_learning_crash_course.md)。作者整理资料；许可和第三方来源范围见阅读指南。
