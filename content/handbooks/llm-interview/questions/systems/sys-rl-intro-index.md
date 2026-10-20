---
id: sys-rl-intro-index
section: systems
order: 27
level: S
title: LLM RL 面试入门会问哪些「系统向」题？
quick: "算法岗很少追 NCCL / 1F1B。更常问：一步 GRPO 谁采样谁打分谁更新、为什么 采样轨迹（rollout） 用 vLLM、为什么重算 logprob、组大小 $n$、只训 response、训练看哪些曲线。先把这一圈讲顺，再提 HybridEngine。"
tags:
  - LLM RL
  - GRPO
  - 真题导航
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: 美团大模型研发二面-日常实习
    url: https://www.nowcoder.com/feed/main/detail/23e19d8300c54f2eb9ed9933aeaa5129
    type: candidate-first-hand
  - title: 滴滴RL实习生面经
    url: https://www.nowcoder.com/discuss/813460704786202624
    type: candidate-first-hand
  - title: DeepSeekMath / GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

算法岗把「RL 系统」答成 NCCL、1F1B、ZeRO stage，是最常见的跑偏。入门圈要的是一步训练在干什么：谁采样、谁打分、谁提供 KL、谁改权重、账本上的 logprob 从哪来。把通信答成主线，面试官会觉得你把 Infra 岗的题搬过来了。框架怎么选型（veRL / slime / TRL）另走 `sys-llm-rl-framework-index`，不要和这张入门图混成一篇。这张卡是地图：点击下面每条即可跳到专题卡。

## 先会画的一张图

按时间轴走，不要先默写 loss。先能在白板上画出五个角色，再允许被追公式。推荐顺序就是下面这串 id：

- 一步里 Actor / Ref / Reward / Rollout 各干什么、谁写权重：`sys-rl-grpo-loop-roles`。这张是总图，其它卡都从这里长出来。
- 为什么 采样轨迹（rollout） 用 vLLM / SGLang，而不是训练图自己 generate：`sys-rl-why-vllm-rollout`。问的是吞吐，不是「引擎 logp 更准」。
- 美团二面：为什么要重新 forward 算 logprob：`meituan-verl-recompute-logprob`。和上一张是一对：一个问快，一个问数。
- 美团二面：GRPO 哪个阶段最耗时：`meituan-grpo-stage-bottleneck`。先 profile 再改，不要默认 backward 慢。
- 损失为什么只回传到 response 文本处理单位（token）：`sys-rl-response-mask`。输入提示（prompt） 是观测，不是动作。
- 组大小 $n$ 为什么必须 $\gt 1$：`sys-rl-group-n`。$n=1$ 不是方差大一点，是优势未定义。
- 为什么 强化学习（RL） 之后回答越来越长：`sys-rl-longer-after-rl`。奖励形状和长度偏置，不是「模型更会思考」这么顺。

我会说：采样是推理、更新是训练、KL 看 Ref、分看 Reward。中间差一本账（logprob / 权重版本），不要把引擎打出来的数直接当 $\pi_{\mathrm{old}}$。三个 $\pi$ 必须分开：old 进 ratio，ref 进 KL，$\theta$ 在训练图上更新。漏掉「只训 response」或「组内才有优势」，后面每张专题卡都会穿。

## 接着会被追的

机制再往下半层，按公司面经抽查，不要假装每张都操过。对方公司出现过哪道，就深讲哪张：

