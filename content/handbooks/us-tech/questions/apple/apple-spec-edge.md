---
id: apple-spec-edge
section: apple
order: 13
level: A
title: Apple：on-device speculative decoding 值得上吗，草稿模型放哪？
quick: >-
  on-device speculative decoding 是否值得，要看草稿成本、平均接受长度、KV 回滚和稳态功耗；草稿很便宜、acceptance
  rate 高时才可能省时。草稿宜与目标同设备、同静态档位，TTS 只能读已验证 token；Apple 公开的 30 token/s 是投机之前的数字。
tags:
  - Apple
  - Speculative Decoding
  - On-device
  - Latency
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: >-
      https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Fast Inference from Transformers via Speculative Decoding
    url: 'https://arxiv.org/abs/2211.17192'
    type: primary
  - title: Deploying Transformers on the Apple Neural Engine
    url: 'https://machinelearning.apple.com/research/neural-engine-transformers'
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: >-
      https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

## 可以这样回答

on-device speculative decoding 值得与否，要看草稿加验证是否比直接生成更省时间和电。比如草稿 acceptance rate 不高，却占了第二份模型和 cache，就可能拖慢目标模型，峰值 token/s 也说明不了长期收益。

2024 AFM 概述给出的 iPhone 15 Pro 约 30 token/s，是采用 token speculation 之前的数字。这里重点按 ANE 静态 shape、功耗和语音出口评估；拒绝后回滚 KV 的正确性要求与 `openai-speculative-decoding` 相同，相关 on-device 约束见 `apple-ane`、`apple-siri-latency`。

## 技术备查

on-device speculative decoding 值得与否，要看草稿加验证是否比直接生成更省时间和电。比如草稿 acceptance rate 不高，却占了第二份模型和 cache，就可能拖慢目标模型，峰值 token/s 也说明不了长期收益。

2024 AFM 概述给出的 iPhone 15 Pro 约 30 token/s，是采用 token speculation 之前的数字。这里重点按 ANE 静态 shape、功耗和语音出口评估；拒绝后回滚 KV 的正确性要求与 `openai-speculative-decoding` 相同，相关 on-device 约束见 `apple-ane`、`apple-siri-latency`。

## 先估算能否节省时间

草稿每步提出 $\gamma$ 个 token，目标一次 forward 验证。设草稿相对目标的代价是 $c$（on-device 应 $c\ll 1$），平均接受长度是 $\tau$（含最后那个被拒后 resampling 的目标 token）。实际耗时粗看：

$$
\text{加速} \approx \frac{\tau}{c\gamma + 1}
$$

$\tau$ 上不去，$c$ 又不小，加速小于 1，还多烧电。on-device $c$ 来自：第二份权重是否常驻、是否掉出 ANE、是否多一次 DRAM 往返。云端可以把草稿塞进空闲 SM；手机上第二份模型会和 3B 目标抢 SRAM 和内存带宽。

acceptance rate 跟任务走。低温度、小 $k$、格式固定的摘要，草稿和目标更容易一致，见 `apple-topk-sample`。高温度闲聊、代码、开放知识，$\tau$ 掉下来，投机变亏。所以按 adapter / 功能开关，不要全局开。

验证必须保持目标分布：草稿只是提议，最终 token 仍来自目标模型的 rejection sampling / 给定前缀的条件分布。质量 evaluation gate 是 greedy 或固定 seed 下，和不开投机逐 token 对齐（允许实现定义的等价 sampling）。对不齐先查 KV 回滚，再查 RoPE 偏移。

## 再选草稿位置和实现

我会按代价排选项：

1. 自投机 / 多 token 头。目标自己出草稿（浅层、共享骨干、或 Medusa 式额外头）。不驻留第二份 3B，ANE 上更像多一个静态出口。训练要加这些头；拒绝仍要截断 cache。
2. distillation 小草稿，和目标同设备。例如很小的 palettized 网，只编同一 vocabulary。必须和目标同一 tokenizer、同一 $S_{\max}$ 档位。两张图都要能留在 ANE，或接受草稿走 GPU、目标走 ANE；拷贝可能把 $c$ 吃掉。
3. 层跳跃。用目标的前几层当草稿，类似 self-spec。和 2025 的 KV sharing 有亲缘：都是后段依赖前段状态，但投机是时间维提议，sharing 是深度维省 cache，见 `apple-ondevice-kv`。
4. 不要。云端草稿 + on-device 验证：RTT 远大于一次本地 逐 token 生成（decode）。on-device 草稿 + PCC 目标：同样会受到网络延迟限制。PCC 内部可以做投机，那是 server 模型的事，不要和 iPhone 30 token/s 混报。

ANE：$\gamma$ 要编进静态 shape。$\gamma=4$ 就导出 $\gamma=4$ 的验证图，不要运行时改。拒绝后 KV 回到接受前缀长度，position 用新的 `cache_len`，不要从 0 再转 RoPE。Paged KV 不是 on-device 主路径；预分配槽位上做截断即可。

语音：TTS 只能吃已提交、已验证的词。草稿若已被喇叭读出，拒绝就要停播或补丁，体验比屏上删字差一个数量级。`apple-siri-latency` 的定义是语音通路默认不用未验证草稿。屏幕上的输入法 / 改写可以更激进。



离线报：$\tau$、$c$、实际耗时 token/s、Joule/token、热节流后的稳态速度。只报峰值 token/s 会把「开了投机但电池掉得更快」藏起来，见 `apple-afm-eval`。正确性：短序列 greedy 对齐；拒绝点注入测试（故意让草稿走错）看 cache 是否回滚。

30 token/s 的公开数字尚未包含投机，草稿 logits 也必须经过目标模型验证才能输出。若改用更弱模型近似验证，就失去了 lossless speculative 的前提；单纯增大 $\gamma$ 还可能让草稿成本 $c$ 接近 1。

和 quantization 叠：目标 2-bit 权、8-bit KV，草稿若仍 fp16 满头 KV，内存反而更炸。草稿也要走同一套 palettize / GQA 配方，或走自投机避免第二份 cache。

## 追问

**$\gamma$ 怎么选？**
从 4 左右扫。$\gamma$ 太大，后面 token acceptance rate 崩，验证一次干的活被拒绝浪费。编进 ANE 档位后，$\gamma$ 是产品常量，不是每步策略。
**和 sampling 温度？**
温度高、nucleus 大，$\tau$ 降。on-device 本就偏贪心，对投机友好；不要为了多样性把投机开在语音上。
**草稿和目标 vocabulary 不同？**
基本不要。对齐 token boundaries 的开销会吃掉 $c$。
**用户抢话？**
和普通 decode 一样：停 TTS、作废未提交 token、KV 回到打断前前缀。未验证草稿本来就不该进这条回滚栈。

## 相关题

- [[sys-spec-sys]]：服务器侧的同一题：草稿长度、KV 回滚和 throughput 怎么测。
- [[google-spec-decode]]：无损性的原理和自投机草稿，on-device 选草稿方案时用得上。
- [[apple-topk-sample]]：同是 Apple on-device 题，讲温度、top-k、nucleus 的顺序；草稿也要用同一套截断策略。
