---
id: code-sharded-checkpoint-io
section: coding
order: 217
level: A
title: 手写分片 Checkpoint 的保存与恢复（清单、原子 rename、校验和）
quick: >-
  每 rank 写 shard 与 sha256，全部齐套后写
  `MANIFEST.json.tmp` 再原子 rename 成 `MANIFEST.json`。没有清单等于不存在。恢复先读清单、核
  digest 再 load。半成功目录不得当成功。概念见 `sys-async-checkpoint`。
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

错法：「每个 rank `torch.save` 完就算成功」。进程在写第 $N-1$ 片时崩溃，目录里会留下半旧半新文件，下次 resume 静默 load 会训飞。生产语义是：清单是提交点。PyTorch DCP 用 planner 写分片、读时可 reshard；本题用手写 IO 把原子性讲清楚。异步上传、步边界一致性见 `sys-async-checkpoint`；换 world size 重切见 `sys-elastic-resume-reshard`。

## 协议

写：各 rank 把 bytes 写到 `ckpt/tmp/shard_{rank}.bin` 并算 sha256 → rank 0 收齐元数据 → 写 `MANIFEST.json.tmp`（version、world、shard 列表、digest）→ `os.replace` 成 `MANIFEST.json`。读：清单不存在则失败；缺文件或 digest 不符则整版作废，回退上一成功目录。不要先 rename 数据目录再写清单，崩溃窗口会把「有目录无清单」和「有清单缺数据」两种半态都制造出来。清单后出现才是 commit。

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

`os.replace` 在同一文件系统上对文件是原子的；对目录在 POSIX 上通常也是。跨盘要先完整写到目标盘再 commit 清单。`fsync` 清单再 rename，避免掉电后清单里有名、盘上无数据。现场不必写分布式 gather，说「rank 0 等齐 metadata」即可。

## 崩溃窗口与读者约定

读者（resume 进程）只承认带完整 `MANIFEST.json` 的目录。`ckpt.writing/` 或只有部分 `shard_*.bin` 的路径一律当不存在，绝不「能 load 多少算多少」。多版本并存时用目录名带 step，例如 `ckpt/step-1000/`，成功后再把 `latest` 指针原子改过去；正在上传的 step 不得成为 `latest`。这和异步落盘的提交点一致，见 `sys-async-checkpoint`。

校验失败要整版拒绝：只修某一个 shard 而不改清单，会造成 digest 与文件不一致的第三种半态。数据文件也建议 `fsync` 再写清单，否则掉电后会出现「清单齐全、打开是短文件」。`world` 与实际文件数必须相等，多出来的旧 shard 不得混入。Rank 间用屏障对齐「我写完了」，rank 0 才 commit。手写 rank 文件够讲清原子性；真正换 TP/EP 需要按逻辑张量存的 DCP，这份 `shard_{rank}.bin` 不能任意 reshard。

## 追问

- **为什么清单不能先写？** 读者会按清单去打开还不存在的 shard。必须数据齐 → 清单 tmp → rename 清单。
- **校验和算哪一层？** 每 shard 一份 sha256，清单里再列出来。只对清单哈希不够，缺片无法定位。
- **和 DCP 的关系？** DCP 把「逻辑张量 → 分片文件」做成 planner；原子提交和校验的语义相同。手写本题是把提交点讲死。
- **async 上传怎么接？** 后台拷到对象存储后，仍然只有齐套清单可见。失败不得覆盖上一 `MANIFEST`。见 `sys-async-checkpoint`。
- **恢复时 world size 变了？** 这份按 rank 存的 blob 不能直接用，需要按逻辑 ID 的 DCP 再切。本题 load 按原 world 校验齐套。
---
