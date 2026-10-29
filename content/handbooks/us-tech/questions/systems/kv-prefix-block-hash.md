---
id: kv-prefix-block-hash
section: systems
order: 35
level: A
title: KV Prefix ⑤：链式块哈希、缓存上下文与碰撞防护
quick: 块身份包含祖先哈希、当前 token 和完整上下文；同一个后缀块处在不同前缀下不能互相命中，模型、adapter、租户或位置语义改变也必须 miss。
tags:
  - 完整编程练习
  - KV Prefix 实现专题
  - Coding
  - KV Cache
  - Radix Tree
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: vLLM automatic prefix caching key and cache isolation
    url: 'https://docs.vllm.ai/en/latest/design/prefix_caching/'
    type: primary
---

## 题目描述

实现按完整 token 块复用 KV 页句柄的前缀缓存，隔离上下文并防止哈希碰撞误命中。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`Context` 是不可变对象，含字符串字段 model、adapter、tokenizer、`position_and_mask`、tenant、multimodal（默认空串）。`BlockHashCache(block_size=4,hash_fn=None)` 以正整数 `block_size` 为页长；`hash_fn` 可注入用于碰撞测试。

`put(tokens,values,context)` 登记完整页，values 含恰好 floor(len(tokens)/`block_size`) 个不可变不透明页句柄，尾部不满一页不存储。`match(tokens,context)` 返回 `(命中token数,句柄tuple)`，仅能命中从开头连续的完整块。

全部 context 字段及当前块之前的完整 token 前缀都影响复用语义；相同块出现在不同前缀下不能误用。重复登记保留已有句柄。哈希碰撞须被识别而不能返回错误页，发生 put 冲突时不能只发布部分新页。token 为非负整数，每条序列不超过 256，不要求淘汰功能。

### 示例

```text
block_size=2，put([1,2,3,4,5],["AB","CD"],ctx)。
match([1,2,3],ctx)=(2,("AB",))。
match([3,4],ctx)=(0,())。
将 ctx 的 tenant 改为另一值后，match([1,2],新ctx)=(0,())。
```

## 解题思路与参考答案

## 完整编程练习（手册原创实现版）

这题用链式块哈希区分「相同 token 块处在不同历史前缀里」的情况，并把模型和租户等计算上下文放入 key。它是手册为理解开源机制写的独立练习，接口、简化条件和测试都由手册定义；代码由手册独立编写。练习依赖 Python 3 与 NumPy，用 CPU 检查数值和状态语义，不报告 GPU throughput。

专题入口：[[kv-prefix-implementation-index]]。

### 题面、接口与约束

实现 `Context` 和 `BlockHashCache.put/match`，只缓存完整 page，page size 必须是正整数。每个完整 page 对应一个不可变的 opaque 句柄，尾部不足一页的 token 不入缓存。

Context 固定包含六项字符串：模型权重版本、adapter、tokenizer、位置及 mask 配置、租户和多模态内容指纹。块摘要要带 parent hash、当前 tokens 和 context，同时保留完整祖先 tokens 做精确校验，发生碰撞就抛错，避免错误复用。put 先检查所有候选碰撞，再发布结果；相同 key 重复写入时保留已有句柄。序列最多 256 token，本题不实现淘汰。

### 输入输出示例

设 page size 为 2，存入 `[1,2,3,4,5]→[AB,CD]`。查询 `[1,2,3]` 时只命中 2 token；查询 `[3,4]` 时不能直接复用 CD，因为 CD 对应的祖先并非空前缀。改变任何一个 Context 字段都应 miss。

### 解题思路与正确性

我会让每个块的摘要接上祖先哈希，记录它是在什么前缀后计算出来的。仅比较块内 token，会把不同历史下的 KV 混在一起。练习额外保留精确 key，并注入恒定 hash 函数测试碰撞，保证摘要相等时仍做语义校验。Context 由调用方声明有效计算状态，权重变化后也必须更新，固定一个 model 名字无法保证安全。

### 完整参考实现（Python 3）

