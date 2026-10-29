---
id: p3a-apple-json-clean-code
section: tech-screen
order: 82
level: A
title: 一亩三分地 Apple AIML Infra：从 JSON 字符串清洗文档记录并汇总拒收原因
quick: >-
  先解析 JSON，再按明确顺序校验字段、应用阈值和按 ID
  保留最佳记录。要区分数据无效、质量不足与重复三种计数，避免一条记录被多个拒收原因重复统计，也要说明布尔值不能当质量数字。
companies:
  - apple
tags:
  - 一亩三分地继续检索
  - Apple
  - AFM 专项 2026-10
  - 一亩三分地
  - 完整编程练习
  - JSON
realInterview: true
status: published
format: markdown
collapseAnswer: true
updatedAt: 2026-10-26T00:00:00.000Z
sources:
  - title: 苹果AIML infra engr全套（只披露 JSON 清洗处理方向）
    url: 'https://www.1point3acres.com/bbs/thread-1149108-1-1.html'
    type: interview
  - title: Python json — JSON encoder and decoder
    url: 'https://docs.python.org/3/library/json.html'
    type: primary
---

## 题目描述

**source attribution 与适用范围：**2026-10-26 经 Chrome 核对，2025-10-07 14:14:15 的候选人原帖说明 Apple AIML Infra 电面给一大段 JSON 字符串做清洗与处理，共有三问，但没有披露 schema、三问内容或代码。下述任务是为数据岗补充的练习约定。

### 输入与接口

实现 `clean_json_records(raw, min_quality=0.5)`。raw 是合法 JSON 字符串，根为数组，数组元素均为对象；元素可以缺字段或字段类型错误。候选字段包括 `doc_id`、`text`、`quality`，其他字段忽略。min_quality 为 `[0,1]` 内数值。只处理一条字符串，不要求流式解析。

### 输出与约束

返回 `(cleaned, counts)`，cleaned 为规范化记录列表，元素只含 doc_id、text、quality；前两项为去掉两端空白后的字符串，quality 为 float。counts 固定包含 invalid、low_quality、duplicate 三个整数计数，按以下顺序处理每条输入：

1. doc_id 或 text 不是非空白字符串，或 quality 不是 `[0,1]` 内的 int/float，记 invalid；布尔值不算数值。跳过该记录。
2. quality 小于阈值，记 low_quality 并跳过。
3. 同一规范化 doc_id 首次合格时保留；以后每个合格重复记录都记 duplicate，若质量严格更高则替换内容，平分保留先出现的记录。

最终结果按每个 doc_id 首次合格出现的顺序排列，替换内容不改变位置。计数互斥，一条记录最多进入一个计数类；被替换的旧记录不额外增加计数。不得用 eval 解析。

### 示例

```text
raw='[{"doc_id":" a ","text":" old ","quality":0.6},
      {"doc_id":"a","text":"new","quality":0.9},
      {"doc_id":"b","text":"ok","quality":0.2},
      {"doc_id":"c","text":"","quality":0.8}]'
cleaned=[{'doc_id':'a','text':'new','quality':0.9}]
counts={'invalid':1,'low_quality':1,'duplicate':1}
```

## 解题思路与参考答案

字段清洗和过滤的顺序是接口语义，不应由 if 条件顺手写成偶然结果。Python 中 bool 是 int 的子类，所以需要明确排除。字典保留插入顺序，可以在替换值的同时保留首次合格位置。

```python
import json


def clean_json_records(raw, min_quality=0.5):
    records = json.loads(raw)
    kept = {}
    counts = {'invalid': 0, 'low_quality': 0, 'duplicate': 0}
    for record in records:
        doc_id, text, quality = (
            record.get('doc_id'),
            record.get('text'),
            record.get('quality'),
        )
        valid = (
            isinstance(doc_id, str)
            and bool(doc_id.strip())
            and isinstance(text, str)
            and bool(text.strip())
            and isinstance(quality, (int, float))
            and not isinstance(quality, bool)
            and 0 <= quality <= 1
        )
        if not valid:
            counts['invalid'] += 1
            continue
        if quality < min_quality:
            counts['low_quality'] += 1
            continue
        doc_id, text, quality = doc_id.strip(), text.strip(), float(quality)
        candidate = {'doc_id': doc_id, 'text': text, 'quality': quality}
        if doc_id in kept:
            counts['duplicate'] += 1
            if quality > kept[doc_id]['quality']:
                kept[doc_id] = candidate
        else:
            kept[doc_id] = candidate
    return list(kept.values()), counts
```

总时间为输入字符串长度与字段处理量的线性量级，平均哈希操作为常数时间。json.loads 会先在内存中建立完整对象；这是题目的单字符串约定，不能把它称为十亿文档的流式实现。

## 简单测试怎么写

将实现与测试放入 `solution.py`，运行 `python3 solution.py`，只需标准库。先核对题面例子，再测试分数 tie、替换后的顺序、threshold endpoints、缺字段与布尔值。

```python
raw = json.dumps(
    [
        {'doc_id': ' a ', 'text': ' old ', 'quality': 0.6},
        {'doc_id': 'a', 'text': 'new', 'quality': 0.9},
        {'doc_id': 'b', 'text': 'ok', 'quality': 0.2},
        {'doc_id': 'c', 'text': '', 'quality': 0.8},
    ]
)
cleaned, counts = clean_json_records(raw)
assert cleaned == [{'doc_id': 'a', 'text': 'new', 'quality': 0.9}]
assert counts == {'invalid': 1, 'low_quality': 1, 'duplicate': 1}
more = json.dumps(
    [
        {'doc_id': 'a', 'text': 'first', 'quality': 0.5},
        {'doc_id': 'b', 'text': 'second', 'quality': 0.7},
        {'doc_id': 'a', 'text': 'tie', 'quality': 0.5},
        {'doc_id': 'a', 'text': 'best', 'quality': 0.9},
        {'doc_id': 'z', 'text': 'bad', 'quality': True},
        {'doc_id': 'y', 'quality': 0.9},
    ]
)
result, tally = clean_json_records(more)
assert [r['doc_id'] for r in result] == ['a', 'b']
assert result[0]['text'] == 'best'
assert tally == {'invalid': 2, 'low_quality': 0, 'duplicate': 2}
tie, _ = clean_json_records(
    json.dumps(
        [
            {'doc_id': 'x', 'text': 'first', 'quality': 1},
            {'doc_id': 'x', 'text': 'later', 'quality': 1},
        ]
    )
)
assert tie[0]['text'] == 'first' and isinstance(tie[0]['quality'], float)
assert clean_json_records('[]') == (
    [],
    {'invalid': 0, 'low_quality': 0, 'duplicate': 0},
)
```

## 面试追问

**解析失败也静默跳过吗？** 本题保证整段 JSON 合法。生产应区分语法错误和记录级质量错误，明确是拒绝整段、隔离文件还是逐行处理；不要捕获所有异常并返回看似成功的空结果。

**记录特别大怎么办？** 使用 bounded input size 或适合流式处理的格式与解析器，按分片输出。按 ID 的全局择优还需要外部分区或状态存储，不是改成 generator 就消除了状态成本。

**质量最高就应保留吗？** 本题按单一分数择优是练习约定。真实数据还需考虑来源、版本、分数 calibration 和分布覆盖，不能用较高质量分掩盖不同授权条件。
