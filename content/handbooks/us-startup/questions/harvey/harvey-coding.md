---
id: harvey-coding
section: harvey
order: 1
level: S
title: Harvey：路径文件库、表格公式环、引用标注
quick: >-
  电面从这三道里抽。文件库是按路径 get/put。表格是格子的 get/set 加公式，要检出环。
  引用标注是找出回答片段在原文中的位置。2025 年 3 月到 2026 年 8 月，引用标注在汇总记录中出现得最多。
tags:
  - Harvey
  - Coding
  - RAG
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Harvey AI Software Engineer experience, file storage, 2025-07-06
    url: https://www.jointaro.com/interviews/companies/harvey-ai/experiences/software-engineer-united-states-july-6-2025-no-offer-negative-32e463e6/
    type: candidate-first-hand
  - title: Harvey AI interview questions catalog, Mar 2025–Aug 2026
    url: https://aceoffer.app/interviews/harvey
    type: secondary
  - title: harvey interview questions (2026), 1Point3Acres
    url: https://www.1point3acres.com/interview/company/harvey
    type: secondary
---

## 真题记录

Harvey 的 SWE 电面是一道编码，大约一小时，CoderPad。AceOffer 把 2025 年 3 月到 2026 年 8 月的报告收成三道编码，出现次数是他们的统计，不是官方频率：

- 检索增强生成（RAG） citation / text matching and tagging，统计里最多，最近一次 2026 年 8 月
- Spreadsheet，格子 get/set、公式、环检测
- File system，按路径存取

2025 年 7 月 6 日 Jointaro 上一位美国 SWE 候选人写的原话是：code a file storage system to get/put via paths。一亩三分地的题目标题里还有 filesystem trie、Excel cell、circular dependency、tagging matched source。这些帖的正文多数要登录，函数签名我不补。

## 路径文件库

路径按 `/` 切开，用嵌套字典或 trie。中间节点是目录，叶子是文件内容。`put` 时缺的目录顺手建出来还是报错，先问。`get` 打到目录上要有明确错误。

不要先写磁盘、权限、分块。那些是设计轮 `harvey-drive-acl` 的内容。电面 45 分钟能把 put/get/list 跑通就够。

## 表格和环

格子存两种东西：字面量，或者一个依赖其他格子的公式。`set` 之后，依赖这个格子的公式要重算。

环的检测做在写公式的时候。格子是点，公式里引用的格子拉一条边。写之前在这张图上从新边 DFS，走到自己就拒绝这次写入。三色标记够用。拓扑排序也能，格子数量在面试里不大。

公式语法公开帖没给。我会假设四则运算加单元格名字，并问清是不是只有这一种。不要自己加上区域引用 `A1:B3`，除非题面写了。

## 引用标注

模型输出一段话，里面有引用，要找出引用在源文本中的位置。公开帖没有打分公式。我的顺序是：空白归一化之后先做精确子串，记下 `(doc_id, start, end)`；精确失败再问面试官能不能模糊、重叠引用留哪一个。

常见误区是只返回文档 id。题名里的 tagging 是在文本上做标记，偏移量是主要结果。

## 追问

**文件很多时 trie 和哈希表？** 电面路径总量小，嵌套 dict 更短。若要前缀列举，trie 和「按路径排序的 map」都能做。先写 dict。

**环已经存在，再读这个格子？** 写入时拒绝，图里就没有环，读的时候不用再测。若题目要求容错读取，环上的格子返回错误，不要无限递归。

**引用对到两处相同句子？** 问要第一处还是全部。默认第一处，把全部命中留在注释里，等面试官要再返回列表。
