---
id: drustz-8297ceb7032dba346c
section: anthropic
order: 25
level: A
title: OA In Memory Database
quick: locally-saved-topic-editorial · OA In Memory Database
companies:
  - anthropic
tags:
  - DrustZ
  - locally-saved-topic-editorial
  - Anthropic · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/company/anthropic/oa-in-memory-database
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## In-memory Database (Online Assessment)

## Problem Overview

You need to build a simple in-memory database. This challenge has **4 levels**. You must solve the current level to unlock the next one.

- **Level 1**: Basic tools to add, update, and get data.
- **Level 2**: Search and filter data.
- **Level 3**: Make data expire automatically (TTL).
- **Level 4**: Look up old data from the past.
You will keep all data from previous levels as you move forward.

## Data Format

**Input**: You will get a list of commands (an array of strings).

**Output**: Return an array of strings with the results for every command.

**Note**: Commands are listed in order of time (strictly increasing timestamps).

## Level 1: Core Features

### Goal

The database stores **records**. Here is how they work:

- **Key**: A unique ID string to find the record.
- **Fields**: Variables inside the record. A field is a string name and an integer value.
Every command has a **timestamp** (in milliseconds). Timestamps are always unique and always increase.

### Commands

#### SET

```text
SET <timestamp> <key> <field> <value>
```



- Add a field-value pair to the record.
- If the field exists, update the `value`.
- If the record does not exist, create it.
- Returns `""`.

#### COMPARE_AND_SET

```text
COMPARE_AND_SET <timestamp> <key> <field> <expectedValue> <newValue>
```



- Update the `field` to `newValue` **only if** the current value is `expectedValue`.
- If the value does not match (or the field is missing), do nothing.
- Returns `"true"` if updated, `"false"` if not.

#### COMPARE_AND_DELETE

```text
COMPARE_AND_DELETE <timestamp> <key> <field> <expectedValue>
```



- Delete the `field` **only if** the current value is `expectedValue`.
- If the value does not match, do nothing.
- Returns `"true"` if deleted, `"false"` if not.

#### GET

```text
GET <timestamp> <key> <field>
```



- Get the value of a `field`.
- If the record or field is missing, return `""`.

### Example

**Queries:**

```javascript
[
  ["SET", "0", "A", "B", "4"],
  ["SET", "1", "A", "C", "6"],
  ["COMPARE_AND_SET", "2", "A", "B", "4", "9"],
  ["COMPARE_AND_SET", "3", "A", "C", "4", "9"],
  ["COMPARE_AND_DELETE", "4", "A", "C", "6"],
  ["GET", "5", "A", "C"],
  ["GET", "6", "A", "B"],
];
```



**Walkthrough:**

- **SET**: Add B=4 to record A. -> `""`
- **SET**: Add C=6 to record A. -> `""`
- **COMPARE_AND_SET**: Value of B is 4. Match! Update to 9. -> `"true"`
- **COMPARE_AND_SET**: Value of C is 6. Expected 4. No match. -> `"false"`
- **COMPARE_AND_DELETE**: Value of C is 6. Match! Delete C. -> `"true"`
- **GET**: Field C is gone. -> `""`
- **GET**: Value of B is 9. -> `"9"`
**Output:** `["", "", "true", "false", "true", "", "9"]`

### Test Case

**Input:**

```javascript
[
  ["SET", "160000000", "a", "a", "1"],
  ["SET", "160000001", "a", "A", "2"],
  ["GET", "160000002", "a", "a"],
  ["COMPARE_AND_DELETE", "160000003", "a", "a", "0"],
  ["GET", "160000004", "a", "a"],
  ["COMPARE_AND_DELETE", "160000005", "a", "a", "1"],
  ["GET", "160000006", "a", "a"],
  ["GET", "160000007", "a", "A"],
  ["COMPARE_AND_DELETE", "160000008", "a", "A", "2"],
  ["SET", "160000009", "a", "A", "7"],
  ["SET", "160000010", "a", "A", "9"],
  ["GET", "160000011", "a", "a"],
  ["GET", "160000012", "a", "A"],
];
```



**Expected Output:**

```javascript
["", "", "1", "false", "1", "true", "", "2", "true", "", "", "", "9"];
```



## Level 2: Filtering Data

### Goal

Now you need to search inside records. This level adds commands to list fields.

### New Commands

#### SCAN

```text
SCAN <timestamp> <key>
```



- Returns a single string listing all fields in the record.
- Format: `"<field_1>(<value_1>), <field_2>(<value_2>), ..."`
- Fields must be sorted **lexicographically** (alphabetical order).
- If the record is empty or missing, return `""`.

#### SCAN_BY_PREFIX

```text
SCAN_BY_PREFIX <timestamp> <key> <prefix>
```



- Returns a string listing fields that start with `prefix`.
- Format: Same as SCAN, sorted **lexicographically**.
- If no fields match, return `""`.

### Example

**Queries:**

```javascript
[
  ["SET", "1", "A", "BC", "1"],
  ["SET", "2", "A", "BD", "2"],
  ["SET", "3", "A", "C", "3"],
  ["SCAN_BY_PREFIX", "4", "A", "B"],
  ["SCAN", "5", "A"],
  ["SCAN_BY_PREFIX", "6", "B", "B"],
];
```



**Walkthrough:**

- **SET** three fields: BC=1, BD=2, C=3.
- **SCAN_BY_PREFIX** "B": Finds BC and BD. -> `"BC(1), BD(2)"`
- **SCAN**: Finds all. -> `"BC(1), BD(2), C(3)"`
- **SCAN_BY_PREFIX**: Record B does not exist. -> `""`
**Output:** `["", "", "", "BC(1), BD(2)", "BC(1), BD(2), C(3)", ""]`

