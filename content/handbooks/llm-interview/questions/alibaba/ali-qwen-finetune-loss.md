---
id: ali-qwen-finetune-loss
section: alibaba
order: 18
level: A
title: 微调 Qwen 时，训练阶段和 Loss 如何选择？
quick: >-
  先定目标：指令遵循用 SFT（只对 assistant/action token 计 loss）；偏好用 DPO；可验证目标用 GRPO。阶段不要跳，数据与
  mask 必须匹配部署协议。
tags:
  - Alibaba
  - Qwen
  - SFT
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
  - title: ↗ Qwen GSPO paper
    url: 'https://arxiv.org/abs/2507.18071'
    type: legacy-reference
---

错法：直接上 DPO / GRPO 微调 Qwen，或对整段对话算 CE。先定目标：指令遵循与工具协议用 SFT（只对 assistant / action token 计 loss）；偏好用 DPO；可验证目标用 GRPO / GSPO。阶段不要跳，数据与 mask 必须匹配部署时的 chat template 和 tool schema。阶段分工见 `ali-sft-then-posttrain`，对齐算法对比见 `ali-ppo-dpo-grpo-ask`。

## 先定目标再选阶段

为何先 SFT 再对齐：先学会格式、角色、工具调用协议，再优化偏好或成功率。跳过 SFT，偏好对里混着格式错误，DPO 会把「会说话」和「格式对」缠在一起。可验证任务（工具成功、数学）再上 on-policy RL。Qwen 系列官方 post-train 还包含 GSPO 等序列级稳定化，面试提到名字时要能说：它针对 token 级重要性比的噪声，把优化放到序列 / 组的相对尺度上，别只会背缩写。

目标与 loss 对齐：模仿示范 → token CE；成对更好 / 更差 → DPO；组内可比较的标量奖励 → GRPO。不要用 SFT 硬学「更有用」，那会把偏好噪声写进最大似然。

## Loss mask 必须对齐协议

user / system / tool response 通常不进 policy loss，只训练模型该说的 token（assistant 文本、tool name、参数）。对工具结果也算 loss，等于让模型背诵 API 返回，浪费容量还泄漏。mask 必须与线上 chat template 一致：Qwen 的 `<|im_start|>` 角色、tool 特殊标记漏一个，训练和推理就错位。Agent 数据里「思考 / 动作 / 观察」要分清哪些是模型输出、哪些是环境写回。

## LoRA 与 chat template

数据少、要多任务隔离时用 LoRA；要大幅改工具行为或领域分布，再考虑更大更新或全参。无论哪种，都先锁死 tokenizer 与 template，再谈 rank。评测用官方对话格式跑，不要用「裸补全」报分。部署协议（并行 tool call、拒绝调用）在 SFT 里就要有正负例，否则后训练只能在错误格式上刷分。

## 追问

- **为何不对 user token 算 loss？** 那些 token 推理时不会由模型生成，算了是在拟合提示分布。
- **LoRA 够不够改工具行为？** 格式和浅层习惯通常够；深层策略或长程规划可能要更大容量或后续 RL。
- **Qwen 和 Llama 微调差在哪？** 差在 template、tool 标记和官方对齐配方；loss 原理相同，协议必须跟模型走。
- **GSPO 和 GRPO？** 都是组相对思路；GSPO 更强调序列级比值稳定。说得出「为何要稳重要性比」即可。
