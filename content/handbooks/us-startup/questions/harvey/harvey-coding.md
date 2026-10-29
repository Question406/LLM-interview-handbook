---
id: harvey-coding
section: harvey
order: 1
level: S
title: Harvey：路径文件库、表格公式环、引用标注
quick: >-
  Harvey 电面从三道里抽：按路径 get/put 的文件库，带公式、要检出环的表格，以及找出回答片段在原文中位置的引用标注。2025 年 3 月到
  2026 年 8 月，引用标注在汇总记录中出现得最多。每道都先把最小版本跑通，constraints 当场问清。
tags:
  - Harvey
  - Coding
  - RAG
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22T00:00:00.000Z
sources:
  - title: 'Harvey AI Software Engineer experience, file storage, 2025-07-06'
    url: >-
      https://www.jointaro.com/interviews/companies/harvey-ai/experiences/software-engineer-united-states-july-6-2025-no-offer-negative-32e463e6/
    type: candidate-first-hand
  - title: 'Harvey AI interview questions catalog, Mar 2025–Aug 2026'
    url: 'https://aceoffer.app/interviews/harvey'
    type: secondary
  - title: 'harvey interview questions (2026), 1Point3Acres'
    url: 'https://www.1point3acres.com/interview/company/harvey'
    type: secondary
---

## 题目描述

公开复盘涉及下面三个独立编程方向，未披露完整原题或函数签名。以下是可用于练习的手册重构约定，不能据此声称是 Harvey 官方完整题面。面试时应先与面试官确认路径、公式和引用格式的具体语义。

### 子题 A：路径文件存储

实现一个内存中的层级文件存储。练习接口提供创建目录、写入/覆盖文件、按路径读取文件和列出目录直属子项。路径是以 `/` 开头的规范绝对路径；所有操作的目标类型及父目录均满足约定，输入合法。目录列表按名称升序返回，不递归展开。

示例：创建 `/docs`，在 `/docs/a.txt` 写入 `hello` 后，读取该文件得到 `hello`，列出 `/docs` 得到 `["a.txt"]`。再次向相同文件写入 `bye` 后读取应得到 `bye`。提交可调用实现及覆盖创建、读取、覆盖、目录层级的简单测试。

### 子题 B：表格公式依赖

维护一张以单元格名为键的表格。练习仅支持整数常量和引用若干单元格相加的公式；引用单元格均存在。支持设置常量、设置公式和读取计算结果。设置新公式时，若会造成直接或间接依赖环，该次更新必须被拒绝且保留原状态；上游单元格修改后，下游读到更新后的值。具体函数签名由练习者自行定义。

示例：A1=2，B1=A1+3 时读取 B1 得到 5；把 A1 改成 4 后得到 7。此时再将 A1 设置为 B1+1 会构成环，更新应被拒绝，A1 和 B1 的原状态保留。

### 子题 C：引用标记

公开复盘只提到 citation tagging，没有披露精确标记规则。为提供一个可运行的小练习，约定输入为正文及一组已给定的半开字符区间 `(start, end, source_id)`；区间合法、互不重叠、按起点递增。输出保留原文，在每个区间结尾紧接插入 `[source_id]`；同一来源可以出现多次。字符索引按 Python 字符串索引解释。

示例：正文 `Alpha beta.`，区间 `(0, 5, "S1")`，输出 `Alpha[S1] beta.`。空区间列表原样返回正文。此区间格式是手册练习约定。

## 解题思路与参考答案

Harvey 的 SWE 电面是一道编码，大约一小时，用 CoderPad，题基本从三道里抽：按路径存取的文件库、带公式和环检测的表格，还有引用标注。三道的算法都不复杂，要做好的是把 constraints 问清，在时间内把最小版本跑通。

AceOffer 把 2025 年 3 月到 2026 年 8 月的报告收成了这三道编码，出现次数是他们自己的统计，不是官方频率。统计里最多的是检索增强生成（RAG） citation / text matching and tagging，最近一次在 2026 年 8 月；然后是 Spreadsheet，格子 get/set、公式、环检测；还有 File system，按路径存取。2025 年 7 月 6 日 Jointaro 上一位美国 SWE 候选人写的原话是 code a file storage system to get/put via paths。一亩三分地的题目标题里还有 filesystem trie、Excel cell、circular dependency、tagging matched source。这些帖子的正文多数要登录，函数签名我不补。

文件库最直接。路径按 `/` 切开，用嵌套字典或 trie，中间节点是目录，叶子是文件内容。`put` 时缺的目录是顺手建出来还是报错，先问清楚；`get` 打到目录上要给明确的错误。磁盘、权限、分块先别写，那些是设计轮 `harvey-drive-acl` 的内容，电面 45 分钟能把 put/get/list 跑通就够了。

表格的格子存两种东西，要么是字面量，要么是一个依赖其他格子的公式。`set` 之后，依赖这个格子的公式要重算。环检测放在写公式的时候做：格子是点，公式里引用的格子连一条边，写入前在这张图上从新边出发 DFS，走回自己就拒绝这次写入。三色标记够用，拓扑排序也能做，面试里格子数量不大。公式语法公开帖没给，我会假设四则运算加单元格名字，并问清是不是只有这一种。区域引用 `A1:B3` 题面没写就别自己加。

引用标注是模型输出一段话，里面带引用，要找出引用在源文本里的位置。公开帖没有打分公式。我的顺序是先把空白 normalization，做精确子串匹配，记下 `(doc_id, start, end)`；精确匹配失败，再问面试官能不能模糊匹配、重叠的引用留哪一个。常见的失分写法是只返回文档 id。题名里的 tagging 是在文本上做标记，偏移量才是主要结果。

## 追问

**文件很多时用 trie 还是哈希表？**
先写嵌套 dict。电面路径总量小，dict 写起来更短。要按前缀列举的话，trie 和「按路径排序的 map」都能做。

**环已经存在时，再读这个格子怎么办？**
写入时就拒绝了，图里不会有环，读的时候不用再测。如果题目要求容错读取，环上的格子返回错误，别无限递归。

**引用在原文里对到两处相同的句子？**
先问要第一处还是全部。默认返回第一处，把全部命中留在注释里，等面试官要了再返回列表。
