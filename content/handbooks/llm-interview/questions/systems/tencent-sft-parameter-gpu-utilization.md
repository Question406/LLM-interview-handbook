---
id: tencent-sft-parameter-gpu-utilization
section: systems
order: 104
level: S
title: 腾讯 WXG：如何估算 SFT 参数量与显卡利用率？
quick: >-
  先按 dtype 计算参数、梯度和 optimizer state，再加 activation、KV / 临时 buffer 与分片开销。吞吐利用率同时看
  tokens/s、MFU、显存峰值、通信等待和 data stall。给出假设、分布式策略和测量口径，而不是只报显存除以显存容量。
tags:
  - Tencent
  - WXG
  - SFT
  - Training Systems
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯WXG暑期实习面经-大模型算法（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/d3c8e5962e1b43aab21aa5af52423b56
    type: candidate-first-hand
  - title: ZeRO
    url: https://arxiv.org/abs/1910.02054
    type: primary
---

这块容易把「参数量」理解成「显存占用 $\div$ 2 字节」，再把「利用率」理解成 `nvidia-smi` 的 occupied%。白板要先声明假设：dtype、是否全参 AdamW、world size、ZeRO/TP/PP、有没有 checkpoint。数字对不上，多半是漏了 optimizer 或 activation，而不是算术错。利用率要分显存占用和计算 MFU，高占用可以很慢。这题常和 ZeRO 分档连问，分片表见 `tencent-zero-123`，bytes/param 总账见 `sys-memory`。

## 真题记录

- 公司：腾讯 WXG
- 团队 / 岗位：大模型算法暑期实习
- 届别 / 流程：暑期实习；具体届别与轮次原帖未披露
- 面试时间：原帖未披露；帖子发布于 2026-05-25
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位、实习性质与发帖时间明确，届别、轮次和面试日期未披露）
- 原始措辞：**“算模型 SFT 的参数量大小及显卡利用率”**

## 参数状态先按 bytes/param 拆

全参 mixed-precision AdamW 常见五份：BF16 权重 $2$、梯度 $2$、FP32 master $4$、Adam $m/v$ 各 $4$，合计约 $16$ bytes/param。对 $N$ 参数，未分片约 $16N$ 字节；7B 量级约 $112\,\mathrm{GB}$，远不是「$7\mathrm{B}\times 2=14\,\mathrm{GB}$」。LoRA 时这份账按可训参数算，底座仍可能占一份 BF16。然后必须加 activation（$\propto B\cdot T\cdot L\cdot d$，checkpoint 可换重算）、attention 临时量、embedding / logits、通信 buffer、allocator 碎片。

ZeRO-1 只分优化器，ZeRO-3 / FSDP 连参数也分，但 activation 仍按本地 micro-batch 全量在。不说 world size 和策略，每卡数字没有定义。监督微调（SFT） 还多一个 packing / padding 口径：名义 batch 相同，有效 token 数可以差一倍，显存峰值跟最长序列走。我会把「参数量」和「训练显存」拆开说：前者是 $N$ 和 dtype，后者是状态 + 激活 + 碎片。 混元 72B 的代入例见 `tencent-zero3-qwen72b-mem`。

## 利用率不是显存占用率

显存利用率只是 `allocated / capacity`，高不代表快，碎片高还会假高；等通信时占用也可以 90%。计算侧用 MFU：实测 FLOPs 对 GPU 峰值。Transformer 粗估每 token 前反向约 $6N$ FLOPs（再加 attention 的 $O(T^2)$）。结合 tokens/s、step time、SM occupancy、all-reduce 等待、data loader stall、loss scaling 的溢出。

