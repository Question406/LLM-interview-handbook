---
id: dt-webgpt-cite
section: labs
order: 32
level: A
title: WebGPT：为什么没有引用，事实偏好几乎标不动？
quick: "浏览轨迹用于教模型搜索，带引用的答案用于评价事实是否有出处。标注员逐句检查引用能否支持答案，避免凭记忆或文笔判真假。苹果场景使用许可网页和 Applebot 数据，不能默认把用户 Safari 历史用于训练。"
companies:
  - apple
tags:
  - OpenAI
  - Factuality
  - Search
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "WebGPT: Browser-assisted question-answering with human feedback"
    url: https://arxiv.org/abs/2112.09332
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

把数据分成两部分。浏览轨迹记录查询、点击链接和滚动，用监督微调（SFT）教模型怎样搜索；工具返回的 observation 不计入损失。最终答案则要带引用，让每句话都能指回支持它的材料，标注员据此比较事实是否得到支持。

没有引用时，事实偏好标签更容易有噪声，见 `dt-annotator-protocol`。拒绝采样可以让奖励模型（RM）挑选带引用的答案。评测时还要去掉引用再比较，防止格式本身让答案显得更可信。必须搜索的题，要检查是否真的调用了搜索工具，见 `dt-when-to-search`、`dt-agent-state-path`。

不要让标注员凭记忆判断真假，也不要把浏览轨迹和答案不加区分地计入同一份交叉熵损失（CE）。引用的作用是让标注员有材料可以核对。即使引用支持答案，来源也可能不可靠，因此「是否支持」和「来源是否可信」要分别评价，否则强硬的语气和引用格式可能掩盖问题。

AFM 的摘要与证据支持检查，主要核对源文档中的信息。网页训练数据仍来自许可网页和 Applebot，不能默认使用用户 Safari 历史，见 `dt-userlog-contrast`。Llama 3 后训练用 Brave Search 补截止之后的事件，工具章节说明，人工按调用步骤标注，不修改工具返回内容，和 WebGPT 同族：搜索负责获取材料，事实标签则检查材料能否支持回答。Reddit 高票不是金标，他们换过不熟悉细则的标注员做对照。

WebGPT 使用文本浏览器：人先演示检索，再比较带引用的回答。在 ELI5 上，模型相对人工演示的偏好胜率为 56%，相对 Reddit 高票回答为 69%；去掉引用后也作了比较。公开实验中，效果最好的组合是行为克隆加拒绝采样。

## 追问

- **引用了不可靠站？** 支撑检查过了，可信度另开一维。混成一个「更好」，人会奖口气硬的引用。
- **不会搜、直接答对？** 产品可以快。训练标签：该搜的题必须出现搜索调用，见 `dt-when-to-search`、`dt-agent-state-path`。
- **ELI5 本身脏不脏？** Reddit 高票不是金标。他们换过不熟悉细则的标注员做对照。