- 阶跃：GRPO 优势怎么算、baseline 是组内均值：`stepfun-grpo-group-advantage`
- 字节：一组全对或全错为什么没梯度：`byte-grpo-all-same-zero-adv`；长尾拖 GPU 见 `byte-grpo-rollout-tail-gpu`
- 百度：$\pi_\theta$ / $\pi_{\mathrm{old}}$ / $\pi_{\mathrm{rollout}}$ 是谁：`baidu-grpo-policy-roles-offpolicy`；序列级损失怎么落到 token：`baidu-grpo-loss-agg`
- 滴滴：veRL 看哪些指标判断训练在走：`didi-verl-metrics`
- 美团：7B GRPO 显存花在哪：`meituan-grpo-7b-mem`，总账 `sys-rl-memory`；clip 为什么存在：`meituan-grpo-why-clip`
- 为什么 RL Systems 比 监督微调（SFT） 复杂：`sys-rl-infra`；权重怎么同步到引擎：`infra-rl-weight-sync`
- HybridEngine 解决什么：`sys-verl-hybridengine`。先讲放置，再讲 reshard，不要一上来背这个词。
- 2026 社区 35 题（算法 + Infra）对照：`pt-rl-algo-infra-bench-index`

蚂蚁会把 rollout / update batch 拧在一起问，见 `ant-verl-rollout-batch-accounting`。动态 batch 见 `sys-verl-dynamic-bsz`。这些已经偏工程会计，入门过关后再看。

## 这张卡怎么用

面试 15 分钟能把「先会画」那一圈讲顺，入门就算过关。「接着会被追」按对方公司抽一张深讲，不要把地图上的每条都展开。算法岗很少下到集合通信；一上来讲 PP bubble，方向就偏了。准备时分三步：先能默画角色和时间轴；再能解释「为什么不用训练图 generate、为什么还要重算 logp」这一对；最后按面经补 $n$、mask、显存、指标。框架对照、slime 字段、FSDP vs Megatron 全部推到 `sys-llm-rl-framework-index`。

三种串台最常见：一是被问「讲一下 GRPO」时开始讲 HybridEngine 的 reshard，角色还没画完；二是被问「为什么用 vLLM」时答「因为 logprob 准」，和重算 logp 那张卡直接打架；三是被问 $n$ 时把它说成 global batch。先定位对方问的是哪一圈，再跳对应 id。面试官从美团二面来，优先准备重算 logp 和阶段耗时；从滴滴来，准备指标；从字节来，准备零梯度。

开场 15 分钟用角色圈就够；对方拿出 veRL 配置再进会计和 HybridEngine。角色圈五张要能画出时间轴；吞吐圈两张成对，把「快」和「准」拆开；优势圈共用「没有组内对照就没有 GRPO」；显存圈只在被问「7B 怎么放」时展开。

## 追问

- **最低闭环是哪几张？** `sys-rl-grpo-loop-roles` → `sys-rl-why-vllm-rollout` → `meituan-verl-recompute-logprob` → `sys-rl-response-mask` → `sys-rl-group-n`。这五张能撑住大多数算法岗开场。
- **什么时候才提 HybridEngine？** 角色和时间轴讲顺之后。先放置，再 reshard。先背这个词，面试官会追「那 OpenRLHF 为什么分卡」，见 `sys-verl-hybridengine`。
- **和框架导航怎么分工？** 本卡问一步在干什么；`sys-llm-rl-framework-index` 问 veRL / slime / TRL 怎么选型。两张都是地图，不要在同一段里既讲角色又讲 Hydra 字段。
- **算法岗会不会问 ZeRO-3？** 会问显存花在哪（`meituan-grpo-7b-mem` / `sys-rl-memory`），很少下到 all-gather 细节。显存答完就停，别自己滑到混元那张 72B 估算，除非对方是 Infra / 训练系统岗。
- **开场怎么收？** 采样推理、更新训练、三个 $\pi$ 分开、只训 response、组内才有优势。中间差一本账：引擎 logp 不能直接当 $\pi_{\mathrm{old}}$。
- **clip fraction 一直是 0 看哪张？** `sys-rl-fw-clip-zero`。那已经不是入门闭环，是训练没在走的诊断。
- **被问「讲一下 GRPO」先翻哪张？** 先 `sys-rl-grpo-loop-roles`，不要先背 loss，也不要先讲 HybridEngine。角色画完再允许被追公式和放置。
