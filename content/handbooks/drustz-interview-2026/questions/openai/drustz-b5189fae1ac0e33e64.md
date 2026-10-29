---
id: drustz-b5189fae1ac0e33e64
section: openai
order: 112
level: A
title: IP Address Iterator (Forward / Backward / CIDR)
quick: >-
  original-structured-preparation-guide · IP Address Iterator (Forward /
  Backward / CIDR)
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
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
      https://www.1point3acres.com/interview/problems/b942bff0-248d-481e-82a1-4c2d4ce905e3
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# IPv4 Iterator：正向、反向与 CIDR 边界

## 证据边界

公开标题与本地直接面经都明确列出 Forward、Backward、CIDR 三部分；下面按同题族公开例子重述。是否排除 network/broadcast address 等业务规则未被标题说明，本指南按“CIDR 内全部地址均可迭代”处理。

## 题面、接口与示例

```text
IPV4Iterator(ip_or_cidr: str, reverse: bool = False)
```



无 CIDR 时，从给定地址正向到 `255.255.255.255`，或反向到 `0.0.0.0`。`IPV4Iterator("192.168.1.250/29")` 返回 `.250` 到 `.255`；`IPV4Iterator("192.168.1.5/29", reverse=True)` 返回 `.5` 到 `.0`。起点在网段中间时，不先跳回网络边界。

## 解法与关键数据

把四个 octet 转成 32 位整数 `x=(a<<24)|(b<<16)|(c<<8)|d`；输出时反向位移取四段。前缀 p 的 host bits 为 `32-p`，mask 为高 p 位 1，`lo=x&mask`，`hi=lo+(1<<(32-p))-1`。current 初始化为输入 IP；正向 limit=hi、步长 +1，反向 limit=lo、步长 -1。next 先判断是否越界，再格式化 current 并移动，因而上下界都是 inclusive。

bitmask的正确性是：与 mask 后清零全部 host bits，得到包含 x 的唯一网络起点；再加 `2^(32-p)-1` 把 host bits 全置一，得到终点。current 每次只向指定方向移动一，所以既不会漏掉块内地址，也不会跨出边界。若产品语义要排除 network/broadcast，只应调整初始与终止边界，不能改 CIDR 计算本身。

## 复杂度与边界

每次 next 时间、游标空间均 `O(1)`；输出 K 个地址总时间 `O(K)`，若收集成 list 才需要 `O(K)` 空间。严格校验恰好四段、每段 0..255、无空段、prefix 0..32。测试 `/32` 单地址、`/31` 两地址、`/0`、起点在块中间、跨 octet 进退位、最小/最大 IP、反向下溢、迭代结束后重复 next，以及是否允许前导零。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/b942bff0-248d-481e-82a1-4c2d4ce905e3)

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
