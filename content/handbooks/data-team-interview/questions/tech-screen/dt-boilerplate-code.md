---
id: dt-boilerplate-code
section: tech-screen
order: 14
level: A
title: CoderPad：HTML 去导航条，文本密度怎么写，什么时候才上 LLM 抽取？
quick: "先用块级的文本密度和链接密度把导航、页脚这类模板块滤掉，这一步最便宜。按域统计抽取失败率，静态抽取失败的域再开 headless 渲染，仍失败才上 LLM 抽取。每页都调大模型成本高，抽取带来的变化也难追踪；用了 LLM 要记模型版本，抽出的正文照样过质量检查和评测污染检查。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Extraction
  - HTML
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Boilerplate Detection using Shallow Text Features (Kohlschütter et al.)
    url: https://www.l3s.de/~kohlschuetter/publications/wsdm187-kohlschuetter.pdf
    type: primary
  - title: Trafilatura
    url: https://aclanthology.org/2021.acl-demo.15/
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

给定已经从网页中提取出的块列表，剔除本题定义的导航、页脚和短按钮等样板内容，将剩余块拼成正文。不需要解析 HTML、启动浏览器或调用语言模型。

### 输入与接口

- 块类型 `Block(tag, text, n_links, n_nodes)` 分别保存标签名、文本、链接节点数、总节点数。
- `density(block)` 返回词数、链接密度、逗号数。词数按空白分词且至少为 1；链接密度分母至少为 1；中英文逗号均计数。
- 实现 `extract(blocks, min_tokens=40, max_link_density=0.5)`。

### 输出与约束

成功返回 `(正文字符串, "ok")`；保留下来的正文词数少于 `min_tokens` 时返回 `(None, "too_short_or_nav")`。正文块按原顺序保留，块内只去除首尾空白，块间用两个换行连接。

排除标签 `nav/footer/header/aside`；排除词数小于 8 且链接密度大于阈值的块；排除词数小于 5 且没有逗号的块。比较边界均按这里给出的严格小于或大于执行。输入字段保证合法。

### 示例

```text
blocks=[Block("div","Home About",2,2), Block("p","A useful paragraph, with enough words.",0,1)]
extract(blocks,min_tokens=5)
-> ("A useful paragraph, with enough words.","ok")
extract([Block("span","Read more",0,1)],min_tokens=5) -> (None,"too_short_or_nav")
```

## 解题思路与参考答案

我会先写一个只看浅层特征的抽取器：链接多、标点少、文本又短的块，大概率是导航条、按钮或页脚，直接扔掉。规则抽不出正文的域，再升级到 headless 渲染，还不行才考虑 LLM 抽取。

抽取在预训练管线的最前面，也是脏数据的第一来源。比如一篇新闻页，顶上是「Home About Contact」，底下是「Copyright 2026, all rights reserved」，抽取器要是把这两段也当正文，cookie 墙和评论框就一起混进了训练文本。Kohlschütter 那篇已经说明浅层特征就能识别样板，Trafilatura 把这类规则做成了能直接跑的抽取器。CoderPad 上给一个打平的块列表就够了，不会让你解析完整浏览器。

## 链接密度和文本密度

每个块我算三个数：词数、链接密度（链接节点数除以节点数）、逗号数。`nav`、`footer`、`header`、`aside` 标签直接跳过；短且链接多的块是导航条或标签云；极短又没有标点的块是按钮或面包屑。剩下的拼起来，总长度还不到下限就返回失败原因，后面好按原因统计。

