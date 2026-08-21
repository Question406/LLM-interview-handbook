---
id: ali-sft-then-posttrain
section: alibaba
order: 13
level: S
title: SFT 核心流程与数据构建？之后 Post-Training 各自解决什么？
quick: >-
  SFT：定任务分布→采/合成指令数据→清洗配比→监督学习。其后 DPO 解决偏好排序；PPO/RLHF 解决复杂主观目标；GRPO 等 RL
  解决可验证/探索目标。
tags:
  - Alibaba
  - SFT
  - Post-Training
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---

陷阱是把 SFT / DPO / PPO / GRPO 堆成 buzzword，或跳过 SFT 直接 RL。它们针对不同监督信号。SFT：定任务分布 → 采 / 合成指令数据 → 清洗配比 → 监督学习。其后 DPO 解决偏好排序；PPO / RLHF 拟合更复杂的主观目标；GRPO 等 RL 解决可验证 / 探索目标。Qwen 上的 mask 与阶段见 `ali-qwen-finetune-loss`，算法对比见 `ali-ppo-dpo-grpo-ask`。

## SFT 解决的是分布与格式

定义场景与输出格式 → 采集或合成 instruction-response → 去重、安全过滤、难度与任务配比 → 设 loss mask → 用离线评测 + 人工看是否真变好。SFT 是在学「这类输入应该长什么样」：角色、工具协议、拒答边界。数据配比决定模型时间花在哪：全是闲聊，工具调用会弱；全是合成正确轨迹，真实失败恢复会差。合成数据要防自污染：模型自己生成再自己学，会放大模板。评测必须含 held-out 真实单，不要只报训练 CE。

## 之后按监督信号选型

- **DPO**：成对偏好，学更好 vs 更差；离线、省采样，怕噪声与长度偏置。
- **RLHF / PPO**：RM + 强化学习，能加权多目标，但 RM hacking、四模型复杂。
- **GRPO 等**：可验证奖励或 group 相对优化，强化推理 / 工具成功率，吃采样多样性。

不是「越后面越高级」。分类、口径、安全偏好常常 DPO 更稳；数学、代码、工具成功更配 GRPO。多负 DPO 后再接 GRPO 的条件见 `ali-multineg-then-grpo`。每一步都要能回答：新的监督信号是什么、旧阶段没解决什么。

## 不要跳阶段

先 SFT 把协议做对，再偏好对齐，再按需 on-policy。跳过 SFT，RL 会在乱格式上探索，credit 更难。SFT 过度会把分布压尖，后续 GRPO 组方差塌掉，需要留一点熵或 replay。验收按阶段：SFT 看格式 / 工具合法率；DPO 看人评胜率；RL 看 verifier 与 held-out，防止奖励涨、能力掉，见 `ali-reward-hacking`。

## 追问

- **SFT 能否代替对齐？** 能教格式，难教「更好」的细粒度权衡；硬学偏好会把标注噪声写进 CE。
- **数据从哪来？** 真实日志清洗 + 合成补长尾；合成必须经规则 / 人审，防止自污染。
- **为何还要人工评？** 离线自动指标会漏口径和安全；SFT 后先盲测再进偏好。
- **Post-training 顺序能反吗？** 能试，但 DPO 在 RL 之后容易拉回旧离线分布；更常见仍是 SFT → 偏好 → 可验证 RL。
