---
id: jd-sft-peft-trick
section: posttrain
order: 144
level: A
title: 京东：SFT 和 PEFT 训练有哪些实用 trick？
quick: >-
  只对回答 token 计 loss、控制轮数防遗忘、按长度 / 难度采样、LoRA 挂注意力投影并扫 rank。PEFT 省显存但不自动更好，数据质量和 mask
  比再加一个 adapter 重要。
tags:
  - JD
  - SFT
  - PEFT
  - LoRA
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 京东大模型算法 实习面经
    url: https://www.nowcoder.com/feed/main/detail/9ce9749030b24f6a9a7afcaa62b27f46
    type: candidate-first-hand
---

## 真题记录

- 公司：京东
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；轮次未披露
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“模型的SFT和PEFT训练的时候有什么小trick”**

陷阱是背一串超参清单。Trick 要能解释「解决什么失败」：prompt 泄漏进 loss、过拟合示范、LoRA 没挂到真正更新的模块、训练模板和线上不一致。PEFT 省显存，不自动更好。数据质量和 mask 比再加一个 adapter 重要。面试官听的是你能不能把 trick 映射到过拟合、遗忘、数值对不齐这几类病。

## 1. SFT：mask、packing、采样和早停

只对 completion token 计交叉熵，prompt 和系统提示 mask 掉，否则模型在学复述用户话，指令遵循看起来很好、换个用户表述就崩。Packing 必须切断跨样本 attention，否则下一条的答案会当上一条的继续，这是复读和串答的隐源。学习率对 embedding / lm_head 可分开：新 special token 没学够，工具调用括号会乱。长样本不要被短样本在 token-mean 里淹没，可按长度分层采样，或明确选择 `seq-mean` 还是 `token-mean`。

流程上：先用几十条过拟合自检「数据进没进图、loss 会不会掉到接近 0」——掉不下去说明模板或 mask 错了。再用 holdout 早停，而不是固定 3 epoch。轮数过多会遗忘通用能力，过少则格式都没锁住。失败模式是训练 loss 很好、线上换模板就崩：根因几乎总是 chat template、停止符、工具 schema 与推理不一致，或系统提示没进训练。评测不能用训练改写过的题目。

和后续 RL 的衔接：SFT 的 tokenizer 与 special token 必须同一套。Mask 错了，GRPO 的 parser 会把大量 rollout 判零，组内全错，优势为 0，看起来像 RL 不稳，其实是 SFT 没把格式锁住。

## 2. LoRA / QLoRA：挂哪、rank 怎么扫、合并后对齐

初始化 A 随机、B 零，保证起步等价于原模型，避免随机 adapter 一起步就打乱 SFT。Rank 从 8/16 扫起；目标模块优先 `q/k/v/o`，任务差得大再加 FFN。$\alpha/r$ 当成有效缩放，改 $r$ 时同步看 $\alpha$，避免「升 rank 却等效更小」。合并 adapter 后要对齐推理数值：是否再量化、是否 fused kernel、是否 droput 还开着。

QLoRA 注意 NF4、分页优化器、以及和全量微调不同的学习率量级。失败时：只挂 $q$、$v$ 在某些架构上不够；rank 很大但数据脏，等于用更多自由度背噪声。验证用「解冻一小块全量 vs LoRA」的同数据对比，而不是只报可训参数量。PEFT 欠拟合难任务时，加数据或解冻一层，比把 rank 拉到 256 更有效。

## 3. 共同坑比 adapter 更致命

模板、停止符、工具 schema 必须与线上一致。SFT 与 RL 的 pack / unpack 要同一套。Trick 的验收是 holdout 任务成功和遗忘指标（通用题、安全题），不是训练 CE。京东场景里 SKU、价格、库存这类槽位错一个就失败，completion-only 还要保证槽位格式在示范里一致，否则 LoRA 再精也学的是乱格式。

## 追问

- **Completion-only 会不会学不会听指令？** 指令已在 context 里，梯度来自「如何回答」；若指令遵循差，加指令多样化数据，而不是对 prompt 计 loss。
- **LoRA 一定比全量稳吗？** 不一定。容量不够会欠拟合；容量太大加脏数据会过拟合。稳来自数据与早停，不是来自 adapter 这个形式。
- **要不要对 embedding 做 LoRA？** 新加 special token 时往往要；旧词表够用时不一定。说清「词表变了没有」。
- **和 RL 怎么衔接？** 先用这些 trick 把格式通过率做高，再上 GRPO；格式门禁失败时不要开始 RL。
