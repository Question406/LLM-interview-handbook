---
id: drustz-eb345b99214de7ebff
section: openai
order: 73
level: A
title: Infectious Disease Simulation (Multi-part)
quick: >-
  original-structured-preparation-guide · Infectious Disease Simulation
  (Multi-part)
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
      https://www.1point3acres.com/interview/problems/00989ada-41f1-405a-8ab3-7792a508c41b
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Infectious Disease Simulation：多阶段状态机

> **证据边界**：多份同家族面经一致确认前三阶段是基础扩散、初始免疫单元、感染若干天后转免疫；另有报告出现死亡 follow-up。当前 UUID 没有公开完整正文，邻接是 4 还是 8、死亡条件是否属于本题都未证实，所以这里给可逐阶段扩展的实现，不伪造 P4/P5。

## 分阶段建模

P1 用 `S/X`：多个感染源按天同步向 `directions` 扩散。P2 加 `I`：免疫格永久不变，既不是目标也不传播。P3 将 `X` 保存为 `infected_at`，到 `infected_at + D` 时转 `I`。若题面另给死亡阈值，再把 `DIED` 当永久状态并单独实现 `death_rule`。

例如 `X . I`、`D=2`：第 1 天中间格感染，最右格始终免疫；初始格在规定的到期阶段转免疫。答案可能是“无新感染的天数”或“所有格均感染/免疫的天数”，两者并不等价，要按题面选择停止条件。

## 算法骨架

P1/P2 可用多源分层 BFS；P3 起用每日事件队列。保留 `collect_infections(old_state)`、`collect_expirations(day)`、`commit(events)` 三个函数，使每日更新只读旧状态。相同坐标收到多个感染事件时只应用一次。

```text
for day = 1...:
    infections = collect_from(currently_contagious)
    expirations = scheduled[day]
    commit_in_declared_order(infections, expirations)
```



## 复杂度与边界

状态只前进、不再感染时总时间 `O(RC·d)`、空间 `O(RC)`；若允许再感染，则按模拟天数为 `O(T·RC)`，并应检测周期。测试 `D=1`、全免疫、健康格被免疫墙包围、同日感染与到期冲突、重复事件，以及“稳定”与“所有人感染或免疫”两个停止定义。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/00989ada-41f1-405a-8ab3-7792a508c41b)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
