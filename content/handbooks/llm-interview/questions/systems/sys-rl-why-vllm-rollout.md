---
id: sys-rl-why-vllm-rollout
section: systems
order: 29
level: S
title: 为什么 LLM RL 的 rollout 要用 vLLM，而不是训练图自己 generate？
quick: >-
  GRPO 每步要为每个 prompt 采多条长回复，生成是 decode、吃 KV，占墙钟大头。vLLM / SGLang
  用 PagedAttention 和连续 batching 把这条路径做快。训练图的 generate 没有这套调度，同卡吞吐差一截。采完仍要用训练图重算
  logprob。
tags:
  - LLM RL
  - vLLM
  - Rollout
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: GRPO with vLLM online training (TRL)
    url: https://huggingface.co/learn/cookbook/grpo_vllm_online_training
    type: primary
  - title: vLLM PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
---

别说「vLLM 的 logprob 更准所以拿去更新」。选推理引擎是因为 **生成是墙钟大头**，训练图的 `generate` 不会做 serving 那套 decode 调度。数值上反而更不能信引擎 logp，ratio 必须回到训练图，见 `meituan-verl-recompute-logprob`。这题和「为什么重算 logp」是一对：一个问吞吐，一个问数学。我先承认引擎为速度牺牲了数值对齐，再讲 PagedAttention，才不会在下一问里自相矛盾。

## 为什么生成会占满一步

SFT 是数据已在磁盘上，做正反向。GRPO / PPO 是在线的：每一步都要现采轨迹，而且一条 prompt 采 $n$ 条、推理还可能很长。Decode 每步只追加一个 token，却要反复读权重和历史 KV，算术强度低、吃带宽，见 `sys-prefill-decode`。现有经验仍然成立：墙钟往往大部分花在采样上，不是 backward。组越大、响应越长，这个比例越高。优化 backward 的 fused kernel、改 ZeRO 桶，对一步墙钟的帮助常常小于把 rollout 换成 vLLM / SGLang。先 profile 再决定改训练还是改生成，不要默认「RL 慢就是并行没配好」。

训练框架里的 `model.generate` 能出字，但按静态 batch、KV 连续存放。组内长短不齐时大量 padding；一条先结束不能立刻把槽位让给下一条。GPU 看着占着，有效 token/s 上不去。这不是实现懒，是训练运行时根本没有为「不等长、持续有请求进出」的 decode 设计过调度器。即便手写一个动态 mask，没有分页 KV 也会按最大长度预留，组一增大就 OOM。PagedAttention 要解决的是 **显存形状和调度** 两件事，缺一都会让 rollout 回落到训练 generate 的吞吐。

## 推理引擎快在哪

vLLM / SGLang 把这条路径当成 serving：

- **PagedAttention**：KV 按页分配，结束的序列立刻释放页，避免按最大长度预留导致显存碎片。
- **Continuous batching**：一步结束就插入新序列，短回复不再拖着长回复的 padding。
- CUDA graph、prefix cache、chunked prefill 等，进一步把 decode step 的内核开销打下去。

这三件套解决的是 decode 的 **内存形状与调度**，不是把 matmul 换成更快的算法。所以换引擎之前先确认 profile 热点在 generate 而不是 backward 或 verifier；若热点在同步权重，换 vLLM 也救不了，应去看 `infra-rl-weight-sync`。RL 的 rollout 还有组内 $n$ 条、变长 CoT，比普通聊天更吃连续 batching，这正是训练 generate 最不擅长的负载。

TRL、veRL、OpenRLHF、slime 把 rollout 接到这类引擎，不是炫技：同卡用训练图硬 generate，一步会慢到实验跑不动。引擎选型（vLLM vs SGLang）见 `sys-verl-vllm-vs-sglang`；动机都是吞吐，不是换一套更「正确」的 logp。团队 serving 已经是 SGLang，RL 用同一引擎还能少两套数值差异；只有数学 GRPO、镜像里已经是 vLLM，就不必为了「更现代」而换。

