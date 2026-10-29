---
id: drustz-29b56fbdbc66e93052
section: labs
order: 5
level: A
title: lab3_data_engine — Teleop 演示数据摄入/管护 Pipeline
quick: 作者完整文档 · lab3_data_engine — Teleop 演示数据摄入/管护 Pipeline
companies: []
tags:
  - DrustZ
  - 作者完整文档
  - Labs · Code、Tests 与 Data
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/labs/lab3_data_engine/README.md
    type: primary
---
# lab3_data_engine — Teleop 演示数据摄入/管护 Pipeline

> The Bot Company（家用机器人，fleet learning 路线）备考 Lab。
> 解释器固定 `/usr/bin/python3`（Python 3.9.6），纯标准库，零依赖，全部确定性，测试全程 < 5 秒。

## 这个 lab 对应什么考点

岗位核心是 **data collection / data engine**：机器人学习公司的护城河不是模型，而是
"teleop 演示 → 清洗管护 → 训练集 → 部署反馈 → 下一轮采集" 这个闭环。本 lab 把闭环的
工程形态做成了四阶段 pipeline，每一阶段都是面试高频追问点：

| 阶段 | 函数（pipeline.py） | 面试考点 |
|---|---|---|
| 1. Schema 校验 | `validate_lines` | 坏数据**进 quarantine 并留机器可读原因**，不静默丢弃（可观测性、可 debug） |
| 2. 去重 | `dedup_records` | 精确去重（content hash，排除 demo_id）+ 近似去重（task/operator/场景 + 量化几何特征分桶），keep-first + 完整 audit trail（谁替谁被丢） |
| 3. 质量过滤 | `filter_by_quality` | **可解释**启发式打分：超长停顿 / 高 jerk 抖动 / 重试过多 / 未完成，各扣多少分写在 config 里而不是代码里，阈值可调 |
| 4. 分层配比 | `stratify` | 按 task 目标分布resampling（盈余 task 按质量分取 top-k，欠缺 task 全收）并输出**采集需求单**：缺哪个 task、缺多少、优先补哪种光照/房间 cohort —— 这就是 curation 反哺 collection 的闭环，data collection 岗的点睛之笔 |

再加 `manifest.py` 的两个生产级设计：

- **内容寻址 manifest**：`manifest_id = sha256(sorted demo_ids)`，训练集身份只由内容决定；
  lineage 记录 parent manifest、pipeline config 快照、每个输入文件的 sha256 —— 任何一个
  训练集都能溯源到原始批次和当时的参数。
- **增量运行**：state 里存已处理文件哈希 + 去重索引 + 幸存记录；重跑只处理新批次
  （阶段 1–2 只碰新数据，阶段 3–4 在幸存池上全局重算，便宜且与到达顺序无关）；
  无新数据的重跑是幂等 no-op；增量构建与一次性全量构建产出**完全相同的 manifest id**。
  输入文件被原地修改、或换 config 继续增量，都是硬错误（保护 lineage 不被悄悄作废）。

## 15–30 分钟熟悉路径（先跑什么，再读什么）

```bash
cd my_interview_prep/ml_sys_prep/bot_company/labs/lab3_data_engine

# 1. (2 min) 生成两个批次的合成 teleop 数据（807 + 127 行，含已知缺陷的 ground truth 侧车文件）
/usr/bin/python3 generate_demos.py --batch 1
/usr/bin/python3 generate_demos.py --batch 2 --cross-dup-from data/demos_batch1.jsonl

# 2. (3 min) 增量构建 manifest，看 stage funnel、manifest id、采集需求单；再跑一次看幂等 no-op
/usr/bin/python3 manifest.py
/usr/bin/python3 manifest.py # "no new inputs; manifest unchanged"

# 3. (2 min) 跑测试（8 个，plain assert）
/usr/bin/python3 test_pipeline.py

# 4. (10 min) 读 pipeline.py：按 Stage 1→4 顺序读四个函数 + PipelineConfig，
#    重点看 content_hash / near_dup_key（生成器 import 它们来保证注入的重复必然碰撞）
#    和 stratify 里采集需求单的构造。

# 5. (8 min) 读 manifest.py 的 run_incremental：state 里存什么、为什么阶段 1-2 增量而 3-4 全局重算、
#    no-op 判定、两个硬错误（输入被改 / config 漂移）。

# 6. (可选) 拧旋钮看 funnel 变化：
/usr/bin/python3 pipeline.py --quality-threshold 0.9 --workdir /tmp/lab3_strict
ls out/ # quarantine.jsonl / dedup_report.json / quality_report.json /
# collection_requests.json / train_set.jsonl / manifests/ / state.json
```



关键数字（种子固定，永远复现）：934 行输入 → 18 条 quarantine → 916 有效 →
35 精确重复 + 35 近似重复 → 846 幸存 → 46 低质量剔除 → 800 → 分层选出 375 条，
2 张采集需求单（sort_laundry 缺 34 条、water_plants 缺 11 条，各附最稀缺光照/房间提示）。

## 面试中怎么引用这段经验（英文一句话）

> "I prototyped a fleet-style data engine for teleop demos: a four-stage pipeline — schema
> quarantine with machine-readable reasons, exact-plus-near dedup with a full audit trail,
> explainable quality gates, and stratified resampling that emits collection tickets for
> under-represented task cohorts — feeding content-addressed, lineage-tracked training
> manifests that are reproducible bit-for-bit across incremental and full rebuilds."

追问弹药：为什么 quarantine 而不是丢弃（fleet 端 bug 的第一现场）；near-dup 桶粒度怎么调
（桶太粗误伤多样性、太细漏重复，用 dedup_report 抽查calibration）；质量分为什么用可解释启发式
而不是学出来的分类器（冷启动没标注、且 ops 团队要能申诉）；采集需求单如何闭环（直接变成
teleop 排班：哪个 task、什么场景、采多少条）；manifest 内容寻址如何支撑训练可复现与回滚。

## 文件清单

```text
generate_demos.py   确定性合成数据生成器：700 clean + 40 差质量 + 25 精确重复 + 30 近似重复
                    + 12 坏 schema 行（batch 1，共 807 行）；batch 2 另含 5 条跨批次重复；
                    每批附 .summary.json ground-truth 侧车，注入的重复用 pipeline 自己的
                    hash/桶函数验证"必然碰撞"
pipeline.py         schema（dataclass）+ 四阶段纯函数 + PipelineConfig + 一次性 CLI
manifest.py         内容寻址 manifest + lineage + 增量 state + 增量 CLI
test_pipeline.py    8 个测试：生成器确定性 / 各阶段计数与 quarantine 原因 / 去重正确性
                    （注入重复全被抓、幸存者双重唯一、audit 指向幸存者）/ 质量过滤恰好剔除
                    注入的差样本 / 分层配比与需求单指向真实欠缺 cohort / manifest 跨 workdir
                    可复现 / 增量幂等 + 增量==全量 + lineage / 两个硬错误守卫
```



运行测试：`/usr/bin/python3 test_pipeline.py`

## generate_demos.py

