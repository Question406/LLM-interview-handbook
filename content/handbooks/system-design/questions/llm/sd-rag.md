---
id: sd-rag
section: llm
order: 24
level: A
title: 生产 RAG：检索、权限、新鲜度与引用
quick: 假设员工问公司报销规则。检索结果不仅要相关，也必须是他有权读取、仍然有效的版本。
companies: []
tags:
  - System Design
  - 设计练习
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: Retrieval-Augmented Generation 原论文
    url: 'https://arxiv.org/abs/2005.11401'
    type: primary
  - title: Google SRE Book：Service Level Objectives
    url: 'https://sre.google/sre-book/service-level-objectives/'
    type: primary
---

## 题目描述

为企业内部文档设计问答服务。文档来自多个部门，权限会变，内容会更新和删除；回答必须附可访问的依据。手册练习目标是秒级回答，索引允许分钟级更新。请输出接入、切分、索引、检索、重排与生成路径，说明过期文档、撤权、拒答与评测。不要把文档中的指令当作调用工具的授权。

### 作答要求与场景

请用文字与图说明输入或业务事件怎样到达最终输出，写清失败或重试时用户能观察到的结果。给至少一个具体请求或事件序列作为示例，最后说明怎样验证设计。场景假设与补充规则由本手册设定。

## 回答思路

> **问题与场景：** 假设员工问公司报销规则。
>
> **做法与原因：** 我会先处理文档与权限，再做检索、reranking 和回答生成，并让引用能指向支持答案的原文。
>
> **检查与取舍：** 评估分别看相关证据是否被召回、答案是否被证据支持，以及权限和更新是否生效。

## 可以这样回答

假设员工问公司报销规则。检索结果不仅要相关，也必须是他有权读取、仍然有效的版本。

我会先处理文档与权限，再做检索、reranking 和回答生成，并让引用能指向支持答案的原文。找不到充分证据时，需要明确说明或继续查，而不是补一个像真的答案。

评估分别看相关证据是否被召回、答案是否被证据支持，以及权限和更新是否生效。这样才知道该修检索还是生成。

## 技术备查

## 参考答案与设计讨论

把文档接入与查询链路分开，权限过滤贯彻检索、重排与引用；评估分别定位检索漏召回和生成无依据。

![生产 RAG：检索、权限、新鲜度与引用：核心数据流](/system-design/rag.svg)

图展示核心数据流；权限、状态和故障恢复以正文约定为准。

### 离线接入与版本

连接器记录文档标识、版本、ACL 与删除标记；解析和切分产出带来源位置的 chunk，索引更新可恢复且幂等。切分与 embedding 版本变化要可回滚，不把新旧向量空间随意混在一起。

### 在线权限与生成

查询认证后执行关键词与向量召回，在可行的阶段应用权限过滤；重排后再检查当前权限和版本。只把允许的片段交给模型，并绑定引用。索引 ACL 传播存在延迟时，敏感授权需要权威校验；不能生成完才发现上下文已经泄漏。

### 评估和降级

用带答案依据的留出集分开测召回、引用正确、忠实性与拒答；加撤权、删除和无答案场景。检索超时可返回明确失败或允许的关键词结果，不能让模型凭记忆编造企业事实。缓存键也应包含权限范围与相关版本。

### 示例与关联

用户 U 退出项目后，即使其旧问题命中缓存，也不应返回项目机密引用。完整细节见[生产 RAG](?book=us-tech&section=design&question=design-prod-rag)、[多模态 RAG](?book=us-tech&section=design&question=design-mm-rag)、[长文档问答](?book=us-tech&section=design&question=design-long-doc)和[混合搜索](?book=us-tech&section=design&question=design-search)。

