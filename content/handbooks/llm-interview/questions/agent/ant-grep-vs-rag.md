---
id: ant-grep-vs-rag
section: agent
order: 160
level: A
title: 蚂蚁：Claude Code 用 grep 不用 RAG，二者有何差别？
quick: "代码仓库要精确符号、最新的工作区和能定位到路径行号的结果，grep 和结构化搜索可以边搜边读、循环缩小范围；检索增强生成（RAG）适合相对静态的语义文档。向量库放在代码上容易漏符号、索引过期，所以 Agent 先搜再读，文档那边照样用 RAG。"
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

Claude Code 用 grep，是因为代码仓库要的是精确符号、最新的工作区和能定位到路径、行号的结果，Agent 可以搜一次、读一下、再缩小范围，循环着找。检索增强生成（RAG）假设知识是相对静态的段落，embedding 一次后按相似度取 top-$k$，适合设计文档、工单、制度、FAQ。所以结论是代码走搜索、文档走 RAG，两者可以并存。别答成「Claude Code 不用 RAG，所以 RAG 过时了」，同一面还问了混合召回，文档侧 BM25 加向量照样成立。

举个例子，要找「`PayService#refund` 现在这一版怎么写」，grep 一下符号就拿到路径和行号，再读文件。向量库适合回答「这段代码大概在讲限流」，问精确的方法实现就不稳了。代码仓库的特点是符号要精确匹配、文件随工作区经常改、需要沿着引用跳转、结果必须能解释到路径和行号。`grep`、AST、结构化搜索延迟低，Agent 可以多轮改 query，先搜符号、再读文件、再缩小范围，这是一个闭环探索的过程，和一次性召回性质不同。

代码上用 RAG 常见几种失败：切块把函数切断，或者把同名符号混在一起；索引落后于还没保存的工作区；embedding 对 `error_code`、内部类名这种不稳；权限和 `.gitignore` 很难对齐。所以 Coding Agent 把仓库当文件系统，把文档当 RAG，混着用完全合理。Agent 和 RAG 的职责边界也可以对照 `jd-agent-vs-rag`。

也别承诺「全库 embed 一次就永远能问」。工作区一直在变，索引只反映建立或更新那一刻的快照。评测要看符号命中、跳转对不对、改完文件能不能马上搜到，光用文档 QA 的 nDCG 不够。Agent 侧还要限制一次 grep 返回多少，先给路径列表，再按需 `read_file`，不然等于把半个仓库塞进上下文。这和 Skill 的渐进披露是同一个思路，Harness 和 Skill 渐进披露见 `ant-skills-vs-harness`。归结起来，「Claude 不用 RAG」否定的是代码侧一次性的向量召回，检索本身还在。

## 追问

**那文档知识库还要不要 RAG？**
要。制度、设计文档、工单还是语义文档，同一面的混合召回见 `ant-bm25-hybrid`，别拿这题否定所有检索。

**grep 会不会漏掉同义的实现？**
会。可以用测试名、注释、调用图或者补一次语义检索来查漏，但主路径还是精确搜索，避免一上来就全库向量。

**为什么不把代码也切块放进向量库？**
可以当辅路，别当唯一的一路。必须处理好索引新鲜度和符号级命中，不然它就和过期的 RAG 一样。

**和 Skill 是什么关系？**
Skill 告诉 Agent「先搜再读」这套流程，grep 是它用的工具。渐进披露靠的是在工作区里搜，用不着把整个仓库塞进输入提示（prompt）。
