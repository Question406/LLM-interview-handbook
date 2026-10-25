---
id: dt-pipeline-talk
section: tech-screen
order: 1
level: S
title: CoderPad：边写边讲，一条预训练 / SFT 数据管线怎么画？
quick: "先问清数据类型、这轮要实现哪一步、输出什么格式，再边写边讲每一步筛掉什么、为什么。整条流程是来源、抽取、过滤、去重、配比、评测隔离；现场只实现被要求的那部分，其余口头补齐版本、失败处理和大规模扩展。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Data Pipeline
  - Python
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: The FineWeb Datasets
    url: https://arxiv.org/abs/2406.17557
    type: primary
  - title: DataComp-LM
    url: https://arxiv.org/abs/2406.11794
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

实现一个按领域 token 配额抽取训练文档的小型管线。先排除质量不达标文档，再在每个领域内部抽样；某个领域没有可用文档时需要明确报告，不能用其他领域补齐。

### 输入与接口

- 文档类型 `Doc(doc_id,domain,n_tokens,quality,text)`；`doc_id` 唯一，token 数为正，quality 为非负模型分。
- 实现 `mix_by_quota(docs,quota,alpha=0.5,min_quality=0.4,rng=None)`。quota 是 `领域 -> 目标token数`，rng 默认使用种子 0。

### 输出与约束

返回 `(picked,empty_domains)`，picked 保存抽中的原文档对象；`empty_domains` 按 quota 顺序列出没有可抽取正权重样本的领域。领域内部每条文档的抽样权重与 `n_tokens**alpha * quality` 成正比。

质量低于 `min_quality` 的文档不能被抽中。每个领域无放回抽样，累计 token 首次达到该领域配额即停止，最后一篇允许超额；样本不够时全部取完。不修改原列表，相同输入与 RNG 状态应给出相同结果。

### 示例

```text
docs=[Doc("w","web",100,0.8,"..."),Doc("m","math",500,0.9,"..."),Doc("junk","web",100,0.1,"...")]
quota={"web":50,"math":1000,"code":10}
mix_by_quota(docs,quota) -> ([w,m],["code"])
```

## 解题思路与参考答案

这题考的是边写边讲：实现被问到的那一步，同时说清它在 crawl → extract → filter → dedup → mix → eval-isolation 里的位置、输入是什么、保留和丢弃什么、评测怎么隔离。闷头写 20 分钟，或者只画流程图不写代码，面试官都很难判断你的水平。

开口我会先问三个问题：数据是网页、对话还是多模态；这轮要的是过滤、去重还是配比；输出是文档还是打包后的 token。然后在白板上或 CoderPad 注释里写下六个阶段，说明现在实现哪一个。

六个阶段可以这样一口气讲完。Crawl / ingest 管来源、许可、robots 和 opt-out，登录墙和付费墙后面的内容不爬，robots.txt 里「不要用来训基础模型」的声明要遵守。Extract 把 HTML 转成正文，规则抽不出的域再上 headless 渲染和 LLM 抽主内容，因为现代网站大量内容由 JS 生成，默认每页调一次 LLM 成本太高。Filter 管语言、PII、脏话和质量，阈值要能按域校准，过猛的启发式会扔掉好 token，所以规则留余地，多靠按语言调过的模型分。Dedup 先用精确哈希去掉相同文本，再用 MinHash / LSH 去近重复，最后和评测集做 overlap，实现见 `dt-minhash-code`。Mix 按域配额抽样，配额对应各项能力的预算，温度采样 $p_i \propto n_i^{\alpha}$，$\alpha$ 越小，长尾域被抬得越多。Eval isolation 是训练侧任何「像评测」的文档，在进 mix 之前打上污染标记，污染检测见 `dt-benchmark-gap`。

CoderPad 里多半只让你写过滤和配比，或者去重。其余的口头补齐：这一步的输入输出 schema，失败时文档是丢掉还是进 quarantine，日志里要留下源 URL 和过滤器版本。

## 现场要写的那段：配额采样

边写我会边解释三件事。`quota` 表示目标能力的预算，和源站的文件大小无关。`quality` 已经是上游模型给的分。采样单位是文档、计费单位是 token，所以短模板在条数上会淹没难例，要用 token 加权，或者先打包再抽。

