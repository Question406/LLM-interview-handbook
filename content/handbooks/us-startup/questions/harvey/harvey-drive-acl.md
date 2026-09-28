---
id: harvey-drive-acl
section: harvey
order: 2
level: A
title: Harvey：网盘加权限，或一套律所 RAG
quick: >-
  设计轮几乎是两选一。网盘要把元数据和文件块分开，权限做到组织，不只到个人。
  RAG 要把爬虫规模讲清楚。只讲检索和模型、不讲爬虫，有人因此挂在这一轮。
tags:
  - Harvey
  - System Design
  - RAG
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Harvey AI interview questions catalog
    url: https://aceoffer.app/interviews/harvey
    type: secondary
  - title: Harvey AI Software Engineer experience, 2025-07-06
    url: https://www.jointaro.com/interviews/companies/harvey-ai/experiences/software-engineer-united-states-july-6-2025-no-offer-negative-32e463e6/
    type: candidate-first-hand
---

## 真题记录

AceOffer 对 Harvey onsite 设计轮的汇总：Google Drive 式文件存储加 ACL，出现次数高于 RAG 系统设计。另有一次 2025 年 9 月的支付排程，只出现一次，不当成常考题。

同一页写了他们从报告里摘的失分点：文件题只做了用户级共享，没有组织级；RAG 题把时间花在模型上，爬虫规模被追问时答不上。也有人需求澄清太久，深挖没时间。

2025 年 7 月那则 Jointaro 经验没有留下设计题原文。作者说设计轮面试官英语难懂，最后没弄清要什么，整体是负面体验、没有 offer。技术面和 onsite 的其他轮他觉得难但公平。

招聘邮件若附了设计题说明，报告里说那份说明足够用来准备。开场先读邮件，不要背一份通用网盘。

## 网盘

元数据（路径、owner、ACL、版本）放数据库。文件字节放对象存储，按块。上传大文件先讲分块和断点，不要等面试官问。

权限三层：用户、组、组织。一个律所是组织，所内小组是组。检查顺序我会做成「显式拒绝优先，否则组织默认为拒绝，组和用户的允许再打开」。预签名 URL 只签到这个人被允许的那些块，URL 泄漏也不能读到别的客户的文件。客户之间的数据不要放在同一条没租户键的查询里。

电面的 get/put trie 是 `harvey-coding`。这轮若还在讲内存字典，层次就错了。

## 律所 RAG

管道按这个顺序讲，每一段一个失败模式：

1. 爬虫：律所网盘、邮件、DMS。增量用修改时间，删文件要能从索引撤掉。这里要讲并发和退避，不是讲 embedding 维度。
2. 切块：合同按条款切，不要按固定 512 token 一切到底。块上带着文档 id 和权限。
3. 检索：先按租户和 ACL 过滤，再做向量近邻。不能先搜全局再在应用层丢掉没权限的块，否则近邻结果被无权限文档占满。
4. 生成：答案里的引用必须落在检索到的块上，对得上 `harvey-coding` 的标注题。
5. 评测：引用是否真在源文里、有没有跨客户串文。串文是这道题的事故，不是抽象的幻觉。

## 追问

**预签名 URL 过期前权限被收回？** URL 仍然能读到过期。短过期加上下载前再验一次权限。验权限的那次不要把整个文件再代理一遍。

**爬虫把客户 A 的文件编进客户 B 的索引？** 索引键从写入起就带租户。重建索引按租户做。一次全局重建中间态会串文。

**60 分钟讲不完？** 先写数据模型和一条上传、一条问答的请求路径，再挑面试官追的那一段往下。两套设计都展开，深挖会空。
