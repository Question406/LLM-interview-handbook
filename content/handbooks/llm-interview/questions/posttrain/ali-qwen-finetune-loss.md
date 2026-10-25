---
id: ali-qwen-finetune-loss
section: posttrain
order: 18
level: A
title: 微调 Qwen 时，训练阶段和 Loss 如何选择？
quick: "先定训练目标：学指令遵循和工具协议用监督微调（SFT），只对助手回复和动作 token 算损失；学偏好用直接偏好优化（DPO）；优化可验证目标用 GRPO。阶段别跳，数据和 mask 要和部署时的协议对齐。"
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

先定训练目标，再选阶段和 loss：要学指令遵循和工具协议，用监督微调（SFT），只对 assistant / action token 计算损失；要学偏好，用直接偏好优化（DPO）；要优化可验证的目标，用 GRPO / GSPO。阶段别跳，数据和 mask 必须和部署时的 chat template、tool 字段和类型规范（schema）一致。

先 SFT 再对齐，是因为模型得先学会格式、角色和工具调用协议，偏好和成功率才有优化的基础。跳过 SFT，偏好对里混着格式错误，DPO 会把「会说话」和「格式对」缠在一起学。可验证任务，比如工具成功、数学，再上 on-policy 强化学习（RL）。目标和 loss 要对上：模仿示范用 token 级的交叉熵损失（CE），成对的更好 / 更差用 DPO，组内可比较的标量奖励用 GRPO。别用 SFT 硬学「更有用」，那会把偏好噪声写进最大似然。阶段分工见 `ali-sft-then-posttrain`，对齐算法的对比见 `ali-ppo-dpo-grpo-ask`。

Qwen 系列官方 post-train 里还有 GSPO 这类序列级稳定化。面试提到这个名字，要能说出它针对的是 token 级重要性比的噪声，把优化放到序列 / 组的相对尺度上，光会背缩写不够。

最容易出错的是损失算在哪些 token 上。一条 Agent 数据里有用户提问、模型的思考和工具调用、工具返回的结果，user / system / tool response 通常不进 policy loss，只训练模型该说的 token，也就是 assistant 文本、tool name 和参数。对工具结果也算 loss，等于让模型背诵 API 返回，浪费容量还会泄漏。「思考 / 动作 / 观察」里哪些是模型输出、哪些是环境写回，要分清楚。直接对整段对话算 CE，是这道题最常见的错误。mask 还得和线上 chat template 一致，Qwen 的 `<|im_start|>` 角色、tool 特殊标记漏一个，训练和推理就错位了。

LoRA 还是全参看需求。数据少、要多任务隔离时用 LoRA；要大幅改工具行为或领域分布，再考虑更大的更新或全参。不管哪种，都先锁死 tokenizer 和 template，再谈 rank。评测用官方对话格式跑，别用「裸补全」报分。部署协议，比如并行工具调用、拒绝调用，在 SFT 里就要有正负例，否则后训练只能在错误格式上刷分。

## 追问

**为什么不对 user token 算 loss？**
推理时这些 token 不由模型生成，算了等于在拟合提示分布。

**LoRA 够不够改工具行为？**
格式和浅层习惯通常够；深层策略或长程规划，可能要更大的容量或者后续 RL。

**Qwen 和 Llama 微调差在哪？**
差在 template、tool 标记和官方对齐配方。loss 原理一样，协议必须跟着模型走。

**GSPO 和 GRPO 什么关系？**
都是组相对的思路，GSPO 更强调序列级比值的稳定。能说清「为什么要稳住重要性比」就够了。