```python
#!/usr/bin/env python3
"""Deterministic generator of synthetic teleop demonstration JSONL batches.

Produces ~800 records (batch 1) with known, labeled defects so the pipeline
stages have ground truth to be tested against:

  * clean demos       -- realistic metadata + trajectory summaries
  * bad-quality demos -- overlong pauses / shaky (high jerk) / incomplete
  * exact duplicates  -- same content re-uploaded under a new demo_id
  * near duplicates   -- same operator re-doing the same scene, tiny deltas
  * schema-bad lines  -- malformed JSON, missing/typed-wrong fields, etc.

The generator intentionally imports ``content_hash`` / ``near_dup_key`` from
``pipeline`` so the injected duplicates are *guaranteed* to collide under the
pipeline's own definitions (honest test fixtures, no coincidences).

Interpreter: Python 3.9 (no 3.10+ syntax). Standard library only.
"""

import argparse
import copy
import json
import os
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from pipeline import (
    CLUTTER_LEVELS,
    KNOWN_TASKS,
    LIGHTING_LEVELS,
    ROOMS,
    DemoRecord,
    PipelineConfig,
    SchemaError,
    content_hash,
    near_dup_key,
)

# Deliberately imbalanced so stage 4 has both surplus and deficit tasks.
TASK_WEIGHTS: Dict[str, float] = {
    "wipe_table": 0.24,
    "load_dishwasher": 0.22,
    "pick_up_toys": 0.20,
    "fold_towel": 0.14,
    "open_drawer": 0.10,
    "water_plants": 0.06,
    "sort_laundry": 0.04,
}

_SCHEMA_BAD_KINDS = (
    "malformed_json",
    "missing_task",
    "duration_as_string",
    "negative_duration",
    "unknown_task",
    "null_operator",
)


@dataclass(frozen=True)
class BatchSpec:
    """Composition of one generated batch (all counts are exact)."""

    batch: int
    n_clean: int
    n_bad_quality: int
    n_exact_dups: int
    n_near_dups: int
    n_schema_bad: int
    n_cross_dups: int = 0
    seed: int = 7
    day_lo: int = 1
    day_hi: int = 5


BATCH1 = BatchSpec(
    batch=1,
    n_clean=700,
    n_bad_quality=40,
    n_exact_dups=25,
    n_near_dups=30,
    n_schema_bad=12,
)
BATCH2 = BatchSpec(
    batch=2,
    n_clean=100,
    n_bad_quality=6,
    n_exact_dups=5,
    n_near_dups=5,
    n_schema_bad=6,
    n_cross_dups=5,
    day_lo=6,
    day_hi=7,
)


@dataclass
class GenerationSummary:
    """Ground truth about what was injected (consumed by test_pipeline.py)."""

    batch: int
    total_lines: int
    n_clean: int
    bad_quality_ids: List[str] = field(default_factory=list)
    exact_dup_ids: List[str] = field(default_factory=list)
    near_dup_ids: List[str] = field(default_factory=list)
    cross_dup_ids: List[str] = field(default_factory=list)
    schema_bad_lines: List[int] = field(default_factory=list)  # 1-based

    @property
    def n_schema_valid(self) -> int:
        return self.total_lines - len(self.schema_bad_lines)

    def to_dict(self) -> Dict[str, object]:
        return {
            "batch": self.batch,
            "total_lines": self.total_lines,
            "n_clean": self.n_clean,
            "n_schema_valid": self.n_schema_valid,
            "bad_quality_ids": self.bad_quality_ids,
            "exact_dup_ids": self.exact_dup_ids,
            "near_dup_ids": self.near_dup_ids,
            "cross_dup_ids": self.cross_dup_ids,
            "schema_bad_lines": self.schema_bad_lines,
        }


def _weighted_task(rng: random.Random) -> str:
    tasks = list(TASK_WEIGHTS)
    weights = [TASK_WEIGHTS[task] for task in tasks]
    return rng.choices(tasks, weights=weights, k=1)[0]


def _make_clean(rng: random.Random, spec: BatchSpec, demo_id: str) -> Dict[str, object]:
    """One schema-valid, quality-passing record (score == 1.0 by construction)."""
    duration = round(rng.uniform(20.0, 180.0), 3)
    num_pauses = rng.randint(0, 5)
    mean_jerk = round(rng.uniform(0.5, 4.0), 3)
    return {
        "demo_id": demo_id,
        "task": _weighted_task(rng),
        "operator_id": "op_%02d" % rng.randint(1, 10),
        "scene": {
            "room": rng.choice(ROOMS),
            "lighting": rng.choices(LIGHTING_LEVELS, weights=[0.6, 0.1, 0.3], k=1)[0],
            "clutter": rng.choice(CLUTTER_LEVELS),
            "num_objects": rng.randint(2, 15),
        },
        "duration_s": duration,
        "traj": {
            "num_steps": int(duration * rng.uniform(8.0, 12.0)),
            "mean_jerk": mean_jerk,
            "max_jerk": round(mean_jerk * rng.uniform(1.5, 3.0), 3),
            "num_pauses": num_pauses,
            "longest_pause_s": round(rng.uniform(0.5, 12.0), 3) if num_pauses else 0.0,
            "num_retries": rng.randint(0, 2),
            "path_length_m": round(rng.uniform(1.0, 12.0), 3),
        },
        "completed": True,
        "collected_at": "2026-08-%02d" % rng.randint(spec.day_lo, spec.day_hi),
    }


def _make_bad_quality(
    rng: random.Random, spec: BatchSpec, demo_id: str, mode: int
) -> Dict[str, object]:
    """Clean record degraded by one decisive defect mode (cycled by caller)."""
    record = _make_clean(rng, spec, demo_id)
    defect = mode % 3
    if defect == 0:  # operator froze / got distracted
        record["traj"]["num_pauses"] = max(3, int(record["traj"]["num_pauses"]))
        record["traj"]["longest_pause_s"] = round(rng.uniform(45.0, 90.0), 3)
    elif defect == 1:  # shaky teleoperation
        mean_jerk = round(rng.uniform(9.0, 15.0), 3)
        record["traj"]["mean_jerk"] = mean_jerk
        record["traj"]["max_jerk"] = round(mean_jerk * 2.0, 3)
    else:  # gave up after many retries
        record["completed"] = False
        record["traj"]["num_retries"] = rng.randint(5, 8)
    return record


def _make_near_dup(
    rng: random.Random,
    source: Dict[str, object],
    demo_id: str,
    config: PipelineConfig,
) -> Dict[str, object]:
    """Same operator/scene/geometry, jitter only fine-grained trajectory stats.

    Guaranteed (and asserted) to land in the same near-dup bucket as the
    source while having a different content hash.
    """
    dup = copy.deepcopy(source)
    dup["demo_id"] = demo_id
    delta = rng.choice([-1.0, 1.0]) * round(rng.uniform(0.05, 0.25), 3)
    dup["traj"]["mean_jerk"] = round(float(source["traj"]["mean_jerk"]) + delta, 3)
    dup["traj"]["longest_pause_s"] = round(
        float(source["traj"]["longest_pause_s"]) + rng.uniform(0.0, 0.8), 3
    )
    if near_dup_key(dup, config) != near_dup_key(source, config):
        raise AssertionError("near-dup injection left its bucket: %s" % demo_id)
    if content_hash(dup) == content_hash(source):
        raise AssertionError("near-dup injection produced an exact dup: %s" % demo_id)
    return dup


def _make_exact_dup(source: Dict[str, object], demo_id: str) -> Dict[str, object]:
    """Identical content re-uploaded under a fresh demo_id."""
    dup = copy.deepcopy(source)
    dup["demo_id"] = demo_id
    if content_hash(dup) != content_hash(source):
        raise AssertionError("exact-dup injection changed content: %s" % demo_id)
    return dup


def _make_schema_bad(
    rng: random.Random, spec: BatchSpec, demo_id: str, kind: str
) -> str:
    """One raw line violating the schema in a specific, labeled way."""
    record = _make_clean(rng, spec, demo_id)
    if kind == "malformed_json":
        return '{"demo_id": "%s", "task": ' % demo_id  # truncated upload
    if kind == "missing_task":
        del record["task"]
    elif kind == "duration_as_string":
        record["duration_s"] = "%.1fs" % float(record["duration_s"])
    elif kind == "negative_duration":
        record["duration_s"] = -5.0
    elif kind == "unknown_task":
        record["task"] = "juggle_chainsaws"
    elif kind == "null_operator":
        record["operator_id"] = None
    else:
        raise ValueError("unknown schema-bad kind: %s" % kind)
    return json.dumps(record, sort_keys=True)


def eligible_cross_sources(
    lines: List[str], summary: GenerationSummary, config: PipelineConfig
) -> List[Dict[str, object]]:
    """Payloads from a previous batch that are safe exact-dup sources.

    Excludes that batch's own near/exact dup copies: near-dup copies were
    dropped at dedup, so their content hash never entered the kept index and
    a copy of them would surface as a *near* (not exact) duplicate.
    """
    excluded = set(summary.near_dup_ids) | set(summary.exact_dup_ids)
    sources: List[Dict[str, object]] = []
    for line in lines:
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        try:
            DemoRecord.from_dict(payload, config)
        except SchemaError:
            continue
        if payload["demo_id"] not in excluded:
            sources.append(payload)
    return sources


def generate_batch(
    spec: BatchSpec,
    cross_sources: Optional[List[Dict[str, object]]] = None,
    config: Optional[PipelineConfig] = None,
) -> Tuple[List[str], GenerationSummary]:
    """Generate one batch as raw JSONL lines plus its ground-truth summary.

    Layout: shuffled base (clean + bad-quality), then near dups, then exact
    dups, then cross-batch dups, then schema-bad lines. Duplicate copies
    always appear *after* their sources so keep-first dedup drops exactly
    the injected ids.
    """
    if spec.n_cross_dups and not cross_sources:
        raise ValueError(
            "batch %d needs cross_sources for cross-batch dups" % spec.batch
        )
    config = config or PipelineConfig()
    rng = random.Random(spec.seed * 1000 + spec.batch)

    counter = {"next": 0}

    def next_id() -> str:
        counter["next"] += 1
        return "d%d_%05d" % (spec.batch, counter["next"])

    clean = [_make_clean(rng, spec, next_id()) for _ in range(spec.n_clean)]
    bad = [
        _make_bad_quality(rng, spec, next_id(), mode=index)
        for index in range(spec.n_bad_quality)
    ]
    base = clean + bad
    rng.shuffle(base)

    near_dups = [
        _make_near_dup(rng, source, next_id(), config)
        for source in rng.sample(clean, spec.n_near_dups)
    ]
    exact_dups = [
        _make_exact_dup(source, next_id())
        for source in rng.sample(clean, spec.n_exact_dups)
    ]
    cross_dups = []
    if spec.n_cross_dups:
        cross_dups = [
            _make_exact_dup(source, next_id())
            for source in rng.sample(list(cross_sources or []), spec.n_cross_dups)
        ]

    lines = [
        json.dumps(record, sort_keys=True)
        for record in base + near_dups + exact_dups + cross_dups
    ]
    schema_bad_lines: List[int] = []
    for index in range(spec.n_schema_bad):
        kind = _SCHEMA_BAD_KINDS[index % len(_SCHEMA_BAD_KINDS)]
        lines.append(_make_schema_bad(rng, spec, next_id(), kind))
        schema_bad_lines.append(len(lines))

    summary = GenerationSummary(
        batch=spec.batch,
        total_lines=len(lines),
        n_clean=spec.n_clean,
        bad_quality_ids=[record["demo_id"] for record in bad],
        exact_dup_ids=[record["demo_id"] for record in exact_dups],
        near_dup_ids=[record["demo_id"] for record in near_dups],
        cross_dup_ids=[record["demo_id"] for record in cross_dups],
        schema_bad_lines=schema_bad_lines,
    )
    return lines, summary


def write_batch(lines: List[str], summary: GenerationSummary, out_path: str) -> str:
    """Write the JSONL plus a ``<name>.summary.json`` ground-truth sidecar."""
    out_dir = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    sidecar = os.path.splitext(out_path)[0] + ".summary.json"
    with open(sidecar, "w", encoding="utf-8") as handle:
        json.dump(summary.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return sidecar


def main() -> None:
    lab_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--batch", type=int, choices=(1, 2), default=1)
    parser.add_argument("--out", default=None, help="output .jsonl path")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument(
        "--cross-dup-from",
        default=None,
        help="batch-1 jsonl (with .summary.json sidecar) for cross-batch dups",
    )
    args = parser.parse_args()

    config = PipelineConfig()
    spec = BATCH1 if args.batch == 1 else BATCH2
    spec = BatchSpec(**{**spec.__dict__, "seed": args.seed})

    cross_sources: Optional[List[Dict[str, object]]] = None
    if spec.n_cross_dups:
        if not args.cross_dup_from:
            raise SystemExit("--cross-dup-from is required for batch 2")
        with open(args.cross_dup_from, "r", encoding="utf-8") as handle:
            source_lines = handle.read().splitlines()
        sidecar_path = os.path.splitext(args.cross_dup_from)[0] + ".summary.json"
        with open(sidecar_path, "r", encoding="utf-8") as handle:
            sidecar = json.load(handle)
        source_summary = GenerationSummary(
            batch=sidecar["batch"],
            total_lines=sidecar["total_lines"],
            n_clean=sidecar["n_clean"],
            bad_quality_ids=sidecar["bad_quality_ids"],
            exact_dup_ids=sidecar["exact_dup_ids"],
            near_dup_ids=sidecar["near_dup_ids"],
            cross_dup_ids=sidecar["cross_dup_ids"],
            schema_bad_lines=sidecar["schema_bad_lines"],
        )
        cross_sources = eligible_cross_sources(source_lines, source_summary, config)

    out_path = args.out or os.path.join(
        lab_dir, "data", "demos_batch%d.jsonl" % spec.batch
    )
    lines, summary = generate_batch(spec, cross_sources=cross_sources, config=config)
    sidecar = write_batch(lines, summary, out_path)

    print("wrote %d lines -> %s" % (summary.total_lines, out_path))
    print("ground truth   -> %s" % sidecar)
    print(
        "  clean=%d bad_quality=%d near_dups=%d exact_dups=%d cross_dups=%d schema_bad=%d"
        % (
            summary.n_clean,
            len(summary.bad_quality_ids),
            len(summary.near_dup_ids),
            len(summary.exact_dup_ids),
            len(summary.cross_dup_ids),
            len(summary.schema_bad_lines),
        )
    )


if __name__ == "__main__":
    main()
```




