---
id: xai-nested-json-safe-viewer-core
section: xai
order: 937
level: A
title: "xAI UI 题型扩展：nested JSON viewer 的安全 HTML renderer"
quick: "我会先把显示内容和 HTML 标签分开。标签由代码固定生成，用户提供的 key 和 string 都必须经过 escaping，不能直接拼进标签。"
companies:
  - xai
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开题型扩展"
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：xAI UI 题型扩展：nested JSON viewer 的安全 HTML renderer"
    url: "https://landthelab.com/companies/xai"
    type: secondary
---

## 题目描述

来源：Land the Lab 的 xAI 目录列出 React nested JSON viewer。下面以 Python 实现其 renderer 核心，HTML schema 与 collapse-path API 由手册设定。

### 输入、接口与规则

实现 `render_json(value, collapsed=frozenset()) -> str`。value 是 JSON-compatible Python value：dict 的 keys 为 strings，values 可递归包含 dict/list/string/int/有限 float/bool/None。输入不含 cycle，nesting depth≤100。collapsed 是 path tuples 的 set：dict 用 string key、list 用整数 index，root path 为 ()。

返回 HTML fragment：scalar 为 `<span class="TYPE">TEXT</span>`，TYPE 为 string/number/boolean/null；TEXT 是该值的 JSON literal，经 HTML escaping。Dict/list 按输入顺序递归，用 braces/brackets 和逗号分隔；dict key 包在 class="key" 的 span 中，与 value 用冒号连接。非空 container 的 path 命中 collapsed 时，返回 class="collapsed" 的 span，内容是 `object(N)` 或 `array(N)`；空 container 保留 {} 或 []。非法类型或非有限 float 抛 ValueError，不修改 value。

### 输入输出示例

```text
value={"x":[1,True]}, collapsed={("x",)}
输出 {<span class="key">&quot;x&quot;</span>:<span class="collapsed">array(2)</span>}。
value="<b>" -> <span class="string">&quot;&lt;b&gt;&quot;</span>。
```

## 回答思路

> **Situation / Task：** JSON 内容包含用户字符串；输出必须可安全插入 HTML。  
> **Approach / Why：** 递归 render containers，用 typed path 控制 collapse，所有 text 先 JSON encode 再 HTML escape。  
> **Result / Check：** 检查 key/value 的 script 字符、bool 与 int 区分、collapse 和 NaN。

## 解题思路与参考答案

我会先把显示内容和 HTML 标签分开。标签由代码固定生成，用户提供的 key 和 string 都必须经过 escaping，不能直接拼进标签。

Path 使用 tuple 而不是点号字符串，这样 key 本身含点号也不会歧义。Python 中 bool 是 int 的 subclass，所以类型判断要先检查 bool，才能给 true 正确的 class。这个模块生成 fragment；React 组件的交互、键盘访问与 virtualization 是后续任务。

### 完整参考实现

```python
import json, math, html


def render_json(value, collapsed=frozenset()):
    def span(kind, text):
        return '<span class="' + kind + '">' + html.escape(text, quote=True) + '</span>'

    def render(node, path):
        if isinstance(node, dict):
            if any(not isinstance(k, str) for k in node):
                raise ValueError('non-string key')
            if node and path in collapsed:
                return span('collapsed', f'object({len(node)})')
            return (
                '{'
                + ','.join(
                    span('key', json.dumps(k, ensure_ascii=False))
                    + ':'
                    + render(v, path + (k,))
                    for k, v in node.items()
                )
                + '}'
            )
        if isinstance(node, list):
            if node and path in collapsed:
                return span('collapsed', f'array({len(node)})')
            return (
                '[' + ','.join(render(v, path + (i,)) for i, v in enumerate(node)) + ']'
            )
        if node is None:
            kind = 'null'
        elif isinstance(node, bool):
            kind = 'boolean'
        elif isinstance(node, str):
            kind = 'string'
        elif type(node) in (int, float):
            if isinstance(node, float) and not math.isfinite(node):
                raise ValueError('non-finite number')
            kind = 'number'
        else:
            raise ValueError('non-JSON value')
        return span(kind, json.dumps(node, ensure_ascii=False, allow_nan=False))

    return render(value, ())
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
assert (
    render_json({'x': [1, True]}, {('x',)})
    == '{<span class="key">&quot;x&quot;</span>:<span class="collapsed">array(2)</span>}'
)
assert render_json('<b>') == '<span class="string">&quot;&lt;b&gt;&quot;</span>'
assert render_json(True) == '<span class="boolean">true</span>'
assert render_json(None) == '<span class="null">null</span>'
assert render_json([], {()}) == '[]'
assert render_json({'a': 1}, {()}) == '<span class="collapsed">object(1)</span>'
assert '<script>' not in render_json({'<script>': '<script>'})
for bad in [float('nan'), float('inf'), {1: 'x'}, set()]:
    try:
        render_json(bad)
    except ValueError:
        pass
    else:
        raise AssertionError('non-JSON value accepted')
print('JSON viewer tests passed')
```

## 复杂度与追问

设实际展开的内容与输出长度合计为 L，时间 `O(L)`，递归深度 O(depth)，另外需要保存输出字符串。Collapse 的子树无需遍历。追问超深或超大 JSON，考虑 iterative traversal 与 virtualization。
