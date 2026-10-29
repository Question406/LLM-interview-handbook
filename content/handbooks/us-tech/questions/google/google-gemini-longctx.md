---
id: google-gemini-longctx
section: google
order: 15
level: S
title: Google：Gemini 长上下文怎么评、position bias 和成本，别只报 1M
quick: >-
  我会按长度、证据位置和任务难度评测长上下文，并同时核算 prefill、decode 和 KV 成本。Needle
  能被找出来，只能证明基础检索能工作，中间证据、多跳推理和缺证据时的拒答还要单独测。attention FLOPs 仍是 $O(T^2)$，decode
  每步还要读历史 KV。
tags:
  - Google
  - Gemini
  - Long Context
  - Evaluation
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: >-
      Gemini 1.5 — Unlocking multimodal understanding across millions of tokens
      of context
    url: 'https://arxiv.org/abs/2403.05530'
    type: primary
  - title: Lost in the Middle — How Language Models Use Long Contexts
    url: 'https://arxiv.org/abs/2307.03172'
    type: primary
  - title: RULER — What's the Real Context Size of Your LLM?
    url: 'https://arxiv.org/abs/2404.06654'
    type: primary
---

## 可以这样回答

要证明 1M 上下文有用，我会同时看任务质量和服务成本。比如会议纪要里的决定放在中间，模型是否仍能找对、能否结合另一处证据回答，都要单独测。Gemini 1.5 报告给出百万 token 窗口、实验到千万，窗口上限还需要这些任务验证。输入 prefill 和decode的成本也要分开算；相关机制见 `google-flash-attention`、`google-block-attn`、`google-gqa-mqa`。

Needle-in-a-haystack 几乎是复制粘贴：干草里埋一句，问这句是什么。Gemini 1.5 在百万 token 上接近饱和，只能说明 RoPE / 窗口实现没把远处 key 丢掉。产品任务不是抄一句。

## 技术备查

要证明 1M 上下文有用，我会同时看任务质量和服务成本。比如会议纪要里的决定放在中间，模型是否仍能找对、能否结合另一处证据回答，都要单独测。Gemini 1.5 报告给出百万 token 窗口、实验到千万，窗口上限还需要这些任务验证。输入 prefill 和逐 token 生成（decode）的成本也要分开算；相关机制见 `google-flash-attention`、`google-block-attn`、`google-gqa-mqa`。

Needle-in-a-haystack 几乎是复制粘贴：干草里埋一句，问这句是什么。Gemini 1.5 在百万 token 上接近饱和，只能说明 RoPE / 窗口实现没把远处 key 丢掉。产品任务不是抄一句。

我会给每条 case 标上长度、证据位置和任务类型，再分别报分：

- 长度桶：32k / 128k / 1M 分开报。短窗口能做，不代表长窗口还在用证据。
- 证据位置：头、中、尾。Lost-in-the-middle（Liu et al.）是默认先验：中间比两端差。会议纪要、仓库里真正的决定经常在中间。
- 跳数：答案要拼两处以上。单针测的是检索，多跳才接近推理。
- 多针 / 干扰针：RULER 一类。会抄最近那句，不等于会选对的那句。
- 拒答：证据不在窗口里时该说没有。流畅编造比答错更糟。
- 模态：视频、PDF、代码仓和纯文本不是同一个 $T$。视觉 token 怎么吃预算见 `google-gemini-mm`。

主指标用归因（句子能否在证据里定位）和任务 F1，生成流畅度当辅助。BLEU 对长文档问答几乎没用。公开小说或著名仓库当评测，模型可能背过；内部时间切分或合成的「中间才出现的约束」更可信。

Transformer 对位置不是平的。训练分布里重要信号爱出现在开头（系统提示）和结尾（当前问题），中间是粘贴进来的文档。RoPE 外推、位置插值、把指令复制到两端，都是在补这个偏置，不是魔法。

白板说：先画准确率对位置的热力图，再谈改位置编码。热力图在某一深度突然变黑，优先查 mask、chunk boundaries、和 KV 是否被截断，别先换模型。Gemini 报告里长上下文更稳，是训练时就喂了长序列；面试不要把「1.5 很强」说成 attention 变成线性了。公式还是 $QK^\top V$，变的是训练分布和 IO 实现。

检索加短窗口经常在 32k 就赢过 naive 全塞 1M，因为噪声少、位置偏置轻。长上下文的正当用途是检索漏召回的那一段、以及多份证据必须同时看见。两者叠，不互相取消。

令层数 $L$、头维 $d$、KV head 数为 $H_{\mathrm{kv}}$。Prefill attention FLOPs 仍是 $\Theta(L T^2 d)$ 量级，FFN 是 $\Theta(L T d_{\mathrm{ff}} d)$。$T$ 从 8k 到 1M 涨 125 倍，二次项先炸掉。Flash 式核砍的是 HBM 往返，不是把二次变成线性。

Decode 的主要压力转到了历史 KV 的读取。每步 $T_q=1$，但要读历史 KV：

$$
\mathrm{KV\ bytes} \approx 2 \cdot L \cdot T \cdot H_{\mathrm{kv}} \cdot d \cdot \mathrm{bytes}
$$

口算一笔：若 $L=48$、$T=10^6$、$H_{\mathrm{kv}}=8$、$d=128$、bf16，单请求 KV 大约 $2\cdot 48\cdot 10^6\cdot 8\cdot 128\cdot 2 \approx 197\,\mathrm{GB}$。还没算权重。并发立刻变成「HBM 里能塞几段 cache」，不是「模型有 1M 窗口」。GQA / 量化 cache / 前缀缓存是一等杠杆；窗口数字不是。

Serving 还要控制长请求的 prefill 尾延迟：用户贴一整本仓库，首 token 延迟跟 $T^2$ 走。产品默认应是检索或分段摘要，1M 当 fallback。这样才能判断长窗口是否适合作为默认路径。

常见误区是：把 needle 准确率当长上下文能力；说 1M 所以 attention 是线性的；只报窗口、不报每千 token 价格和 KV 字节。

## 追问

**Needle 完全没用吗？**
有用，当实现回归：位置 $\times$ 长度热力图，抓 RoPE、mask、chunk boundaries。它不是产品验收。

**10M 和 1M 差在哪？**
同一套评测切片再拉长。实验能跑不等于默认配额；成本按 $T^2$ 和 KV（decode 线性）涨，产品要单独定价。

**位置编码怎么补？**
训练就用长序列最稳。推理期插值是补丁，要在中间位置重测，不要只测尾巴。

**为什么还要检索？**
窗口是上限，不是质量保证。检索控制权限和噪声；长上下文处理漏召回和必须同时看见的多份证据。