## manifest.py

```python
#!/usr/bin/env python3
"""Content-addressed training-set manifests with lineage + incremental runs.

Manifest identity
-----------------
``manifest_id = sha256("\n".join(sorted(selected_demo_ids)))`` -- the id is a
function of *what is in the training set*, nothing else. Re-running on the
same inputs with the same config reproduces the same id, whether the data
arrived in one shot or incrementally.

Lineage
-------
Each manifest records its parent manifest id, a full pipeline-config
snapshot, and the sha256 of every input file that fed it, so any training
set can be traced back to raw batches and the exact knobs used.

Incremental runs
----------------
``run_incremental`` keeps a state file per workdir:
  * input files already processed (by name + sha256)  -> skipped on rerun
  * dedup indices (content hash / near-dup bucket)    -> new batches are
    deduped against everything already kept, without re-reading old batches
  * post-dedup survivors                              -> stages 3-4 (quality,
    stratification) are cheap global recomputations over the survivor pool
Only stages 1-2 ever touch raw data, so a rerun processes *only new files*;
a rerun with no new files is a no-op returning the existing manifest.

Interpreter: Python 3.9 (no 3.10+ syntax). Standard library only.
"""

import argparse
import datetime
import glob
import hashlib
import json
import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple

from pipeline import (
    DemoRecord,
    PipelineConfig,
    dedup_records,
    filter_by_quality,
    stratify,
    validate_lines,
)

STATE_FILENAME = "state.json"
MANIFEST_DIRNAME = "manifests"
LATEST_FILENAME = "MANIFEST_LATEST"
_STATE_SCHEMA_VERSION = 1
_MANIFEST_SCHEMA_VERSION = 1


def file_sha256(path: str) -> str:
    """sha256 of a file's bytes (input files are treated as immutable)."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_manifest_id(record_ids: Iterable[str]) -> str:
    """Content address of a training set: sha256 over its sorted demo ids."""
    joined = "\n".join(sorted(record_ids))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


@dataclass
class RunResult:
    """Outcome of one incremental run."""

    manifest: Dict[str, object]
    manifest_path: str
    new_files: List[str]  # basenames processed in *this* run
    noop: bool  # True when nothing changed (idempotent rerun)
    run_counts: Dict[str, int]  # stage counts for this run only

    @property
    def manifest_id(self) -> str:
        return str(self.manifest["manifest_id"])


def _empty_state(config: PipelineConfig) -> Dict[str, object]:
    return {
        "schema_version": _STATE_SCHEMA_VERSION,
        "config": config.to_dict(),
        "processed_files": {},  # basename -> {"sha256":, "lines":}
        "exact_index": {},  # content hash -> kept demo_id
        "bucket_index": {},  # near-dup bucket -> kept demo_id
        "survivors": [],  # post-dedup record dicts (stage 1-2 output)
        "latest_manifest_id": None,
        "cumulative": {
            "input_lines": 0,
            "quarantined": 0,
            "validated": 0,
            "dropped_exact": 0,
            "dropped_near": 0,
        },
    }


def _load_state(workdir: str, config: PipelineConfig) -> Dict[str, object]:
    path = os.path.join(workdir, STATE_FILENAME)
    if not os.path.exists(path):
        return _empty_state(config)
    with open(path, "r", encoding="utf-8") as handle:
        state = json.load(handle)
    if state.get("schema_version") != _STATE_SCHEMA_VERSION:
        raise ValueError("state schema version mismatch in %s" % path)
    if state.get("config") != config.to_dict():
        raise ValueError(
            "pipeline config drift detected in %s; incremental runs require the "
            "original config -- use a fresh workdir to rebuild with new knobs" % workdir
        )
    return state


def _atomic_write_json(path: str, obj: object) -> None:
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp_path, path)


def run_incremental(
    input_paths: List[str],
    config: PipelineConfig,
    workdir: str,
) -> RunResult:
    """Process any new input files, then rebuild the manifest.

    Files are keyed by basename; re-presenting an already-processed file is
    free (skipped by hash check), and mutating a processed file in place is
    an error, because it would silently invalidate lineage.
    """
    os.makedirs(os.path.join(workdir, MANIFEST_DIRNAME), exist_ok=True)
    state = _load_state(workdir, config)
    processed: Dict[str, Dict[str, object]] = state["processed_files"]

    new_files: List[Tuple[str, str, str]] = []  # (path, basename, sha256)
    for path in sorted(input_paths, key=os.path.basename):
        name = os.path.basename(path)
        digest = file_sha256(path)
        if name in processed:
            if processed[name]["sha256"] != digest:
                raise ValueError(
                    "input file %s changed since it was ingested; inputs are "
                    "immutable -- publish a new batch file instead" % name
                )
            continue
        new_files.append((path, name, digest))

    survivors: List[DemoRecord] = [
        DemoRecord.from_dict(payload, config) for payload in state["survivors"]
    ]
    seen_ids: Set[str] = set(record.demo_id for record in survivors)
    exact_index: Dict[str, str] = state["exact_index"]
    bucket_index: Dict[str, str] = state["bucket_index"]

    run_counts = {
        "input_lines": 0,
        "quarantined": 0,
        "validated": 0,
        "dropped_exact": 0,
        "dropped_near": 0,
        "new_survivors": 0,
    }
    run_quarantined = []
    run_dropped = []

    for path, name, digest in new_files:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        records, quarantined = validate_lines(
            lines, config, seen_ids=seen_ids, source=name
        )
        seen_ids.update(record.demo_id for record in records)
        dedup = dedup_records(records, config, exact_index, bucket_index)
        exact_index = dedup.exact_index
        bucket_index = dedup.bucket_index
        survivors.extend(dedup.kept)

        run_quarantined.extend(quarantined)
        run_dropped.extend(dedup.dropped)
        run_counts["input_lines"] += len(lines)
        run_counts["quarantined"] += len(quarantined)
        run_counts["validated"] += len(records)
        run_counts["dropped_exact"] += sum(
            1 for entry in dedup.dropped if entry.reason == "exact_duplicate"
        )
        run_counts["dropped_near"] += sum(
            1 for entry in dedup.dropped if entry.reason == "near_duplicate"
        )
        run_counts["new_survivors"] += len(dedup.kept)
        processed[name] = {"sha256": digest, "lines": len(lines)}

    # Stages 3-4 are global recomputations over the survivor pool: cheap,
    # deterministic, and independent of arrival order.
    kept_quality, rejected = filter_by_quality(survivors, config)
    strat = stratify(kept_quality, config)
    record_ids = sorted(record.demo_id for record in strat.selected)
    manifest_id = compute_manifest_id(record_ids)

    manifest_path = os.path.join(workdir, MANIFEST_DIRNAME, manifest_id + ".json")
    if not new_files and state["latest_manifest_id"] == manifest_id:
        with open(manifest_path, "r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        return RunResult(
            manifest=manifest,
            manifest_path=manifest_path,
            new_files=[],
            noop=True,
            run_counts=run_counts,
        )

    for key in (
        "input_lines",
        "quarantined",
        "validated",
        "dropped_exact",
        "dropped_near",
    ):
        state["cumulative"][key] += run_counts[key]

    manifest = {
        "schema_version": _MANIFEST_SCHEMA_VERSION,
        "manifest_id": manifest_id,
        "num_records": len(record_ids),
        "record_ids": record_ids,
        "per_task_selected": strat.per_task_selected,
        "target_counts": strat.target_counts,
        "collection_requests": [request.to_dict() for request in strat.requests],
        "stage_counts": {
            "cumulative": dict(state["cumulative"]),
            "survivors_after_dedup": len(survivors),
            "rejected_quality": len(rejected),
            "after_quality": len(kept_quality),
            "selected": len(strat.selected),
        },
        "lineage": {
            "parent_manifest_id": state["latest_manifest_id"],
            "pipeline_config": config.to_dict(),
            "inputs": [
                {
                    "name": name,
                    "sha256": processed[name]["sha256"],
                    "lines": processed[name]["lines"],
                }
                for name in sorted(processed)
            ],
        },
        "created_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # Per-run reports + current training set (reports describe the last
    # mutating run; quarantine.jsonl is append-only across runs).
    _atomic_write_json(manifest_path, manifest)
    with open(os.path.join(workdir, LATEST_FILENAME), "w", encoding="utf-8") as handle:
        handle.write(manifest_id + "\n")
    with open(
        os.path.join(workdir, "quarantine.jsonl"), "a", encoding="utf-8"
    ) as handle:
        for entry in run_quarantined:
            handle.write(json.dumps(entry.to_dict(), sort_keys=True) + "\n")
    _atomic_write_json(
        os.path.join(workdir, "dedup_report.json"),
        [entry.to_dict() for entry in run_dropped],
    )
    _atomic_write_json(
        os.path.join(workdir, "quality_report.json"),
        [entry.to_dict() for entry in rejected],
    )
    _atomic_write_json(
        os.path.join(workdir, "collection_requests.json"),
        [request.to_dict() for request in strat.requests],
    )
    with open(
        os.path.join(workdir, "train_set.jsonl"), "w", encoding="utf-8"
    ) as handle:
        for record in sorted(strat.selected, key=lambda r: r.demo_id):
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")

    state["exact_index"] = exact_index
    state["bucket_index"] = bucket_index
    state["survivors"] = [record.to_dict() for record in survivors]
    state["latest_manifest_id"] = manifest_id
    _atomic_write_json(os.path.join(workdir, STATE_FILENAME), state)

    return RunResult(
        manifest=manifest,
        manifest_path=manifest_path,
        new_files=[name for _, name, _ in new_files],
        noop=False,
        run_counts=run_counts,
    )


def main() -> None:
    lab_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(
        description="Incremental manifest build over a directory of demo batches."
    )
    parser.add_argument("--data-dir", default=os.path.join(lab_dir, "data"))
    parser.add_argument("--workdir", default=os.path.join(lab_dir, "out"))
    parser.add_argument("--budget", type=int, default=420)
    parser.add_argument("--quality-threshold", type=float, default=0.75)
    args = parser.parse_args()

    config = PipelineConfig(
        train_budget=args.budget, quality_threshold=args.quality_threshold
    )
    paths = sorted(glob.glob(os.path.join(args.data_dir, "*.jsonl")))
    if not paths:
        raise SystemExit(
            "no .jsonl files under %s (run generate_demos.py first)" % args.data_dir
        )

    result = run_incremental(paths, config, args.workdir)

    if result.noop:
        print("no new inputs; manifest unchanged (idempotent rerun)")
    else:
        print("processed new files: %s" % (result.new_files or "(none)"))
        print("this run: %s" % json.dumps(result.run_counts, sort_keys=True))
    print("manifest_id: %s" % result.manifest_id)
    print("parent:      %s" % result.manifest["lineage"]["parent_manifest_id"])
    print("num_records: %s" % result.manifest["num_records"])
    print("per-task selected:")
    for task, count in sorted(result.manifest["per_task_selected"].items()):
        target = result.manifest["target_counts"][task]
        print("  %-16s %4d / %d" % (task, count, target))
    requests = result.manifest["collection_requests"]
    print("collection requests (%d):" % len(requests))
    for request in requests:
        print(
            "  %-16s have=%-4d target=%-4d gap=%-4d %s"
            % (
                request["task"],
                request["have"],
                request["target"],
                request["gap"],
                request["note"],
            )
        )
    print("manifest file: %s" % result.manifest_path)


if __name__ == "__main__":
    main()
```




