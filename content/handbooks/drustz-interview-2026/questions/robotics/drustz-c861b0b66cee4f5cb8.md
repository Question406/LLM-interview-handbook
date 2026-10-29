---
id: drustz-c861b0b66cee4f5cb8
section: robotics
order: 15
level: A
title: '02 — 轮次形式与情报（The Bot Company Onsite, 13:00–17:00） · 3. 五种轮型的应对策略'
quick: '作者文档章节 · 02 — 轮次形式与情报（The Bot Company Onsite, 13:00–17:00） · 3. 五种轮型的应对策略'
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
## 3. 五种轮型的应对策略

### 3.1 Technical deep-dive（项目盘问）— 权重最高，必然出现

**风格预判：** Cruise/Tesla 系面试官 = "hand-wave and you're done" 文化（Skild 同款）。他们不听叙事听参数：每个决策都会被追问「为什么不是另一个方案」「数字是多少」「怎么知道是这个原因」。

**准备动作：** 把你最硬的 post-training 项目重构成四段式，每一段都能独立扛 5–10 分钟追问：

1. **Failure mode**：模型/系统具体怎么坏的（不是「效果不好」，是「在 X 类输入上出现 Y 行为，占比 Z%」）。
2. **诊断手段**：你看了什么（loss 曲线分段？per-slice eval？logit/entropy 分布？rollout 逐条读？），怎么排除了其他假设。
3. **改动**：data mixture 怎么调（比例、来源、过滤规则）/ eval 怎么收紧（新增什么 slice、什么 held-out）/ 训练配方改了什么（LR、KL 系数、reward shaping）。
4. **量化增益**：改前改后数字，以及**哪些没修好**——主动交代残留问题是高级信号。

**面试时怎么说（转折句示范）：**

> "Let me give you the concrete version. The failure mode was X — I can quantify it: about N% of eval rollouts showed this pattern. My first hypothesis was A, but the per-slice breakdown ruled that out because Z. What actually fixed it was changing the data mixture from P to Q, which moved the metric from M1 to M2. What it did NOT fix — and I want to be upfront about this — is Y, which I believe needs a different intervention."

**关键姿态：** 被问到不知道的数字时，不要糊弄。说 "I don't remember the exact number, but it was on the order of X, and here's how I'd verify" —— mental acuity 考的是推理透明度，不是记忆力。

**跨域追问预案：** 他们明文说会 "reason across unfamiliar domains"。你没有机器人经验，大概率会被问「你的 LLM post-training 经验怎么迁移到 robot policy」。提前想好映射：SFT ↔ behavior cloning；RLHF/RLVR ↔ RL fine-tuning on real rollouts；LLM eval slices ↔ per-task/per-scene success rate；data mixture ↔ teleop/sim/real 配比。**不要假装懂机器人，要展示你能用一手原理把两边接起来。**

### 3.2 ML system design（开放式：数据引擎 / eval 体系）

**最可能的题面（推断，基于 JD + CTO 推文 + field ops 实证）：** "Design the post-training data engine for a home robot: teleop data + real-robot rollouts + data from customer homes. How do you close the loop?"

**答题骨架（用 Tesla data engine 语言讲，面试官一听就是自己人）：**

1. **先问清目标和约束**（2 分钟）：什么任务分布？多少台机器人在真实家庭？隐私约束？标注预算？—— 不问就开讲会被判 hand-wave。
2. **数据分层**：teleop（高质量、贵、覆盖窄）/ sim（便宜、无限量、有 sim2real gap）/ 真机 rollout（分布对但质量混杂）/ 用户家庭数据（分布最真实但有隐私和长尾噪声）。给出每层的角色和大致配比逻辑，以及**配比怎么随阶段演化**。
3. **闭环机制（核心得分点）**：failure mining —— 线上失败案例自动回流（触发条件：human intervention、task timeout、anomaly detector），进入 triage → 分类 → 定向补数据（针对性 teleop 重演 / sim 复现）→ 重训 → shadow eval → 灰度部署。这就是 Tesla data engine 的 corner-case 循环，明说这个类比。
4. **Eval 体系（CTO 点名，必须主动展开）**：分层 eval —— 离线（held-out per-task/per-scene success、回归集 = 历史 failure 案例全量重跑）、sim eval（快、可控变量）、真机 eval（金标准、贵，设计 sampling 策略）、线上 proxy metrics（intervention rate、task completion）。强调「每修一个 failure mode 就把它固化成回归 eval」。
5. **主动交代 trade-off**：eval 真机throughput是瓶颈 → 怎么用 sim eval 做预筛并定期calibration sim-real 相关性；用户数据的隐私 → on-device 过滤 / opt-in。

**面试时怎么说（开场示范）：**

> "Before I design anything, let me pin down the loop we're optimizing: I assume the bottleneck is not model capacity but data coverage of the long tail of real homes. So I'll structure this as a data engine — the same philosophy as an autonomy data engine: deploy, mine failures, target data collection at those failures, retrain, and gate redeployment on evals. Let me walk through each stage, and I'll flag the two places where I think this breaks first."

### 3.3 Debugging 现场题（log / 训练数据分析）

**两种子形态：**

