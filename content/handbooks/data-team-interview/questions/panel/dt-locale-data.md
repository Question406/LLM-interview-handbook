---
id: dt-locale-data
section: panel
order: 14
level: A
title: Panel：多语和 locale 数据怎么做，为什么翻译题不能当门禁？
quick: "训练和评测用不同来源：训练可以用验证过的机翻和爬取语料补覆盖，母语者示范和人评改善自然度；正式评测让母语者直接出题，因为翻译题不自然，只是在测英语题的影子。过滤阈值按语言校准，配额逐步提高，桶内做温度采样。AFM 公开把多语比例从 8% 提到 30%，人评不用翻译题。"
companies:
  - apple
tags:
  - Apple
  - Multilingual
  - Locale
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Applebot model training and individual privacy rights
    url: https://support.apple.com/en-us/120320
    type: primary
---

训练和评测应该用不同来源。训练用验证过的机翻和爬取语料补覆盖，用母语者示范和人评改善自然程度；正式评测由母语者直接出题。把英语题机翻一遍、同时当训练数据和评测题，评测就测不出真实的多语能力。

## 为什么翻译题不能当门禁

多语评测要测的是模型在当地语言里好不好用，机翻的英语题只能测到「会不会英语推理」。翻译过来的题本身就不自然，AFM 的标注员也这样判断，所以 AFM 2025 公开弃用这种题做 hill-climb，改用各语言母语者写的几百条输入提示（prompt）。用翻译题当门禁，测到的只是英语题换了个语言。

## 训练侧怎么做

覆盖靠验证过的机翻和爬取语料，配额逐步抬高，桶内做温度采样。AFM 的 mid 阶段就是用验证过的机翻文档补覆盖，多语权重从 8% 提到 30%，再用课程保护英语能力。词表也会影响多语：AFM 把词表从 100k 扩到 150k，多语言多用 50% 的文本处理单位（token）来换取更好的表示。

过滤器要按语言选训练文档和标签：英语上 0.6 的质量阈值，换一门语言可能几乎全杀，见 `dt-quality-filter-code`、`dt-temp-mix-code`。

后训练阶段也要定配比。AFM 的 SFT 和基于人类反馈的强化学习（RLHF）阶段，英语和多语约 80:20，另有 0.4% 的混合语言对，允许问和答不是同一种语言。默认行为仍是输出语言跟随输入，混合语言对只是打开「可以不同」这个选项。人评上 RLHF 相对 SFT 有 16:9 的 win/loss。

视觉这一侧也要单独做。OCR 要覆盖印刷体和手写体，以及海报、菜单、店招这类场景，并覆盖要支持的语言。视觉多语能力不会作为文本 mix 的副作用自动出现。

## 追问

- **低资源语言只有 200 篇怎么办？** 温度采样会过拟合。先提高抽取召回、做许可采集，合成只扩可验证的题，不要把 200 篇读 40 遍。
- **英式和美式英语算不同 locale 吗？** 人评看的是像不像当地人说话。football / soccer 这类差异要进评测，但不必在 core 里给大配额。
- **0.4% 的混合语言数据会不会打乱默认行为？** 公开报告说默认仍匹配输入语言，小比例只是打开选项。配额再加大，就要盯住默认行为有没有回归。
