---
id: dt-pre-mid-post
section: senior
order: 1
level: S
title: Director：pre-training / mid-training / post-training 的数据策略怎么切？
quick: "先判断能力缺口属于哪一阶段，再选数据：pre-training 扩大知识覆盖并清理网页；mid-training 用高质量材料和验证过的合成调整能力配比；post-training 用示范、过程监督、偏好和规则奖励教行为。覆盖性能力（数学、多语、长上下文）靠 SFT 的条数改不动底座，所以 continued PT 和 SFT 要分开设计。"
companies:
  - apple
tags:
  - Apple
  - Pre-training
  - Mid-training
  - Post-training
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Apple Intelligence Foundation Language Models (2024)
    url: https://arxiv.org/abs/2407.21075
    type: primary
---

我先判断能力缺口属于哪个训练阶段，再决定用什么数据。Pre 决定模型见过什么世界；mid 决定哪些能力被加权和验证；post 决定它听谁的、用什么工具、拒绝什么。我默认把可验证的能力缺口放进 mid，把格式、工具和主观偏好放进 post，只有覆盖性的质量问题才回到 pre，因为每回一次 pre 都要重花大部分算力。

所有能力问题都交给监督微调（SFT），或者把 continued pre-training 和 SFT 统称为「再训一会儿」，就解释不了数据和成本上的取舍。

## 为什么要分段：每段的代价不同

每一段的代价和可逆程度不同。Core 预训练最贵，过滤错了，那些 token 花掉的算力后面补不回来。Mid 会改变能力剖面，配比动错会伤到英语或通用知识。Post 最便宜，也最容易过拟合模板和 RM。

## 三个阶段使用不同数据

现在社区说的 mid-training，指核心预训练之后、SFT 和基于人类反馈的强化学习（RLHF）之前的一段：用更高质量的 mix 和验证过的合成扩展能力。AFM 2024 报告把预训练拆成 core / continued / context-lengthening，2025 年的 continued 就是这个意思。下表的数据例子取自这两份公开报告。

| 段 | 目标 | 数据 | 典型干预 |
| --- | --- | --- | --- |
| Pre（core） | 语言 / 世界的宽覆盖，消耗大部分算力 | 许可、公开集、粗过滤后的网页，图文对 | 抽取、启发式+模型过滤、去重、域配额 |
| Mid（continued PT） | 补特定能力，少伤已有能力 | 验证合成 + 最高质量的非合成数据 + 一部分 bulk；视觉再混交错和 caption | 改权重（多语 8%→30%）、验证门、课程 |
| Post（SFT + 强化学习（RL）） | 指令、工具、偏好、输出格式 | 人写示范、过程监督轨迹、偏好对、规则奖励题 | 协议、验证器（verifier）、奖励模型（RM） |

按能力看 mid 的数据：数学和代码靠提高比例、加验证过的题解；多语靠提高配额和验证机翻；长上下文靠真实长文加合成的检索数据。多语配额按课程逐步提高时，组内仍用温度采样，避免低资源语言过拟合。公开数字可以参考 AFM 2024 / 2025 报告：continued 阶段在 8k 上下文上训约 1T token，多语配额提到 30%，最后把上下文扩到 65K。

Post 阶段教行为：指令遵循、工具调用、偏好。常见做法是 RL 混用 RM 和规则奖励：能验证的（数学、代码、格式）用规则，主观质量用 RM。通用后训练做好会抬高下游所有任务，工具调用则需要单独造数据。

## 缺口来了，先判断归哪段

- 某种语言的理解普遍弱，指令还没开始训：进 mid，提高配额、验证机翻、按语言校准过滤。不要先 SFT 一万条聊天。
- 会解题，但不会按用户要求的格式回答，工具的字段和类型规范（schema）也乱：进 post，用 SFT 示范加过程监督。Mid 解决不了 schema。
- 网页正文混入杂质、重复转载很多：先修复 pre 阶段的抽取与去重。直接把这批网页用于 SFT，会浪费后训练预算。
- 长文档检索差，短题还行：进 context mid，用真实长文加合成 ICL 数据。chat SFT 的 4k 对话教不会长文检索。
- 视觉编码器对齐差：进 mid 的视觉适配段，先做适配再上 RLHF。RL 可以更新视觉编码器，所以顺序是先适配后 RL。

## 追问

- **Mid 和 Post 都用合成，怎么分？** Mid 的合成像文档：验证过的题解、机翻书、长文。Post 的合成像对话：带 user / assistant 角色、工具调用、拒答。验证强度可以一样，schema 不同。
- **能不能跳过 mid，全靠 SFT？** 数学、多语、长上下文这类覆盖性能力，SFT 的条数通常不够改变底座的表示，所以要先 continued 再 SFT。
- **蒸馏算哪一段？** 看蒸馏损失加在哪段训练里。小模型在 core 末段用教师模型（teacher）的 logits 蒸馏，仍属于 pre；AFM 2025 报告里这一段约 1.4T token。教师 logits 的质量取决于教师的数据，跟 post 无关。