**(a) 训练不收敛 / 训练异常。** 标准排查树背熟并现场说出声：
- 先看**曲线形状**：loss 不降（LR/数据/初始化/bug）、降了又炸（LR 过大、数值溢出、bad batch）、train 降 eval 不降（overfitting/eval 泄漏或错位）、周期性尖刺（数据顺序/特定 shard 脏数据）。
- 再做**二分隔离**：固定 seed 缩小到单 batch 能否 overfit（能 → 数据/规模问题；不能 → 代码 bug）；关掉 augmentation/mixed precision/分布式逐项排除。
- 常见 PyTorch 现场 bug 清单：忘 `zero_grad`、`train()/eval()` 模式错、loss 没 `mean` 导致 scale 错、label 错位 off-by-one、`softmax` 后又接 `CrossEntropyLoss`、dataloader shuffle 泄漏、fp16 溢出、梯度未 clip、tokenizer/padding mask 错。

**(b) 真机行为异常（贴合他们 Airbnb field-test 日常）。** 你没有真机经验，但可以用通用的分层定位法 + 数据人视角：

> "I haven't debugged a physical robot before, so let me reason from first principles and you can correct my priors. I'd bisect the stack: first, is the input wrong — replay the sensor stream, check timestamps and calibration drift. Second, is the model wrong — run the same observation through the policy offline, compare action distribution against a known-good checkpoint. Third, is the execution wrong — compare commanded vs. actual trajectories. The fastest discriminator is usually replaying logged observations offline: if the policy output matches the bad behavior, it's a model or data problem, and then I'm in my home territory — I'd look at whether this scene is out-of-distribution relative to training data."

这个回答同时展示了：诚实（没碰过真机）、跨域推理（JD 明文要的）、以及把问题拉回自己主场（数据分布）的能力。

**通用纪律：出声思考 + 每一步说「我预期看到什么、看到什么说明什么」。** 这类轮考的是排查过程的结构，不是撞对答案。

### 3.4 Coding（实战向，非 LeetCode）

**预判题型（按类比公司概率排序）：**
1. 向量化数值代码（Skild 风格：单遍 reverse 迭代算 discounted returns；rolling statistics；masked mean）。
2. 手写 attention / 简版 transformer block（Tesla 电面高频）。
3. 修一段有 bug 的训练循环（结合 3.3a 的 bug 清单）。
4. 数据管道题：清洗/去重/流式处理大文件。

**策略：**
- 先 30 秒复述题目 + 确认边界（shape、dtype、空输入），再写。他们要 mental acuity，磨蹭比小 bug 更减分。
- **先写对再写快**：先给 naive 循环版本说 "let me get a correct baseline first, then vectorize" —— 这句话本身就是加分项。
- 写 NumPy/PyTorch 时把 shape 注释写在行尾（`# [B, T, D]`），Tesla 系面试官吃这套。
- 手写 attention 提前默写到肌肉记忆：`scores = q @ k.transpose(-2,-1) / sqrt(d_k)` → mask → softmax → `@ v`，加上 causal mask 和 padding mask 两个变体。
- 如果被丢 C++ 相关问题：不硬写，聊你懂的（内存布局、为什么推理侧用 C++/Rust），承认 Python 是主语言。JD 写的是 "Python, C++, **or** Rust"。

### 3.5 Founder / culture chat（可能被砍到 20 分钟——那是好信号）

**红线（来自 Vogt 公开语录，非猜测）：**
- 不聊晋升、管理轨道、带团队（"Everyone is an IC"；"manager, senior manager, director... become horribly inefficient"）。
- 不表现出对 remote/hybrid 的任何留恋。全岗位 SF onsite，卖点是 "10 feet from desk to running code on a robot"。
- 不把公司当跳板叙事。Vogt 明言不再卖公司、要长期做大。

**必答题预案：「为什么家用机器人、为什么是现在、为什么是你」——** 答案要真诚且个人化。示范（按 Ray 的背景起草，需自己calibration细节）：

> "Two reasons. First, I've spent my career on the interface between humans and intelligent systems — my PhD was in HCI, and my recent work is post-training LLMs to act, not just talk. A home robot is the most extreme version of that interface: it lives in your space, and the gap between a demo and a product is entirely in the long tail of real human environments. That long tail is a data and evaluation problem, which is exactly the work I love. Second, I want the sub-100-person version of this: everyone an IC, no layers, walk ten feet and run your code on a robot. I've seen what process-heavy orgs do to iteration speed, and I'm deliberately choosing the opposite."

**High agency 证据准备：** 挑 1–2 个「没人叫我做、我发现问题直接把它做完」的故事，30 秒能讲完，有结果数字。founder 轮问 "tell me about a time" 时直接用。

**你反问的问题（准备 3 个，测你 curiosity 的环节）：**
- "What does the data flywheel look like today — how does a failure observed in a test home end up changing the next training run, and where's the biggest friction in that loop?"
- "How do you split eval between sim and real robots today, and how do you keep sim eval honest?"
- "What's the sharpest disagreement inside the team right now about the training recipe?"（测他们，也展示你）

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/02_interview_rounds_intel.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/02_interview_rounds_intel.md)。作者整理资料；许可和第三方来源范围见阅读指南。