## pipeline.py

```python
#!/usr/bin/env python3
"""Teleop demonstration curation pipeline (lab3_data_engine).

Four independently testable stages, mirroring a fleet-learning data engine:

    Stage 1  validate_lines      raw JSONL -> DemoRecord | quarantine(reason)
    Stage 2  dedup_records       exact dups (content hash) + near dups
                                 (feature bucketing), keep-first, full audit
    Stage 3  filter_by_quality   explainable heuristic score vs. threshold
    Stage 4  stratify            per-task target mix -> train selection +
                                 collection request sheet for missing cohorts

Design notes
------------
* Standard library only; every stage is a pure function of (records, config)
  so each is unit-testable in isolation.
* Determinism: no wall clock in any decision, stable sort keys everywhere,
  keep-first dedup preserves input order semantics across incremental runs.
* This module owns the canonical schema, content hashing and bucketing keys;
  ``generate_demos.py`` imports them so injected duplicates are guaranteed to
  collide, and ``manifest.py`` imports them for incremental state.

Interpreter: Python 3.9 (no 3.10+ syntax).
"""

import argparse
import glob
import hashlib
import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

# --------------------------------------------------------------------------
# Domain vocabulary (single source of truth, shared with the generator).
# --------------------------------------------------------------------------

KNOWN_TASKS = (
    "fold_towel",
    "load_dishwasher",
    "open_drawer",
    "pick_up_toys",
    "sort_laundry",
    "water_plants",
    "wipe_table",
)
ROOMS = ("bedroom", "kitchen", "laundry_room", "living_room")
LIGHTING_LEVELS = ("bright", "dark", "dim")
CLUTTER_LEVELS = ("high", "low", "medium")


class SchemaError(ValueError):
    """Raised when a raw payload violates the demo schema.

    The exception message doubles as the machine-readable quarantine reason,
    e.g. ``missing_field:task`` or ``bad_type:duration_s``.
    """


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class PipelineConfig:
    """All tunable knobs for the four stages.

    Frozen so a config snapshot stored in a manifest cannot drift from the
    config that actually produced the run.
    """

    known_tasks: Tuple[str, ...] = KNOWN_TASKS

    # Stage 1: schema bounds.
    min_duration_s: float = 1.0
    max_duration_s: float = 600.0

    # Stage 2: near-dup bucketing granularity.
    duration_bucket_s: float = 5.0
    steps_bucket: int = 50
    path_bucket_m: float = 1.0

    # Stage 3: quality heuristics (penalty weights are explainable on purpose).
    max_longest_pause_s: float = 20.0
    max_mean_jerk: float = 6.0
    max_retries: int = 3
    penalty_incomplete: float = 0.5
    penalty_pause: float = 0.35
    penalty_jerk: float = 0.35
    penalty_retries: float = 0.3
    quality_threshold: float = 0.75

    # Stage 4: stratified selection.
    train_budget: int = 420
    target_mix: Optional[Dict[str, float]] = None  # None -> uniform over tasks

    def resolved_target_mix(self) -> Dict[str, float]:
        """Return the task -> fraction target mix (uniform if unset)."""
        if self.target_mix is not None:
            return dict(self.target_mix)
        share = 1.0 / len(self.known_tasks)
        return {task: share for task in self.known_tasks}

    def to_dict(self) -> Dict[str, object]:
        """JSON-serializable snapshot for manifest lineage."""
        return {
            "known_tasks": list(self.known_tasks),
            "min_duration_s": self.min_duration_s,
            "max_duration_s": self.max_duration_s,
            "duration_bucket_s": self.duration_bucket_s,
            "steps_bucket": self.steps_bucket,
            "path_bucket_m": self.path_bucket_m,
            "max_longest_pause_s": self.max_longest_pause_s,
            "max_mean_jerk": self.max_mean_jerk,
            "max_retries": self.max_retries,
            "penalty_incomplete": self.penalty_incomplete,
            "penalty_pause": self.penalty_pause,
            "penalty_jerk": self.penalty_jerk,
            "penalty_retries": self.penalty_retries,
            "quality_threshold": self.quality_threshold,
            "train_budget": self.train_budget,
            "target_mix": self.resolved_target_mix(),
        }


# --------------------------------------------------------------------------
# Schema (records)
# --------------------------------------------------------------------------


def _get_present(payload: Dict[str, object], key: str, ctx: str) -> object:
    if key not in payload or payload[key] is None:
        raise SchemaError("missing_field:%s%s" % (ctx, key))
    return payload[key]


def _get_str(payload: Dict[str, object], key: str, ctx: str = "") -> str:
    value = _get_present(payload, key, ctx)
    if not isinstance(value, str) or not value:
        raise SchemaError("bad_type:%s%s" % (ctx, key))
    return value


def _get_bool(payload: Dict[str, object], key: str, ctx: str = "") -> bool:
    value = _get_present(payload, key, ctx)
    if not isinstance(value, bool):
        raise SchemaError("bad_type:%s%s" % (ctx, key))
    return value


def _get_float(
    payload: Dict[str, object],
    key: str,
    ctx: str = "",
    lo: Optional[float] = None,
    hi: Optional[float] = None,
) -> float:
    value = _get_present(payload, key, ctx)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SchemaError("bad_type:%s%s" % (ctx, key))
    number = float(value)
    if (lo is not None and number < lo) or (hi is not None and number > hi):
        raise SchemaError("out_of_range:%s%s" % (ctx, key))
    return number


def _get_int(
    payload: Dict[str, object],
    key: str,
    ctx: str = "",
    lo: Optional[int] = None,
) -> int:
    value = _get_present(payload, key, ctx)
    if isinstance(value, bool) or not isinstance(value, int):
        raise SchemaError("bad_type:%s%s" % (ctx, key))
    if lo is not None and value < lo:
        raise SchemaError("out_of_range:%s%s" % (ctx, key))
    return value


def _get_obj(payload: Dict[str, object], key: str) -> Dict[str, object]:
    value = _get_present(payload, key, "")
    if not isinstance(value, dict):
        raise SchemaError("bad_type:%s" % key)
    return value


@dataclass(frozen=True)
class Scene:
    """Static scene context captured at collection time."""

    room: str
    lighting: str
    clutter: str
    num_objects: int

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "Scene":
        return cls(
            room=_get_str(payload, "room", "scene."),
            lighting=_get_str(payload, "lighting", "scene."),
            clutter=_get_str(payload, "clutter", "scene."),
            num_objects=_get_int(payload, "num_objects", "scene.", lo=0),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "room": self.room,
            "lighting": self.lighting,
            "clutter": self.clutter,
            "num_objects": self.num_objects,
        }


@dataclass(frozen=True)
class TrajStats:
    """Summary statistics of one teleop trajectory (not the raw traces)."""

    num_steps: int
    mean_jerk: float
    max_jerk: float
    num_pauses: int
    longest_pause_s: float
    num_retries: int
    path_length_m: float

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "TrajStats":
        return cls(
            num_steps=_get_int(payload, "num_steps", "traj.", lo=1),
            mean_jerk=_get_float(payload, "mean_jerk", "traj.", lo=0.0),
            max_jerk=_get_float(payload, "max_jerk", "traj.", lo=0.0),
            num_pauses=_get_int(payload, "num_pauses", "traj.", lo=0),
            longest_pause_s=_get_float(payload, "longest_pause_s", "traj.", lo=0.0),
            num_retries=_get_int(payload, "num_retries", "traj.", lo=0),
            path_length_m=_get_float(payload, "path_length_m", "traj.", lo=0.0),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "num_steps": self.num_steps,
            "mean_jerk": self.mean_jerk,
            "max_jerk": self.max_jerk,
            "num_pauses": self.num_pauses,
            "longest_pause_s": self.longest_pause_s,
            "num_retries": self.num_retries,
            "path_length_m": self.path_length_m,
        }


@dataclass(frozen=True)
class DemoRecord:
    """One validated teleop demonstration (metadata + trajectory summary)."""

    demo_id: str
    task: str
    operator_id: str
    scene: Scene
    traj: TrajStats
    duration_s: float
    completed: bool
    collected_at: str

    @classmethod
    def from_dict(
        cls, payload: Dict[str, object], config: PipelineConfig
    ) -> "DemoRecord":
        """Parse and validate a raw payload; raises SchemaError with reason."""
        task = _get_str(payload, "task")
        if task not in config.known_tasks:
            raise SchemaError("unknown_task:%s" % task)
        return cls(
            demo_id=_get_str(payload, "demo_id"),
            task=task,
            operator_id=_get_str(payload, "operator_id"),
            scene=Scene.from_dict(_get_obj(payload, "scene")),
            traj=TrajStats.from_dict(_get_obj(payload, "traj")),
            duration_s=_get_float(
                payload,
                "duration_s",
                lo=config.min_duration_s,
                hi=config.max_duration_s,
            ),
            completed=_get_bool(payload, "completed"),
            collected_at=_get_str(payload, "collected_at"),
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "demo_id": self.demo_id,
            "task": self.task,
            "operator_id": self.operator_id,
            "scene": self.scene.to_dict(),
            "traj": self.traj.to_dict(),
            "duration_s": self.duration_s,
            "completed": self.completed,
            "collected_at": self.collected_at,
        }


# --------------------------------------------------------------------------
# Content identity (shared by dedup, generator, and manifest state)
# --------------------------------------------------------------------------


def content_hash(payload: Dict[str, object]) -> str:
    """sha256 of the canonical record content, excluding the assigned id.

    Two uploads of the same demo differ only in ``demo_id``; everything else
    identical means the same content.
    """
    body = {key: value for key, value in payload.items() if key != "demo_id"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def near_dup_key(payload: Dict[str, object], config: PipelineConfig) -> str:
    """Coarse feature bucket: same task/operator/scene + quantized geometry.

    Records landing in the same bucket are near-duplicates: they add almost
    no new information to the training set, so we keep only the first.
    """
    scene = payload["scene"]
    traj = payload["traj"]
    return "|".join(
        [
            str(payload["task"]),
            str(payload["operator_id"]),
            str(scene["room"]),
            str(scene["lighting"]),
            str(scene["clutter"]),
            str(int(float(payload["duration_s"]) // config.duration_bucket_s)),
            str(int(int(traj["num_steps"]) // config.steps_bucket)),
            str(int(round(float(traj["path_length_m"]) / config.path_bucket_m))),
        ]
    )


# --------------------------------------------------------------------------
# Stage 1: schema validation
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class QuarantinedLine:
    """One rejected raw line, with provenance and a machine-readable reason."""

    source: str
    line_no: int
    reason: str
    raw_prefix: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "source": self.source,
            "line_no": self.line_no,
            "reason": self.reason,
            "raw_prefix": self.raw_prefix,
        }


def validate_lines(
    lines: Iterable[str],
    config: PipelineConfig,
    seen_ids: Optional[Set[str]] = None,
    source: str = "<memory>",
) -> Tuple[List[DemoRecord], List[QuarantinedLine]]:
    """Stage 1: parse raw JSONL lines into DemoRecords.

    Bad lines are never dropped silently: each goes to quarantine with the
    line number, a reason, and a prefix of the raw payload for debugging.
    ``seen_ids`` lets incremental runs reject demo_id collisions with
    already-ingested batches.
    """
    seen: Set[str] = set(seen_ids) if seen_ids is not None else set()
    records: List[DemoRecord] = []
    quarantined: List[QuarantinedLine] = []

    for line_no, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if not stripped:
            continue

        def _quarantine(reason: str) -> None:
            quarantined.append(
                QuarantinedLine(
                    source=source,
                    line_no=line_no,
                    reason=reason,
                    raw_prefix=stripped[:120],
                )
            )

        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            _quarantine("malformed_json")
            continue
        if not isinstance(payload, dict):
            _quarantine("not_an_object")
            continue
        try:
            record = DemoRecord.from_dict(payload, config)
        except SchemaError as exc:
            _quarantine(str(exc))
            continue
        if record.demo_id in seen:
            _quarantine("duplicate_demo_id:%s" % record.demo_id)
            continue
        seen.add(record.demo_id)
        records.append(record)

    return records, quarantined


# --------------------------------------------------------------------------
# Stage 2: deduplication
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class DropEntry:
    """Audit trail for one dropped duplicate."""

    demo_id: str
    reason: str  # "exact_duplicate" | "near_duplicate"
    duplicate_of: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "demo_id": self.demo_id,
            "reason": self.reason,
            "duplicate_of": self.duplicate_of,
        }


@dataclass
class DedupResult:
    """Kept records plus updated indices (for incremental state carry-over)."""

    kept: List[DemoRecord]
    dropped: List[DropEntry]
    exact_index: Dict[str, str]  # content hash -> kept demo_id
    bucket_index: Dict[str, str]  # near-dup bucket key -> kept demo_id


def dedup_records(
    records: Sequence[DemoRecord],
    config: PipelineConfig,
    exact_index: Optional[Dict[str, str]] = None,
    bucket_index: Optional[Dict[str, str]] = None,
) -> DedupResult:
    """Stage 2: keep-first exact + near dedup.

    Exact dups (same content hash, only the id differs) are checked before
    near dups so the audit reason is as precise as possible. Passing the
    indices from a previous run makes this stage incremental: new records
    are deduped against everything already kept.
    """
    exact = dict(exact_index) if exact_index is not None else {}
    buckets = dict(bucket_index) if bucket_index is not None else {}
    kept: List[DemoRecord] = []
    dropped: List[DropEntry] = []

    for record in records:
        payload = record.to_dict()
        digest = content_hash(payload)
        if digest in exact:
            dropped.append(DropEntry(record.demo_id, "exact_duplicate", exact[digest]))
            continue
        bucket = near_dup_key(payload, config)
        if bucket in buckets:
            dropped.append(DropEntry(record.demo_id, "near_duplicate", buckets[bucket]))
            continue
        exact[digest] = record.demo_id
        buckets[bucket] = record.demo_id
        kept.append(record)

    return DedupResult(
        kept=kept, dropped=dropped, exact_index=exact, bucket_index=buckets
    )


# --------------------------------------------------------------------------
# Stage 3: quality filtering
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class QualityAssessment:
    """Explainable score: 1.0 minus named penalties, clamped to [0, 1]."""

    demo_id: str
    score: float
    penalties: Tuple[str, ...]

    def to_dict(self) -> Dict[str, object]:
        return {
            "demo_id": self.demo_id,
            "score": self.score,
            "penalties": list(self.penalties),
        }


def assess_quality(record: DemoRecord, config: PipelineConfig) -> QualityAssessment:
    """Score one demo with human-readable penalty reasons.

    Heuristics (all thresholds live in the config, not in code):
      * incomplete demo        -> heavy penalty (label noise for BC)
      * very long pause        -> operator hesitation / distraction
      * high mean jerk         -> shaky teleoperation, poor action targets
      * too many retries       -> demonstrated strategy is unreliable
    """
    score = 1.0
    penalties: List[str] = []

    if not record.completed:
        score -= config.penalty_incomplete
        penalties.append("incomplete(-%.2f)" % config.penalty_incomplete)
    if record.traj.longest_pause_s > config.max_longest_pause_s:
        score -= config.penalty_pause
        penalties.append(
            "longest_pause_s=%.1f>%.1f(-%.2f)"
            % (
                record.traj.longest_pause_s,
                config.max_longest_pause_s,
                config.penalty_pause,
            )
        )
    if record.traj.mean_jerk > config.max_mean_jerk:
        score -= config.penalty_jerk
        penalties.append(
            "mean_jerk=%.1f>%.1f(-%.2f)"
            % (record.traj.mean_jerk, config.max_mean_jerk, config.penalty_jerk)
        )
    if record.traj.num_retries > config.max_retries:
        score -= config.penalty_retries
        penalties.append(
            "num_retries=%d>%d(-%.2f)"
            % (record.traj.num_retries, config.max_retries, config.penalty_retries)
        )

    return QualityAssessment(
        demo_id=record.demo_id,
        score=round(max(score, 0.0), 4),
        penalties=tuple(penalties),
    )


def filter_by_quality(
    records: Sequence[DemoRecord], config: PipelineConfig
) -> Tuple[List[DemoRecord], List[QualityAssessment]]:
    """Stage 3: keep records scoring >= threshold; return rejections with reasons."""
    kept: List[DemoRecord] = []
    rejected: List[QualityAssessment] = []
    for record in records:
        assessment = assess_quality(record, config)
        if assessment.score >= config.quality_threshold:
            kept.append(record)
        else:
            rejected.append(assessment)
    return kept, rejected


# --------------------------------------------------------------------------
# Stage 4: stratified selection + collection requests
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class CollectionRequest:
    """One line of the collection request sheet handed back to teleop ops.

    This is the curation -> collection feedback loop: instead of silently
    shipping an unbalanced training set, the pipeline says exactly which
    cohort is short and what to prioritize next.
    """

    task: str
    have: int
    target: int
    gap: int
    scarcest_lighting: str
    scarcest_room: str
    note: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "task": self.task,
            "have": self.have,
            "target": self.target,
            "gap": self.gap,
            "scarcest_lighting": self.scarcest_lighting,
            "scarcest_room": self.scarcest_room,
            "note": self.note,
        }


@dataclass
class StratifyResult:
    selected: List[DemoRecord]
    requests: List[CollectionRequest]
    per_task_selected: Dict[str, int]
    target_counts: Dict[str, int]


def compute_target_counts(config: PipelineConfig) -> Dict[str, int]:
    """Turn the fractional target mix into integer counts (largest remainder).

    Guarantees ``sum(counts) == train_budget`` with deterministic tie-breaks.
    """
    mix = config.resolved_target_mix()
    total = sum(mix.values())
    if abs(total - 1.0) > 1e-6:
        raise ValueError("target_mix fractions must sum to 1.0, got %.6f" % total)

    exact = {task: config.train_budget * frac for task, frac in mix.items()}
    counts = {task: int(value) for task, value in exact.items()}
    remainder = config.train_budget - sum(counts.values())
    by_fraction = sorted(mix, key=lambda task: (-(exact[task] - counts[task]), task))
    for task in by_fraction[:remainder]:
        counts[task] += 1
    return counts


def _scarcest(records: Sequence[DemoRecord], attr: str, domain: Sequence[str]) -> str:
    """Least represented value of ``scene.<attr>`` (alphabetical tie-break)."""
    counts = {value: 0 for value in domain}
    for record in records:
        value = getattr(record.scene, attr)
        if value in counts:
            counts[value] += 1
    return min(sorted(counts), key=lambda value: counts[value])


def stratify(records: Sequence[DemoRecord], config: PipelineConfig) -> StratifyResult:
    """Stage 4: resample toward the target task mix.

    Surplus tasks: keep the top-``target`` demos by quality score (stable
    tie-break on demo_id). Deficit tasks: keep everything AND emit a
    collection request quantifying the gap plus scene-cohort hints.
    """
    scores = {r.demo_id: assess_quality(r, config).score for r in records}
    by_task: Dict[str, List[DemoRecord]] = defaultdict(list)
    for record in records:
        by_task[record.task].append(record)

    targets = compute_target_counts(config)
    selected: List[DemoRecord] = []
    requests: List[CollectionRequest] = []
    per_task_selected: Dict[str, int] = {}

    for task in sorted(targets):
        candidates = sorted(
            by_task.get(task, []),
            key=lambda r: (-scores[r.demo_id], r.demo_id),
        )
        target = targets[task]
        if len(candidates) >= target:
            chosen = candidates[:target]
        else:
            chosen = candidates
            scarcest_lighting = _scarcest(candidates, "lighting", LIGHTING_LEVELS)
            scarcest_room = _scarcest(candidates, "room", ROOMS)
            if candidates:
                note = "need %d more '%s' demos; prioritize %s lighting in %s" % (
                    target - len(candidates),
                    task,
                    scarcest_lighting,
                    scarcest_room,
                )
            else:
                note = "no usable demos for '%s'; bootstrap collection" % task
            requests.append(
                CollectionRequest(
                    task=task,
                    have=len(candidates),
                    target=target,
                    gap=target - len(candidates),
                    scarcest_lighting=scarcest_lighting,
                    scarcest_room=scarcest_room,
                    note=note,
                )
            )
        selected.extend(chosen)
        per_task_selected[task] = len(chosen)

    requests.sort(key=lambda req: (-req.gap, req.task))
    return StratifyResult(
        selected=selected,
        requests=requests,
        per_task_selected=per_task_selected,
        target_counts=targets,
    )


# --------------------------------------------------------------------------
# One-shot CLI (no manifest/state; see manifest.py for incremental runs)
# --------------------------------------------------------------------------


def _write_json(path: str, obj: object) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main() -> None:
    lab_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="One-shot curation run (no state).")
    parser.add_argument(
        "--data-dir", default=os.path.join(lab_dir, "data"), help="dir with *.jsonl"
    )
    parser.add_argument(
        "--workdir", default=os.path.join(lab_dir, "out_oneshot"), help="output dir"
    )
    parser.add_argument("--budget", type=int, default=420)
    parser.add_argument("--quality-threshold", type=float, default=0.75)
    args = parser.parse_args()

    config = PipelineConfig(
        train_budget=args.budget, quality_threshold=args.quality_threshold
    )
    paths = sorted(glob.glob(os.path.join(args.data_dir, "*.jsonl")))
    if not paths:
        raise SystemExit(
            "no .jsonl files under %s (run generate_demos.py first)" % args.data_dir
        )
    os.makedirs(args.workdir, exist_ok=True)

    all_records: List[DemoRecord] = []
    all_quarantined: List[QuarantinedLine] = []
    seen_ids: Set[str] = set()
    total_lines = 0
    for path in paths:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        total_lines += len(lines)
        records, quarantined = validate_lines(
            lines, config, seen_ids=seen_ids, source=os.path.basename(path)
        )
        seen_ids.update(record.demo_id for record in records)
        all_records.extend(records)
        all_quarantined.extend(quarantined)

    dedup = dedup_records(all_records, config)
    kept_quality, rejected = filter_by_quality(dedup.kept, config)
    strat = stratify(kept_quality, config)

    with open(
        os.path.join(args.workdir, "quarantine.jsonl"), "w", encoding="utf-8"
    ) as handle:
        for entry in all_quarantined:
            handle.write(json.dumps(entry.to_dict(), sort_keys=True) + "\n")
    _write_json(
        os.path.join(args.workdir, "dedup_report.json"),
        [entry.to_dict() for entry in dedup.dropped],
    )
    _write_json(
        os.path.join(args.workdir, "quality_report.json"),
        [entry.to_dict() for entry in rejected],
    )
    _write_json(
        os.path.join(args.workdir, "collection_requests.json"),
        [request.to_dict() for request in strat.requests],
    )
    with open(
        os.path.join(args.workdir, "train_set.jsonl"), "w", encoding="utf-8"
    ) as handle:
        for record in sorted(strat.selected, key=lambda r: r.demo_id):
            handle.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")

    counts = {
        "input_lines": total_lines,
        "quarantined": len(all_quarantined),
        "validated": len(all_records),
        "dropped_exact": sum(1 for d in dedup.dropped if d.reason == "exact_duplicate"),
        "dropped_near": sum(1 for d in dedup.dropped if d.reason == "near_duplicate"),
        "after_dedup": len(dedup.kept),
        "rejected_quality": len(rejected),
        "after_quality": len(kept_quality),
        "selected": len(strat.selected),
    }
    _write_json(os.path.join(args.workdir, "stage_counts.json"), counts)

    print("stage funnel:")
    for key in [
        "input_lines",
        "quarantined",
        "validated",
        "dropped_exact",
        "dropped_near",
        "after_dedup",
        "rejected_quality",
        "after_quality",
        "selected",
    ]:
        print("  %-18s %d" % (key, counts[key]))
    print("collection requests (%d):" % len(strat.requests))
    for request in strat.requests:
        print(
            "  %-16s have=%-4d target=%-4d gap=%-4d %s"
            % (request.task, request.have, request.target, request.gap, request.note)
        )
    print("outputs -> %s" % args.workdir)


if __name__ == "__main__":
    main()
```




