---
id: drustz-d9b28cac4b3bde4da1
section: openai
order: 39
level: A
title: Classifier Noisy Annotators
quick: locally-saved-research-summary · Classifier Noisy Annotators
companies:
  - openai
tags:
  - DrustZ
  - locally-saved-research-summary
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/classifier-noisy-annotators
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Classifier with Noisy Annotators / Human-Data 分类器——MLE/RS/RE tech screen 60min

官方题库：classifier-noisy-annotators，coding，high，9 帖，60min tech screen，roles MLE/RS/RE，tags: ml-knowledge/data-cleaning，last_asked 2026-05-26。断档期细节：thread-1178049（2026-05-26 MLE 视频面过经）两轮 screening 共 4 题，其一为 'human data 分类器'（回复区问是否用 pandas——楼主答有 utility）；thread-1176684（2026-05-14《OAI research technical 整套面经》）镜像摘要含 'noisy data handling'。OJ 镜像：'Find the Incorrect Data Labeler'、'Human Labeling and Training a Classifier (ML Coding)'。与候选人 post-training 数据管线背景高度对口。

### 解题与准备提示

（我的推断）给多标注员对同一样本的标签：先算 inter-annotator agreement / 每标注员与多数票的一致率找出坏标注员；清洗后训练简单分类器（logistic regression / 小 NN）；进阶讨论 Dawid-Skene 式标注员置信度加权、类别不平衡与confidence interval。

### 来源与内容类型

- Content kind: `locally-saved-research-summary`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/classifier-noisy-annotators)
- [相关来源](https://www.1point3acres.com/bbs/thread-1178049-1-1.html)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