padding / 变长会让名义 batch 下的有效 token 差一截，packing 才能把 MFU 从「看起来在算」拉到「有效算」。回答给闭环：理论 token FLOPs → profiler 核对 → 指出是通信、数据还是激活在拖。低于 20% 先查这三件事，而不是先加卡。SFT 和预训练的差在序列不齐、常有 mask；LoRA 时优化器很小，MFU 可能被小 kernel 开销打掉，不要用预训练的「正常区间」硬套。 除了 DeepSpeed 还能靠哪些手段把瓶颈拆开，见 `tencent-beyond-deepspeed`。

白板顺序我一般固定：先报 $N$ 和 dtype，再写 16 bytes/param 表，再问 $D$ 和 ZeRO stage，再加 activation 的 $B,T,L$，最后才谈 MFU。颠倒顺序就会被追「那你这个 40GB 包不包含激活」。SFT 特有的坑是变长：同一名义 batch，pack 前后峰值和有效 token 都可以差一倍，所以「每卡几条」不能当利用率的分母。分母用有效 token 或实测 FLOPs。loss 在降但 tokens/s 很低，优先查 pad、checkpoint 过密、通信；占用 90% 但 MFU 20%，优先查等待而不是再买更贵的卡。

参数量和利用率是两道题写在同一句里，必须拆开答。参数量问的是 $N$、dtype 和状态怎么分；利用率问的是这些状态放进去之后 GPU 有没有在算有效 token。假设说不清时，主动问全参还是 LoRA、有没有 packing，比猜一个数字安全。占用率和 MFU 同时报：一个看放得下，一个看算得动。

## 追问

- **为什么不能用 `nvidia-smi` 当利用率？** 它看的是占用，不是 FLOPs。等通信、等数据时占用也可以很高。要 MFU 和 tokens/s。
- **SFT 和预训练的账差在哪？** SFT 序列更不齐、常有 packing / mask；LoRA 时优化器只挂 adapter。口径要先说全参还是 PEFT。
- **ZeRO-3 后每卡参数怎么算？** BF16 权重约 $2N/D$，Adam 状态同样 $/D$，但 all-gather 时有峰值；activation 不分。
- **MFU 多少算正常？** 大模型大 batch 常见 30% 到 50%；低于 20% 先查 padding、通信、checkpoint 过密，而不是先加卡。
- **参数量和显存为什么对不上？** 漏了 $m/v$、master、activation 或碎片。先写 bytes/param 表，再代入 $N$ 和策略。
- **有效 token 和名义 batch 为什么要分开报？** 变长 + pad 会让「每卡 4 条」的 MFU 看起来像算满，实际大量在算 pad。packing 前后都要量一次。
- **白板先写哪一行？** $N$ 和 dtype → 16 bytes/param → 除以 $D$ → 再加激活。先报一个 GB 一定会被追假设。
- **activation checkpoint 对利用率的影响？** 显存降、计算重复前向，MFU 分母仍是峰值 FLOPs，分子多了重算。占用好看、step time 变长是预期，不要当成故障。
- **占用率和 MFU 为什么要同时报？** 一个看放得下，一个看算得动。占用 90%、MFU 20% 说明在等，不是还差一张卡。只报其中一个，原话里的「参数量」和「利用率」只答了一半。
- **面试官不给 $D$ 和是否 packing 怎么办？** 主动问。不先问假设就报 GB，数字一定会被改条件打穿。问清全参还是 LoRA、有没有 packing，再代入 bytes/param 表。
- **7B 全参未分片先报哪两个数？** 权重约 14GB，Adam 状态约 112GB。14GB 是推理直觉，112GB 才是训练起点，然后再除 $D$、加激活。这两个数说反了，后面利用率没有意义。
- **packing 为什么既影响显存又影响 MFU？** 显存跟最长序列走，MFU 跟有效 token 走。不 pack 时两者一起差；pack 之后占用更稳、有效 FLOPs 上升，这是 SFT 相对预训练最该主动提的口径。
- **原话里两个词分别对应哪本账？** 「参数量」对应 $N$ 和状态分片；「显卡利用率」对应 MFU 与有效 token。两本账都要报，只报显存占用没有回答利用率。
