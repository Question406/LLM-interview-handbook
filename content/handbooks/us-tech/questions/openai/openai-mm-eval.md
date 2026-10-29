---
id: openai-mm-eval
section: openai
order: 33
level: A
title: OpenAI：多模态评测坑，图文泄漏、OCR 当语义、MMMU 一类怎么拆
quick: "我会先把图去掉跑同一批题，再比较带图提升，并把 OCR、布局和学科视觉推理分开看。盲文得分高可能来自语言先验或泄漏；分辨率、裁切、工具和选项展示方式都要固定，才能比较模型是否更会看图。"
tags:
  - OpenAI
  - Multimodal
  - Evaluation
  - MMMU
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: MMMU — A Massive Multi-discipline Multimodal Understanding Benchmark
    url: https://arxiv.org/abs/2311.16502
    type: primary
  - title: Are We on the Right Way for Evaluating Large Vision-Language Models? (MMStar)
    url: https://arxiv.org/abs/2403.20330
    type: primary
  - title: GPT-4V System Card
    url: https://openai.com/index/gpt-4v-system-card/
    type: primary
  - title: openai/simple-evals
    url: https://github.com/openai/simple-evals
    type: primary
---

我会先跑不给图的基线，再看图带来了多少增益。比如题目问哪种已灭绝的鸟，选项里却只有一种鸟，模型不看图也能答；这样的高分不足以证明视觉能力。GPT-4V / GPT-4o 的 MMMU、文档和图表评测同样需要区分语言先验、训练见图和真正看图后的收益。MMStar（Chen et al.）就报告过 Gemini 不给图仍远超随机。

## 盲文基线：先把图关掉

每条样本先测常规图文 $S_v$，再把图换空白或删除 image part、保持题干选项不动，测盲文 $S_{wv}$。如果拿得到基座，再测对应的纯 LM $S_t$，观察多模态训练是否增加了背题迹象。

MMStar 定义 multimodal gain $MG=S_v-S_{wv}$，leakage $ML=\max(0,S_{wv}-S_t)$。$S_{wv}$ 比随机高一大截，这张榜就不能当「看图能力」。MMMU 上公开数字：强 LM 不看图也能到四十出头，因为学院选择题的选项和题干已经泄漏了学科常识。面试先报盲文，再报带图；只报一个 MMMU 总分，评委会当没测视觉。

定位时分别查题面是否自包含、选项是否印在图上、训练是否见过原图，以及开发是否反复看测试图调协议。模型从 A/B/C 旁 OCR 出文字再答阅读题，不能代表空间推理；网页、教材或 MMMU 原图进训练，则要用图像哈希、近邻检查补文本 n-gram，canary 可对照 `openai-eval-harness`。公开图上调 high-detail 涨 3 点，也可能只是挑中了更好的协议。

Holdout 必须是从未用来选 checkpoint 的图。公开 MMMU 只能沟通，不能当唯一升模型信号。

## OCR 切片和语义切片不要合成一个分

切片先分 OCR、图表布局、学科视觉推理。白板公式、UI 字符串、发票数字可用外部 OCR 对照；只有抄字能力的模型遇到无字示意图可能失败。轴、图例、柱高还需要相对位置，但题干若重复写“2019 年最大”，又退化成文本题。电路、病理切片、乐谱应确保必须看图，MMMU-Pro 后续筛除文本可答题和 vision-only 设定也针对这一点。

协议锁死：分辨率（low vs high，见 `openai-mm-gpt`）、是否把选项画进图、decoding 温度、是否允许工具。GPT-4V 系统卡自己也按类别谈局限；内部 harness 要按类切片，不要一个 macro。判分：选择题对选项顺序敏感；开放描述不要用被测模型当法官，法官隔版本，同 `openai-eval-harness`。

比较时要保持 CoT 和是否带图等条件一致，OCR 榜不能直接代表 MMMU。指令遵循也单测：“用 JSON 列出图中物体”失败可能只因格式，可接 `openai-if-eval` 排查。

相关：`openai-mm-gpt`

## 追问

**盲文很高一定是作弊吗？**
不一定。有的题就是语言知识。要人审一小部分「必须看图」的金标，不能只看平均。
**提高分辨率算新模型还是新协议？**
新协议。数字要并排报 low / high，不要把 high 的新高写进同一条曲线。
**视频评测多了什么？**
抽帧率和时间戳。描述对、事件安错分钟，不算过。抽样必须固定。
**和 Arena？**
人比看图回答会把文笔和礼貌混进视觉分。私有看图 holdout 仍要留，见 `openai-eval-harness`。
