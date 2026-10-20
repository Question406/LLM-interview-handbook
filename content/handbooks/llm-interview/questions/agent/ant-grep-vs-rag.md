---
id: ant-grep-vs-rag
section: agent
order: 160
level: A
title: 蚂蚁：Claude Code 用 grep 不用 RAG，二者有何差别？
quick: "Grep 和结构化搜索面向代码仓库的精确符号与路径，可以循环缩小范围；检索增强生成（RAG） 面向语义文档召回。代码任务需要精确命中和可解释定位，向量库容易漏符号、索引过期，所以 Agent 常先搜再读，而不是先 embed 全库。"
tags:
  - Ant Group
  - RAG
  - Agent
  - Claude Code
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 蚂蚁智能体与大模型应用 一面
    url: https://www.nowcoder.com/discuss/888874988554448896
    type: candidate-first-hand
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：智能体与大模型应用
- 届别 / 流程：一面
- 面试时间：2026-05-20
- 来源类型与可信度：牛客候选人原帖，A（公司、日期与岗位明确）
- 原始措辞：**“Claude Code是给模型用grep检索，没有用RAG检索，这俩有什么区别？为什么没用rag？”**

常见误区是：「Claude Code 不用 RAG，所以 RAG 过时了」。同一面还问混合召回，文档侧 BM25+向量仍然成立。我会对比工作区精确搜索和静态语义召回，再说明代码 Agent 为什么先搜再读。Harness 与 Skill 渐进披露见 `ant-skills-vs-harness`。

## 二者假设不同

检索增强生成（RAG） 假设知识是相对静态的段落，一次 embedding 后按相似度取 top-$k$。适合设计文档、工单、制度、FAQ。代码仓库相反：符号要精确匹配、文件随工作区常改、需要沿引用跳转、结果必须可解释到路径和行号。`grep` / AST / 结构化搜索延迟低，Agent 可以多轮改 query：先搜符号，再读文件，再缩小范围。这是闭环探索，不是一次召回。

## 代码上 RAG 容易怎么失败

切块切断函数或把同名符号混在一起；索引落后于未保存的工作区；embedding 对 `error_code`、内部类名不稳；权限与 `.gitignore` 难对齐。向量库适合「这段代码大概在讲限流」，不适合「`PayService#refund` 现在这一版怎么写」。所以 Coding Agent 把仓库当文件系统，把文档当 RAG。混合完全合理：文档走 RAG，代码走搜索工具。Agent vs RAG 的职责边界也可对照 `jd-agent-vs-rag`。

不要承诺「全库 embed 一次就永远可问」。工作区不断变化，索引只反映建立或更新时的快照。评测应用符号命中、跳转正确、以及改文件后能否立刻搜到，而不是只用文档 QA 的 nDCG。Agent 侧还要限制一次 grep 的结果体积：先给路径列表，再按需 `read_file`，否则等于把半个仓库塞进上下文。这和 Skill 渐进披露是同一思想。代码走精确搜索闭环，文档走 RAG；「Claude 不用 RAG」否定的是代码侧一次向量召回，不是检索本身。

## 追问

- **那文档知识库还要不要 RAG？** 要。制度、设计、工单仍是语义文档。同面混合召回见 `ant-bm25-hybrid`，不要用这题否定所有检索。
- **grep 会不会漏同义实现？** 会。可用测试名、注释、调用图或一次语义检索补漏，但主路径仍是精确搜索，避免一上来全库向量。
- **为什么不把代码也切块进向量库？** 可以当辅路，不能当唯一路。必须处理索引新鲜度和符号级命中，否则和过期 RAG 一样。
- **和 Skill 的关系？** Skill 告诉 Agent 先搜再读的程序；grep 是工具。渐进披露靠工作区搜索，不是把全仓塞进 输入提示（prompt）。
