---
id: google-mm-sft
section: google
order: 31
level: A
title: Google：多模态 SFT，交错图文、纯文本回退、灾难遗忘
quick: "多模态 SFT 要把交错图文对话和纯文本回放混着训，避免模型只适应看图回答、损害原来的文本能力。数据里应包含中途插图、多图和撤图后的对话；解冻视觉塔或 LM 的范围，要结合细节识别和遗忘的验证结果决定。"
tags:
  - Google
  - Multimodal
  - SFT
  - Forgetting
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Gemini — A Family of Highly Capable Multimodal Models
    url: https://arxiv.org/abs/2312.11805
    type: primary
  - title: Gemini 1.5 — Unlocking multimodal understanding across millions of tokens of context
    url: https://arxiv.org/abs/2403.05530
    type: primary
  - title: Flamingo — a Visual Language Model for Few-Shot Learning
    url: https://arxiv.org/abs/2204.14198
    type: secondary
  - title: PaliGemma — A versatile 3B VLM for transfer
    url: https://arxiv.org/abs/2407.07726
    type: secondary
---

我会把交错图文对话和纯文本回放一起做 SFT，再根据验证结果决定解冻哪些模块。比如用户先聊三轮文字、再贴截图追问表里的数，训练样本就要覆盖这种顺序。Gemini 报告把后训练列为多模态对齐的一部分，但配比和解冻细节未公开；预训练交错见 `google-gemini-mm`，PaLI 多任务前缀见 `google-pali`。

连接器时代的默认样本是：图像 token 前缀 + 一句问 + 一句答。真实产品是聊天：先纯文本三轮，再贴截图，再追问图里的数，中间还可能夹另一张图。序列形状是文本和视觉在 $T$ 维上拼成 $[B,\ T_{\mathrm{txt}}+T_{\mathrm{vis}},\ D]$。因果掩码仍从左到右，但指代要跨模态：「上面那张表的第三列」依赖位置和轮次边界，不是依赖 CLIP 相似度。图永远放开头，模型会学到错误先验：所有视觉条件都在 输入提示（prompt） 顶部。评测要包含中途插图、多图、图后纯文本追问。

PaLI 用任务前缀（caption / VQA / OCR）也能做生成，但不等于对话。把前缀机直接当 chat 模型，会表现为会做题不会拒绝、不会追问缺的图。PaliGemma 公开定位是 transfer 底座，要聊天还得再 SFT。Flamingo 则几乎不靠 SFT 对话，靠交错 few-shot，见 `google-flamingo`。三种配方别并成一个「视觉对齐」。

开始调学习率前，我会先检查图文监督是否对应。网页 alt-text、PPT 里图和旁边段落、视频旁白广告，都会变成指令。过滤要用「离开图是否仍能答」：能，这条不算多模态监督。OCR 任务和开放描述的配比决定模型是读字还是吹牛。分辨率策略见 `google-vit-patch`。

上线流量大量是纯文本。SFT 若 100% 带图，条件分布漂到「总在等视觉 token」，表现是短指令变差、拒答变少、代码和数学回退。这是灾难遗忘的产品面，不只是学术 MMLU 掉点，见 `google-eval-mmlu`。

我会给不同数据设显式配额，分别追踪验证分数：

- 多模态对话（交错、多图、文档页）。
- 纯文本指令 / 代码 / 安全拒答，从原 SFT 回放。
- 可选：无图但任务是视觉的负例（「你没看到图，请说明」），教模型不要编像素。

学习率上视觉新模块可以更高，LM 主干更低；或者只适配交叉注意 / 投影。全程大学习率解冻 LM，图任务涨得快，文本掉得也快。Flamingo 冻 LM 是另一极端：文本能力保住，细节上不去。取舍要对着错误类型，不要对着论文年份。

Serving 回退还要在格式层：没有图时不要留无意义的视觉占位；有图时 $T_{\mathrm{vis}}$ 进同一预算。用户把图撤了继续聊，模型应接着文本上下文走，而不是假装图还在。

我会把遗忘分开量：纯文本能力看 MMLU、指令遵循和代码；旧视觉任务看 OCR 与自然场景 caption 是否互相损害；输出格式则单独检查。具体来说：

1. **纯文本能力。** MMLU、指令遵循、代码。掉了说明 LM 条件被视觉数据改写。
2. **旧视觉任务。** 只训文档 OCR 之后，自然场景 caption 变干，或反过来。多任务配比和 PaLI 是同一问题。
3. **格式。** 仍会做题，但变成不按用户语言答、不引用图中数字、乱输出任务前缀。

补救优先级：先把文本回放比例提到掉点可接受（用验证曲线，不要背一个常数），再考虑冻底层、回放预训练文本。不要一掉点就加参数。评测集要固定：同一条 case 的带图版和不带图版都跑，防止「平均分」靠视觉题涨、文本题崩。

视频 SFT 和图片 SFT 不能当一种。时间采样和预算见 `google-video-token`。只喂图片再问视频时间戳，是分布外。

常见误区是：把冻塔投影说成 Gemini 预训练；说做了多模态 SFT 所以纯文本一定更好；用 caption 分数当对话验收。

## 追问

**只训投影、冻 LM 行不行？**
原型行，UI 小字和复杂指代往往不够。要解冻就用更低学习率和文本混。

**交错预训练还要不要 SFT？**
要。预训练教的是条件生成，SFT 教的是指令、拒答、多轮指代。两者数据分布不同。

**安全数据放哪？**
纯文本拒答和「图里有敏感内容」要分开切片。混在 caption 里会被描述目标盖掉。

**和工具调用怎么分阶段？**
先保证看见图和纯文本都不崩，再上工具环，见 `google-gemini-agent`。否则分不清是视觉忘了还是 工具 schema 没学会。
