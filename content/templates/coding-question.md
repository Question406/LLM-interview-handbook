---
id: replace-with-stable-coding-id
section: coding
order: 999
level: A
title: 替换为具体编程任务
quick: 简述题目要完成的任务；正文题面必须可以独立阅读。
tags:
  - Coding
realInterview: false
status: draft
format: markdown
updatedAt: 2026-10-25
sources:
  - title: 原题或接口定义来源
    url: https://example.com
    type: primary
---

## 题目描述

在这里完整描述给定什么、要计算或修改什么，以及任务完成的条件。必须能不看题解和测试就理解，不要只复述标题。如果接口和规则是手册补充的，应明确标注为练习约定。

### 输入与接口

列出函数或类的方法签名，并解释每个参数的类型、数据形状、单位与含义。多轮操作题说明初始状态与每种操作规则。

解释一行数据对应什么对象。训练题必须区分 feature、label、preference probability 与 sample weight，不能只列变量名和 shape。预处理只用哪些数据拟合、哪些输入需要 gradient，也在这里说明。

### 输出与约束

明确返回内容、返回顺序、是否允许多解以及是否原地修改。给出有效输入范围、平票规则、掩码含义或随机性约定。默认输入合法，不强加异常参数校验。

复杂返回值按字段说明类型、shape、单位与指标定义。训练题列明模型、初始化、optimizer、loss / reduction、update 次数和 validation protocol；不要用“标准训练流程”省略交付要求。扩展阅读不属于默认必做部分。

### 示例

给一组具体可手算的输入与输出；输出应与将要提供的参考实现和默认测试一致。

```text
输入：替换为实际输入
输出：替换为明确的预期结果
```

## 解题思路与参考答案

题面结束后再解释实现方法、正确性与复杂度。然后补全参考实现和“简单测试怎么写”小节。
