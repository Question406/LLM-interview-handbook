---
id: dt-webgpt-cite
section: labs
order: 32
level: A
title: WebGPT：为什么没有引用，事实偏好几乎标不动？
quick: "因为没有引用，标注员只能凭记忆或文笔判断真假，事实偏好标签噪声很大。WebGPT 把数据拆成两部分：浏览轨迹教模型怎么搜，带引用的答案让标注员逐句核对出处。「引用是否支持」和「来源是否可信」要分开评，评测时再去掉引用比一次，防止引用格式本身让答案显得可信。"
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

因为没有引用，标注员手里没有材料可以核对，只能凭记忆或文笔判断哪个回答更真实，事实偏好标签自然噪声很大（见 `dt-annotator-protocol`）。引用的作用就是让每句话都能指回支持它的材料，标注员据此比较。

## WebGPT 怎么做

WebGPT 使用文本浏览器：人先演示检索，再比较带引用的回答。在 ELI5 上，模型相对人工演示的偏好胜率为 56%，相对 Reddit 高票回答为 69%；他们也在去掉引用后做了比较。公开实验里效果最好的组合是行为克隆加拒绝采样。Reddit 高票本身也不是金标，他们换过不熟悉细则的标注员做对照。

Llama 3 后训练用 Brave Search 补训练截止之后的事件，工具章节说明人工按调用步骤标注、不修改工具返回内容。思路和 WebGPT 一样：搜索负责获取材料，事实标签检查材料能否支持回答。

## 数据怎么拆

1. 浏览轨迹：记录查询、点击链接和滚动，用监督微调（SFT）教模型怎样搜索。工具返回的 observation 不计入损失，浏览轨迹和答案也不要不加区分地计入同一份交叉熵损失（CE）。
2. 带引用的答案：每句话指回支持它的材料，标注员按材料比较事实是否得到支持。
3. 拒绝采样：可以让奖励模型（RM）挑选带引用的答案。
4. 去引用对照：评测时去掉引用再比一次，防止引用格式本身让答案显得更可信。
5. 查搜索调用：必须搜索的题，要检查是否真的调用了搜索工具，见 `dt-when-to-search`、`dt-agent-state-path`。

还要注意，即使引用支持答案，来源也可能不可靠。「是否支持」和「来源是否可信」要分开评价，混成一个「更好」，强硬的语气和引用格式就会掩盖问题。

## 追问

- **模型不搜、直接答对了呢？** 产品上可以快，但训练标签要求该搜的题必须出现搜索调用。
