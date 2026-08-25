---
id: align-best-of-n
section: alignment
order: 13
level: A
title: 对齐：Best-of-N 推理时对齐，成本与 RM over-optimize
quick: >-
  BoN 从同一策略抽 $N$ 条，用 RM 挑最高。它把对齐从训练挪到推理：不更新权重，但 decode 近线性变贵，且 $N$
  大时 proxy 分涨、gold 掉。前缀 KV 可共享，不能把 $N$ 当成免费质量旋钮。
tags:
  - OpenAI
  - Inference
  - Best-of-N
  - Reward Model
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Scaling Laws for Reward Model Overoptimization
    url: https://arxiv.org/abs/2210.10760
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
---

OpenAI 对齐和推理岗都爱问 Best-of-N：InstructGPT 用它当 RLHF 基线；Gao 等人把「加大 $N$」画成和加大 RL 步数同类的 overoptimization。不是某次现场逐字题。我会按「质量从哪来、钱花在哪、何时分叉」答，并接到 `align-reward-model`。

## 它在对什么齐

策略 $\pi$ 先按正常温度采样 $N$ 条 $y_1,\ldots,y_N$，奖励模型给分，返回 $\arg\max_i r_\phi(x,y_i)$。权重不变，变的是推理分布：更集中到 RM 喜欢的区域。这是推理时对齐，和 SFT / DPO / PPO 改 $\pi$ 互补。$N=1$ 就是原策略。

和 beam 不同：beam 优化的是模型自己的 logp，不是 $r_\phi$。和拒绝采样不同：拒绝采样有阈值，BoN 是固定预算取最大。DPO 的 implicit reward 也能打分，同一 $x$ 下 $Z(x)$ 公共，见 `align-dpo`；换一张和训练无关的 RM 更适合当验收，避免自己给自己挑。

```python
def best_of_n(logps_rm, n):
    # logps_rm: [B, N]  scores from frozen RM
    idx = logps_rm.argmax(dim=-1)
    return idx
```

可验证任务用对错 / 单测当 $r$，BoN 接近搜索。开放对话只有 proxy RM，搜索的是 RM 的缝，不是真目标。

## 成本：不是「再调一个温度」

朴素实现是 $N$ 次独立 decode，墙钟和 token 都近线性。对话场景 prompt 很长：系统提示和历史应走前缀 KV 复用，只对分叉后的 response 付费，见 `sys-prefix-cache`。即便如此，decode 仍是 $N$ 路。连续批处理能把 $N$ 路塞进同一 iteration，但显存按活着的序列数涨，见 `openai-continuous-batching`。

预算写法：先定 token 上限，再反推 $N$ 和最大长度。$N=64$ 配长回答，会把 p95 和 KV 打爆。产品上常见折中：免费档 $N=1$，难查询或付费档小 $N$，且对短答案提前停。别在面试里甩单价；说吞吐、p95、KV 页数。

多样性不够时加大 $N$ 是浪费：温度太低，64 条近重复，RM 挑的还是同一句话。先看 unique n-gram，再加 $N$。

## Over-optimize：Gao 的分叉

proxy RM 不是 gold。$N$ 增大时，训练 RM 分单调往上，held-out RM 或人工分会先升后降。这和 RL 步数加大是同一条 Goodhart 曲线，只是发生在推理期，见 `align-reward-hack`。长度几乎一定被选中：更长更容易撞上 RM 喜欢的 n-gram，见 `align-length-bias`。

护栏：

- 用 **另一张** RM 或人抽查看分叉，训练 RM 不能同时当选模器和验收器。
- 长度惩罚、对 $r$ 做长度归一，再 argmax。
- 把 SFT 样本强制留在候选里，防止完全离开参考文风。
- $N$ 当超参扫，对着 gold 曲线停，不要对着 proxy 新高停。

BoN 还能当离线造偏好的办法：同一 prompt 抽一堆，RM 排序产生 pair，再拿去 DPO。那是在用 proxy 写训练集，污染和 overoptimize 会进权重，比纯推理 BoN 更危险，要和 `align-eval-contam` 同一纪律。

## 追问

- **$N$ 越大越好吗？** 只对 proxy。gold 有拐点，过了就是刷 RM。
- **和 RL 比谁更划算？** 流量小、要快速试奖励：BoN。流量大、同一奖励要摊到每次请求：把能力训进 $\pi$。
- **过程奖励能 BoN 吗？** 可以按步骤分搜，见 `align-process-reward`。步骤 RM 同样会过优化。
- **隐式 DPO 奖励做 BoN？** 同一 $x$ 可以。切勿跨 prompt 比绝对 $\log(\pi/\pi_{\mathrm{ref}})$。