采样仍要用训练图重算 logprob：paged attention、chunked prefill、不同 TP、量化（尤其 FP8 rollout）都会让 token logp 和 FSDP/Megatron 差出能进 $\rho$ 的误差。正确拆法是 **采样用快引擎，ratio / KL 用训练图**。

## 同卡还是分卡

两种摆法面试提清楚即可，细节见 `sys-verl-hybridengine`、`slime-colocate-vs-split`：

- **同卡（HybridEngine / `--colocate`）。** 采样完卸 KV，把权重交回训练布局或把推理进程 offload 掉。省卡，一步内训推串行，要切换成本。
- **分卡。** vLLM / SGLang 常驻一套 GPU，训练另一套，按步同步权重。吞吐更好扩，但多一份模型、要管版本和带宽（`infra-rl-weight-sync`、`slime-weight-sync`）。

同卡方案里引擎快，不代表一步快：卸 KV 和 reshard / offload 可能吃掉省下来的 decode 时间。分卡方案里引擎可以一直 CUDA graph 着，但权重来晚了仍要空等。选型要对着「一步墙钟拆分」说话：generate、sync、backward 各占多少，而不是对着框架 logo。生成占比不高时，先别为了 vLLM 再拆一套集群。

不要把「用了 vLLM」理解成已经做了异步 RL。Continuous batching 是引擎一步之内的请求交错；异步 RL 是 trainer 与 rollout 之间的流水线，带 policy staleness，见 `sys-rl-infra`。

## 训练图 generate 慢在哪

组内 $n$ 条回复长度差一个数量级时，静态 batch 必须 pad 到最长。先结束的序列仍占着整行 KV 和计算槽，直到最长那条写完。PagedAttention + continuous batching 把结束的页还给后来者，这才是「同卡吞吐差一截」的来源，而不是 vLLM 的 matmul 魔法更快。长 CoT、组采样越大，这个差距越明显；短 SFT 式固定长度反而看不太出来，所以有人会误以为「训练 generate 也够用」。

切换成本也要算进墙钟：同卡方案每次 rollout 前后要卸 KV、换布局或 offload 进程，这部分不是 decode 本身，但会随同步频率线性涨。分卡把切换换成权重传输。选引擎之后仍要选放置，见 `sys-verl-hybridengine`。Profile 时用分段计时：`generate`、`update_weights`、`recompute_logp`、`backward` 四段。只看到总 step time 下降，说不清是 vLLM 快了还是同步碰巧变少。vLLM 解决 generate 段；sync 看放置；recompute 看训练图；backward 才轮到并行策略。四段里任何一段都能让「换了 vLLM 还是慢」成立，所以不要把引擎当万能加速器。采样用快引擎，ratio 用训练图，放置另选题。不要在同一句里承诺「vLLM 又快又数值对齐」。那两件事正好冲突，下一问重算 logp 就会把这句话拆掉。引擎可以量化、可以 PagedAttention，训练图必须可导、可复现；把这两条要求绑在同一个 generate 调用上，是训练框架自己 decode 又慢又不准的根源。

## 追问

- **HF `generate` 加 `use_cache=True` 能不能凑合？** 能出数，组内 padding 和无法连续补位仍在。小模型玩具实验可以，正经 GRPO 长 CoT 会先被采样墙钟打死。Cache 只解决逐步追加，不解决调度。
- **为什么还说「采完仍要重算」？** 引擎为吞吐牺牲了和训练完全对齐的算子与精度。重算不是为了省显存，HybridEngine 才是。把两件事说成一件，下一问「那为什么还 HybridEngine」就会答穿。
- **SGLang 是不是同一逻辑？** 是。slime 默认 SGLang 也是因为 decode 调度，不是因为可以跳过 Megatron logp。多轮工具、约束解码时 SGLang 更常被点名，见 `sys-verl-vllm-vs-sglang`。
- **n 很大时引擎够不够？** 可能还要看组内长度尾部、KV 页是否碎片、以及是否 PD 分离。先确认瓶颈在 decode 而不是权重同步或 verifier。组内一条超长回复拖住整组，continuous batching 也只能部分缓解，动态 batch 和长度过滤要一起上。
