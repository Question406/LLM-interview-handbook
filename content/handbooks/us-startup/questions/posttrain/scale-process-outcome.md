---
id: scale-process-outcome
section: posttrain
order: 2
level: A
title: Scale 岗位：多 agent 同时学过程奖励和结果奖励
quick: >-
  假设 Agent 每次工具参数都合法，但最终工单没有关闭。Process reward 可以描述中间步骤，outcome reward
  判断任务是否完成，二者不能互相替代。
tags:
  - Scale AI
  - Post-training
  - GRPO
  - Agent
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 'Staff MLRE, Agent Post-training, Enterprise GenAI'
    url: 'https://job-boards.greenhouse.io/scaleai/jobs/4625337005'
    type: primary
  - title: 'ML Systems Research Engineer, Agent Post-training'
    url: 'https://job-boards.greenhouse.io/scaleai/jobs/4625341005'
    type: primary
  - title: 'DeepSeekMath, GRPO'
    url: 'https://arxiv.org/abs/2402.03300'
    type: primary
---

## 回答思路

> **问题与场景：** 假设 Agent 每次工具参数都合法，但最终工单没有关闭。
>
> **做法与原因：** 我会把最终结果作为主要目标，只给可信、可验证的进展辅助分，并明确失败时辅助分怎样处理。
>
> **检查与取舍：** 在相同预算下比较最终成功、调用成本与违规行为，再看辅助奖励有没有帮助。

## 可以这样回答

假设 Agent 每次工具参数都合法，但最终工单没有关闭。Process reward 可以描述中间步骤，outcome reward 判断任务是否完成，二者不能互相替代。

我会把最终结果作为主要目标，只给可信、可验证的进展辅助分，并明确失败时辅助分怎样处理。若格式或调用次数能刷高分，就可能让模型优化了过程表象。

在相同预算下比较最终成功、调用成本与违规行为，再看辅助奖励有没有帮助。这是岗位方向推演，不能把它说成已确认的现场题。

## 技术备查

我会用结果奖励决定任务成败，把过程奖励作为系数较小的辅助信号，失败时截掉过程项。比如 agent 每次工具调用的参数都合法，最后却没关掉工单，这条轨迹仍应算失败。

题来自 Scale Enterprise GenAI 的 Agent Post-training 岗位，`realInterview: false`。岗位里有两句和后训练直接相关：使用 RLHF 和 RLVR，以及 PPO / GRPO；让多 agent、多工具的系统同时从过程奖励和结果奖励学习。平台岗位还写了他们内部有一套 LLM 训练框架，给研究和数据质量评估用。2026 年那篇 MLE 挂经只证实第一面是后训练八股，没有证实问过这道，见 `scale-posttrain-oral`。

先把两种奖励说清楚。结果奖励 $R_{\mathrm{out}}$ 在轨迹结束时给一次，企业题里就是工单关没关、单测过没过、最终答案和标注对不对得上。这个信号很稀疏：十步工具调用只有最后一步拿到奖励，很难判断前面哪几次检索对成功有贡献。过程奖励 $R_{\mathrm{proc}}$ 打在中间步上，看工具参数的字段和类型是否符合 schema、规定必须调的工具调没调、引用是否落在检索到的文档里。信号密集多了，可它衡量的是中间步骤满不满足细则，说明不了任务成没成。agent 完全可以每一步都把细则做满，最后答案还是错的。

两项进同一个标量，过程项的系数要小：

$$
r_t = \lambda R_{\mathrm{proc},t} + \mathbf{1}[t=T]\, R_{\mathrm{out}}
$$

$\lambda$ 大到过程项能盖过结果，策略就会去刷细则。再加上结果失败时截断过程项，「过程很漂亮」就抵消不了失败。

多 agent 还多一个问题：这份奖励给谁。只给最终发言的那个 agent 结果奖励，检索 agent 的梯度就是零。共享结果奖励能让大家都关心终局，可检索错了、回答碰巧蒙对的时候，检索 agent 也会被奖。所以过程项要按角色拆开：检索看召回，执行看工具调用是否成功，汇总看最终答案。用一个 LLM judge 给整段轨迹打一个分再广播给所有 agent，这个分学到的是文风。

算法上，GRPO 适合结果已经是一个标量的情况：同一题抽一组轨迹，优势在组内 standardization，不另训 value network。

$$
\hat A_i = \frac{r_i - \mathrm{mean}(r)}{\mathrm{std}(r)}
$$

组里奖励全相同，也就是全对或全错时，标准差是 0，这组要丢掉，否则优势是 NaN。PPO 的 value network 在长工具轨迹上更难训，岗位把 GRPO 和 PPO 写在一起，问的就是你什么时候可以省掉价值评估模型（critic）。

## 追问

**验证器和人的偏好冲突怎么办？**
分开管。比如 RLVR 的验证器说单测过了，人说方案不能维护。我把可自动判定的部分留给验证器，风格和取舍仍交给人或细则模型，两套奖励不要加进同一个没有权重的和里。

**过程奖励用模型打分行吗？**
可以，但打分模型要固定住。它和策略一起更新的话，策略会钻打分模型的空子。固定之后用另一批没参与训练的轨迹抽查，抽查里人和打分模型不一致的那些步，就是细则要改的地方。

**on-policy 太贵怎么办？**
贵主要贵在环境执行，GPU 计算倒在其次。一组 GRPO 要为每题 sampling 多次完整轨迹，工具调用的成本主要来自环境执行。能缓存的工具结果按参数哈希缓存。有副作用的工具（写库、发信）不能在训练里打到生产，见 `fireworks-rft` 里他们讲的隔离。
