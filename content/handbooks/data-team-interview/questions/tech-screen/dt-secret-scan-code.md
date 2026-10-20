---
id: dt-secret-scan-code
section: tech-screen
order: 24
level: A
title: CoderPad：爬到的网页和仓库里，API 密钥怎么扫出来？
quick: "结合提供商前缀和字符串熵找凭证，命中整文件隔离，并人工核对高价值来源。示例密钥可白名单，但脱敏不能替代来源与安全检查。检测无法覆盖所有提供商，教师合成输出也需要扫描。"
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

检测结合高熵字符串与提供商前缀，例如 `sk-`、`AKIA`、`ghp_`。命中后将整文件放入隔离区（quarantine），不要仅删除密钥再继续训练；测试夹具和明显假密钥经过核对可列入白名单。卡号、邮箱检查见 `dt-pii-luhn-code`。真实密钥进入预训练后，存在被模型记忆、补全的风险。

GitHub 公开了一张提供商前缀表。开源仓库和抓取页里都有。现场按前缀加熵写检测，不要声称能覆盖所有云。

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

假阳性：文档里的 `sk-example`、base64 图片、长 hash。熵能挡一部分。白名单：`YOUR_API_KEY`、全 0、连续 `abc`、官方文档的示例格式。

处理：整文档 / 整文件进 quarantine，lineage 记 kind。挖空再训仍可能从上下文补全密钥形态。高价值许可书命中要人工看，可能是文档在讲密钥格式。

## 和 PII 分开报

卡号可以按协议脱敏；密钥文件不能仅靠脱敏就默认安全，模型仍会学习 `AKIA` 后跟 16 位的上下文和格式。安全评测另造「拒绝回显密钥」数据，见 `dt-safety-refuse`，那是后训练，不是把真密钥留在预训练里。

Apple 公开口径会滤标识、避开汇聚个人信息的站。密钥扫描是同一治理口：许可网页不等于可以含凭证。

## 追问

- **熵阈值怎么定？** 抽 1k 命中人工看。语言不同，base64 正文熵高，对 HTML 要先剥标签。
- **私有仓库能当训练吗？** 许可问题，见 `dt-legal-capability`。通过密钥检查不代表来源许可合格。
- **模型自己生成了看起来像密钥的字符串？** 合成侧拦。训练侧仍扫教师输出，教师会抄网页。
