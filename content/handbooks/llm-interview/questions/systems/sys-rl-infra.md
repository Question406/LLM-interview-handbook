---
id: sys-rl-infra
section: systems
order: 16
level: S
title: 为什么 RL Systems 比 SFT 复杂？
quick: >-
  SFT 是 dataset 进 forward/backward。RL 还要 rollout engine、environment/verifier/RM、trajectory
  buffer、policy/reference/value、weight sync 和 freshness。Agent RL 再加 sandbox/browser/API 和长
  episode。
tags:
  - RL Infra
  - Post-training
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: HybridFlow / veRL
    url: https://arxiv.org/abs/2409.19256
    type: primary
---

这块容易把 RL 训练画成「换一个 loss 的 SFT」。SFT 的数据在磁盘上已经写死，一步就是取 batch、前向、反向。On-policy RL 的数据是**当前策略刚生成的轨迹**，还要打分、对齐版本、再写回推理引擎。系统多出来的不是一行公式，而是一条带状态的环。

## 1. 典型 loop 比 SFT 多四类组件

$$
\pi_{\mathrm{now}} \to \text{rollout} \to \text{reward / env} \to \text{buffer} \to \text{trainer} \to \pi_{\mathrm{new}} \to \text{sync}.
$$

| 组件 | SFT | RL |
| --- | --- | --- |
| 数据面 | 静态 dataset | 在线 generation，长度随机、可中止 |
| 打分 | token NLL | verifier / RM / 环境，常在 EOS 才出标量 |
| 模型角色 | 一份可训权重 | policy + 冻结 reference（+ 可选 critic / RM） |
| 版本 | checkpoint 即可 | rollout 必须知道自己在用哪一版 $\theta$ |

HybridFlow（veRL）把这套拆成可组合的 dataflow：generation、reward、advantage、update 可以换引擎、换并行，而不把「算法公式」和「谁占哪张卡」焊死。我会讲清 **multi-controller + 混合部署**，不必背框架 API。

Agent RL 再叠加 sandbox / browser / 搜索 API：一步动作的延迟从毫秒变成秒，失败要重试，episode 远长于单轮 chat。此时 rollout 才是真正的吞吐瓶颈。

## 2. 墙钟往往卡在 generation，不是 backward

长 CoT 是自回归、decode 偏 memory-bound；工具调用还要等外部世界。Trainer 可能闲等一批 $G$ 条完成。同步 on-policy 最干净：采完立刻训，freshness 好，GPU 利用差。异步能把 rollout 与训练重叠，但轨迹相对 $\pi_{\mathrm{now}}$ 变旧，重要性比 $\rho$ 偏离 $1$，方差和偏差一起来。

两种拓扑：

- **Colocated：** 同卡或同节点在推理图与训练图之间切换，权重共享或短拷贝，实现简单，显存毛刺和调度复杂。
- **Disaggregated：** rollout 池与 trainer 池独立扩容，有效吞吐更高，但要设计参数传输（NCCL / 共享存储 / 分片广播）和版本号。

100B 级全量同步一次很贵，所以「同步频率 $\times$ staleness」是一等一的产品决策，不是调参边角。

## 3. 还要管 freshness 与正确性

Buffer 里每条轨迹应带 `policy_version`。Gap 过大就降权、丢弃，或换更能容忍 off-policy 的算法。监控 KL、`logratio`、组内 reward 方差、超时与工具失败率。SFT 没有「这批数据已经不是当前策略」这个问题；RL 有。

## 追问

- **vLLM rollout 权重怎么同步？** 周期性 `load` checkpoint、GPU/CPU tensor 直拷、参数广播或共享内存映射。全量百亿参数走 PCIe / 跨机都贵，因此要权衡步频与 staleness；只同步 LoRA 或增量切片能降流量，但版本语义必须仍一致。
- **异步 RL 怎么控制 trajectory age？** 记录 version，设最大 gap；按 age 降权或丢弃；盯 KL / $\rho$ 的分位数；或换带 IS / 更稳 advantage 的目标。不能只看吞吐上涨。
- **为什么很多栈坚持 vLLM / SGLang 做 rollout？** 训练框架的 generate 缺 paging、continuous batch 和投机解码；RL 的时间多花在 decode，值得用专用引擎，再单独解决 weight sync。
