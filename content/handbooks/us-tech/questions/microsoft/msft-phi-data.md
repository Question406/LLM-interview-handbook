---
id: msft-phi-data
section: microsoft
order: 11
level: S
title: Microsoft：Phi「教科书数据」质量 vs 规模，污染和评测切片
quick: >-
  Phi
  把过滤、合成和课程作为数据质量的操作手段，并与规模一起扩展。高质量过滤不等于去污，还要查直接重叠、教师泄漏与改写近邻。验收同时保留公开榜、去污切片、新鲜私有题和同计算数据对照，才能判断收益来自哪里。
tags:
  - Microsoft
  - Phi
  - Data Quality
  - Contamination
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Textbooks Are All You Need
    url: 'https://arxiv.org/abs/2306.11644'
    type: primary
  - title: Textbooks Are All You Need II
    url: 'https://arxiv.org/abs/2309.05463'
    type: primary
  - title: Phi-3 Technical Report
    url: 'https://arxiv.org/abs/2404.14219'
    type: primary
  - title: Phi-4 Technical Report
    url: 'https://arxiv.org/abs/2412.08905'
    type: primary
---

## 可以这样回答

Phi 的数据路线是提高每个 token 的有效信息，再与规模一起扩展。过滤、合成和课程要分别做对照，公开榜提升还要检查是否来自泄漏。例如教师见过 HumanEval，生成一份改写题，学生即使没直接复制题面也可能获得不公平收益。

Phi-1 约 $1.3\mathrm{B}$，使用约 $7\mathrm{B}$ 高质量代码 token，包括过滤 The Stack / StackOverflow 的 CodeTextbook 与 GPT-3.5 合成教材，再用约 $180\mathrm{M}$ CodeExercises 做习题微调，HumanEval 胜过使用更大、较脏语料的代码模型。网页中的模板、重复和错误会让有效 $N$ 低于总计数，高质量并不意味着越少越好。

## 技术备查

Phi 的数据路线是提高每个 token 的有效信息，再与规模一起扩展。过滤、合成和课程要分别做对照，公开榜提升还要检查是否来自泄漏。例如教师见过 HumanEval，生成一份改写题，学生即使没直接复制题面也可能获得不公平收益。

本卡依据 Phi-1 / Phi-1.5、Phi-3、Phi-4 的公开报告讨论配方，未声明逐字面经，`realInterview: false`。小模型产品定位见 `msft-phi-slm`。

## 将质量变成可以比较的管线

Phi-1 约 $1.3\mathrm{B}$，使用约 $7\mathrm{B}$ 高质量代码 token，包括过滤 The Stack / StackOverflow 的 CodeTextbook 与 GPT-3.5 合成教材，再用约 $180\mathrm{M}$ CodeExercises 做习题微调，HumanEval 胜过使用更大、较脏语料的代码模型。网页中的模板、重复和错误会让有效 $N$ 低于总计数，高质量并不意味着越少越好。

Phi-3 将过滤网文扩到约 $3.3\mathrm{T}$ token，mini 先用有教育价值的网文学习知识语言，再用更严过滤子集与合成补推理。Phi-4 将合成扩到预训练主料之一，不能继续把配方说成仅用 7B token。

过滤可以让分类器打教育价值、代码正确性，清掉模板、重复、有害内容，同时保留未过滤对照检查风格偏差。合成用大模型编章节、习题、步骤证明，补长尾也会带入 hallucination 与测试题。课程从基础到难题，借鉴 Orca 的轨迹学习，相关见 `msft-phi-slm`。

Chinchilla 讨论计算、参数与 token 数量，Phi 强调信息密度，两者可以同时改进。同样数据用于 70B 往往也会更好，3.8B 部署限制并不表示数据只对小模型有效。采集过滤和教师合成各自需要计算预算。

## 去污与能力验收分开

直接重叠用 n-gram / MinHash 查 HumanEval、MBPP、MMLU，exact hash 会漏空白标点变化。教师间接泄漏还需 embedding 近邻、答案指纹与教师也未见的私有题；Phi-4 也指出标准 n-gram 难挡 paraphrase，协议见 `align-eval-contam`。

Phi-1 曾按 embedding 与 AST 编辑距离删去大量相似 CodeExercises，论文约 40% 量级，重训后仍领先。这提供了去污对照，不能证明所有后续数据都干净。

| 切片 | 测什么 | 为什么 Phi 特别怕 |
| --- | --- | --- |
| 公开榜 | HumanEval / MMLU / GSM8K | 合成和网文最容易撞 |
| 去污后公开榜 | 同一套但去掉 n-gram 命中的题 | 看分数是掉一点还是塌 |
| 新鲜 / 私有 | 日期在训练截止之后的竞赛、内部题 | 教师也没见过才算能力 |
| 能力轴 | 代码执行、多步数学、世界知识、指令 | 教科书强在讲解，弱在长尾事实 |
| 对照轴 | 同计算脏数据 vs 过滤数据 | 没有这组，质量故事无法证伪 |

产品再加端侧延迟、拒答和检索引用。Phi-3 的 128k 也要按长度与证据位置切，见 `msft-long-context`，流畅纪要或 needle 不够。质量改善能力与成本取舍，世界知识、新内部 API 和对抗鲁棒仍可能需要大模型或 RAG。

## 追问

**合成算 distillation 吗？**
属于手段之一，Phi-1 也有人类代码。Phi-4 若要在部分 STEM 超过教师，需要执行代码、符号推导等可校验数据和新鲜题证明。

**内部评测就不会污染吗？**
也会。做时间切分、与训练检索隔离并人写新题，HuggingFace 新榜可能只是旧题改写。

**过滤会不会损伤多语言？**
会。教育价值分类器可能偏正式英文和竞赛数学，方言、低资源语言和企业黑话需单独检查阈值与召回。
