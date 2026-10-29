---
id: jd-sft-peft-trick
section: posttrain
order: 144
level: A
title: 京东：SFT 和 PEFT 训练有哪些实用 trick？
quick: >-
  最有用的几条是只对回答 token 算 loss、packing 切断跨样本 attention、用 holdout 早停防遗忘、按长度 / 难度
  sampling，LoRA 挂 attention 投影并扫 rank。PEFT 只是省显存，效果不会自动更好，数据质量、mask
  和模板与线上一致比再加一个 adapter 重要。
tags:
  - JD
  - SFT
  - PEFT
  - LoRA
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 京东大模型算法 实习面经
    url: 'https://www.nowcoder.com/feed/main/detail/9ce9749030b24f6a9a7afcaa62b27f46'
    type: candidate-first-hand
---

## 真题记录

- 公司：京东
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；轮次未披露
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“模型的 SFT 和 PEFT 训练的时候有什么小 trick”**

我会把 trick 按它解决的失败来讲：prompt 被错误地计入 loss、overfitting 示范、LoRA 没挂到真正在更新的模块、训练模板和线上不一致，大体落在 overfitting、遗忘、数值对不齐这几类。背一串超参清单，面试官一问「这个解决什么」就答不上来。PEFT 省显存，效果不会自动更好，数据质量和 mask 比再加一个 adapter 重要。

先说 SFT。只对 completion token 算 cross entropy，prompt 和系统提示 mask 掉，不然模型在学复述用户的话，指令遵循看着很好，用户换个说法就崩。Packing 一定要切断跨样本的 attention，否则下一条的答案会被当成上一条的续写，这是复读和串答的一个隐藏来源。embedding / lm_head 的学习率可以单独设，新加的 special token 没学够，工具调用的括号就会乱。长样本别在 token-mean 里被短样本淹没，可以按长度 stratified sampling，或者明确选好用 `seq-mean` 还是 `token-mean`。

流程上，我会先拿几十条数据做 overfitting 自检，看数据有没有进计算图、loss 能不能掉到接近 0。掉不下去，多半是模板或 mask 写错了。然后用 holdout 早停，别固定跑 3 个 epoch：轮数太多会遗忘通用能力，太少连格式都没锁住。最典型的失败是训练 loss 很好，线上一换模板就崩，根因几乎总是 chat template、停止符、工具 schema 和推理时不一致，或者系统提示没进训练。评测也别用训练时改写过的题。

SFT 还要为后面的 RL 铺路，tokenizer 和 special token 必须是同一套。Mask 错了，GRPO 的 parser 会把大量 sampling 轨迹（rollout）判成零分，组内全错、优势为 0，看起来像 RL 不稳，其实是 SFT 没把格式锁住。

再说 LoRA / QLoRA。初始化时 A 随机、B 置零，保证起步时等价于原模型，随机 adapter 一上来就不会把 SFT 打乱。Rank 从 8/16 开始扫；目标模块优先 `q/k/v/o`，任务差得远再加 FFN。$\alpha/r$ 要当成有效缩放看，改 $r$ 时同步看 $\alpha$，免得「rank 升了，等效缩放却变小」。合并 adapter 之后要对齐推理时的数值：有没有再量化、是不是 fused kernel、dropout 还开着没有。

QLoRA 要留意 NF4、分页优化器，以及它的学习率量级和全量微调不一样。常见失败是只挂 $q$、$v$，在有些架构上不够；或者 rank 很大但数据脏，等于用更多自由度去背噪声。验证时用「解冻一小块做全量 vs LoRA」在同一份数据上对比，光报可训参数量说明不了问题。PEFT 在难任务上 underfitting 时，加数据或者解冻一层，比把 rank 拉到 256 有效。

SFT 和 PEFT 共同的坑比 adapter 本身更致命：模板、停止符、工具 schema 必须和线上一致，SFT 和 RL 的 pack / unpack 用同一套。trick 有没有用，看 holdout 任务成功率和遗忘指标（通用题、安全题），训练 cross entropy loss（CE）说明不了。京东的场景里，SKU、价格、库存这类槽位错一个就算失败，所以做 completion-only 时还要保证示范里的槽位格式一致，不然 LoRA 调得再细，学到的也是乱格式。

## 追问

**Completion-only 会不会学不会听指令？**
不会。指令已经在 context 里，梯度来自「怎么回答」。指令遵循差的话，加指令多样化的数据，别去对 prompt 算 loss。

**LoRA 一定比全量稳吗？**
不一定。容量不够会 underfitting，容量太大再加上脏数据会 overfitting。稳定来自数据和早停，跟 adapter 这个形式关系不大。

**要不要对 embedding 做 LoRA？**
新加了 special token 时往往要，旧 vocabulary 够用时不一定。关键是说清楚 vocabulary 有没有变。

**和 RL 怎么衔接？**
先用这些 trick 把格式通过率做高，再上 GRPO。格式 acceptance checks 没过就别开始 RL。