## test_pipeline.py

```python
#!/usr/bin/env python3
"""Tests for lab3_data_engine (plain assert, no pytest).

Run:  /usr/bin/python3 test_pipeline.py

Covers: generator determinism, per-stage counts, dedup correctness,
quality filtering, stratification + collection requests, manifest
reproducibility, incremental idempotency, and lineage.
"""

import json
import os
import shutil
import tempfile
from typing import Dict, List, Set, Tuple

import generate_demos as gen
import manifest as mf
import pipeline as pl

CONFIG = pl.PipelineConfig()


# --------------------------------------------------------------------------
# Fixtures (generated once, deterministic)
# --------------------------------------------------------------------------


def build_fixtures() -> Tuple[
    List[str], gen.GenerationSummary, List[str], gen.GenerationSummary
]:
    lines1, summary1 = gen.generate_batch(gen.BATCH1, config=CONFIG)
    cross_sources = gen.eligible_cross_sources(lines1, summary1, CONFIG)
    lines2, summary2 = gen.generate_batch(
        gen.BATCH2, cross_sources=cross_sources, config=CONFIG
    )
    return lines1, summary1, lines2, summary2


LINES1, SUMMARY1, LINES2, SUMMARY2 = build_fixtures()


def write_data_dir(
    base: str, batches: List[Tuple[List[str], gen.GenerationSummary]]
) -> str:
    data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)
    for lines, summary in batches:
        path = os.path.join(data_dir, "demos_batch%d.jsonl" % summary.batch)
        gen.write_batch(lines, summary, path)
    return data_dir


# --------------------------------------------------------------------------
# Generator
# --------------------------------------------------------------------------


def test_generator_deterministic() -> None:
    lines_a, summary_a = gen.generate_batch(gen.BATCH1, config=CONFIG)
    lines_b, summary_b = gen.generate_batch(gen.BATCH1, config=CONFIG)
    assert lines_a == lines_b, "same spec+seed must produce identical bytes"
    assert summary_a.to_dict() == summary_b.to_dict()
    assert summary_a.total_lines == 807, summary_a.total_lines  # ~800 by design
    assert len(summary_a.schema_bad_lines) == gen.BATCH1.n_schema_bad
    assert len(summary_a.exact_dup_ids) == gen.BATCH1.n_exact_dups
    assert len(summary_a.near_dup_ids) == gen.BATCH1.n_near_dups
    assert len(summary_a.bad_quality_ids) == gen.BATCH1.n_bad_quality


# --------------------------------------------------------------------------
# Stage 1: schema validation
# --------------------------------------------------------------------------


def test_stage1_schema_validation() -> None:
    records, quarantined = pl.validate_lines(LINES1, CONFIG, source="b1")
    assert len(quarantined) == gen.BATCH1.n_schema_bad, len(quarantined)
    assert len(records) == SUMMARY1.n_schema_valid, len(records)
    assert len(records) + len(quarantined) == SUMMARY1.total_lines

    # Quarantine points at exactly the injected bad line numbers, with reasons.
    assert sorted(entry.line_no for entry in quarantined) == SUMMARY1.schema_bad_lines
    reasons = {entry.reason for entry in quarantined}
    assert "malformed_json" in reasons, reasons
    assert "missing_field:task" in reasons, reasons
    assert "bad_type:duration_s" in reasons, reasons
    assert "out_of_range:duration_s" in reasons, reasons
    assert "unknown_task:juggle_chainsaws" in reasons, reasons
    assert "missing_field:operator_id" in reasons, reasons  # null operator
    for entry in quarantined:
        assert entry.reason and entry.raw_prefix and entry.source == "b1"

    # demo_id collision with an already-seen batch is quarantined, not merged.
    dup_line = json.dumps(records[0].to_dict(), sort_keys=True)
    more, quar = pl.validate_lines(
        [dup_line], CONFIG, seen_ids={records[0].demo_id}, source="b1_again"
    )
    assert not more and len(quar) == 1
    assert quar[0].reason.startswith("duplicate_demo_id:")


# --------------------------------------------------------------------------
# Stage 2: dedup
# --------------------------------------------------------------------------


def _validated_batch1() -> List[pl.DemoRecord]:
    records, _ = pl.validate_lines(LINES1, CONFIG)
    return records


def test_stage2_dedup() -> None:
    records = _validated_batch1()
    result = pl.dedup_records(records, CONFIG)

    assert len(result.kept) + len(result.dropped) == len(records)

    dropped_by_reason: Dict[str, Set[str]] = {
        "exact_duplicate": set(),
        "near_duplicate": set(),
    }
    for entry in result.dropped:
        dropped_by_reason[entry.reason].add(entry.demo_id)
        assert entry.duplicate_of, "every drop must name its kept twin"
        assert entry.duplicate_of != entry.demo_id

    # Every injected duplicate is caught, with the right reason.
    assert set(SUMMARY1.exact_dup_ids) <= dropped_by_reason["exact_duplicate"]
    assert set(SUMMARY1.near_dup_ids) <= dropped_by_reason["near_duplicate"]

    # Survivors are unique under both identity definitions.
    hashes = [pl.content_hash(r.to_dict()) for r in result.kept]
    buckets = [pl.near_dup_key(r.to_dict(), CONFIG) for r in result.kept]
    assert len(set(hashes)) == len(hashes), "exact dup survived"
    assert len(set(buckets)) == len(buckets), "near dup survived"

    # duplicate_of must reference a surviving record.
    kept_ids = {record.demo_id for record in result.kept}
    for entry in result.dropped:
        assert entry.duplicate_of in kept_ids, entry

    # Incremental form: feeding the same records against the returned indices
    # drops everything as exact duplicates.
    again = pl.dedup_records(
        result.kept, CONFIG, result.exact_index, result.bucket_index
    )
    assert not again.kept
    assert all(entry.reason == "exact_duplicate" for entry in again.dropped)


# --------------------------------------------------------------------------
# Stage 3: quality
# --------------------------------------------------------------------------


def test_stage3_quality_filter() -> None:
    records = _validated_batch1()
    dedup = pl.dedup_records(records, CONFIG)
    kept, rejected = pl.filter_by_quality(dedup.kept, CONFIG)

    assert len(kept) + len(rejected) == len(dedup.kept)
    rejected_ids = {assessment.demo_id for assessment in rejected}
    survivor_ids = {record.demo_id for record in dedup.kept}

    # Exactly the injected bad-quality demos (that survived dedup) fail.
    assert rejected_ids == set(SUMMARY1.bad_quality_ids) & survivor_ids

    for assessment in rejected:
        assert assessment.penalties, "rejections must be explainable"
        assert assessment.score < CONFIG.quality_threshold
    for record in kept:
        assert pl.assess_quality(record, CONFIG).score >= CONFIG.quality_threshold

    # Each defect mode produces its named penalty.
    all_penalties = ";".join(";".join(a.penalties) for a in rejected)
    assert "incomplete" in all_penalties
    assert "longest_pause_s=" in all_penalties
    assert "mean_jerk=" in all_penalties

    # Threshold is a config knob: raising it to 1.0 must not reject clean demos
    # (clean generator output scores exactly 1.0).
    strict = pl.PipelineConfig(quality_threshold=1.0)
    strict_kept, strict_rejected = pl.filter_by_quality(dedup.kept, strict)
    assert {a.demo_id for a in strict_rejected} == rejected_ids
    assert len(strict_kept) == len(kept)


# --------------------------------------------------------------------------
# Stage 4: stratification + collection requests
# --------------------------------------------------------------------------


def test_stage4_stratify_and_requests() -> None:
    records = _validated_batch1()
    dedup = pl.dedup_records(records, CONFIG)
    kept, _ = pl.filter_by_quality(dedup.kept, CONFIG)
    result = pl.stratify(kept, CONFIG)

    targets = pl.compute_target_counts(CONFIG)
    assert sum(targets.values()) == CONFIG.train_budget

    have: Dict[str, int] = {task: 0 for task in CONFIG.known_tasks}
    for record in kept:
        have[record.task] += 1

    selected_by_task: Dict[str, int] = {task: 0 for task in CONFIG.known_tasks}
    for record in result.selected:
        selected_by_task[record.task] += 1

    requested_tasks = {request.task for request in result.requests}
    for task in CONFIG.known_tasks:
        expected = min(have[task], targets[task])
        assert selected_by_task[task] == expected, (
            task,
            selected_by_task[task],
            expected,
        )
        if have[task] < targets[task]:
            assert task in requested_tasks, "deficit task %s missing a request" % task
        else:
            assert task not in requested_tasks, "surplus task %s got a request" % task

    # The imbalanced generator guarantees both surpluses and deficits.
    assert result.requests, "expected at least one collection request"
    assert any(have[task] > targets[task] for task in CONFIG.known_tasks)

    # Requests quantify the correct gap and point at the scarcest cohort.
    for request in result.requests:
        assert request.gap == targets[request.task] - have[request.task]
        assert request.gap > 0
        cohort = [r for r in kept if r.task == request.task]
        lighting_counts = {level: 0 for level in pl.LIGHTING_LEVELS}
        for record in cohort:
            lighting_counts[record.scene.lighting] += 1
        assert lighting_counts[request.scarcest_lighting] == min(
            lighting_counts.values()
        )
        assert request.task in request.note

    # Requests are sorted most-urgent first.
    gaps = [request.gap for request in result.requests]
    assert gaps == sorted(gaps, reverse=True)

    # Surplus tasks keep their highest-quality demos (all clean here => 1.0),
    # and no selected demo is below threshold.
    for record in result.selected:
        assert pl.assess_quality(record, CONFIG).score >= CONFIG.quality_threshold


# --------------------------------------------------------------------------
# Manifest: reproducibility, incremental runs, lineage
# --------------------------------------------------------------------------


def test_manifest_reproducible_across_workdirs() -> None:
    base = tempfile.mkdtemp(prefix="lab3_repro_")
    try:
        data_dir = write_data_dir(base, [(LINES1, SUMMARY1)])
        paths = [os.path.join(data_dir, "demos_batch1.jsonl")]
        result_a = mf.run_incremental(paths, CONFIG, os.path.join(base, "wd_a"))
        result_b = mf.run_incremental(paths, CONFIG, os.path.join(base, "wd_b"))
        assert result_a.manifest_id == result_b.manifest_id
        assert result_a.manifest["record_ids"] == result_b.manifest["record_ids"]
        # The id really is the content address of the sorted ids.
        recomputed = mf.compute_manifest_id(result_a.manifest["record_ids"])
        assert recomputed == result_a.manifest_id
        assert os.path.exists(result_a.manifest_path)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_incremental_runs_and_lineage() -> None:
    base = tempfile.mkdtemp(prefix="lab3_incr_")
    try:
        data_dir = write_data_dir(base, [(LINES1, SUMMARY1), (LINES2, SUMMARY2)])
        path1 = os.path.join(data_dir, "demos_batch1.jsonl")
        path2 = os.path.join(data_dir, "demos_batch2.jsonl")
        workdir = os.path.join(base, "wd")

        # Run 1: batch 1 only.
        run1 = mf.run_incremental([path1], CONFIG, workdir)
        assert run1.new_files == ["demos_batch1.jsonl"]
        assert run1.manifest["lineage"]["parent_manifest_id"] is None
        assert run1.run_counts["input_lines"] == SUMMARY1.total_lines

        # Run 2: both batches -> only batch 2 is processed.
        run2 = mf.run_incremental([path1, path2], CONFIG, workdir)
        assert run2.new_files == ["demos_batch2.jsonl"], run2.new_files
        assert run2.run_counts["input_lines"] == SUMMARY2.total_lines
        assert run2.run_counts["quarantined"] == gen.BATCH2.n_schema_bad
        assert not run2.noop
        assert run2.manifest["lineage"]["parent_manifest_id"] == run1.manifest_id
        assert run2.manifest_id != run1.manifest_id

        # Cross-batch exact dups were caught against run-1 state.
        with open(os.path.join(workdir, "dedup_report.json"), "r") as handle:
            drops2 = json.load(handle)
        drops2_by_id = {entry["demo_id"]: entry for entry in drops2}
        for cross_id in SUMMARY2.cross_dup_ids:
            entry = drops2_by_id[cross_id]
            assert entry["reason"] == "exact_duplicate", entry
            assert entry["duplicate_of"].startswith("d1_"), entry

        # Run 3: same inputs again -> idempotent no-op.
        run3 = mf.run_incremental([path1, path2], CONFIG, workdir)
        assert run3.noop
        assert run3.new_files == []
        assert run3.manifest_id == run2.manifest_id
        assert run3.run_counts["input_lines"] == 0

        # Full rebuild in a fresh workdir reproduces the incremental manifest.
        rebuild = mf.run_incremental(
            [path1, path2], CONFIG, os.path.join(base, "wd_full")
        )
        assert rebuild.manifest_id == run2.manifest_id
        assert rebuild.manifest["record_ids"] == run2.manifest["record_ids"]

        # Lineage carries the config snapshot and hashed inputs.
        lineage = run2.manifest["lineage"]
        assert lineage["pipeline_config"] == CONFIG.to_dict()
        assert [entry["name"] for entry in lineage["inputs"]] == [
            "demos_batch1.jsonl",
            "demos_batch2.jsonl",
        ]
        for entry in lineage["inputs"]:
            assert len(entry["sha256"]) == 64

        # Guardrails: mutated input and config drift are hard errors.
        with open(path2, "a", encoding="utf-8") as handle:
            handle.write("\n")
        try:
            mf.run_incremental([path1, path2], CONFIG, workdir)
            raise AssertionError("mutated input file must be rejected")
        except ValueError as exc:
            assert "immutable" in str(exc)
        try:
            mf.run_incremental([path1], pl.PipelineConfig(train_budget=999), workdir)
            raise AssertionError("config drift must be rejected")
        except ValueError as exc:
            assert "config drift" in str(exc)

        # Train set on disk matches the manifest exactly.
        with open(os.path.join(workdir, "train_set.jsonl"), "r") as handle:
            train_ids = [json.loads(line)["demo_id"] for line in handle if line.strip()]
        assert train_ids == run2.manifest["record_ids"]
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_collection_requests_in_manifest() -> None:
    base = tempfile.mkdtemp(prefix="lab3_req_")
    try:
        data_dir = write_data_dir(base, [(LINES1, SUMMARY1)])
        paths = [os.path.join(data_dir, "demos_batch1.jsonl")]
        result = mf.run_incremental(paths, CONFIG, os.path.join(base, "wd"))
        requests = result.manifest["collection_requests"]
        assert requests, "imbalanced batch 1 must yield collection requests"
        per_task = result.manifest["per_task_selected"]
        targets = result.manifest["target_counts"]
        for request in requests:
            # The request points at a genuinely under-filled cohort.
            assert per_task[request["task"]] < targets[request["task"]]
            assert request["have"] + request["gap"] == request["target"]
        # And no non-requested task is under target.
        requested = {request["task"] for request in requests}
        for task, count in per_task.items():
            if task not in requested:
                assert count == targets[task], (task, count)
    finally:
        shutil.rmtree(base, ignore_errors=True)


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------


def run_all() -> None:
    tests = [
        test_generator_deterministic,
        test_stage1_schema_validation,
        test_stage2_dedup,
        test_stage3_quality_filter,
        test_stage4_stratify_and_requests,
        test_manifest_reproducible_across_workdirs,
        test_incremental_runs_and_lineage,
        test_collection_requests_in_manifest,
    ]
    for test in tests:
        test()
        print("PASS %s" % test.__name__)
    print("all %d tests passed" % len(tests))


if __name__ == "__main__":
    run_all()
```

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/labs/lab3_data_engine/README.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/labs/lab3_data_engine/README.md)。作者整理资料；许可和第三方来源范围见阅读指南。
