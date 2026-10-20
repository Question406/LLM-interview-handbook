---
id: kv-prefix-block-hash
section: systems
order: 35
level: A
title: "KV Prefix ⑤：链式块哈希、缓存上下文与碰撞防护"
quick: "块身份包含祖先哈希、当前 token 和完整上下文；同一个后缀块处在不同前缀下不能互相命中，模型、adapter、租户或位置语义改变也必须 miss。"
tags:
  - 完整编程练习
  - KV Prefix 实现专题
  - Coding
  - KV Cache
  - Radix Tree
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "vLLM automatic prefix caching key and cache isolation"
    url: https://docs.vllm.ai/en/latest/design/prefix_caching/
    type: primary
---

## 完整编程练习（手册原创实现版）

本题是为理解开源机制而编写的独立练习，不是某家公司的已确认原题，也不是SGLang/vLLM源码逐字翻译。接口、简化条件和测试由手册定义。依赖Python 3与NumPy，使用CPU测试数值及状态语义，不报告GPU吞吐。

专题入口：[[kv-prefix-implementation-index]]。

### 题面、接口与约束

实现 `Context` 和 `BlockHashCache.put/match`。仅缓存完整page，page size正整数；每完整page一个不可变opaque句柄，尾部不足page不入缓存。Context固定六项字符串：模型权重版本、adapter、tokenizer、位置及mask配置、租户和多模态内容指纹。块摘要包含parent hash、当前tokens和context；同时保留完整祖先tokens作精确校验，碰撞抛错而不误复用。put须先验证所有候选碰撞再发布；重复相同key保留已存在句柄。序列≤256token；不实现淘汰。

### 输入输出示例

page size2，存 `[1,2,3,4,5]→[AB,CD]`，查 `[1,2,3]` 仅命中2token；查 `[3,4]` 不能直接拿CD，因为其祖先不是空前缀。改变任一Context字段均miss。

### 解题思路与正确性

链式摘要记录“这个块位于哪个前缀之后”，不只是块内token。练习额外保留精确key并注入恒定hash函数测试碰撞，确保摘要相等不能绕过语义校验。Context是调用方对有效计算状态的声明，不能填一个永不更新的model名字就宣称安全。

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
        if not isinstance(context, Context) or any(type(t) is not int or t < 0 for t in tokens):
            raise ValueError('context or tokens')
        # The complete exact key is retained too: a digest collision is not a hit.
        parent_hash = None
        for offset in range(0, len(tokens)-self.block_size+1, self.block_size):
            block = tokens[offset:offset+self.block_size]
            exact = (context, tokens[:offset], block)
            encoded = json.dumps([asdict(context), self.block_size, parent_hash, block],
                                 sort_keys=True, separators=(',', ':')).encode()
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
        return len(values)*self.block_size, tuple(values)
```

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
    assert cache.match([3, 4], context) == (0, ())  # suffix block needs its full ancestry
    for field in asdict(context):
        other = replace(context, **{field: getattr(context, field)+'-changed'})
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

摘要输入按块计算，完整祖先校验的tuple前缀副本使本参考实现最坏空间和准备工作达到 $O(T^2/B)$；生产实现通常依赖强哈希并避免保存所有祖先副本。本题故意以空间换可见的碰撞校验，不声称复刻vLLM全部实现。

多模态prompt即使token IDs相同，图像/音频内容也可能不同；指纹须覆盖有效内容及预处理版本。相同token但不同RoPE起点或非因果mask不可复用；生产系统还有混合attention、滑窗等专门语义。

## 相关题

- [[kv-prefix-implementation-index]]：专题入口，看本题在 8 道里的位置和三条练习路线。
- [[kv-prefix-radix]]：另一种前缀索引：token 粒度的 radix tree，可以命中压缩边中间，不按整块对齐。
- [[sys-prefix-cache]]：口述版，讲命中条件为什么必须包含 token ID、权重、LoRA 和位置语义。
- [[xai-prompt-cache]]：xAI 问法，重点是多租户下 cache key 怎么隔离、系统提示改版怎么断开。
- [[sys-radix-tree]]：口述对比块哈希和 radix tree 各适合哪种共享模式。
