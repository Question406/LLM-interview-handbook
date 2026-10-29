---
id: drustz-59bfd18203cbc8eddf
section: openai
order: 174
level: A
title: Resumable List Iterator with Save and Restore Functionality
quick: >-
  original-structured-preparation-guide · Resumable List Iterator with Save and
  Restore Functionality
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
      https://www.1point3acres.com/interview/problems/9c8fae11-23cc-4f3c-a51a-29ac5840c093
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Resumable List Iterator：保存并恢复“下一个元素”位置

## 证据边界

标题明确是 list iterator 的 save/restore；本地同题族公开页给出 `__iter__`、`__next__`、`get_state`、`set_state`。多维、跨文件和 async 是其他变体，不合并成当前题面的必选项。

## 题面、接口与例子

```python
class ResumableListIterator:
    def __next__(self): ...
    def get_state(self) -> dict: ...
    def set_state(self, state: dict) -> None: ...
```



对 `['a','b','c','d']` 连续取出 `a,b` 后，状态应表示 `index=2`。即使创建同数据的新 iterator，set_state 后下一次也应返回 `c`；恢复同一状态多次，每次都从 `c` 开始。状态必须可 JSON 序列化，不能保存 Python iterator 或文件句柄。

## 解法与不变量

对象只保存原列表与“下一项索引” `index`。`next` 先检查 `index < len(items)`，取值后加一；否则抛 `StopIteration`。state 至少含 schema version、index、数据长度，生产版再含稳定的 `data_id/version`，防止把旧游标应用到另一份等长数据。set_state 先完整校验 `0<=index<=n` 和身份，再一次更新；坏状态不能改变当前游标。

核心不变量是已经返回的前缀恰为 `items[:index]`，剩余序列恰为 `items[index:]`。next 保持这个不变量，get_state 只复制 index，set_state 则重新建立它，所以暂停、跨实例恢复和重复恢复都不会漏项或重复项；主动回到旧状态产生的重读是调用者要求的行为。

## 复杂度与边界测试

next、保存和恢复均为 `O(1)` 时间；游标额外空间 `O(1)`，输入列表本身不计。测试空列表、初始状态、消费最后一项后的状态、结束后恢复、负数/越界 index、缺字段、不同数据版本、重复 get_state 不推进，以及保存后原列表被插入或删除。必须先约定 snapshot 指向“上次返回项”还是“下次待返回项”，本指南采用后者。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/9c8fae11-23cc-4f3c-a51a-29ac5840c093)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
