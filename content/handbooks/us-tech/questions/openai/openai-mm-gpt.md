---
id: openai-mm-gpt
section: openai
order: 27
level: A
title: OpenAI：GPT-4o 类原生多模态，视觉 token 怎么进 Transformer，分辨率怎么抢上下文
quick: "我会用视觉向量映射到语言模型维度、再与文本拼接的形状解释多模态输入，同时把它标为机制示意。图像分辨率和切块数决定 token 预算，也占 KV；GPT-4o 未公开的编码器和内部层数不能从 API 计费反推。"
tags:
  - OpenAI
  - Multimodal
  - Vision tokens
  - GPT-4o
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Hello GPT-4o
    url: https://openai.com/index/hello-gpt-4o/
    type: primary
  - title: GPT-4o System Card
    url: https://arxiv.org/abs/2410.21276
    type: primary
  - title: GPT-4V System Card
    url: https://openai.com/index/gpt-4v-system-card/
    type: primary
  - title: Images and vision (OpenAI API)
    url: https://platform.openai.com/docs/guides/images-vision
    type: primary
---

视觉输入最终要变成模型能处理的向量，并占用序列长度 $T$ 和 KV 预算。比如边长 336、patch 14，按 ViT 算术有约 $24\times 24=576$ 个 patch，尚未算 CLS 或分隔符；这只是数量级示意，不是 GPT-4o 公布的超参。

GPT-4V 给 GPT-4 增加看图能力，GPT-4o 博客描述文本、视觉、音频端到端由同一网络处理，区别于原来语音三模型串联。内部层数和 encoder 名称未公开，下面画的是通用机制，不由“原生”二字推断私有结构。

## 视觉 token 进同一条因果链

公开层能明确固定下来的只有形状和训练目标，不要编 GPT-4o 的 encoder 名字。

一张图先变成 $N$ 个视觉向量，每个 $D_{\mathrm{vis}}$，再线性（或一小段 MLP）映到语言模型残差维 $D$。拼在序列维：

$$
X=\mathrm{concat}(E_{\mathrm{txt}},\, W E_{\mathrm{vis}})\quad\text{shape }[T_{\mathrm{txt}}+N,\, D].
$$

音频也可用波形切帧、映射成 token 后和文字交错来说明。GPT-4o 的公开描述强调从训练起把模态纳入同一 autoregressive 目标，不能把推理时接 CLIP 向量的原型当成同一训练方式。

位置：视觉 token 有二维（行、列）或 tile 下标，文本是一维位置。RoPE / 绝对位置必须能区分「这是图上第 (i,j) 块」和「这是第 t 个词」。面试抓住「不能共用纯 1D 词位置」，不要假装见过内部公式。因果 mask：图通常作为当前 user 消息的前缀，后面的文本可以看到全部视觉 token；视觉段内部有的实现双向、有的仍因果。白板先声明假设，再写 mask。错 mask 的症状和 `openai-softmax-bug` 一类：shape 对、loss 能降，图文对不上。

和连接器（LLaVA）的差别：连接器冻视觉塔，只训投影和（部分）LM；原生把视觉表示也暴露给 LM 损失。产品原型可以冻；要读 UI 小字、图表坐标，冻住的塔往往先墙。别把「端到端」说成「没有视觉编码器」：像素总要变成 $D$ 维向量，只是编码器是不是和 LM 一起更新、是不是同一套权重。

## 分辨率抢的是上下文，不是画质形容词

$N$ 跟分辨率和切块走，不跟「几张图」走。OpenAI API 把这件事写成可核对的计费：`detail=low` 压到大约 512 边、固定一笔 token（GPT-4o 文档是 85）；`high` 先把图放进 2048 方框、短边收到 768，再按 512 砖计数，每砖 170 再加 85 底。1024 方图 high 大约 4 砖，$4\times 170+85=765$。这是账单上的视觉 token，不一定等于内部 patch 数，但方向一致：要看清字就多砖，多砖就少留给对话和工具观察。

serving 要根据任务分配预算：风景、有人与否、主色通常用 low；截图、表格、公式、UI 状态考虑 high 或先裁区域。整页 4k 截图进入长聊天，会同时增加 prefill 和 KV；多图按张数乘各自 $N$，视频抽帧也是同样累计。相关计算见 `openai-prefill-decode`、`openai-kv-cache-impl`。

长窗训练要按图文总和预算，见 `openai-long-ctx-train`。产品上可先 OCR 提取文档内容，再决定哪些区域必须看图，避免把全部像素塞入 128k。一张图远不止一个 token，连接器微调的细节也不能当作 GPT-4o 预训练事实。

相关：`openai-vit-connect`、`openai-mm-eval`、`google-gemini-mm`

## 追问

**视觉 token 要不要进 KV cache？**
要。它们是序列里的合法位置，逐 token 生成（decode） 每步都在读。图很大时，decode 带宽墙里有一块是图的 KV，不只是文字历史。
**和工具怎么分？**
读像素上的字、比两张图，模型自己看；查库、精确算术、点按钮，仍走工具，见 `openai-function-calling`。原生不是取消工具。
**音频帧和图像砖能混在一个窗口吗？**
能，GPT-4o 的公开叙事就是混。预算仍是相加。失败模式是时间对齐：画面和「第 3 秒的话」对不上。
**降 sampling 算不算数据增强？**
训练可以多分辨率；推理降 sampling 会抹掉判别像素。评测必须锁分辨率，见 `openai-mm-eval`。
