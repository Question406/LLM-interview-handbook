---
id: code-sharded-checkpoint-io
section: coding
order: 217
level: A
title: 手写分片 Checkpoint 的保存与恢复（清单、原子 rename、校验和）
quick: >-
  每个 rank 写自己的 shard 和 sha256，全部到齐后写 `MANIFEST.json.tmp`，再原子 rename 成 `MANIFEST.json`，没有清单就等于这个 checkpoint 不存在。恢复时先读清单、核对 digest 再 load，半成功的目录不能当成功。概念见 `sys-async-checkpoint`。
tags:
  - Checkpoint
  - Coding
  - Distributed
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: PyTorch Distributed Checkpoint
    url: https://pytorch.org/tutorials/recipes/distributed_checkpoint_recipe.html
    type: primary
---

## 题目描述

实现一个小型分片 checkpoint 的保存与加载接口，只有全部分片和清单写完后才发布最终目录，并在读取时核验内容完整性。本题不要求分布式进程或框架 checkpoint 集成。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `save_shards(state:dict[int,bytes],ckpt_dir:str)` 和 `load_shards(ckpt_dir:str)`。state将rank编号映射到原始字节；保存目标是尚不存在的新目录，其父目录可用，且无并发写同一路径。

### 输出与约束

每个rank有独立分片文件；清单记录version、world及每片的rank/file/sha256。先写临时 .writing 目录，再通过重命名发布。加载返回与state相同的字典，并核对每片摘要；缺片或内容损坏时不能静默当作有效checkpoint。摘要校验是本题业务要求，无需额外扩展参数合法性检查。

### 示例

```text
state={0:b"A",1:b"BC"}
save_shards(state,新目录)后load_shards(该目录) -> {0:b"A",1:b"BC"}
若把任意已发布分片字节改掉，load不能成功返回原始有效state。
```

## 解题思路与参考答案

分片 checkpoint 的提交点是清单：每个 rank 写完自己的 shard 和 sha256，rank 0 收齐以后先写 `MANIFEST.json.tmp`，再原子 rename 成 `MANIFEST.json`。读的一方只认带完整清单的目录，读时逐片核对 digest。「每个 rank `torch.save` 完就算成功」是最常见的错误想法：进程在写第 $N-1$ 片时崩了，目录里会留下半旧半新的文件，下次恢复直接加载，就可能把训练状态搞坏。

PyTorch DCP 用 planner 写分片，读的时候还能 reshard；这题用手写 IO，把原子性讲清楚就行。异步上传和步边界一致性见 `sys-async-checkpoint`，换 world size 重切见 `sys-elastic-resume-reshard`。

## 协议

写的流程是：各 rank 把 bytes 写到 `ckpt/tmp/shard_{rank}.bin` 并算 sha256 → rank 0 收齐元数据 → 写 `MANIFEST.json.tmp`，里面有 version、world、shard 列表和 digest → `os.replace` 成 `MANIFEST.json`。读的时候，清单不存在就失败；缺文件或 digest 对不上，整版作废，回退到上一个成功的目录。

先 rename 数据目录再写清单是不行的，崩溃窗口里会同时制造出「有目录没清单」和「有清单缺数据」两种半态。清单出现，才算 commit。

```python
import hashlib, json, os

def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def save_shards(state: dict[int, bytes], ckpt_dir: str) -> None:
    tmp = ckpt_dir + ".writing"
    os.makedirs(tmp, exist_ok=True)
    shards = []
    for rank, blob in sorted(state.items()):
        name = f"shard_{rank}.bin"
        with open(os.path.join(tmp, name), "wb") as f:
            f.write(blob)
        shards.append({"rank": rank, "file": name, "sha256": _digest(blob)})
    man = {"version": 1, "world": len(state), "shards": shards}
    man_tmp = os.path.join(tmp, "MANIFEST.json.tmp")
    with open(man_tmp, "w") as f:
        json.dump(man, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(man_tmp, os.path.join(tmp, "MANIFEST.json"))
    os.replace(tmp, ckpt_dir)

def load_shards(ckpt_dir: str) -> dict[int, bytes]:
    man = json.load(open(os.path.join(ckpt_dir, "MANIFEST.json")))
    out = {}
    for s in man["shards"]:
        p = os.path.join(ckpt_dir, s["file"])
        blob = open(p, "rb").read()
        if _digest(blob) != s["sha256"]:
            raise ValueError(f"checksum {s['file']}")
        out[s["rank"]] = blob
    if len(out) != man["world"]:
        raise ValueError("incomplete shards")
    return out
```

`os.replace` 在同一个文件系统上对文件是原子的，对目录在 POSIX 上通常也是。跨盘的话，要先把数据完整写到目标盘，再 commit 清单。清单先 `fsync` 再 rename，免得掉电后清单里有名字、盘上没数据。现场不用写分布式 gather，说一句「rank 0 等齐 metadata」就够了。

## 崩溃窗口与读者约定

读者，也就是 resume 进程，只承认带完整 `MANIFEST.json` 的目录。`ckpt.writing/` 或者只有部分 `shard_*.bin` 的路径，一律当它不存在，绝不「能 load 多少算多少」。多个版本并存时，目录名带上 step，比如 `ckpt/step-1000/`，成功以后再把 `latest` 指针原子地改过去；正在上传的 step 不能成为 `latest`。这和异步落盘的提交点是一致的。

校验失败要整版拒绝。只修某一个 shard、不改清单，会造成 digest 和文件对不上的第三种半态。数据文件也最好先 `fsync` 再写清单，否则掉电后可能出现「清单齐全，打开却是短文件」。`world` 必须等于实际的文件数，多出来的旧 shard 不能混进来。rank 之间用屏障对齐「我写完了」，之后 rank 0 才 commit。手写按 rank 存文件，足够讲清原子性；真要换 TP/EP，需要按逻辑张量存的 DCP，这份 `shard_{rank}.bin` 没法任意 reshard。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

在临时目录里保存两份字节串，再读回比较。随后篡改一个 shard，应触发校验和错误；临时目录自动清理。

```python
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as directory:
    destination = str(Path(directory) / "checkpoint")
    expected = {0: b"rank-zero", 1: b"rank-one"}
    save_shards(expected, destination)
    assert load_shards(destination) == expected
    (Path(destination) / "shard_0.bin").write_bytes(b"corrupt")
    try:
        load_shards(destination)
    except ValueError:
        pass
    else:
        raise AssertionError("corrupted shard must fail")
print("simple tests passed")
```

## 追问

**清单为什么不能先写？**
读者会按清单去打开还不存在的 shard。顺序必须是数据齐 → 写清单 tmp → rename 清单。

**校验和算在哪一层？**
每个 shard 一份 sha256，清单里再列出来。只对清单算哈希不够，缺了哪一片定位不到。

**和 DCP 是什么关系？**
DCP 把「逻辑张量 → 分片文件」做成了 planner，原子提交和校验的语义是一样的。手写这一版是为了把提交点说清楚。

**async 上传怎么接？**
后台拷到对象存储以后，也只有齐套的清单才可见。上传失败不能覆盖上一个 `MANIFEST`。

**恢复时 world size 变了怎么办？**
这份按 rank 存的 blob 不能直接用，要换成按逻辑 ID 存的 DCP 再切。这里的 load 是按原来的 world 校验齐套的。
