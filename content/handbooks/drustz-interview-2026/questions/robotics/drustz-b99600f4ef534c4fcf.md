---
id: drustz-b99600f4ef534c4fcf
section: robotics
order: 19
level: A
title: 03 · Robot Learning 一天速成（写给 LLM post-training 背景的你） · TL;DR — 只有 20 分钟就看这段
quick: >-
  作者文档章节 · 03 · Robot Learning 一天速成（写给 LLM post-training 背景的你） · TL;DR — 只有 20
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/03_robot_learning_crash_course.md
    type: primary
---
## TL;DR — 只有 20 分钟就看这段

1. **一句话总纲**：过去三年 robot learning 完成了「LLM 化」——VLA (vision-language-action) 模型 = 拿 VLM 当 base model，把机器人动作当一种新输出模态，走 pretrain → SFT → RL 的 post-training 流水线。你的技能栈迁移度极高。
2. **三个关键差异**：(a) 没有「机器人的互联网」，数据要自己采，数据工程 > 算法；(b) 动作是连续、高频（20–50Hz+）、有物理后果的，延迟和安全是一等公民；(c) 评估没有 ground truth 文件，每次 eval 都是一次物理实验。
3. **术语翻译**：机器人圈说的 "post-training / fine-tuning" ≈ 你的 SFT；behavior cloning (BC) = 在遥操作演示上做 supervised fine-tuning；compounding error = exposure bias 的物理放大版。
4. **动作表示三条路**：离散 token（RT-2/OpenVLA，慢且量化伤精度）→ diffusion policy（表达多模态动作分布）→ **flow matching**（π0 路线，当前一线主流）。Action chunking = 一次预测未来 50–100 步，类比多 token 预测。
5. **延迟矛盾的标准解**：双系统/分层架构——大 VLM 低频出语义（7–9Hz），小策略高频出动作（200Hz+），Figure Helix 02 甚至有 1000Hz 的 System 0。
6. **RL fine-tuning 是 2026 最热战场**：真机 RL 的里程碑是 π*0.6/RECAP（advantage-conditioned offline RL，throughput翻倍）；机器人版 RLHF 不是 pairwise preference，而是**人类接管纠正 (intervention/correction)**。
7. **Evaluation 是全行业公认未解难题**：一次 rollout 数分钟 + 人工 reset，方差大、不可复现，且 **validation action MSE 与真机成功率脱钩**（没有 validation loss 可看）——这是 LLM 人最不适应的一点，也是你最能建立话语权的地方。
8. **当前第一梯队**：Physical Intelligence（π0→π0.7，领域的 OpenAI）、Figure Helix、NVIDIA GR00T、Google DeepMind Gemini Robotics。格局分「robot brain 实验室」vs「机器人 OEM」两条线。
9. **面试定位**：把自己卖成「post-training + evaluation 的人」，这两块 2026 年刚起爆、方法论未收敛、恰好是你的主场。
10. **一句英文总纲（开场可用）**："Robot learning has converged on the LLM recipe—a VLM backbone, behavior cloning as SFT, and RL fine-tuning on top—but the bottlenecks are different: data has to be collected physically, inference runs under hard real-time constraints, and every evaluation is a physical experiment."

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/03_robot_learning_crash_course.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/03_robot_learning_crash_course.md)。作者整理资料；许可和第三方来源范围见阅读指南。
