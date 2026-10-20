---
id: dt-winnow-code
section: tech-screen
order: 23
level: A
title: CoderPad：代码近克隆怎么指纹，Winnowing 窗口怎么写？
quick: >-
  我会先规范化源码，切 k-gram 哈希，每个窗口只留最小哈希，指纹集合比 Jaccard。
  许可证头和 import 块要剥掉，否则全世界 Python 文件两两相似。
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Dedup
  - Code
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Winnowing: Local Algorithms for Document Fingerprinting"
    url: https://theory.stanford.edu/~aiken/publications/papers/sigmod03.pdf
    type: primary
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
---

先规范化源码，切成 k-gram 并计算哈希，每个窗口只保留最小哈希，再用 Jaccard 比较指纹集合。许可证头和 import 块要先去掉，否则许多无关 Python 文件也会显得相似。直接套网页 MinHash 时，空白、重命名和许可证头都可能干扰 shingle。

Winnowing 是 Moss / 抄袭检测那套窗口最小值。Llama 3 代码后训练还要执行验证，去克隆是上游，避免同一题 40 份拷贝占满 监督微调（SFT）。

## 规范化，再窗口最小值

先：去注释、压空白、可选地把标识符换成占位（重命名克隆）。再对 token 或字符 k-gram 计算哈希。窗口 $w$ 内只保留最小哈希，保证任意长度 $\ge k+w-1$ 的匹配至少共享一个指纹。

```python
import hashlib
import re

# 行注释用 [^\n]* 截到行尾；块注释才需要跨行。整体开 re.S 会让 #.* 吞掉文件剩余部分
COMMENT = re.compile(r"#[^\n]*|//[^\n]*|/\*.*?\*/", re.S)
SPACE = re.compile(r"\s+")
IDENTIFIER = re.compile(r"\b[_a-z]\w*\b")


def normalize_src(src, drop_idents=False):
    """去注释、压空白、小写；drop_idents=True 时把标识符都换成 id，用来抓重命名克隆。"""
    src = COMMENT.sub(" ", src)
    src = SPACE.sub(" ", src).strip().lower()
    if drop_idents:
        src = IDENTIFIER.sub("id", src)
    return src


def kgram_hashes(text, k=5):
    tokens = text.split()
    if len(tokens) < k:
        return []
    hashes = []
    for i in range(len(tokens) - k + 1):
        gram = " ".join(tokens[i:i + k])
        hashes.append(int(hashlib.blake2b(gram.encode(), digest_size=8).hexdigest(), 16))
    return hashes


def winnow(hashes, w=4):
    """每个长度 w 的窗口取最小哈希作为指纹。不足一个窗口时整段当一个窗口。"""
    if not hashes:
        return set()
    if len(hashes) < w:
        return {min(hashes)}
    fingerprints = set()
    last = None
    for i in range(len(hashes) - w + 1):
        smallest = min(hashes[i:i + w])
        # 同一最小值在窗口内右移时不重复记，和论文一致
        if smallest != last:
            fingerprints.add(smallest)
            last = smallest
    return fingerprints


def jaccard_fp(a, b):
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)
```

### 可执行测试

```python
original = """
def total(xs):
    # sum the list
    acc = 0
    for x in xs:
        acc += x
    return acc
"""
reformatted = (
    "def total(xs):\n  acc = 0  // other comment style\n"
    "  for x in xs:\n      acc += x\n  return acc\n"
)
renamed = original.replace("acc", "s").replace("xs", "values")

# 行注释只删到行尾，后面的代码保留
assert normalize_src("x = 1  # set x\ny = 2") == "x = 1 y = 2"
assert normalize_src("a /* block\ncomment */ b") == "a b"

# 只改了空白和注释的克隆，指纹完全相同
fp_original = winnow(kgram_hashes(normalize_src(original)))
assert winnow(kgram_hashes(normalize_src(reformatted))) == fp_original

# 重命名克隆：默认不像，drop_idents=True 后指纹相同
fp_renamed = winnow(kgram_hashes(normalize_src(renamed)))
assert jaccard_fp(fp_original, fp_renamed) < 0.5
assert winnow(kgram_hashes(normalize_src(original, drop_idents=True))) == winnow(
    kgram_hashes(normalize_src(renamed, drop_idents=True))
)

# 短于一个窗口的哈希序列仍然留一个指纹
assert winnow([5, 3], w=4) == {3}
assert winnow([], w=4) == set()

# 窗口最小值：[5, 1, 4, 2, 6] 在 w=2 时取 1, 2
assert winnow([5, 1, 4, 2, 6], w=2) == {1, 2}

# 两个空指纹集合视为相同
assert jaccard_fp(set(), set()) == 1.0
```

阈值按语言定。剥不掉的 `apache license version 2.0` 会让无关文件 $J$ 很高：许可证文件白名单，或先砍文件头 30 行再指纹。

## 和执行验证的分工

去克隆解决「同一份拷贝刷高 HumanEval」。执行验证解决「看起来不像克隆但测试是模型自己改的」，见 `dt-code-exec-synth`。两层都要。评测泄漏仍走 `dt-substr-dedup-code` 和 `dt-code-bench-bleed`。

`drop_idents=True` 能抓重命名克隆，也也可能把实际不同的函数判为相似。默认关，只在高价值题解桶开。

## 追问

- **AST 哈希呢？** 更稳，现场写不完 tree-sitter。口播：生产按语言上 AST 精确去重，Winnowing 做近克隆。
- **二进制 / notebook？** notebook 先抽代码格。二进制不进文本管线。
- **k 和 w 怎么选？** $k$ 大约 5 个 token，$w=4$ 是论文量级。短文件指纹少，$J$ 不稳，短于 20 行只做精确哈希。