```python
from dataclasses import dataclass

BOILERPLATE_TAGS = {"nav", "footer", "header", "aside"}


@dataclass
class Block:
    tag: str
    text: str
    n_links: int
    n_nodes: int


def density(block):
    """返回 (词数, 链接密度, 逗号数)。链接密度 = 链接节点数 / 节点数。"""
    n_words = max(len(block.text.split()), 1)
    link_density = block.n_links / max(block.n_nodes, 1)
    n_commas = block.text.count(",") + block.text.count("，")
    return n_words, link_density, n_commas


def extract(blocks, min_tokens=40, max_link_density=0.5):
    """保留像正文的块并拼接。返回 (text, "ok") 或 (None, 失败原因)。"""
    kept = []
    for block in blocks:
        if block.tag in BOILERPLATE_TAGS:
            continue
        n_words, link_density, n_commas = density(block)
        # 短且链接多：导航条、标签云
        if n_words < 8 and link_density > max_link_density:
            continue
        # 极短且没有标点：按钮、面包屑
        if n_words < 5 and n_commas == 0:
            continue
        kept.append(block)
    text = "\n\n".join(block.text.strip() for block in kept if block.text.strip())
    if len(text.split()) < min_tokens:
        return None, "too_short_or_nav"
    return text, "ok"
```

测试覆盖正文保留、导航和按钮剥掉、中文逗号、除零这几种情况：

```python
article = Block("p", "This is a long paragraph, with commas, " * 10, n_links=0, n_nodes=1)
nav = Block("div", "Home About Contact", n_links=3, n_nodes=3)
footer = Block("footer", "Copyright 2026, all rights reserved, " * 10, n_links=0, n_nodes=1)
button = Block("span", "Read more", n_links=0, n_nodes=1)

# 正文块保留，导航、footer 标签和短按钮被剥掉
text, reason = extract([nav, article, footer, button])
assert reason == "ok"
assert "Home" not in text
assert "Copyright" not in text
assert "Read more" not in text
assert text == article.text.strip()

# 只有导航时正文太短，返回失败原因而不是空字符串
assert extract([nav, button]) == (None, "too_short_or_nav")

# 中文逗号也算标点：短的中文句子不会被当成按钮
assert density(Block("p", "你好，世界", n_links=0, n_nodes=1)) == (1, 0.0, 1)

# n_nodes 为 0 时不除零
assert density(Block("p", "", n_links=2, n_nodes=0)) == (1, 2.0, 0)
```

返回 `None` 的页面先隔离检查，别当作短文档混进训练集，PDF 扫描件、纯图片页也走同一个失败原因。这套规则有一个已知误伤：注释、代码块和表格的文本密度低，会被当成样板扔掉，所以文档站和 GitHub README 要按域关掉链接密度门，或者对 `tag in {pre, code, table}` 直接放行。复杂度是块数的线性一遍，成本几乎可以忽略。

## 什么时候升级到 headless 和 LLM

默认用静态 HTML 加密度规则，成本最低。同时按域记录失败率，某个域有 40% 的页面抽空，就对这个域开 headless 渲染；AFM 2025 公开写了先 headless 渲染、再用 LLM 抽主内容，因为现代网站大量内容由 JS 生成。headless 之后仍然抽空，或者主内容藏在 JSON 里，才上 LLM 抽取。抽取模型的版本要写进 lineage，抽出来的正文还要过质量门和评测指纹，这部分在 `dt-pipeline-talk` 里讲。

一开始就对每页调 GPT-4o 抽取，会同时带来高成本、教师偏差和评测污染风险，版本追踪的负担也重。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert reason == "ok"` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 追问

**评论区留不留？**
预训练通常扔掉。SFT 要用的论坛答疑是另一个桶，别拿网页样板门去筛它。

**多语言的逗号怎么处理？**
特征要按语言定义：中文用 `，`，日语用 `、`。这和 `dt-quality-filter-code` 是同一个教训。

**抽取模型会不会泄漏评测？**
会，所以它的输出照样要过 `dt-ngram-contam-code`。

**这题和 Panel 上的网页抽取题有什么区别？**
`dt-web-extract` 是 Panel 版，讲整体取舍；这里要求的是把密度函数现场写出来，跑通测试。

相关：`dt-web-extract`、`dt-pipeline-talk`、`dt-quality-filter-code`、`dt-ngram-contam-code`
