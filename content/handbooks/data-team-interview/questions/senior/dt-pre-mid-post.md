---
id: dt-pre-mid-post
section: senior
order: 1
level: S
title: Director：pre-training / mid-training / post-training 的数据策略怎么切？
quick: "先判断能力缺口属于哪一阶段：pre-training 扩大知识覆盖并清理网页；mid-training 用高质量材料和验证合成调整能力配比；post-training 用示范、过程监督、偏好与规则奖励教行为。不能把所有问题都交给 SFT，也不能把 continued PT 与 SFT 混为一谈。"
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

先判断能力缺口属于哪个训练阶段，再选择数据。不能每次遇到问题都重训 14T token。

guideline 强调这个岗位覆盖整个训练生命周期。所有能力问题都用监督微调（SFT）解决，或把 continued pre-training 与 SFT 统称「再训一会儿」，就无法解释数据与成本选择。Core 最昂贵，错误过滤造成的算力浪费，后面很难补回来。

## 三个阶段使用不同数据

AFM 2024 已经把预训练拆成 core / continued / context-lengthening。2025 把 continued 写得更像现在社区说的 mid-training：在核心预训练之后，用更高质的 mix 和验证合成扩能力，再接 SFT + 基于人类反馈的强化学习（RLHF）。

| 段 | 目标 | 数据 | 典型干预 |
| --- | --- | --- | --- |
| Pre（core） | 语言 / 世界的宽覆盖，消耗大部分算力 | 许可、公开集、Applebot 粗过滤后的网页，图文对 | 抽取、启发式+模型过滤、去重、域配额 |
| Mid（continued PT） | 补特定能力，少伤已有能力 | 验证合成 + 最高质量的非合成数据 + 一部分 bulk；视觉再混交错和 caption | 改权重（多语 8%→30%）、验证门、课程 |
| Post（SFT + 强化学习（RL）） | 指令、工具、偏好、产品格式 | 人写示范、过程监督轨迹、偏好对、规则奖励题 | 协议、验证器（verifier）、奖励模型（RM） cohesion、adapter |

2024 报告里 continued 在 8k 上下文上约 1T token，抬数学 / 代码、压低 bulk crawl，并加入许可数据。2025 文本 continued 明确用验证过的合成（代码、数学、机翻多语文档），多语配额用课程抬到 30%，组内仍温度采样，避免低资源过拟合。视觉 mid：60% 高质文本、10% 交错、28.5% caption、1.5% 领域图文。最后一段 context 用到 65K，来源是许可长书 / 代码库、针对 ICL 和检索的合成长文、以及前一段的 mix。

Post 的公开要点：改进通用后训练能抬所有 feature adapter；工具单独提高质量；RL 混 RM 和规则。产品功能很多走 adapter，但底座后训练仍值得做。

## 缺口来了，先点名段落

某语言理解普遍弱，指令还没开始训：进 mid，抬配额、验证机翻、按语言校准过滤。不要先 SFT 一万条聊天。

会解题，不会按用户格式答，工具 字段和类型规范（schema） 乱：进 post，SFT 示范 + 过程监督。Mid 解决不了 schema。

网页正文混入杂质、重复转载很多时，先修复 pre 阶段的抽取与去重。直接将这批网页用于 SFT，会浪费后训练预算。

长文档检索差，短题还行：进 context mid，真长文 + 合成 ICL，不要只靠 chat SFT 的 4k 对话。

视觉编码器对齐差：进 mid 的视觉适配段，不是 RLHF 第一刀。RL 可以更新视觉编码器，但 AFM 也是先适配再 RL。

Director 要听的是你知道每一段的不可逆代价。Core 最贵，滤错了后面补不回那些 token 的计算。Mid 会改能力剖面，配比动错会伤英语或通用知识。Post 最便宜也最容易过拟合模板和 RM。

## 我会怎么切

「Pre 决定模型见过什么世界；mid 决定哪些能力被加权和验证；post 决定它听谁的、用什么工具、拒绝什么。我默认把可验证的能力缺口放进 mid，把格式、工具和主观偏好放进 post，只有覆盖性的质量问题才回 pre。」

端侧和 server 共用这条切法，但端侧 mid / post 还要受 token 预算和 adapter 绑定约束。3B 不是开放 chatbot，灌开放世界长知识进 post，不符合端侧产品的任务要求。

## 追问

- **Mid 和 Post 都用合成，怎么分？** Mid 的合成像文档：验证过的题解、机翻书、长文。Post 的合成像对话：带 user / assistant、工具、拒答。验证强度可以一样，schema 不同。
- **能不能跳过 mid，全靠 SFT？** 覆盖性的数学 / 多语 / 长上下文，SFT 条数通常不够改底座表示。AFM 选择先 continued 再 SFT。
- **蒸馏算哪一段？** 端侧 core 末段用 MoE 教师模型（teacher） 蒸 1.4T，仍是 pre。教师logits 的质量跟着教师数据走，不是 post。
