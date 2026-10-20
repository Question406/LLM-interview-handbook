---
id: google-gemini-longctx
section: google
order: 15
level: S
title: Google：Gemini 长上下文怎么评、位置偏差和成本，别只报 1M
quick: "窗口数字只是上限。评测按长度桶和证据位置切，默认失败是中间丢掉。成本上注意力 FLOPs 仍是 $O(T^2)$，逐 token 生成（decode） 每步读整段 KV。针能捞出来，不等于产品能用，也不等于 serving 算得过来。"
tags:
  - Google
  - Gemini
  - Long Context
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Gemini 1.5 — Unlocking multimodal understanding across millions of tokens of context
    url: https://arxiv.org/abs/2403.05530
    type: primary
  - title: Lost in the Middle — How Language Models Use Long Contexts
    url: https://arxiv.org/abs/2307.03172
    type: primary
  - title: RULER — What's the Real Context Size of Your LLM?
    url: https://arxiv.org/abs/2404.06654
    type: primary
---

Gemini / PaLM 研究岗爱问「1M 上下文你怎么证明它真的在用」。1.5 技术报告把窗口推到百万量级、实验里到千万，那是产品叙事。面试拆成三笔账：评测切什么、位置偏差怎么现、输入预填充（prefill，即处理输入并建立缓存） / 逐 token 生成（decode） / KV 各贵在哪。注意力 IO 见 `google-flash-attention`，跨设备分块见 `google-block-attn`，KV head 见 `google-gqa-mqa`。

## 评测：针只是回归

Needle-in-a-haystack 几乎是复制粘贴：干草里埋一句，问这句是什么。Gemini 1.5 在百万 token 上接近饱和，只能说明 RoPE / 窗口实现没把远处 key 丢掉。产品任务不是抄一句。

我会按失败模式切片，每条 case 带元数据，报表是一张表：

- 长度桶：32k / 128k / 1M 分开报。短窗口能做，不代表长窗口还在用证据。
- 证据位置：头、中、尾。Lost-in-the-middle（Liu et al.）是默认先验：中间比两端差。会议纪要、仓库里真正的决定经常在中间。
- 跳数：答案要拼两处以上。单针测的是检索，多跳才接近推理。
- 多针 / 干扰针：RULER 一类。会抄最近那句，不等于会选对的那句。
- 拒答：证据不在窗口里时该说没有。流畅编造比答错更糟。
- 模态：视频、PDF、代码仓和纯文本不是同一个 $T$。视觉 token 怎么吃预算见 `google-gemini-mm`。

主指标用归因（句子能否在证据里定位）和任务 F1，生成流畅度当辅助。BLEU 对长文档问答几乎没用。公开小说或著名仓库当评测，模型可能背过；内部时间切分或合成的「中间才出现的约束」更可信。

## 位置偏差：先承认，再量

Transformer 对位置不是平的。训练分布里重要信号爱出现在开头（系统提示）和结尾（当前问题），中间是粘贴进来的文档。RoPE 外推、位置插值、把指令复制到两端，都是在补这个偏置，不是魔法。

白板说：先画准确率对位置的热力图，再谈改位置编码。热力图在某一深度突然变黑，优先查 mask、chunk 边界、和 KV 是否被截断，别先换模型。Gemini 报告里长上下文更稳，是训练时就喂了长序列；面试不要把「1.5 很强」说成注意力变成线性了。公式还是 $QK^\top V$，变的是训练分布和 IO 实现。

检索加短窗口经常在 32k 就赢过 naive 全塞 1M，因为噪声少、位置偏置轻。长上下文的正当用途是检索漏召回的那一段、以及多份证据必须同时看见。两者叠，不互相取消。

## 成本：1M 是钱

令层数 $L$、头维 $d$、KV head 数为 $H_{\mathrm{kv}}$。Prefill 注意力 FLOPs 仍是 $\Theta(L T^2 d)$ 量级，FFN 是 $\Theta(L T d_{\mathrm{ff}} d)$。$T$ 从 8k 到 1M 涨 125 倍，二次项先炸掉。Flash 式核砍的是 HBM 往返，不是把二次变成线性。

Decode 更狠。每步 $T_q=1$，但要读历史 KV：

$$
\mathrm{KV\ bytes} \approx 2 \cdot L \cdot T \cdot H_{\mathrm{kv}} \cdot d \cdot \mathrm{bytes}
$$

口算一笔：若 $L=48$、$T=10^6$、$H_{\mathrm{kv}}=8$、$d=128$、bf16，单请求 KV 大约 $2\cdot 48\cdot 10^6\cdot 8\cdot 128\cdot 2 \approx 197\,\mathrm{GB}$。还没算权重。并发立刻变成「HBM 里能塞几段 cache」，不是「模型有 1M 窗口」。GQA / 量化 cache / 前缀缓存是一等杠杆；窗口数字不是。

Serving 还会被 prefill 尾巴拖死：用户贴一整本仓库，首 token 延迟跟 $T^2$ 走。产品默认应是检索或分段摘要，1M 当兜底。面试主动报这条，比背「我们支持 1M」加分。

常见误区是：把 needle 准确率当长上下文能力；说 1M 所以注意力是线性的；只报窗口、不报每千 token 价格和 KV 字节。

## 追问

- **Needle 完全没用吗？** 有用，当实现回归：位置 $\times$ 长度热力图，抓 RoPE、mask、chunk 边界。它不是产品验收。
- **10M 和 1M 差在哪？** 同一套评测切片再拉长。实验能跑不等于默认配额；成本按 $T^2$ 和 KV（decode 线性）涨，产品要单独定价。
- **位置编码怎么补？** 训练就用长序列最稳。推理期插值是补丁，要在中间位置重测，不要只测尾巴。
- **为什么还要检索？** 窗口是上限，不是质量保证。检索控制权限和噪声；长上下文处理漏召回和必须同时看见的多份证据。
