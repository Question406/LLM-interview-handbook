---
id: anduril-reported
section: anduril
order: 1
level: A
title: Anduril：Daily Temperatures、Game of Life、文件夹和雷达
quick: >-
  Anduril 的公开面经里，有人电面被要求用三种写法做每日温度；Senior 轮第一轮是修一段坏代码，点名的题是 Game of Life。另一份面经考了连通图、可折叠的文件夹，以及一个很开放的雷达数据处理设计。行为面会反复追为什么做国防，要提前想好自己的理由。
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

## 题目描述

公开复盘汇总了多个独立轮次，并未给出一份统一试卷。下面将已披露方向分开表述；算法题按常见题型重述，UI 和雷达设计部分缺失的接口、规模和领域细节均需先澄清。

### 子题 A：每日温度

给定按天排列的整数温度数组 `temperatures`，返回等长数组 `answer`。`answer[i]` 表示第 i 天之后首次出现严格更高温度需要等待的天数；若以后没有更高温度，则为 0。输入非空，不修改输入。

示例：`[73,74,75,71,69,72,76,73]` 返回 `[1,1,4,2,1,1,0,0]`。相同温度不算更高，例如 `[70,70,71]` 返回 `[2,1,0]`。

### 子题 B：生命游戏

给定由 0（死亡）和 1（存活）组成的非空矩形网格，计算并原地更新一轮。每个格子有最多八个相邻格子，网格外视为死亡；所有格子按更新前的状态同时决定下一状态。活格子若有 2 或 3 个活邻居则存活，否则死亡；死格子恰有 3 个活邻居则变活。

示例：`[[0,1,0],[0,0,1],[1,1,1],[0,0,0]]` 更新为 `[[0,0,0],[1,0,1],[0,1,1],[0,1,0]]`。提交更新函数和至少一个可直接运行的测试。

### 子题 C：可折叠文件夹界面

在给定前端脚手架中呈现树状文件/文件夹，点击文件夹可独立展开或折叠其后代；文件作为叶子展示。手册小练习约定节点包含唯一 ID、名称、类型，文件夹另含 children。展开状态由节点 ID 保持；折叠父目录后再次展开，应保留子目录原有展开状态。无需连接真实文件系统。示例：展开根目录和其中的 docs，再折叠/展开根目录，docs 仍保持展开。此节点 schema 和状态规则为手册补充。

### 子题 D：雷达相关设计

公开复盘只确认与雷达系统有关，具体设计层级和数据字段不确定。练习时可选择并声明“接收传感器目标观测并向操作员提供目标态势”这一重构场景：说明观测输入、目标查询/订阅输出、乱序及丢失数据、时间语义、更新延迟和故障行为；先列明假设，再交付需求、接口、数据流及验收指标。不要把此场景扩写视为真实面试官要求。

## 解题思路与参考答案

Anduril 公开能对上的题主要是这几道：Daily Temperatures 要写三种解法，Senior 轮出过 Game of Life 和修坏代码，前端做一个可展开折叠的文件夹，设计是很开放的雷达数据处理。行为面会一直追为什么是 Anduril、为什么做国防，这个要提前准备好自己的理由。

先说来源。Reddit 上一份 Anduril 面经，题目是能对上的。开场是自我介绍、为什么 Anduril 和简历。电面是 LeetCode 739 Daily Temperatures，要了三种写法：暴力、单调栈，以及输出数组之外 O(1) 额外空间的 DP。另一轮电话是连通图相关的 medium，大约 50 分钟编码。现场前端是做一个能展开折叠的文件夹系统，界面已经有了。设计题是雷达收到多路传感器数据，处理后能导出给用户，作者自己也不确定他们要哪一层。

2025 年 5 月 1 日 Jointaro 上一位美国 Senior SWE，第一轮是线上修坏代码。完整 loop 是系统设计、两轮编码和行为面，可以拆成两天，都是远程。作者写自己「过了」loop，团队却让招聘去别的组找位置，后面又加了现场编码和经理电话，最后没有 offer。这则里点名的题是 Game of Life，LeetCode 289。

2026 年 Exponent 上一则校招没有 OA。招聘电话之后是 60 分钟工程师电话，HackerRank 题故意写得含糊。终面三轮各 60 分钟，题目会往外加需求。高级面试官按简历每一行追，反复问为什么是 Anduril、为什么是国防。作者自认电话面很差，第二天仍进了下一轮，最后没有 offer。

Daily Temperatures 是对每个下标找右边第一个更暖的一天，输出要等几天。暴力就是对每个 i 往右扫。单调栈里存还没找到更暖日的下标，从栈顶到栈底温度递增，新的一天比栈顶暖，就弹出并写下距离。他们要的第三种「输出之外 O(1)」是从右往左填答案：如果 `j = i+1` 更暖，答案是 1；否则顺着 `answer[j]` 跳到下一个更暖的候选，跳的时候不用额外的栈。最坏情况下跳跃次数摊还是 O(n)，到不了 O(n^2)。

Game of Life 要原地做的话，用数字的第二位存下一状态，第一位留给邻居读，八个方向都数完再右移一位。板子很小就先复制一份，Senior 轮要是追空间，再写原地的版本。

文件夹就是一棵树，节点有名字、孩子和是否展开。界面已经给了，就对着它的回调写，别重做 UI。追问一般是重名、移动和很深的路径。

雷达题我会先问传感器的记录长什么样、要不要按时间对齐、导出是快照还是流。对象模型是每种传感器一个解析器，上面一个统一的 track。他们要是想听分布式系统，再谈缓冲和迟到数据。Reddit 作者自己都不确定考查点，所以两种各准备一句，看面试官往哪边接。

## 追问

**「为什么 Anduril」真的要准备吗？**
要。校招那则里面试官反复追这个问题，空话会被按简历打回来，得准备一句你自己的理由。

**修坏代码怎么准备？**
在一个小仓库里练从失败的测试走到一行 diff。Senior 的第一轮就是这个，题面没有公开。Anduril 的编码题也会中途加约束，先把当前约束的测试跑绿。