```python
import random
from dataclasses import dataclass


@dataclass
class Doc:
    doc_id: str
    domain: str
    n_tokens: int
    quality: float  # 模型分，已按语言校准
    text: str


def mix_by_quota(docs, quota, alpha=0.5, min_quality=0.4, rng=None):
    """quota: domain -> 目标 token 数。alpha 越小越抬小域。

    域内按 n_tokens**alpha * quality 加权、无放回抽文档，直到达到该域 token 配额
    （最后一篇可能略超）。返回 (抽中的文档, 没有可用文档的域)。
    """
    rng = rng or random.Random(0)
    buckets = {}
    for doc in docs:
        if doc.quality < min_quality:
            continue
        buckets.setdefault(doc.domain, []).append(doc)

    picked = []
    empty_domains = []
    for domain, target in quota.items():
        pool = buckets.get(domain, [])
        # p ∝ n^alpha * quality，避免纯按文件数抽
        weights = [(doc.n_tokens ** alpha) * doc.quality for doc in pool]
        if not pool or sum(weights) <= 0:
            # 空域要报出来，不能静默少抽
            empty_domains.append(domain)
            continue
        used = 0
        seen = set()
        while used < target and len(seen) < len(pool):
            doc = rng.choices(pool, weights=weights, k=1)[0]
            if doc.doc_id in seen:
                continue
            seen.add(doc.doc_id)
            picked.append(doc)
            used += doc.n_tokens
    return picked, empty_domains
```

测试就是一个小例子：三个域，其中 code 的 pool 是空的。

```python
docs = [Doc(f"web-{i}", "web", 100, 0.8, "...") for i in range(100)]
docs += [Doc(f"math-{i}", "math", 500, 0.9, "...") for i in range(4)]
docs += [Doc("junk", "web", 100, 0.1, "...")]
quota = {"web": 1000, "math": 10_000, "code": 5000}
picked, empty = mix_by_quota(docs, quota)

# 小例子：三个域，其中 code 没有文档，被报为空域
assert empty == ["code"]

# web 抽到配额为止
assert sum(d.n_tokens for d in picked if d.domain == "web") == 1000

# math 文档不够配额时整域取完，且无放回
math_ids = [d.doc_id for d in picked if d.domain == "math"]
assert sorted(math_ids) == ["math-0", "math-1", "math-2", "math-3"]

# 质量分低于 min_quality 的文档不会被抽中
assert all(d.doc_id != "junk" for d in picked)

# 同一个 rng 种子结果可复现
assert mix_by_quota(docs, quota)[0] == picked
```

写完先跑这个例子，空域要报出来，别静默少抽。还要补一句：生产上这是 map-reduce 或流式加权水库抽样，网页级语料用内存里的 `choices` 扛不住。质量分怎么来、启发式和模型分怎么叠，见 `dt-quality-filter-code`。

失败处理我也会主动讲。抽取失败的页面，比如正文为空、导航条被当成正文、PDF 扫描件，进 quarantine，别当短文档混进 mix。过滤要校准，同一个阈值在英语和低资源语言上的通过率会差一个数量级，所以训练文档和标签要按语言挑。去重会过头，公式、许可证和常见 boilerplate 的 Jaccard 很高，阈值要按域、按长度分层。评测要先冻结 URL 和 n-gram 指纹，再做训练侧去重，顺序反过来，会把答案洗进训练集。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert empty == ["code"]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 追问

**如果是 10B 文档呢？**
签名和质量分离线预计算，LSH 只比候选对，mix 在预聚合的 `(domain, bucket)` 计数上做。示例代码说明的是逻辑，大规模系统还需要分布式实现。

**为什么不直接 concat 再 shuffle？**
体积大的爬取域会吃掉数学、代码和多语言的预算。AFM 2025 报告在 continued PT 里把多语言从 8% 提到 30%，靠的是调配额。

**LLM 抽取自己会不会带来污染？**
会。抽取模型的版本要进 lineage，抽出来的正文仍要过质量门和评测指纹。

**SFT 管线和预训练差在哪？**
SFT 多了指令模板、assistant mask、verifier 和人写示范。六个阶段都还在，只是单位从文档变成了 `(prompt, completion, gate)`。

相关：`dt-minhash-code`、`dt-benchmark-gap`、`dt-quality-filter-code`
