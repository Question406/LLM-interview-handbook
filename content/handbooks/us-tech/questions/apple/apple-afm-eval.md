---
id: apple-afm-eval
section: apple
order: 14
level: A
title: Apple：端侧 LLM 怎么评，延迟、耗电、隐私，为什么不能只报 BLEU？
quick: "BLEU 测的是 n-gram 重叠，测不到通知摘要有没有剧透、首个 token 的等待时间有没有超出预算、这一轮有没有把邮件送出设备。端侧门禁至少四层：任务成功、有实际证据支持、系统（延迟 / 功耗 / 热）、隐私事故。人评和 locale 比开放 chatbot 排行榜更贴近 AFM 的产品要求。"
tags:
  - Apple
  - Evaluation
  - On-device
  - Privacy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

Apple 公开评 AFM 时，主叙事是人评、feature adapter、locale，再辅 IFEval 一类指令跟随。端侧模型写明不是开放世界 chatbot。把 BLEU 当门禁，等于用机器翻译指标去收 iPhone 通知摘要。Bedrock 侧同一类错误见 `amazon-titan-eval`；这里还要检查：功耗、热、数据有没有离开设备。Exponent 也把 on-device limits 列为 MLE 深度。

## BLEU 在这里骗什么

BLEU / ROUGE 要参考译文。邮件摘要、通知改写常常没有唯一金句：合法说法有很多，换词就掉分；抄一句检索块再加幻觉，n-gram 还可能不低。开放知识问答经常没有参考答案。AFM 的产品任务更是有证据 $E$ 的条件生成，见 `apple-siri-grounded`：源里没有就该拒，BLEU 给不出这个契约。

公开报告用人做 side-by-side，维度包括分析推理、头脑风暴、分类、抽取、摘要、工具、安全。locale 还要看是否像当地人在说话（英式 football vs soccer）。feature 层另做 adapter 评测：邮件 / 信息 / 通知各自 750 条量级的分层样本，好 / 中 / 差按多维度全好才算好。这才是「上线门禁」的形状，不是 WMT 分数。

自动指标可以当回归测试：IFEval、内部指令集、工具参数合法率。它们不能替代人评，尤其是「摘要有没有删掉关键限定词」。安全用对抗输入提示（prompt）的 violation rate，和任务分拆开报。

## 端侧必须多报的三张图

任务质量之外，现场主动给系统图和隐私图，否则像在评云端 API。

1. 延迟。Prefill ms/prompt-token、逐 token 生成（decode）的 token/s、首个 token 的等待时间（TTFT）、语音则是首包音频。公开约 0.6 ms/prompt-token 和 30 token/s 是能力上限，产品看 p95 和热降频后的稳态。拆法见 `apple-siri-latency`。投机只报验证后的有效 token/s，见 `apple-spec-edge`。
2. 功耗和热。Talaria / Instruments：每层时延和能量，指导 palettization，见 `apple-ane`、`apple-ondevice-quant`。Joule/token、连续对话是否掉到不可用。30 token/s 瞬时、两分钟后节流，门禁要有稳态。
3. 隐私。这一轮 $E$ 是否离设备；PCC 切片大小和驻留；日志是否含原文。训练基础模型不用用户私有数据是声明，评测要能指出产品路径有没有把邮件打到不该去的通道。DP 只在学人群规律时花 $\varepsilon$，见 `apple-diff-privacy`。把「有 PCC」当成隐私指标，是概念错误。

有实际证据支持：句子能否对齐到本地证据或工具结果；错误引用过期日历算事故。格式：通知是否两句、是否剧透，这是 adapter 有没有干活，见 `apple-rank-adapter`、`apple-personalize`。不要合成一个「质量 0.82」。

设备矩阵：至少一块目标 SoC、一个低内存档、前台 / 后台。ANE 掉到 GPU/CPU 的层要单列，那是正确性也是电量。Compute unit 不全是 Neural Engine，先修图再刷分数。

## 一套能上线的报表

我会钉四层，缺一层就说门禁不完整：

- 任务。人评 + 工具成功率；feature 集和基础模型通测集分开。换基础模型时 adapter 要重训、重评，公开 toolkit 也是这么说的。
- 有实际证据支持 / 安全。无证据生成率、拒答是否该拒、有害 / 敏感、剧透。
- 系统。TTFT、token/s、Joule/token、峰值内存、ANE 驻留。KV 变长后的曲线，见 `apple-ondevice-kv`。
- 隐私。离设备字节、PCC 调用率、opt-in 分析是否走聚合 / DP。

线上：用户改写率、重说率、「你说错了」、打断、过热关特性。离线结果与线上结果冲突时，优先检查线上任务指标。不要为了 BLEU 把提示改成更像参考译文、更不像用户邮件。

常见误区是：用开放 chatbot 竞技场给 3B 打分然后说「不够智能所以全走 PCC」。那会把私有上下文送出去。能力边界见 `apple-foundation-models`。另一常见误区是：只在英语 US 评，其他语言和地区的表现出问题。

## 追问

- **完全没有金标怎么办？** 有实际证据支持（是否超出 $E$）加任务代理指标（用户是否点开、是否撤销摘要）。人评一小份校准，再放大。不要用 BLEU 假装有金标。
- **LLM-as-judge 能用吗？** 能做扫描，但评委若是云端大模型，等于把评测集送出设备。端侧评测管道本身也有隐私约束；高风险抽人审。
- **MMLU 涨了能不能发版？** 只能解释基础模型。通知摘要 adapter、延迟、电量不过，照样不能发。
- **和量化回归怎么叠？** 同一评测集在 fp16、palettized、8-bit KV 上跑 greedy 对齐加任务分。分掉了先查 mask 和 RoPE，再查码本，见 `apple-ondevice-quant`。
