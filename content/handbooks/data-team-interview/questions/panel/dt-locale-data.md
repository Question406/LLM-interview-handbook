---
id: dt-locale-data
section: panel
order: 14
level: A
title: Panel：多语和 locale 数据怎么做，为什么翻译题不能当门禁？
quick: "训练可以用验证过的机翻补覆盖，但评测应让母语者直接出题，避免只测英语题的翻译。过滤阈值要按语言校准，配额可以逐步提高，桶内再做温度采样。AFM 公开把多语比例从 8% 提到 30%，其人评不使用翻译题。"
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

训练和评测应采用不同来源。训练用验证过的机翻和爬取语料补覆盖，母语者示范与人评改善自然程度。正式评测由母语者直接出题，不能只把英语题机翻后同时当训练数据和评测题。

不这么选的理由：苹果产品按 locale 出，不是按「会不会英语推理」出。翻译题被标注员判成不自然。AFM 2025 公开弃用这种题当 hill-climb。

## 训练和评测用来源不同

AFM 2025 公开写了这些：

- 词表从 100k 扩到 150k，多语言用 50% 多余 文本处理单位（token） 换表示。
- mid 用验证过的机翻文档补覆盖，多语权重 8%→30%，桶内温度采样，课程护英语。
- SFT / 基于人类反馈的强化学习（RLHF） 英语:多语约 80:20。另有 0.4% 的混合语言对，允许问和答不是同一语言。
- 默认行为：输出语言跟输入。混合对用来打开「可以不同」。
- hill-climb 用各语言母语者写的几百条 输入提示（prompt）。翻译题被标注员判成不自然。
- 人评里 RLHF 相对 SFT 有 16:9 的 win/loss。

过滤器按语言选训练文档和标签。英语 0.6 的质量阈值在另一门语言上可能几乎全杀，见 `dt-quality-filter-code`、`dt-temp-mix-code`。

OCR 还要印刷 / 手写、海报菜单店招，覆盖要支持的语言。视觉多语不是文本 mix 的副作用。

现场我这么收：覆盖用验证机翻和爬取，自然度用母语者种子和人评，门禁用母语题。能对上公开报告。不要承诺内部语言列表或上线排期。

## 追问

- **低资源只有 200 篇怎么办？** 温度采样会过拟合。先抬抽取召回、许可采集，合成只扩可验证题，不要把 200 篇读 40 遍。
- **英式和美式算 locale 吗？** AFM 人评看像不像当地人说话。football / soccer 这类要进评测，不必进 core 大配额。
- **混合语言 0.4% 会不会把默认行为打乱？** 公开说默认仍匹配输入。小比例只开选项。配额再大就要盯默认行为回归。
