---
id: sys-moe-train-infer-routing-mismatch
section: systems
order: 35
level: A
title: 训练和推理的 MoE 路由不一致会怎样？怎么检测？
quick: >-
  训推路由配置或精度不同，同一前缀就可能选到不同 expert，输出和 logprob 都会漂。固定一批 prompt，对比 trainer eval 与
  serving 的专家份额直方图、输出 KL、drop 率和 top-1 翻转率，再对齐噪声、bias、router 精度及
  capacity。sampling 温度改变不了已经选定的专家。
tags:
  - MoE
  - Routing
  - Train-Serve Gap
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: DeepSeek-V3 Technical Report
    url: 'https://arxiv.org/abs/2412.19437'
    type: primary
---

训推路由不一致会让同一个前缀走进不同子网络，后续输出和 logprob 都可能改变。MoE 的选择是离散 top-$k$，比如量化让两个接近的 affinity 分数换了顺序，专家集合就可能翻转。检测时要固定输入，对照训练图 eval 和推理引擎的路由及输出；噪声、bias、精度和 capacity 都要逐项核对。

## 哪些配置会让专家选择改变

- **训练专用噪声**：jitter / noisy top-$k$ 只在 train 开，eval 关。这是刻意的，但要冻结一份「推理路由」做回归，不能拿带噪声的 train 直方图当上线基线。
- **Expert bias**：训练逐步更新 $b_i$，推理若清零或用另一套 checkpoint，top-$k$ 集合会变。应把末期 bias 写进权重，或明确推理不再更新。
- **精度**：训练 FP16/BF16 router，推理 INT8/FP8。Affinity 排序对小扰动敏感，top-$k$ 容易翻盘。Router 常单独保高精度。
- **Capacity / drop 策略**：训练 CF 大、几乎不丢；推理为 throughput 把 CF 砍小。被丢弃的 token 等于这一层 MoE 被跳过。
- **RL 两套引擎**：sampling 轨迹（rollout） 用 vLLM/SGLang 融合 kernel，trainer 用 Megatron 自己的 dispatch。这是字节 GSPO 卡（`byte-moe-rollout-routing-gspo`）的工程背景：算法用 sequence-level ratio 降局部路由噪声，系统仍要对齐实现。本题强调一致性工程，不是再讲一遍 GSPO。

## 用固定输入分清路由漂移和数值漂移

固定一批 prompt，分别在 trainer eval 模式和 serving 上记录：

1. 每层每个 expert 的 token 份额直方图（JS / TV 距离）。
2. 最终 logits 或 hidden 的 KL / cosine。
3. drop 率、以及 top-1 expert 翻转率。

如果直方图先漂、KL 随后漂，优先查路由；如果直方图稳定、KL 仍然很大，再查量化、融合 kernel 和数值误差。

## 追问

**能不能靠温度把推理路由「软回去」？**
温度改的是 sampling，不改已经离散化的 expert 选择。要对齐的是 router 输入输出，不是 decoder 温度。
**Shared expert？**
共享专家每 token 都走，能缓冲一部分 routed expert 翻盘，但不能当对齐的替代。
- **上线 checklist**：同一份 bias、同一份 capacity 配置、router 精度、以及一份金标 expert-id dump。
**RL 更新这一步怎么钉住路由？**
GSPO 降的是 token 级 $\rho$ 方差，对齐不了走错的专家。Keep Routing / R3 重放推理引擎路径，R2 重放训练图旧策略路径，见 `pt-r3-routing-replay`。
