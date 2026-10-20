---
id: openai-moe-aux-loss
section: openai
order: 13
level: A
title: OpenAI：MoE 辅助损失和负载均衡，路由塌缩怎么发现
quick: "辅助损失把 token 分配比例 $f_i$ 和平均路由概率 $P_i$ 对齐，逼专家均匀吃 token。塌缩是几乎所有质量进同一个专家， 其它专家梯度消失。看专家占用直方图、路由熵、drop 率，不要只看 loss 下降。"
tags:
  - OpenAI
  - MoE
  - Load Balancing
  - Routing
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Switch Transformers — Scaling to Trillion Parameter Models with Simple and Efficient Sparsity
    url: https://arxiv.org/abs/2101.03961
    type: primary
  - title: ST-MoE — Designing Stable and Transferable Sparse Expert Models
    url: https://arxiv.org/abs/2202.08906
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 题怎么来的

万亿稀疏模型的公开教科书是 Switch / GShard / ST-MoE，不是某篇 OpenAI 技术报告里的结构图。GPT-4 是否 MoE 没有官方确认，面试里不当事实。问到负载均衡，我按 Switch 的 aux 损失（loss） 答，并声明这是训练稳定性，不是推理 cache。并行大图见 `nvidia-trillion-train`。

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

我会看的仪表：

1. 每层专家占用直方图，而不是一个全局平均值。塌缩常从某一层开始。
2. $L_{\mathrm{aux}}$ 和真实 $\mathrm{std}(f)$。aux 已经很小但 $\mathrm{std}(f)$ 很大，说明公式和你关心的均衡不是一回事，或者 dropless 实现没把 drop 算进 $f$。
3. dropped token 比例。capacity 太紧时「均衡」是靠扔掉 token 装出来的。
4. 验证集 vs FLOP 匹配的 dense 基线。稀疏模型不赢，先怀疑路由而不是数据。

常见误区是：把 aux 加进 eval loss 一起报；用训练 batch 的 $f_i$ 当推理负载（推理 top-1 更尖，要单独测）。推理若做 expert parallelism，还要看 逐 token 生成（decode） 步的 all-to-all 延迟，那是 `openai-prefill-decode` 的 MoE 版。

## 追问

- **没有 aux 能训吗？** 小 $N$、强噪声有时能，大 $N$ 几乎都会塌。aux、capacity、甚至 token 选择的 jitter 是一套。
- **均衡一定均匀最好？** 不一定。数据本身就偏领域时，完全均匀会伤害质量。aux 是防死专家，不是业务 SLO。
- **和 dropout 的差别？** dropout 随机遮激活；塌缩是离散路由的赢家通吃，梯度根本到不了冷专家。
- **共享专家？** DeepSeek 一类把一部分 FFN 做成 always-on，减轻对 aux 的依赖。要声明这是另一条实现。

## 相关题

- [[google-gemini-moe]]：Google 版的 MoE 路由和容量题，aux loss 只是其中一环，更多讲 capacity 丢 token 和 decode 成本。
- [[google-moe-routing]]：路由、容量因子的实现细节，追问里也问到 aux 权重 $\alpha$ 怎么调。
- [[sys-ep-dispatch]]：负载不均落到推理时的样子，aux 只在训练生效，推理靠 EPLB 和部署表压热点。