## Level 3: Automatic Expiration (TTL)

### Goal

Add **Time-To-Live (TTL)** support. This means data can expire and delete itself automatically.

**How it works:**

- If you set a value at `timestamp` with a `ttl`, the data is alive from `timestamp` up to `timestamp + ttl`.
- At exactly `timestamp + ttl`, the data is dead. You cannot access it anymore.
- If you update the value, you update the TTL too.

### New Command

#### SET_WITH_TTL

```text
SET_WITH_TTL <timestamp> <key> <field> <value> <ttl>
```



- Add or update a field with a timer.
- The field works normally until time `timestamp + ttl`.
- Returns `""`.

### Changes to Old Commands

All previous commands must now check for expiration:

- **GET**: Return `""` if the field has expired.
- **SCAN**: Do not show expired fields.
- **COMPARE**: Cannot update or delete expired fields.

### Example 1

**Queries:**

```javascript
[
  ["SET_WITH_TTL", "1", "A", "BC", "1", "9"],
  ["SET_WITH_TTL", "5", "A", "BC", "2", "10"],
  ["SET", "6", "A", "BD", "3"],
  ["SCAN_BY_PREFIX", "14", "A", "B"],
  ["SCAN_BY_PREFIX", "15", "A", "B"],
];
```



**Walkthrough:**

- **SET_WITH_TTL**: BC=1. Expires at 1+9 = 10.
- **SET_WITH_TTL**: Update BC=2. Expires at 5+10 = 15.
- **SET**: BD=3. No TTL (lives forever).
- **SCAN (Time 14)**: BC expires at 15, so it is still alive. -> `"BC(2), BD(3)"`
- **SCAN (Time 15)**: BC expired exactly at 15. Only BD remains. -> `"BD(3)"`
**Output:** `["", "", "", "BC(2), BD(3)", "BD(3)"]`

### Example 2

**Queries:**

```javascript
[
  ["SET", "1", "A", "B", "1"],
  ["SET_WITH_TTL", "2", "X", "Y", "5", "15"],
  ["GET", "3", "X", "Y"],
  ["SET_WITH_TTL", "4", "A", "D", "2", "10"],
  ["SCAN", "13", "A"],
  ["SCAN", "14", "A"],
  ["SCAN", "16", "X"],
  ["SCAN", "17", "X"],
  ["COMPARE_AND_DELETE", "20", "X", "Y", "5"],
];
```



**Walkthrough:**

- **SET**: B=1 (forever).
- **SET_WITH_TTL**: Y=5 (expires at 17).
- **GET**: Y is alive. -> `"5"`
- **SET_WITH_TTL**: D=2 (expires at 14).
- **SCAN (Time 13)**: B and D are alive. -> `"B(1), D(2)"`
- **SCAN (Time 14)**: D expired at 14. -> `"B(1)"`
- **SCAN (Time 16)**: Y is alive (expires 17). -> `"Y(5)"`
- **SCAN (Time 17)**: Y expired at 17. -> `""`
- **COMPARE_AND_DELETE**: Y is already expired/gone. -> `"false"`
**Output:** `["", "", "5", "", "B(1), D(2)", "B(1)", "Y(5)", "", "false"]`

## Level 4: Historical Data

### Goal

You need to look at the past. This level lets you see what value a field had at a specific time in history.

### New Command

#### GET_WHEN

```text
GET_WHEN <timestamp> <key> <field> <at_timestamp>
```



- Return the value the field had at time `at_timestamp`.
- **Note**: The field might be deleted *now*, but if it existed *then*, you must return it.
- You are guaranteed that `at_timestamp` ≤ current `timestamp`.
- If `at_timestamp` is 0, treat it like a normal GET for the current time.
- If nothing existed at that specific past time, return `""`.

### Example

**Queries:**

```javascript
[
  ["SET_WITH_TTL", "1", "A", "B", "10", "5"],
  ["GET", "2", "A", "B"],
  ["SET", "3", "A", "B", "20"],
  ["GET_WHEN", "10", "A", "B", "2"],
  ["GET_WHEN", "10", "A", "B", "7"],
  ["GET", "10", "A", "B"],
];
```



**Walkthrough:**

- **SET_WITH_TTL**: B=10. Expires at 6.
- **GET**: Time 2. B is alive. -> `"10"`
- **SET**: Update B=20 (forever). This overwrites the old value.
- **GET_WHEN (Time 10, asking about Time 2)**: At Time 2, B was 10. -> `"10"`
- **GET_WHEN (Time 10, asking about Time 7)**:

The first value (10) expired at 6.
- The new value (20) was set at 3.
- So at Time 7, the value was 20. -> `"20"`
- **GET**: Current value is 20. -> `"20"`
**Output:** `["", "10", "", "10", "20", "20"]`

### Important Logic

- **History**: You must save old data. Even if a record is deleted now, you might need to query it later using `GET_WHEN`.
- **Merges**: If records are merged or changed, keep the history of the previous states.
- **TTL**: When checking past data, check if the TTL was valid **at that specific past moment**.

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100014*)

---


## 未能解锁的外链帖（请自行打开查看）

- [Bootloader](https://www.1point3acres.com/interview/thread/7100492)

---

### 用户本地练习实现（仅通过 Python 语法检查，未验证算法正确性）

- practice/anthropic/in_memory_db.py

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/oa-in-memory-database)

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
