---
id: dt-secret-scan-code
section: tech-screen
order: 24
level: A
title: CoderPad：爬到的网页和仓库里，API 密钥怎么扫出来？
quick: "用提供商前缀加字符串熵来找凭证，命中后整个文件隔离，高价值来源再人工核对。示例密钥可以白名单；只做脱敏的文件仍可能教会模型密钥格式，来源和安全检查都要做。检测覆盖不了所有提供商，教师模型的合成输出也要扫。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Security
  - Filtering
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: GitHub secret scanning patterns
    url: https://docs.github.com/en/code-security/secret-scanning/introduction/supported-secret-scanning-patterns
    type: primary
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
  - title: "How Bad Can It Git? Characterizing Secret Leakage in Public GitHub Repositories"
    url: https://www.ndss-symposium.org/ndss-paper/how-bad-can-it-git-characterizing-secret-leakage-in-public-github-repositories/
    type: primary
---

真实密钥进了预训练，就有被模型记住、再补全出来的风险。检测靠两条信号：提供商前缀（比如 `sk-`、`AKIA`、`ghp_`）和高熵字符串。命中后整个文件进隔离区（quarantine）；测试夹具和明显的假密钥核对后可以放白名单。卡号和邮箱的检查见 `dt-pii-luhn-code`。

开源仓库和抓取页里都有这类凭证。GitHub 公开了一张提供商前缀表，现场按前缀加熵写检测即可，不要声称能覆盖所有云。

## 前缀加熵，整文件扔

```python
import math
import re
from collections import Counter

PREFIX = [
    ("aws_akid", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{16,}\b")),
    ("slack", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("generic_sk", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
]
ASSIGN = re.compile(
    r"(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?([A-Za-z0-9_\-/+=]{16,})",
    re.I,
)


def entropy(s):
    """字符级香农熵（bit / 字符）。"""
    n = len(s) or 1
    counts = Counter(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def find_secrets(text, min_entropy=3.5):
    """返回 [(kind, start, value)]。提供商前缀直接报；赋值语句里的值要过熵门。"""
    hits = []
    for kind, pattern in PREFIX:
        for m in pattern.finditer(text):
            hits.append((kind, m.start(), m.group()))
    for m in ASSIGN.finditer(text):
        value = m.group(1)
        if entropy(value) >= min_entropy:
            hits.append(("assign", m.start(), value))
    return hits
```

### 可执行测试

```python
# 提供商前缀：AWS access key id 和 GitHub token
text = "aws = AKIAIOSFODNN7EXAMPLE\ngh = ghp_abcdefghijklmnopqrstuvwxyz0123"
assert [kind for kind, _, _ in find_secrets(text)] == ["aws_akid", "github"]

# 赋值语句里的高熵值被报出来
leaked = 'api_key = "Zx9Qw7Er5Ty3Ui1Op8As"'
assert find_secrets(leaked) == [("assign", 0, "Zx9Qw7Er5Ty3Ui1Op8As")]

# 低熵占位符（全是同一字符）不报
assert find_secrets('password = "aaaaaaaaaaaaaaaaaaaa"') == []

# 太短的 sk- 字符串不算密钥
assert find_secrets("see sk-example in the docs") == []

# 熵：单一字符为 0，两种字符各半为 1 bit
assert entropy("aaaa") == 0.0
assert entropy("abab") == 1.0
assert entropy("") == 0.0
```

假阳性来自文档里的 `sk-example`、base64 图片和长 hash，熵能挡掉一部分。白名单放 `YOUR_API_KEY`、全 0、连续的 `abc`，以及官方文档里的示例格式。

整个文件进 quarantine、lineage 记下 kind，是因为挖空之后，模型仍可能从上下文里补全出密钥的形态。高价值的许可书命中时要人工看，它可能只是在讲密钥格式。

## 和 PII 分开报

卡号可以按协议脱敏，密钥文件不能靠脱敏就默认安全，因为模型仍会学到 `AKIA` 后面跟 16 位这类上下文和格式。「拒绝回显密钥」的能力要另外造安全数据来教，见 `dt-safety-refuse`，那是后训练的事，真密钥仍要从预训练里清掉。

密钥扫描和 PII 过滤属于同一类治理：许可合格的网页里也可能有凭证。

## 追问

- **熵阈值怎么定？** 抽 1k 个命中人工看。不同语言的情况不一样，base64 正文的熵很高，HTML 要先剥标签再算。
- **私有仓库能拿来训练吗？** 这是许可问题，见 `dt-legal-capability`。通过了密钥检查，不代表来源许可合格。
- **模型自己生成了像密钥的字符串怎么办？** 在合成侧拦截。训练侧仍要扫教师输出，因为教师会抄网页。
