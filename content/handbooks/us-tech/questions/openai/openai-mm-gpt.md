---
id: openai-mm-gpt
section: openai
order: 27
level: A
title: OpenAI：GPT-4o 类原生多模态，视觉 token 怎么进 Transformer，分辨率怎么抢上下文
quick: >-
  原生指图和文本进同一条解码器、同一套残差，不是冻 CLIP 再点积。图被切成 patch / tile，投影到 $D$ 后拼在序列维上，和文字抢同一个
  $T$。分辨率涨的是视觉 token 数，不是「一张图算 1」。API 的 high-detail 按 512 砖计费，是公开的预算语言，不是内部层数。
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

## 题怎么来的

GPT-4V 把看图做成 GPT-4 的能力；GPT-4o 博客写明 **一个新模型端到端吃文本 / 视觉 / 音频**，同一套网络，不再是语音三模型串联。OpenAI 多模态岗问的不是内部层数——那没公开——而是：像素怎么变成 Transformer 能吃的 token，以及高分辨率会不会把对话窗口吃光。连接器路线见 `openai-vit-connect`；评测坑见 `openai-mm-eval`。Gemini 的交错叙事见 `google-gemini-mm`，机制同类，别背成 OpenAI 超参。

我会先画序列，再谈分辨率预算。评委听的是 **视觉占 $T$**，不是「原生所以免费」。

## 视觉 token 进同一条因果链

公开层能钉死的只有形状和训练目标，不要编 GPT-4o 的 encoder 名字。

一张图先变成 $N$ 个视觉向量，每个 $D_{\mathrm{vis}}$，再线性（或一小段 MLP）映到语言模型残差维 $D$。拼在序列维：

$$
X=\mathrm{concat}(E_{\mathrm{txt}},\, W E_{\mathrm{vis}})\quad\text{shape }[T_{\mathrm{txt}}+N,\, D].
$$

口算数量级：边长 336、patch 14，大约 $24\times 24=576$ 个 patch，还没算 CLS / 特殊分隔。这不是 4o 的公开超参，是 ViT 算术。音频同理：波形切帧，每帧一个 token，和文本交错。GPT-4o 的卖点是这些模态 **从训练起就在同一自回归目标上**，不是推理时才把 CLIP 向量粘上去。

位置：视觉 token 有二维（行、列）或 tile 下标，文本是一维位置。RoPE / 绝对位置必须能区分「这是图上第 (i,j) 块」和「这是第 t 个词」。面试抓住「不能共用纯 1D 词位置」，不要假装见过内部公式。因果 mask：图通常作为当前 user 消息的前缀，后面的文本可以看到全部视觉 token；视觉段内部有的实现双向、有的仍因果。白板先声明假设，再写 mask。错 mask 的症状和 `openai-softmax-bug` 一类：shape 对、loss 能降，图文对不上。

和连接器（LLaVA）的差别：连接器冻视觉塔，只训投影和（部分）LM；原生把视觉表示也暴露给 LM 损失。产品原型可以冻；要读 UI 小字、图表坐标，冻住的塔往往先墙。别把「端到端」说成「没有视觉编码器」——像素总要变成 $D$ 维向量，只是编码器是不是和 LM 一起更新、是不是同一套权重。

## 分辨率抢的是上下文，不是画质形容词

$N$ 跟分辨率和切块走，不跟「几张图」走。OpenAI API 把这件事写成可核对的计费：`detail=low` 压到大约 512 边、固定一笔 token（GPT-4o 文档是 85）；`high` 先把图放进 2048 方框、短边收到 768，再按 512 砖计数，每砖 170 再加 85 底。1024 方图 high 大约 4 砖，$4\times 170+85=765$。这是 **账单上的视觉 token**，不一定等于内部 patch 数，但方向一致：要看清字就多砖，多砖就少留给对话和工具观察。

所以 serving 先问任务：

- 风景、是否有人、主色：low 就够。
- 截图、表格、公式、UI 状态：high 或先裁相关区域。整页 4k 截图塞进已经很长的聊天，prefill 和 KV 一起涨，见 `openai-prefill-decode`、`openai-kv-cache-impl`。
- 多图：张数乘每张 $N$，和长视频抽帧是同一笔账。

长上下文训练见 `openai-long-ctx-train`：窗口是图+文的和。产品上该 OCR 的文档先 OCR，原生能力不是把所有像素原样倒进 128k。错法：说一张图「就是 1 个视觉 token」；说原生多模态所以不占上下文；用连接器微调的故事冒充 GPT-4o 预训练。

## 追问

- **视觉 token 要不要进 KV cache？** 要。它们是序列里的合法位置，decode 每步都在读。图很大时，decode 带宽墙里有一块是图的 KV，不只是文字历史。
- **和工具怎么分？** 读像素上的字、比两张图，模型自己看；查库、精确算术、点按钮，仍走工具，见 `openai-function-calling`。原生不是取消工具。
- **音频帧和图像砖能混在一个窗口吗？** 能，GPT-4o 的公开叙事就是混。预算仍是相加。失败模式是时间对齐：画面和「第 3 秒的话」对不上。
- **降采样算不算数据增强？** 训练可以多分辨率；推理降采样会抹掉判别像素。评测必须锁分辨率，见 `openai-mm-eval`。
