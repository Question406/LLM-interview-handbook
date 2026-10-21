---
id: dt-boilerplate-code
section: tech-screen
order: 14
level: A
title: CoderPad：HTML 去导航条，文本密度怎么写，什么时候才上 LLM 抽取？
quick: "先用块级的文本密度和链接密度把导航、页脚这类模板块过滤掉，这一步最便宜。按域统计抽取失败率，静态抽取失败的域再开 headless 渲染，仍失败才上 LLM 抽取。默认每页调用大模型成本高，也更难追踪抽取带来的变化；用了 LLM 也要记录模型版本，抽出的正文照样过质量检查和评测污染检查。"
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

这题要写的是一个便宜的正文抽取器：给一串已经打平的 HTML 块，判断哪些是正文、哪些是导航条、按钮、页脚这类模板。思路是看浅层特征：链接多、标点少、文本又短的块，大概率是模板。规则抽不出正文的域，再升级到 headless 渲染，仍失败才考虑 LLM 抽取。

抽取放在预训练管线的最前面，也是脏数据的第一来源：导航被当成正文，cookie 墙和评论框混进训练文本。Kohlschütter 证明了浅层特征就能识别样板，Trafilatura 把这类规则做成了能直接跑的抽取器。CoderPad 上给你一个打平的块列表就够了，不会让你解析完整浏览器。

## 浅层特征：链接密度和文本密度

每个块算三个数：词数、链接密度（链接节点数除以节点数）、逗号数。`nav`、`footer`、`header`、`aside` 标签直接跳过；短且链接多的块是导航条或标签云；极短又没有标点的块是按钮或面包屑。剩下的块拼起来，如果总长度还不到下限，就返回失败原因，方便后面按原因统计。

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

返回 `None` 的页面要先隔离检查，不能当作短文档混进训练集。PDF 扫描件、纯图片页也走同一个失败原因。

这套规则有一个已知误伤：注释、代码块和表格的文本密度低，会被当成样板扔掉。文档站和 GitHub README 要按域关掉链接密度门，或者对 `tag in {pre, code, table}` 直接放行。

## 什么时候升级到 headless 和 LLM

1. 默认用静态 HTML 加密度规则，成本最低。
2. 按域记录失败率。某个域有 40% 的页面抽空，再对这个域开 headless 渲染。AFM 2025 公开写了先 headless 渲染、再用 LLM 抽主内容，因为现代网站大量内容由 JS 生成。
3. headless 之后仍然抽空，或者主内容藏在 JSON 里，才上 LLM 抽取。抽取模型的版本要写进 lineage，抽出来的正文仍要过质量门和评测指纹，见 `dt-pipeline-talk`。

一开始就对每页调用 GPT-4o 抽取，会同时带来高成本、教师偏差和评测污染风险，版本追踪的负担也重。`dt-web-extract` 是这题的 Panel 版，这里要求的是能把密度函数现场写出来。

## 追问

- **评论区留不留？** 预训练通常扔掉。监督微调（SFT）要用的论坛答疑是另一个桶，不要拿网页样板门去筛。
- **多语言的逗号怎么处理？** 中文用 `，`，日语用 `、`，特征要按语言定义，这和 `dt-quality-filter-code` 是同一个教训。
- **抽取模型会不会泄漏评测？** 会，所以它的输出仍要过 `dt-ngram-contam-code`。
