---
id: meta-llama3-pretrain
section: meta
order: 15
level: S
title: Meta：Llama 3 预训练公开故事——数据、退火、长上下文阶段怎么讲
quick: >-
  405B 先在约 $15.6\mathrm{T}$ token、$8\mathrm{k}$ 窗上做 next-token；再约 $800\mathrm{B}$ token、六段把窗拉到
  $128\mathrm{k}$；最后 $40\mathrm{M}$ token 把学习率线性收到 $0$，上采样高质量数据并做 Polyak 平均。别把退火和长窗说成同一段。
tags:
  - Meta
  - Llama
  - Pretraining
  - Long Context
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Introducing Meta Llama 3
    url: https://ai.meta.com/blog/meta-llama-3/
    type: primary
  - title: Introducing Llama 3.1
    url: https://ai.meta.com/blog/meta-llama-3-1/
    type: primary
  - title: Llama 2 — Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
---

GenAI / Llama 预训练岗不会让你背「用了多少卡」。Herd 论文把 405B 写成三段：**初始预训练 → 长上下文继续训 → 退火**。8B / 70B 配方同类。公开材料够答，不要假装见过内部 mix 表。词表见 `meta-llama3-tokenizer`，RoPE 见 `meta-llama-rope`。

## 第一段：8k 窗上把世界知识读完

405B 在约 $15.6\mathrm{T}$ token、上下文 $8\mathrm{k}$ 上做因果 LM。FLOPs 论文写成约 $3.8\times 10^{25}$，相对 Llama 2 70B 大约 $50\times$。Llama 3 博客里 8B / 70B 写的是约 $15\mathrm{T}$，同一量级。小模型故意训得比 compute-optimal 更久，换的是同样推理预算下更强。

数据 mix 用知识分类器 + 小模型 scaling law 扫，不是「爬到什么训什么」。论文对外的最终配比大约是：一般知识 $50\%$、数学与推理 $25\%$、代码 $17\%$、多语言 $8\%$。网上娱乐类被下调；训练中途还加过非英语、数学、更新的网页，并下调后来判定为低质的子集。现场别编「每个语言多少 T」。

过滤叙事是多层的：启发式、去重、模型打质量分。面试说「分类器决定 upsample / downsample」，比说「我们去了毒性」更像训过数据的人。tokenizer 压缩（英语大约 $3.17\to 3.94$ 字符/token）让同样 $T$ 读到的字变多，这是数据题也是算力题。

实现上这段就是标准 packed causal LM：文档拼进 $8\mathrm{k}$，next-token CE。文档边界和 mask 的坑见 `meta-pack-seq`。GQA 从 8B 起就在，不是 70B 才有，见 `meta-llama-gqa`。

## 第二段：长窗必须后置，分六段验收

注意力算力跟 $T^2$ 走，所以**不要一上来就训 128k**。405B 从 $8\mathrm{k}$ 起分六段加长，直到 $128\mathrm{k}$，这段大约 $800\mathrm{B}$ token。每段过关条件写得很死：

1. 短上下文评测完全恢复；
2. 该长度上 needle-in-a-haystack 全对。

只报 haystack、短任务还没回来，就是过拟合到长窗相位。RoPE 侧公开做法是提高 `rope_theta` 并在目标长度上继续训，不是推理时改 `max_position_embeddings`。社区 NTK / YaRN 是另一条旋钮，见 `meta-yarn-ntk`。

长窗阶段仍是预训练目标，不是 SFT。序列变长后，激活显存和 attention 墙钟一起涨，训练栈要跟着改 packing、checkpoint、wrap 粒度，见 `meta-fsdp-llm`。

## 第三段：退火不是「再训 800B」

最后 **$40\mathrm{M}$ token**（注意是 M 不是 B）：学习率线性收到 $0$，窗仍是 $128\mathrm{k}$，数据改成上采样非常高质量的来源，尤其代码和数学。最后对退火期间的 checkpoint 做 Polyak 平均，得到预训练权重。

退火还被他们拿来当**小数据集试金石**：在训到一半的 8B 上，用 $40\mathrm{B}$ token 把学习率收到 $0$，新数据占 $30\%$、原 mix 占 $70\%$，看值不值得进正餐。这比每次都做 scaling law 便宜。

错法：把 $800\mathrm{B}$ 长窗和 $40\mathrm{M}$ 退火混成「末期高质量长文本」。一个改长度，一个改 LR 和 mix。另一个错法：以为退火就是把 GSM8k / MATH **训练集**加进去。论文明确说正式退火不含常用 benchmark 训练集会；他们按 OpenAI 的做法做过对照：8B 在 GSM8k / MATH 验证集上大约 $+24\%$ / $+6.4\%$，405B 上几乎没涨。大模型不靠背训练集。评测污染见 `meta-llama-eval`。

## 追问

- **为什么不全程 128k？** 自注意力二次，早训长窗会把 FLOPs 浪费在还没学好的表示上。先 8k 把知识装进去，再分段加窗。
- **15.6T 和 Llama 2 的 2T 怎么比？** 量级差一截，再叠加词表、GQA、数据过滤。不要只说「数据多了就强」。
- **Polyak 平均和 EMA 的差别？** 论文写的是退火阶段 checkpoint 平均。面试说「末期多份权平均，减抖动」，不要发明系数。
- **和后训练的关系？** 预训练产出 base；SFT / DPO / 合成数据是另一段，见 `meta-synth-sft`。Code 专家是从主 run 分叉再继续训，见 `meta-continual-pt`。
