---
id: openai-moe-aux-loss
section: openai
order: 13
level: A
title: OpenAI：MoE 辅助损失和负载均衡，路由塌缩怎么发现
quick: >-
  我会用 Switch 的辅助损失约束路由集中，再逐层看专家占用、路由熵和 drop 率。语言 loss
  还在降时也可能只剩一个专家在学习，所以要把真实负载和匹配 FLOPs 的 dense 基线一起检查。
tags:
  - OpenAI
  - MoE
  - Load Balancing
  - Routing
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: >-
      Switch Transformers — Scaling to Trillion Parameter Models with Simple and
      Efficient Sparsity
    url: 'https://arxiv.org/abs/2101.03961'
    type: primary
  - title: ST-MoE — Designing Stable and Transferable Sparse Expert Models
    url: 'https://arxiv.org/abs/2202.08906'
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: >-
      https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 可以这样回答

MoE 负载均衡要防止路由长期集中到少数专家，再用真实占用检查辅助损失是否有效。比如一个专家越来越强，路由把更多 token 交给它，其他专家收不到梯度，即使训练 loss 继续下降，有效容量也可能只像一个 dense 小模型。这里按 Switch、GShard、ST-MoE 的公开训练方法讲；GPT-4 是否 MoE 没有官方确认，不能据此作推断。

均匀时 $f_i=P_i=1/N$，$L_{\mathrm{aux}}=\alpha$。由柯西不等式，$\sum f P$ 在均匀处最小。$\alpha$ 太小，路由器抄近路把一切送给当前最好的专家；太大，为了均衡牺牲语言质量。capacity factor 再卡死每个专家这一批能收多少 token，溢出的被 drop 或漏到 backup。

## 技术备查

MoE 负载均衡要防止路由长期集中到少数专家，再用真实占用检查辅助损失是否有效。比如一个专家越来越强，路由把更多 token 交给它，其他专家收不到梯度，即使训练 loss 继续下降，有效容量也可能只像一个 dense 小模型。这里按 Switch、GShard、ST-MoE 的公开训练方法讲；GPT-4 是否 MoE 没有官方确认，不能据此作推断。

## aux loss 在惩罚什么

Switch 对每个 token 做 softmax 路由，通常 top-1。专家 $i$ 上：

$$
f_i=\frac{1}{T}\#\{\text{tokens routed to }i\},\qquad
P_i=\frac{1}{T}\sum_{t} p_t(i).
$$

$N$ 个专家时

$$
L_{\mathrm{aux}}=\alpha\, N \sum_{i=1}^{N} f_i P_i.
$$

均匀时 $f_i=P_i=1/N$，$L_{\mathrm{aux}}=\alpha$。由柯西不等式，$\sum f P$ 在均匀处最小。$\alpha$ 太小，路由器抄近路把一切送给当前最好的专家；太大，为了均衡牺牲语言质量。capacity factor 再卡死每个专家这一批能收多少 token，溢出的被 drop 或漏到 backup。

ST-MoE 还加了 router z-loss，压 logits 的绝对值，减少 fp16 下的不稳。面试提到它能说明你知道 aux 不是唯一稳定项。

## 塌缩长什么样，怎么发现

塌缩：$\max_i f_i\to 1$，路由熵 $-\sum P_i\log P_i\to 0$。表现是训练 loss 还在降（那个赢家专家在学），但有效参数量和 dense 小模型差不多，后面加专家不涨点。all-to-all 上有的 rank 空转、有的打满。

我会逐层画专家占用直方图，塌缩常从局部开始，全局平均会遮住它。把 $L_{\mathrm{aux}}$ 和 $\mathrm{std}(f)$ 并排看：aux 小而占用差异大，可能损失与负载定义不同，或 dropless 实现没有把 drop 算进 $f$。

再看 dropped token 比例，capacity 太紧时看似均匀可能只是丢掉了溢出 token。验证集还要比较 FLOP 匹配的 dense 基线；稀疏模型没赢，先查路由是否真的用了这些参数。

aux 与 eval 语言 loss 分开报，训练 batch 的 $f_i$ 也不能当推理负载，推理 top-1 更尖，需要单独测。expert parallelism 还要计 decode 每步的 all-to-all 延迟，可联系 `openai-prefill-decode`。

相关：`nvidia-trillion-train`

## 追问

**没有 aux 能训吗？**
小 $N$、强噪声有时能，大 $N$ 几乎都会塌。aux、capacity、甚至 token 选择的 jitter 是一套。
**均衡一定均匀最好？**
不一定。数据本身就偏领域时，完全均匀会伤害质量。aux 是防死专家，不是业务 SLO。
**和 dropout 的差别？**
dropout 随机遮激活；塌缩是离散路由的赢家通吃，梯度根本到不了冷专家。
**共享专家？**
DeepSeek 一类把一部分 FFN 做成 always-on，减轻对 aux 的依赖。要声明这是另一条实现。

## 相关题

- [[google-gemini-moe]]：Google 版的 MoE 路由和容量题，aux loss 只是其中一环，更多讲 capacity 丢 token 和 decode 成本。
- [[google-moe-routing]]：路由、容量因子的实现细节，追问里也问到 aux 权重 $\alpha$ 怎么调。
- [[sys-ep-dispatch]]：负载不均落到推理时的样子，aux 只在训练生效，推理靠 EPLB 和部署表压热点。
