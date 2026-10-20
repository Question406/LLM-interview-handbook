---
id: dt-pipeline-talk
section: tech-screen
order: 1
level: S
title: CoderPad：边写边讲，一条预训练 / SFT 数据管线怎么画？
quick: "先确认数据类型、要实现的步骤和输出格式，再边编码边解释每步筛什么、为什么。整体流程包含来源、抽取、过滤、去重、配比和评测隔离；现场只实现要求的部分，同时说明版本、失败处理和大规模扩展。"
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

边实现被问到的部分，边解释它在 crawl → extract → filter → dedup → mix → eval-isolation 中的位置。说明输入是什么、保留和丢弃哪些内容，以及如何隔离评测。不要沉默写 20 分钟才解释，也不要只画完整流程而没有实现具体函数。

## 先立合同，再写函数

开口先问三句：数据是网页、对话还是多模态；这轮要的是过滤、去重还是配比；输出是文档还是打包后的 token。然后在白板上（或 CoderPad 注释里）写下六个阶段，声明你现在实现哪一个：

1. Crawl / ingest。来源、许可、robots / opt-out。Applebot 公开口径：不爬登录墙和付费墙，尊重 robots.txt 的「不要用来训基础模型」。
2. Extract。HTML → 正文。规则抽不过的域再上模型，不要默认每页都调一次 LLM。AFM 2025 写了 headless 渲染和用 LLM 抽主内容，因为现代站大量是 JS。
3. Filter。语言、PII、脏话、质量。阈值要能按域校准。AFM 的经验是过猛启发式会扔掉好 token，所以减弱规则、加重按语言调过的模型分。
4. Dedup。精确哈希去同文，MinHash / LSH 去近重复，再对评测集做 overlap。实现见 `dt-minhash-code`。
5. Mix。按域配额抽样，而不是按原始体积 concat。温度 $p_i \propto n_i^{\alpha}$，$\alpha$ 越小越抬长尾。
6. Eval isolation。训练侧任何「像评测」的文档在进 mix 之前打污染标记。污染检测见 `dt-benchmark-gap`。

CoderPad 里他们多半只让你写 3+5，或 4。剩下的用口播补齐：这一步的输入输出 schema、失败时文档是丢还是进 quarantine、日志里要留下源 URL 和过滤器版本。

## 手里写的那截：配额采样

边写边说：`quota` 是目标能力的预算，不是源站文件大小。`quality` 已经是上游模型分。采样单位是文档，计费单位是 token，所以短模板会在条数上淹没难例，要用 token 加权或先打包再抽。

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

### 可执行测试

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

写完先跑一个小例子：三个域、其中一个 pool 为空。空域要报出来，不要静默少抽。再补一句：生产上这是 map-reduce / 流式加权水库抽样，内存里 `choices` 扛不住网页级语料。

质量分怎么来、启发式和模型分怎么叠，见 `dt-quality-filter-code`。

## 口播时主动报规模

提取失败：正文为空、导航条当正文、PDF 扫描件。进 quarantine，不要当短文档混进 mix。

过滤校准：同一阈值在英语和低资源语言上的通过率会差一个数量级。AFM 写了按语言选训练文档和标签。

去重过头：公式、许可证、常见 boilerplate 的 Jaccard 很高。按域、按长度分层阈值。

评测泄漏：先冻结评测 URL / n-gram 指纹，再开训练侧去重。反过来做会把答案洗进训练集。

评委打断「如果是 10B 文档呢？」答：签名和质量分离线预计算，LSH 只比候选对，mix 在预聚合的 `(domain, bucket)` 计数上做，不在 Python list 上做。示例代码说明逻辑，大规模系统还需要分布式实现。

## 追问

- **为什么不直接 concat 再 shuffle？** 体积大的爬取域会吃掉数学 / 代码 / 多语预算。AFM 在 continued PT 里把多语从 8% 提到 30%，这就是在改配额，不是多爬一点。
- **LLM 抽取会不会自己污染？** 会。抽取模型的版本要进 lineage；抽出来的正文仍要过质量门和评测指纹。
- **监督微调（SFT） 管线和预训练差在哪？** SFT 多了指令模板、assistant mask、验证器（verifier）、人写示范。六个阶段还在，只是单位从文档变成 `(prompt, completion, gate)`。
