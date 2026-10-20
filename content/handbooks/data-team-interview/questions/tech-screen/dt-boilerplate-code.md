---
id: dt-boilerplate-code
section: tech-screen
order: 14
level: A
title: CoderPad：HTML 去导航条，文本密度怎么写，什么时候才上 LLM 抽取？
quick: "先利用块级文本密度和链接密度过滤导航等模板内容。静态抽取失败的域再用 headless，仍失败时考虑 LLM 抽取。模型版本、质量检查和评测污染检查都要保留；默认每页调用大模型会增加成本，也更难追踪抽取造成的变化。"
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

先计算块级特征，把链接多、标点少且文本短的内容视作可能的模板。规则抽不出正文的域，再用 headless；仍失败时才考虑 LLM。每页都调用抽取模型，会增加成本和版本追踪的负担，见 `dt-web-extract`。抽取失败是预训练脏数据的第一来源：导航当正文、cookie 墙、评论框。

Kohlschütter 用浅层特征抓样板；Trafilatura 把这类规则做成能跑的抽取器。AFM 2025 写了 headless 渲染再 LLM 抽主内容，因为现代站大量是 JS。CoderPad 给你一棵已经打平的块列表就够，不会让你解析完整浏览器。

## 浅层特征：链接密度和文本密度

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

### 可执行测试

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

返回 `return None` 的内容先隔离检查，不能直接当短文档混进训练集。PDF 扫描件、纯图片页同样走这条失败原因。

## 升级顺序

1. 静态 HTML + 密度。便宜。
2. 按域记失败率。某域 40% 抽空，再对该域开 headless。
3. headless 仍空或主内容在 JSON 里，才上 LLM 抽取。抽取模型版本进 lineage，抽出来的正文仍过质量门和评测指纹，见 `dt-pipeline-talk`。

一开始就对每页调用 GPT-4o 抽取，会同时引入高成本、教师偏差和评测污染风险。`dt-web-extract` 是 Panel 版，这里要能把密度函数写出来。

注释、代码块、表格密度低，会被当样板扔掉。文档站和 GitHub README 要按域关链接密度门，或按 `tag in {pre, code, table}` 放行。

## 追问

- **评论区留不留？** 预训练通常扔。监督微调（SFT） 的论坛答疑是另一个桶，别用网页样板门。
- **多语言逗号？** 中文用 `，`，日语用 `、`。特征要按语言，和 `dt-quality-filter-code` 同一教训。
- **抽取模型会不会泄漏评测？** 会。输出仍要过 `dt-ngram-contam-code`。