```python
from dataclasses import dataclass, asdict
import hashlib
import json


@dataclass(frozen=True)
class Context:
    model: str
    adapter: str
    tokenizer: str
    position_and_mask: str
    tenant: str
    multimodal: str = ''


class BlockHashCache:
    def __init__(self, block_size=4, hash_fn=None):
        if type(block_size) is not int or block_size < 1:
            raise ValueError('block size')
        self.block_size = block_size
        self.hash_fn = hash_fn or (lambda data: hashlib.sha256(data).hexdigest())
        self.blocks = {}

    def chain(self, tokens, context):
        tokens = tuple(tokens)
        if not isinstance(context, Context) or any(
            type(t) is not int or t < 0 for t in tokens
        ):
            raise ValueError('context or tokens')
        # The complete exact key is retained too: a digest collision is not a hit.
        parent_hash = None
        for offset in range(0, len(tokens) - self.block_size + 1, self.block_size):
            block = tokens[offset : offset + self.block_size]
            exact = (context, tokens[:offset], block)
            encoded = json.dumps(
                [asdict(context), self.block_size, parent_hash, block],
                sort_keys=True,
                separators=(',', ':'),
            ).encode()
            digest = self.hash_fn(encoded)
            yield digest, exact
            parent_hash = digest

    def put(self, tokens, values, context):
        keys = list(self.chain(tokens, context))
        values = tuple(values)
        if len(keys) != len(values):
            raise ValueError('one immutable value per full block')
        # Check all collisions before publishing any newly computed blocks.
        for digest, exact in keys:
            if digest in self.blocks and self.blocks[digest][0] != exact:
                raise ValueError('hash collision: refuse to reuse')
        if len({d for d, _ in keys}) != len(keys):
            raise ValueError('intra-request hash collision')
        for (digest, exact), value in zip(keys, values):
            self.blocks.setdefault(digest, (exact, value))

    def match(self, tokens, context):
        values = []
        for digest, exact in self.chain(tokens, context):
            entry = self.blocks.get(digest)
            if entry is None:
                break
            if entry[0] != exact:
                raise ValueError('hash collision: refuse to reuse')
            values.append(entry[1])
        return len(values) * self.block_size, tuple(values)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert cache.match([1, 2, 3, 4, 9], context) == (4, ('AB', 'CD'))` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

把实现与以下测试放进同一文件执行；测试覆盖正确性，不是生产环境的性能基准。

```python
def test():
    from dataclasses import replace

    context = Context('weights-v1', 'lora-A', 'tok-v1', 'rope0-causal', 'tenant-A')
    cache = BlockHashCache(2)
    cache.put([1, 2, 3, 4, 5], ['AB', 'CD'], context)
    assert cache.match([1, 2, 3, 4, 9], context) == (4, ('AB', 'CD'))
    assert cache.match([1, 2, 3], context) == (2, ('AB',))
    assert cache.match([9, 2, 3, 4], context) == (0, ())
    assert cache.match([3, 4], context) == (
        0,
        (),
    )  # suffix block needs its full ancestry
    for field in asdict(context):
        other = replace(context, **{field: getattr(context, field) + '-changed'})
        assert cache.match([1, 2], other) == (0, ())
    cache.put([1, 2], ['duplicate-handle'], context)
    assert cache.match([1, 2], context)[1] == ('AB',)
    collision = BlockHashCache(2, hash_fn=lambda _: 'constant')
    collision.put([1, 2], ['AB'], context)
    try:
        collision.match([3, 4], context)
    except ValueError:
        pass
    else:
        raise AssertionError('collision became a false hit')


if __name__ == '__main__':
    test()
```

### 复杂度与追问

摘要输入按块计算，完整祖先校验的 tuple 前缀副本使本参考实现最坏空间和准备工作达到 $O(T^2/B)$；生产实现通常依赖强哈希并避免保存所有祖先副本。本题故意以空间换可见的碰撞校验，不声称复刻 vLLM 全部实现。

多模态 prompt 即使 token IDs 相同，图像/音频内容也可能不同；指纹须覆盖有效内容及预处理版本。相同 token 但不同 RoPE 起点或非因果 mask 不可复用；生产系统还有混合 attention、滑窗等专门语义。

## 相关题

- [[kv-prefix-implementation-index]]：专题入口，看本题在 8 道里的位置和三条练习路线。
- [[kv-prefix-radix]]：另一种前缀索引：token 粒度的 radix tree，可以命中压缩边中间，不按整块对齐。
- [[sys-prefix-cache]]：口述版，讲命中条件为什么必须包含 token ID、权重、LoRA 和位置语义。
- [[xai-prompt-cache]]：xAI 问法，重点是多租户下 cache key 怎么隔离、系统提示改版怎么断开。
- [[sys-radix-tree]]：口述对比块哈希和 radix tree 各适合哪种共享模式。
