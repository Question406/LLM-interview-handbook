---
id: scale-process-outcome
section: posttrain
order: 2
level: A
title: Scale 岗位：多 agent 同时学过程奖励和结果奖励
quick: "岗位原文要求 agent 同时从过程奖励（process reward）和结果奖励（outcome reward）学习，算法点名 PPO 和 GRPO。 结果奖励只在轨迹结束时给一次，过程奖励提供更密集的信号，但 agent 也可能只满足评分细则而没有完成任务。这是招聘说明，不是某一场的逐字题。"
tags:
  - Scale AI
  - Post-training
  - GRPO
  - Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Staff MLRE, Agent Post-training, Enterprise GenAI
    url: https://job-boards.greenhouse.io/scaleai/jobs/4625337005
    type: primary
  - title: ML Systems Research Engineer, Agent Post-training
    url: https://job-boards.greenhouse.io/scaleai/jobs/4625341005
    type: primary
  - title: DeepSeekMath, GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

## 题怎么来的

Scale Enterprise GenAI 的 Agent Post-training 岗位写了两句和后训练直接相关的话：用 基于人类反馈的强化学习（RLHF） / 基于可验证奖励的强化学习（RLVR），以及 PPO / GRPO；让多 agent、多工具的系统同时从过程奖励和结果奖励学习。平台岗位还写他们内部有一套 LLM 训练框架，给研究和数据质量评估用。`realInterview: false`。2026 年那篇 MLE 挂经只证实第一面是后训练八股，没有证实他们问了这道，见 `scale-posttrain-oral`。

## 两种奖励

结果奖励 $R_{\mathrm{out}}$ 在轨迹结束时给一次。企业题里它是工单关没关、单测过没过、最终答案是否匹配标注。信号比较稀疏。十步工具调用只有最后一步拿到奖励，很难判断前面哪些检索步骤对成功有贡献。

过程奖励 $R_{\mathrm{proc}}$ 打在中间步：工具参数的字段和类型是否符合 schema、是不是调了规定必须调的工具、引用是否落在检索到的文档里。信号更密集，但衡量的是中间步骤是否满足细则，不能直接说明任务是否成功。agent 可以逐步把细则做满，最后答案仍然是错的。

我会把成功与否只绑在结果奖励上。过程奖励的系数设小，并且在结果为失败时把过程项截断，避免「过程很漂亮」抵消失败。两个都进同一个标量：

$$
r_t = \lambda R_{\mathrm{proc},t} + \mathbf{1}[t=T]\, R_{\mathrm{out}}
$$

$\lambda$ 大到过程项能盖过结果时，策略会去刷细则。

## 多 agent 谁拿这份奖励

只给最终发言的那个 agent 结果奖励，检索 agent 的梯度是零。共享结果奖励能让大家都关心终局，但检索错了、回答碰巧蒙对时，检索 agent 也会被奖。过程项按角色拆开：检索看召回，执行看工具是否成功，汇总看最终答案。不要用一个 LLM judge 给整段轨迹打一个分再广播，那个分学到的是文风。

GRPO 适合结果已经是一个标量的情况：同一题抽一组轨迹，优势用组内标准化，不另训价值网络。

$$
\hat A_i = \frac{r_i - \mathrm{mean}(r)}{\mathrm{std}(r)}
$$

组里奖励全相同（全对或全错）时标准差是 0，这组要丢掉，否则优势是 NaN。PPO 的价值网络在长工具轨迹上更难训，岗位把 GRPO 和 PPO 写在一起，就是在问你什么时候省去价值评估模型（critic）。

## 追问

**验证器和人的偏好冲突？** RLVR 的验证器说单测过了，人说方案不能维护。我把可自动判定的部分留给验证器，风格和取舍仍用人或细则模型，两套奖励不要加进同一个没有权重的和。

**过程奖励用模型打分？** 打分模型和策略一起更新时，策略会钻打分模型的空子。打分模型固定住，用另一批没参与训练的轨迹抽查。抽查里人和打分模型不一致的那些步，就是细则要改的地方。

**on-policy 太贵？** 一组 GRPO 要为每题采样多次完整轨迹，工具调用的成本主要来自环境执行，而不是 GPU 计算。能缓存的工具结果按参数哈希缓存。有副作用的工具（写库、发信）不能在训练里打到生产，见 `fireworks-rft` 里他们讲的隔离。
