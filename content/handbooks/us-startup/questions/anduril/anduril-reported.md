---
id: anduril-reported
section: anduril
order: 1
level: A
title: Anduril：Daily Temperatures、Game of Life、文件夹和雷达
quick: >-
  有人电面被要求用三种写法做每日温度。Senior 轮出现过 Game of Life，第一轮是修一段坏代码。
  另一方面经是连通图、可折叠文件夹，以及一个很开放的雷达数据处理。行为面会追为什么做国防。
tags:
  - Anduril
  - Coding
  - System Design
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Anduril Interview Experience
    url: https://www.reddit.com/r/leetcode/comments/1dde20u/anduril_interview_experience/
    type: candidate-first-hand
  - title: Anduril Senior Software Engineer, United States, 2025-05-01
    url: https://www.jointaro.com/interviews/companies/anduril/experiences/senior-software-engineer-united-states-may-1-2025-no-offer-negative-5f6eb9b4/
    type: candidate-first-hand
  - title: Anduril Software Engineer (New Grad) Interview Experience
    url: https://www.tryexponent.com/experiences/anduril-software-engineer-interview-a63a76
    type: candidate-first-hand
---

## 真题记录

Reddit 上一份 Anduril 面经，题是能对上的：

- 自我介绍、为什么 Anduril、简历。
- LeetCode 739 Daily Temperatures。要了三种：暴力、单调栈、以及输出数组之外 O(1) 额外空间的 DP。
- 另一轮电话：连通图相关的 medium，大约 50 分钟编码。
- 现场前端：做一个能展开折叠的文件夹系统，界面已经有了。
- 设计：雷达收到多路传感器数据，处理后能导出给用户。作者自己也不确定他们要哪一层。

2025 年 5 月 1 日 Jointaro，美国 Senior SWE。第一轮是线上修坏代码。完整 loop 是系统设计、两轮编码、行为面，可以拆两天，都是远程。作者写自己「过了」loop，团队却让招聘去别的组找位置，后面又加了现场编码和经理电话，没有 offer。这则里点名的题是 Game of Life，LeetCode 289。

2026 年 Exponent 上一则校招：没有 OA。招聘电话之后是 60 分钟工程师电话，HackerRank 故意写得含糊。终面三轮各 60 分钟，题目会往外加需求。高级面试官按简历每一行追，并反复问为什么是 Anduril、为什么是国防。作者电话面自认很差，第二天仍进入下一轮，最后没有 offer。

## Daily Temperatures

对每个下标，找右边第一个更暖的一天，输出等几天。

暴力是对每个 i 向右扫。单调栈存还没找到更暖日的下标，温度从栈顶到栈底递增。新的一天比栈顶暖，就弹出并写下距离。

第三种他们要的「输出之外 O(1)」：从右往左填答案。若 `j = i+1` 更暖，答案是 1。否则顺着 `answer[j]` 跳到下一个更暖的候选，跳的时候不用额外栈。最坏仍是 O(n) 次跳跃摊还，不是 O(n^2)。

## Game of Life

原地的话，用数字的第二位存下一状态，第一位留着给邻居读。八个方向数完再右移一位。板子很小就复制一份，Senior 轮若追空间，再写原地。

## 文件夹和雷达

文件夹：树，节点有名字、孩子、是否展开。已有界面就对着它的回调写，不要重做 UI。追问一般是重名、移动、很深的路径。

雷达：先问传感器的记录长什么样、要不要按时间对齐、导出是快照还是流。对象模型是一种传感器一个解析器，上面一个统一的 track。他们若要的是分布式系统，再谈缓冲和迟到数据。Reddit 作者不确定考查点，把两种都准备一句，看面试官往哪边接。

## 追问

**为什么 Anduril 要准备？** 校招那则里这是反复追问，不是寒暄。需要一句你自己的理由，空话会被按简历打回来。

**修坏代码怎么准备？** Senior 的第一轮就是这个，题面没有公开。练在一个小仓库里从失败测试走到一行 diff。Anduril 的编码题也会中途加约束，先把当前约束的测试跑绿。
