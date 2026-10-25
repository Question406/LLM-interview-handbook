---
id: apple-rank-adapter
section: apple
order: 15
level: S
title: Apple：低秩适配器做个性化，和检索怎么选，数据如何不出设备？
quick: "会变的事实走本地检索，稳定格式和任务行为走 LoRA；按用户训练时，数据和权重应留在设备。公开产品 adapter 常为 rank 16，开发者 toolkit 提到 rank 32，16-bit 存储约几十 MB，可在冻结量化底模上热切换；遗忘和版本绑定也要设计。"
tags:
  - Apple
  - LoRA
  - Personalization
  - On-device
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
  - title: LoRA — Low-Rank Adaptation of Large Language Models
    url: https://arxiv.org/abs/2106.09685
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

LoRA 适合调整稳定的任务行为，本地检索适合提供会过期、需要随时删除的用户事实。比如通知摘要的长度约束可以用功能 adapter，今晚的日程仍要查本地工具。低秩让需要训练和切换的参数较少，但不会自动解决事实更新和遗忘。

Apple 公开的准确率恢复 adapter 为 rank 16、16-bit、几十 MB，开发者 toolkit 提到 rank 32，基础模型 palettize 后冻结。这里按公开技术设计解释；产品层面的检索、任务 adapter 和 DP 分工见 `apple-personalize`。

## 秩决定你能改多少行为、付多少内存

LoRA 把 $\Delta W = BA$ 插进注意力投影和 FFN，$A\in \mathbb{R}^{r\times k}$，$B\in \mathbb{R}^{d\times r}$（实现里常反过来写，参数量一样）。一份 adapter 的参数大约：

$$
\#\theta \approx r \cdot \sum_{(d,k)\in \mathcal{L}} (d+k)
$$

$r=16$ 相对满秩 $dk$ 是几个数量级的小。16-bit 存下来，公开「tens of megabytes」，可以动态加载、缓存、换掉。ANE 底图静态，换任务只换外置小权，见 `apple-ane`。初始化来自量化 accuracy-recovery adapter，不是随机 $A,B$，否则 2-bit 基础模型上的产品 adapter 需要先恢复量化损失。

$r$ 怎么选：

- 偏小（8–16）。格式、语气、长度、拒答风格。「通知两句、不要剧透」这种。过拟合慢，热切换便宜。Apple 产品功能 adapter 公开落在 16。
- 偏大（32）。开发者要教 3B 一个新技能（领域槽位、内部 字段和类型规范（schema））。公开 toolkit 用 32，仍要跟基础模型版本绑定，基础模型一升就要重训。
- 再大。接近小全量微调，端上驻留和过拟合都变差。事实类知识仍不该塞进 $\Delta W$。

同一基础模型上叠多份功能 adapter（邮件 vs 通知），不要每人一份上传的权重。个性化来自这一刻的本地证据 $E$，不是每人一个云端 LoRA。

## 检索 vs adapter：写进权重的东西很难忘

日历、邮件、今晚和谁吃饭，明天就过期。写入 $B,A$ 既违反「不用私有数据训基础模型」，也来不及更新，用户删邮件后模型还会「记得」。做法：

- 事实、标识符、会过期的槽：设备内索引 + 工具。$n$ 是单用户规模，暴力 / IVF 足够，见 `apple-kmeans`。生成条件 $(q,E)$，有实际证据支持见 `apple-siri-grounded`。
- 稳定任务头：LoRA。摘要格式、语言风格约束、工具调用格式、guided generation 的结构先验。
- 「像我一样写」：先检索用户近期已发送邮件当 few-shot $E$，用完可不落盘。仍不够再考虑端上小 $r$ 的用户 adapter，权重不离开设备。

端上若真训用户 adapter：本地数据、本地 SGD / 几步 LoRA，预算要卡 epoch 和验证，防止把某一封薪资邮件记进权重。遗忘是产品功能：删数据应能卸 adapter 或从快照恢复，不能只靠「再训一次盖住」。不要默认联邦平均，梯度仍可能泄漏 $E$，没有用户级 DP 就不要画成主路径，见 `apple-diff-privacy`。Apple 公开 AFM 训练没用这条。

PCC：3B + 本地 $E$ 不够时，送最小切片给 server 模型，不是把用户 LoRA 上传融合进全球基础模型。



今日日程数字：检索 / 工具，不要 LoRA。  
邮件摘要 vs 通知摘要：功能 LoRA，$r=16$ 量级。  
用户显式「记住这个」：可删的本地键值，不是偷偷写入 $B$。  
全球基础模型变好：许可数据 + 合成数据 + 恢复 adapter，不是用户邮箱。

评测拆开：有实际证据支持率（检索）、格式分（adapter）、隐私事故（$E$ 或权重是否离设备）、延迟（切换摊还到任务边界，不要每个 token 换一份）。量化回归要在「底模 + recovery + 产品 adapter」整条链上做，见 `apple-ondevice-quant`、`apple-afm-eval`。

QLoRA 主要解决训练显存，AFM 这里讨论的是推理时一份量化底模加多份小 adapter。云端 RAG 同步全邮箱不符合这里的隐私前提；即使 rank 开到 256，写进权重的事实也无法像检索索引那样直接更新和删除。

```python
# 参数量数量级：只算一组 [d, k] 投影
def lora_params(d, k, r):
    return r * (d + k)
# 例：d = k = 3072, r = 16 -> 98304；满秩是 3072**2
```

## 追问

**为什么不直接 输入提示（prompt） 几条范例？**
可以，而且常是第一选择。范例占上下文和 KV，见 `apple-ondevice-kv`。任务头稳定、要常驻，才值得一份几十 MB 的 LoRA。
**多 adapter 同时加载？**
权重要加起来，ANE 驻留和切换成本上升。产品是按功能切，一次一份，缓存最近用过的。
**用户 LoRA 能不能做备份？**
备份等于数据离设备。若做 iCloud，要按敏感数据通路讲加密和用户控制，不要默认开。
**和 Palettization 的关系？**
先压基础模型，再训 recovery LoRA，产品 adapter 从 recovery 初始化。顺序反了，2-bit 上直接训任务，质量通常崩。
