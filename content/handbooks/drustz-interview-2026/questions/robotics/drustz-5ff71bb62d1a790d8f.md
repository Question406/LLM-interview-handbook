---
id: drustz-5ff71bb62d1a790d8f
section: robotics
order: 22
level: A
title: >-
  03 · Robot Learning 一天速成（写给 LLM post-training 背景的你） · §2. Robot Post-Training
  全流程（逐段对照你的技能栈）
quick: >-
  作者文档章节 · 03 · Robot Learning 一天速成（写给 LLM post-training 背景的你） · §2. Robot
  Post-Training 全流程（逐段对照你的技能栈）
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
## §2. Robot Post-Training 全流程（逐段对照你的技能栈）

这是你面试的主战场。每个 stage 都按「LLM 里你怎么做 → 机器人里怎么做 → 差异在哪」展开。

### Stage 0 — Base model：拿 VLM 白嫖 web 知识

拿现成 VLM（PaliGemma、Qwen-VL、Cosmos-Reason）当起点。语义理解、OCR、常识空间关系全部免费继承——这就是为什么 VLA 能听懂 "put the coke can next to the apple" 而不需要机器人数据里出现过可乐罐。

> "The VLM backbone gives you web-scale semantics for free—the robot data only needs to teach the model how to move, not what things are."

### Stage 1 — Robot pre-training ≈ continued pretraining / mid-training

在跨本体大杂烩（OXE + 自采 + 人类视频 + 仿真）上训练动作预测。π0 配方约 1 万小时多样数据。**关键工程点：与 web VQA 数据 co-training 防止 VLM 能力灾难性遗忘**（π0.5 明确这么做）——就是你熟悉的 replay/data mixing，配方思路完全同构。

> "Cross-embodiment pre-training is like multilingual pretraining—each robot body is a 'language,' and you co-train with web VQA data to prevent catastrophic forgetting of the VLM's semantic abilities."

### Stage 2 — SFT = Behavior Cloning on demonstrations

**术语排雷**：机器人圈把这一步叫 "post-training" 或 "fine-tuning"，本质就是 SFT——在目标任务的高质量遥操作演示上做监督学习，目标是 next-action-chunk prediction。

和 LLM 相同的规律：**数据质量 >> 数量**。演示的一致性、operator 的操作水平直接决定策略上限；50–100 条演示即可完成任务适配（Gemini On-Device 的卖点，对应你熟悉的少样本 LoRA 适配）。

**BC 特有的病：compounding error / distribution shift**。策略执行时一旦有小偏差，就进入演示里没见过的状态，在 OOD 状态下犯更大的错，错误滚雪球。这是 exposure bias 的物理放大版——LLM 里跑偏了大不了生成一段烂文本，机器人跑偏了会把杯子扫到地上，而且回不去了。

缓解手段（按面试出现频率）：
1. **DAgger**：策略上线跑，专家对它到达的（偏离）状态标注正确动作，加回训练集迭代——本质是 iterated SFT on the policy's own failure states。
2. **Action chunking**：减少决策次数，误差累积更慢（见 §3）。
3. **根治方案：RL**（见 Stage 3）。

> "Behavior cloning's fundamental failure mode is compounding error: one small deviation puts the policy in a state the demos never covered, and errors snowball—it's exposure bias, except the consequences are physical and irreversible. DAgger mitigates it by iteratively collecting expert labels on the states the policy actually visits."

### Stage 3 — RL fine-tuning：2026 年的最热战场

**Sim RL**：locomotion 的标准答案。Isaac Gym 万级并行环境 + PPO，几小时训出四足/人形行走；用「特权信息 teacher → 视觉 student」distillation后 sim2real 直接部署。**但 manipulation 在仿真里做 RL 再迁移仍不可靠**（原因见 §4）。

**Offline RL**：CQL/IQL/AWAC 一脉，在固定数据集上学超越演示者的策略；痛点是out-of-distribution动作的价值高估——**reward hacking 的离线版**。

**RLPD**（RL with Prior Data）：真机 RL 的实用配方——SAC + 每个 batch 一半采 offline demos、一半采 online 经验，样本效率高到真机上一两小时学会插接件。衍生的 **HIL-SERL** 加人类实时接管纠正，真机成功率能推到 ~100%。

**Residual RL**：冻结 BC 基座，RL 只学修正量 delta——安全稳定，2026 年还被用来给 VLA 自产训练数据。

**真机 RL 四大难（必背，面试大概率追问）**：
1. **Reset**：谁把杯子放回去？需要人力或 reset-free RL。
2. **Reward**：没有 verifiable reward；VLM-as-judge 判成功正在兴起（≈ RLAIF）。
3. **安全探索**：随机动作会砸东西，探索必须受限。
4. **样本贵 + 环境非平稳**：物体磨损、光照变化，环境自己在漂移。

> "Real-robot RL has four hard problems that don't exist in LLM RL: resets require physical labor, rewards aren't verifiable so people are turning to VLM-as-judge, exploration has to be safe because random actions break things, and samples are expensive in a non-stationary environment."

**2026 前沿（点名即可加分）**：
- **RECAP / π\*0.6**：advantage-conditioned offline RL，统一吸收演示、人类纠正、自主经验三种数据，真机throughput翻倍。方法论上 ≈ conditional SFT / RCSL（advantage conditioning），你可以直接对上。
- **π0.7**：把 RL 特调专家的经验数据回灌通才模型——RL 产出的数据成为下一代通才的语料。
- **SimpleVLA-RL**（ICLR 2026）：GRPO 式 online RL 直接调 VLA。
- **ReinFlow / πRL**：穿透 flow matching 策略做 RL 的技术路线（flow 策略的 log-prob 不好算，是技术难点）。
- **LWD**：fleet-scale offline-to-online——整个机器人车队的 rollout + 人类干预进共享 replay buffer，训完重新下发。机器人版「从生产流量持续学习」。

### Stage 4 — RLHF 的类比：Intervention 取代 Preference

机器人领域**最主流的人类反馈不是 pairwise preference，而是「接管纠正」(intervention/correction)**：操作员看策略跑偏就抢过手柄。接管这个动作本身 = 天然负信号 + 正确示范，一石二鸟（HG-DAgger、RLIF、HIL-SERL、RECAP 全走这条路）。

为什么？机器人失败肉眼可见、纠正即演示，比让人对比两段视频高效得多。纯 preference 路线存在但小众：老一代 PEBBLE/T-REX，新一代 **GRAPE**（对 VLA 轨迹做 DPO 式 trajectory preference optimization）。

**RM 的对应物**：学到的 value function / success classifier + 新兴的 VLM-as-reward-judge。

> "In robotics, RLHF becomes 'RL from human takeover': instead of ranking two trajectories, an operator intervenes when the policy drifts, and that intervention gives you both a failure label and a corrective demonstration in one shot—strictly more information per unit of human time."

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/03_robot_learning_crash_course.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/03_robot_learning_crash_course.md)。作者整理资料；许可和第三方来源范围见阅读指南。
