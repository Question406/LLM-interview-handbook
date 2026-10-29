---
id: afm-web-reference-guide
section: guide
order: 4
level: A
title: AFM 网站参考题：13 张练习卡、来源与筛选入口
quick: 搜索「AFM 网站参考题」筛选本批 14 张卡：13 张练习与 1 张导读。逐题保留外部来源、AFM 改写范围、回答思路与完整回答。
companies:
  - apple
tags:
  - Apple
  - AFM 网站参考题
  - AFM Web References 2026-10-27
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: Exponent / Aced — AI interview questions
    url: 'https://www.tryexponent.com/questions?page=2&type=artificial-intelligence'
    type: reference
  - title: TechAIInterview — Post-training & Alignment
    url: 'https://www.techaiinterview.com/topics/post-training-alignment/'
    type: reference
---

## 怎么筛选这批卡

切换到 Apple 面试题本，搜索 **AFM 网站参考题**，即可找到本批全部 **14 张卡**：13 张练习与本张导读。也可搜索统一 ID 前缀 `afm-web-`。题卡按知识章节分布，标签将它们连成一批。

本批题目参考公开面试培训网站，按 AFM 备考方向改编。除明确标注的候选人报告外，本批来源是培训题、课程或 mock interview；即使平台给出公司名，也没有据此认定 AFM 出题归属。所有参考答案为本手册独立撰写，设计题用“我会”，没有补造个人经历和结果。

## 对应卡片

| 章节 | 练习 | 外部来源 |
| --- | --- | --- |
| alignment | [[afm-web-dpo-beta|DPO：β 控制什么，为什么不能只用“大或小”解释训练行为？]] | [OpenSkill — Preference Alignment: RLHF, DPO & GRPO](https://app.openskill.ai/interviews/llm.preference-alignment-and-rlhf) |
| alignment | [[afm-web-judge-bias|LLM-as-a-Judge：怎样发现 position、verbosity 和 self-preference bias？]] | [TechAIInterview — Question bank: LLM judge reliability](https://www.techaiinterview.com/questions/) |
| alignment | [[afm-web-posttraining|Post-Training Design：从 base model 到可靠 assistant，数据怎样分工？]] | [TechAIInterview — Post-training & Alignment Q7](https://www.techaiinterview.com/topics/post-training-alignment/) |
| alignment | [[afm-web-reward-hacking|Reward Model：怎样训练，并识别高分却退化的 reward hacking？]] | [TechAIInterview — Post-training & Alignment Q4](https://www.techaiinterview.com/topics/post-training-alignment/) |
| data | [[afm-web-data-pipeline|Data Pipeline：怎样从杂乱语料构建可追溯、可扩展的训练数据？]] | [Exponent / Aced — Designing a Data Processing Pipeline](https://www.tryexponent.com/courses/ml-system-design/mlsd-data-pipeline) |
| evaluation | [[afm-web-agent-evals|Agent Evaluation：客服 agent 上线前后怎样评估，并把失败转成训练信号？]] | [Exponent / Aced — Agent evaluation question](https://www.tryexponent.com/questions/6610/evals-ai-customer-support) |
| evaluation | [[afm-web-benchmark-two-points|Benchmark Debugging：500 题提高 2 个点，真的变强了吗？]] | [TechAIInterview — Question bank: benchmark improvement](https://www.techaiinterview.com/questions/) |
| multimodal | [[afm-web-photos-search|Multimodal Search：私人照片搜索的数据、评估和 model upgrade 怎么设计？]] | [DataInterview — Design Google Photos search](https://www.datainterview.com/courses/google-machine-learning-engineer/photos-search) |
| projects | [[afm-web-apple-project-deepdive|Apple AI 项目追问：data gap、model choice、eval 与 production readiness 怎样讲清楚？]] | [Exponent / Aced — Apple Senior AI PM interview experience](https://www.tryexponent.com/experiences/apple-senior-product-manager-interview-6f4f3b?returnPath=%2Fexperiences) |
| synthetic | [[afm-web-synthetic-loop|Synthetic Data：只有几百条 seed，怎样生成并筛出有用的训练样本？]] | [Sahi Padhai — Training Data and Synthetic Data](https://sahipadhai.cc/course/ai-engineer-interview/training-data-and-synthetic-data) |
| synthetic | [[afm-web-synthetic-privacy-bias|Synthetic Data Audit：合成数据为什么仍会泄露隐私或放大 bias？]] | [Sahi Padhai — Training Data and Synthetic Data: follow-ups](https://sahipadhai.cc/course/ai-engineer-interview/training-data-and-synthetic-data) |
| systems | [[afm-web-video-feedback|Recommendation Flywheel：观看行为怎样变成标签，又怎样避免 feedback bias？]] | [Hello Interview — Video Recommendations](https://www.hellointerview.com/learn/ml-system-design/problem-breakdowns/video-recommendations) |
| tensor | [[afm-web-attention-code|Self-Attention Coding：实现 batched causal attention，并处理全 padding 行]] | [Deep-ML — Implement Self-Attention Mechanism](https://www.deep-ml.com/problems/53) |

## 来源可见范围

核对日期：2026-10-27。Deep-ML 可见题名与 coding 入口；Exponent 的 agent 题可见题面，data pipeline 为标注 Premium 的课程，其公开部分可读。TechAIInterview 的搜索索引可见题目、部分简答与 walkthrough 说明，直接抓取部分页面失败，未声称完整长答案均已核验。OpenSkill 可见样题，未运行付费或登录后的动态 mock。Sahi Padhai 搜索索引可见完整相关章节，直接页面抓取失败。DataInterview Photos 可见 preview，完整课程锁定。Hello Interview 可见 video recommendation worked example。Apple AI PM 为平台上的个人候选人报告，未核实其具体团队。

## 与 AFM 的匹配程度与适用范围

直接匹配：attention coding、reward model、DPO、post-training、judge bias、benchmark 统计。场景迁移：agent evaluation、synthetic tool-use、private photo search 和 recommendation feedback。Apple 项目卡来自其他岗位的候选人报告，只用于练习追问。

尚不能用现成题完全覆盖：pre/mid/post-training 的统一 data strategy、复杂 reasoning/tool-use synthetic factory、See Around Corners 真实个人故事。已在相关卡中加入设计追问，扩展部分由本手册编写。

推荐先做 attention、reward hacking、judge bias 和 agent evaluation，再讲 post-training 与 Photos search。详细说明折叠在原题技术备查中；每题完整回答顶部有 Situation、Task、Approach、Result callout。

