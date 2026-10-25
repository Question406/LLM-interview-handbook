---
id: sys-rl-infra
section: systems
order: 16
level: S
title: 为什么 RL Systems 比 SFT 复杂？
quick: "监督微调（SFT）主要是读取固定数据，做前向和反向。强化学习（RL）还需要轨迹采样引擎、环境或评分器、轨迹缓存、策略与参考模型、可选的价值模型，以及权重同步和样本新鲜度管理。Agent RL 还要处理沙箱、浏览器、API 和长回合。"
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

RL 比 SFT 多了一条持续生成和消费数据的循环，还要保证数据与策略版本对得上。SFT 从磁盘读取固定 batch 后做前向、反向；on-policy RL 则先用当前策略生成轨迹、打分和训练，再把新权重同步回推理引擎。比如 trainer 已更新了策略，队列里却还积压旧轨迹，就需要按版本决定继续用、降权还是丢弃。

## 一步里有哪些组件

$$
\pi_{\mathrm{now}} \to \text{rollout} \to \text{reward / env} \to \text{buffer} \to \text{trainer} \to \pi_{\mathrm{new}} \to \text{sync}.
$$

| 组件 | SFT | RL |
| --- | --- | --- |
| 数据面 | 静态 dataset | 在线 generation，长度随机、可中止 |
| 打分 | token NLL | 验证器（verifier） / 奖励模型（RM） / 环境，常在 EOS 才出标量 |
| 模型角色 | 一份可训权重 | policy + 冻结 reference（+ 可选 价值评估模型（critic） / RM） |
| 版本 | checkpoint 即可 | 采样轨迹（rollout） 必须知道自己在用哪一版 $\theta$ |

HybridFlow（veRL）把这套拆成可组合的 dataflow：generation、奖励分数（reward）、advantage、update 可以换引擎、换并行，而不把「算法公式」和「谁占哪张卡」焊死。讲清 multi-controller + 混合部署即可，不必背框架 API。

Agent RL 再叠加 sandbox / browser / 搜索 API：一步动作的延迟从毫秒变成秒，失败要重试，episode 远长于单轮 chat。此时 rollout 往往才是吞吐瓶颈。

## 按瓶颈选择部署方式

长 思维链（CoT，即分步推理过程） 是自回归、逐 token 生成（decode） 偏 memory-bound；工具调用还要等外部世界。Trainer 可能闲等一批 $G$ 条完成。同步 on-policy 最干净：采完立刻训，freshness 好，GPU 利用差。异步能把 rollout 与训练重叠，但轨迹相对 $\pi_{\mathrm{now}}$ 变旧，重要性比 $\rho$ 偏离 $1$，方差和偏差一起来。

两种拓扑：

- **Colocated：** 同卡或同节点在推理图与训练图之间切换，权重共享或短拷贝，实现简单，显存毛刺和调度复杂。
- **Disaggregated：** rollout 池与 trainer 池独立扩容，有效吞吐更高，但要设计参数传输（NCCL / 共享存储 / 分片广播）和版本号。

100B 级权重做一次全量同步很贵，因此要一起权衡「同步频率 $\times$ staleness」，它直接影响系统吞吐和数据质量。

Buffer 里每条轨迹应带 `policy_version`。Gap 过大就降权、丢弃，或换更能容忍 off-policy 的算法。监控 KL、`logratio`、组内 奖励方差、超时与工具失败率。SFT 没有「这批数据已经不是当前策略」这个问题；RL 有。

## 追问

**vLLM rollout 权重怎么同步？**
周期性 `load` checkpoint、GPU/CPU tensor 直拷、参数广播或共享内存映射。全量百亿参数走 PCIe / 跨机都贵，因此要权衡步频与 staleness；只同步 LoRA 或增量切片能降流量，但版本语义必须仍一致。
**异步 RL 怎么控制 trajectory age？**
记录 version，设最大 gap；按 age 降权或丢弃；盯 KL / $\rho$ 的分位数；或换带 IS / 更稳 advantage 的目标。不能只看吞吐上涨。
**为什么很多栈坚持 vLLM / SGLang 做 rollout？**
训练框架的 generate 缺 paging、continuous batch 和投机解码；RL 的时间多花在 decode，值得用专用引擎，再单独解决 weight sync。
