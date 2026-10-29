---
id: drustz-932edff76fa617727e
section: labs
order: 3
level: A
title: lab1_fleet_triage — 「一批 bot 不 work 了」fleet 数据排查实战
quick: 作者完整文档 · lab1_fleet_triage — 「一批 bot 不 work 了」fleet 数据排查实战
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/labs/lab1_fleet_triage/README.md
    type: primary
---
# lab1_fleet_triage — 「一批 bot 不 work 了」fleet 数据排查实战

## 对应什么考点

The Bot Company 面试点名的 **debug + 数据分析题**（见 `../../05_debug_playbook.md` 的
cohort 决策表、`../../02_interview_rounds_intel.md` 的 practical 情景 B）。典型题面：
"10k 台家用机器人，客服报告一批 bot 成功率掉了，你怎么查？"这个 lab 把那道口头题
变成了可以真手跑的数据：5,000 条 episode telemetry 里埋了三个分层 root cause——

- **(a) OOD cohort 回归**：model v2.4 只在 `carpet x dim` 交集上大跌（OTA 引入的out-of-distribution回归）；
- **(b) 单机硬件故障**：一台机器人 `grip_current` 逐日漂移，pick/place 连续失败；
- **(c) 红鲱鱼**：一个 home 集中在晚上（dim）+ 满屋地毯 + 早升级，raw 成功率最差，
  但控制变量后差距消失——练"相关 != 因果"的标准反驳。

练的正是面试官要看的完整链路：**整体 → 切片 → 交叉 → 对齐 OTA 时间线 → 个体
z-score → 控制混淆变量**，以及"一台坏 vs 一批坏"的分叉判断。

## 15–30 分钟熟悉路径（先跑什么再读什么）

解释器固定用 `/Users/mingrui/Documents/codes/interview/.venv/bin/python`
（Python 3.9.6，numpy 2.0.2；本 lab 只用 numpy + 标准库，无 pandas、无网络）。

```bash
cd /Users/mingrui/Documents/codes/interview/my_interview_prep/ml_sys_prep/bot_company/labs/lab1_fleet_triage
PY=/Users/mingrui/Documents/codes/interview/.venv/bin/python

# 1. (1 min) 生成数据
$PY generate_logs.py

# 2. (10-15 min) 打开 EXERCISE.md，按三问自己挖（别看任何 .py 源码，生成器里有答案）
#    建议开 $PY -i，用 json + collections.Counter 徒手切片

# 3. (2 min) 跑参考解法对答案，读六步报告 + 末尾 [verify]
$PY triage.py

# 4. (5-10 min) 读 triage.py：六个分析函数就是可复用的面试口头模板
#    (slice_by / crosstab / before_after_upgrade / robot_success_zscores /
#     grip_current_slopes / raw_and_adjusted_gap)

# 5. (1 min) 全绿确认
$PY test_triage.py
```



测试命令（plain assert，无 pytest，全程 < 60 秒）：

```bash
/Users/mingrui/Documents/codes/interview/.venv/bin/python test_triage.py
```



## 文件说明

| 文件 | 作用 |
|---|---|
| `generate_logs.py` | 确定性 telemetry 模拟器（固定种子，同 seed 字节级一致）；**含答案，先别读** |
| `data/episodes.jsonl` | 5,000 条 episode（200 台机器人 x 25 条，14 天窗口） |
| `EXERCISE.md` | 任务书：三问 + L1/L2/L3 提示阶梯 |
| `triage.py` | 参考解法 = 可复用 cohort 分析工具，结论用 assert 钉死 |
| `test_triage.py` | 测试：确定性、schema、a/b 可检出、红鲱鱼被排除、端到端 |

## 面试中怎么引用这段经验（英文一句话）

> "To pressure-test my fleet-debug workflow I built a synthetic triage drill:
> 5,000 episodes with a planted OOD regression (v2.4 only fails on carpet in
> dim light), one robot with drifting grip current, and a confounded
> 'bad home' red herring — and my cohort-analysis script isolates all three:
> aggregate first, slice, cross dimensions, align with the OTA timeline,
> z-score individual robots, and stratify before blaming a correlated
> dimension."

## generate_logs.py

```python
#!/usr/bin/env python3
"""Deterministic fleet-telemetry simulator for lab1_fleet_triage.

Generates episode-level telemetry for a simulated fleet of ~200 home robots
over a 14-day window and writes it as JSONL (one episode per line) to
``data/episodes.jsonl``.

Planted ground truth (SPOILERS -- candidates should run this script but not
read it before finishing EXERCISE.md):

  (a) Cohort regression: model ``v2.4`` fails hard on episodes where
      ``floor_type == "carpet"`` and ``lighting == "dim"`` (an
      out-of-distribution perception regression shipped via OTA).
  (b) Hardware fault: one specific robot's ``grip_current`` drifts upward
      day over day; once it crosses ``GRIP_FAULT_THRESHOLD_A`` its
      pick/place episodes fail almost every time.
  (c) Red herring: one home runs most of its episodes in the evening (dim
      lighting) on wall-to-wall carpet and was upgraded to v2.4 early, so
      its *raw* success rate looks terrible -- but the home itself has no
      causal effect. Controlling for (model_version, floor_type, lighting)
      makes the gap disappear.

Schema of each JSONL record (all keys always present):
    robot_id          str   e.g. "RB-042"
    fw_version        str   firmware, non-causal distractor ("5.1.0"/"5.2.0")
    model_version     str   policy model, "v2.3" or "v2.4" (per-robot OTA)
    task_type         str   pick | place | navigate | wipe | dock
    home_id           str   e.g. "home_003"
    floor_type        str   hardwood | carpet | tile
    lighting          str   bright | dim
    battery_pct       int   15..100
    cpu_temp          float degrees C
    grip_current      float amps (meaningful for pick/place, idle otherwise)
    policy_latency_ms float per-step policy latency
    success           bool  episode outcome
    error_code        str or null (null on success)
    ts                str   ISO-8601 UTC, e.g. "2026-07-24T19:41:00Z"

Determinism: a single ``random.Random(seed)`` instance drives all sampling
in a fixed iteration order, so identical seeds produce byte-identical files.

Usage:
    python generate_logs.py [--out PATH] [--seed N]
"""

import argparse
import json
import random
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Fleet / simulation constants
# ---------------------------------------------------------------------------

DEFAULT_SEED = 20260810
DEFAULT_OUT = Path(__file__).resolve().parent / "data" / "episodes.jsonl"

N_ROBOTS = 200
EPISODES_PER_ROBOT = 25  # 200 * 25 = 5000 episodes total
N_DAYS = 14
START_DATE = date(2026, 7, 20)

TASK_TYPES = ["pick", "place", "navigate", "wipe", "dock"]
TASK_WEIGHTS = [0.30, 0.20, 0.20, 0.15, 0.15]
GRIP_TASKS = ("pick", "place")  # tasks where the gripper is load-bearing

FLOOR_TYPES = ["hardwood", "carpet", "tile"]
FLOOR_WEIGHTS_NORMAL = [0.40, 0.33, 0.27]
FLOOR_WEIGHTS_RED_HERRING = [0.20, 0.65, 0.15]

FW_VERSIONS = ["5.1.0", "5.2.0"]

# --- Ground truth for the three planted root causes (used by tests) --------

REGRESSED_MODEL_VERSION = "v2.4"
REGRESSED_FLOOR_TYPE = "carpet"
REGRESSED_LIGHTING = "dim"
COHORT_REGRESSION_SUCCESS_P = 0.25  # success prob inside the broken cohort

BAD_ROBOT_ID = "RB-042"  # the hardware-fault robot
GRIP_DRIFT_A_PER_DAY = 0.13  # amps of upward drift per day
GRIP_FAULT_THRESHOLD_A = 1.80  # above this, grasps slip
GRIP_FAULT_SUCCESS_P = 0.05

RED_HERRING_HOME_ID = "home_003"  # evening-heavy, carpeted, early OTA

BASE_SUCCESS_P = 0.92
OTA_DAY_RANGE = (5, 8)  # upgraded robots flip to v2.4 in here
UPGRADE_FRACTION = 0.60


@dataclass(frozen=True)
class RobotProfile:
    """Static per-robot attributes fixed at fleet-construction time."""

    robot_id: str
    home_id: str
    fw_version: str
    ota_day: Optional[int]  # day index the robot switched to v2.4; None = never
    grip_faulty: bool


# ---------------------------------------------------------------------------
# Fleet construction
# ---------------------------------------------------------------------------


def build_fleet(rng: random.Random) -> List[RobotProfile]:
    """Create the 200-robot fleet with home assignments and OTA schedule.

    Layout: homes 000..005 are "large" homes with 4 robots each (indices
    0..23); the remaining 176 robots live in 2-robot homes (006..093).
    home_003 is the red-herring home (robots RB-012..RB-015).
    """
    robots: List[RobotProfile] = []
    for idx in range(N_ROBOTS):
        robot_id = "RB-{:03d}".format(idx)
        if idx < 24:
            home_id = "home_{:03d}".format(idx // 4)
        else:
            home_id = "home_{:03d}".format(6 + (idx - 24) // 2)

        fw_version = rng.choice(FW_VERSIONS)

        # OTA schedule. The draw below happens for every robot so that the
        # RNG stream (and therefore the whole dataset) is stable even when
        # the special-case robots override the result.
        upgraded = rng.random() < UPGRADE_FRACTION
        ota_day_draw = rng.randint(*OTA_DAY_RANGE)
        ota_day: Optional[int] = ota_day_draw if upgraded else None

        if home_id == RED_HERRING_HOME_ID:
            ota_day = OTA_DAY_RANGE[0]  # early adopter home
        if robot_id == BAD_ROBOT_ID:
            ota_day = None  # keep causes cleanly separable

        robots.append(
            RobotProfile(
                robot_id=robot_id,
                home_id=home_id,
                fw_version=fw_version,
                ota_day=ota_day,
                grip_faulty=(robot_id == BAD_ROBOT_ID),
            )
        )
    return robots


# ---------------------------------------------------------------------------
# Episode simulation
# ---------------------------------------------------------------------------


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _sample_context(rng: random.Random, robot: RobotProfile) -> Dict[str, object]:
    """Sample the environmental context (when/where) for one episode."""
    day = rng.randint(0, N_DAYS - 1)

    if robot.home_id == RED_HERRING_HOME_ID:
        # This household mostly runs the robot after dinner, on carpet.
        hour = rng.randint(19, 23) if rng.random() < 0.85 else rng.randint(9, 17)
        floor_type = rng.choices(FLOOR_TYPES, weights=FLOOR_WEIGHTS_RED_HERRING, k=1)[0]
    else:
        hour = rng.randint(8, 22)
        floor_type = rng.choices(FLOOR_TYPES, weights=FLOOR_WEIGHTS_NORMAL, k=1)[0]

    # Lighting is driven by time of day -- this is what makes the
    # "home_003 is broken" correlation spurious rather than causal.
    p_dim = 0.85 if hour >= 19 else 0.08
    lighting = "dim" if rng.random() < p_dim else "bright"

    return {"day": day, "hour": hour, "floor_type": floor_type, "lighting": lighting}


def _pick_error_code(rng: random.Random, cause: str) -> str:
    """Sample an error code consistent with the failure cause."""
    if cause == "grip_fault":
        return rng.choices(["GRIP_SLIP", "GRIP_STALL"], weights=[0.8, 0.2], k=1)[0]
    if cause == "cohort_regression":
        return rng.choices(
            ["VISION_MISDETECT", "GRASP_PLAN_FAIL", "TIMEOUT"],
            weights=[0.55, 0.30, 0.15],
            k=1,
        )[0]
    return rng.choices(
        ["TIMEOUT", "NAV_STUCK", "PLAN_FAIL", "E_STOP", "LOW_BATTERY"],
        weights=[0.35, 0.25, 0.20, 0.10, 0.10],
        k=1,
    )[0]


def simulate_episode(rng: random.Random, robot: RobotProfile) -> Dict[str, object]:
    """Simulate one episode for ``robot`` and return the telemetry record."""
    ctx = _sample_context(rng, robot)
    day: int = ctx["day"]  # type: ignore[assignment]

    model_version = (
        REGRESSED_MODEL_VERSION
        if robot.ota_day is not None and day >= robot.ota_day
        else "v2.3"
    )
    task_type = rng.choices(TASK_TYPES, weights=TASK_WEIGHTS, k=1)[0]
    battery_pct = rng.randint(15, 100)
    cpu_temp = round(_clamp(rng.gauss(54.0, 5.0), 38.0, 85.0), 1)

    if task_type in GRIP_TASKS:
        if robot.grip_faulty:
            grip_current = 1.20 + GRIP_DRIFT_A_PER_DAY * day + rng.gauss(0.0, 0.05)
        else:
            grip_current = rng.gauss(1.20, 0.07)
    else:
        grip_current = rng.gauss(0.30, 0.05)
    grip_current = round(max(0.05, grip_current), 3)

    if model_version == REGRESSED_MODEL_VERSION:
        policy_latency_ms = round(max(25.0, rng.gauss(88.0, 14.0)), 1)
    else:
        policy_latency_ms = round(max(25.0, rng.gauss(75.0, 12.0)), 1)

    # --- Success model -----------------------------------------------------
    p = BASE_SUCCESS_P
    if ctx["lighting"] == "dim":
        p -= 0.03
    if ctx["floor_type"] == "carpet":
        p -= 0.02
    if battery_pct < 20:
        p -= 0.08

    cause = "nominal"
    if (
        model_version == REGRESSED_MODEL_VERSION
        and ctx["floor_type"] == REGRESSED_FLOOR_TYPE
        and ctx["lighting"] == REGRESSED_LIGHTING
    ):
        p = COHORT_REGRESSION_SUCCESS_P
        cause = "cohort_regression"
    if (
        robot.grip_faulty
        and task_type in GRIP_TASKS
        and grip_current > GRIP_FAULT_THRESHOLD_A
    ):
        p = GRIP_FAULT_SUCCESS_P
        cause = "grip_fault"

    success = rng.random() < _clamp(p, 0.01, 0.99)
    error_code: Optional[str] = None if success else _pick_error_code(rng, cause)

    ts = "{d}T{h:02d}:{m:02d}:00Z".format(
        d=(START_DATE + timedelta(days=day)).isoformat(),
        h=ctx["hour"],
        m=rng.randint(0, 59),
    )

    return {
        "robot_id": robot.robot_id,
        "fw_version": robot.fw_version,
        "model_version": model_version,
        "task_type": task_type,
        "home_id": robot.home_id,
        "floor_type": ctx["floor_type"],
        "lighting": ctx["lighting"],
        "battery_pct": battery_pct,
        "cpu_temp": cpu_temp,
        "grip_current": grip_current,
        "policy_latency_ms": policy_latency_ms,
        "success": success,
        "error_code": error_code,
        "ts": ts,
    }


def generate_episodes(seed: int = DEFAULT_SEED) -> List[Dict[str, object]]:
    """Generate the full dataset, sorted by timestamp then robot_id."""
    rng = random.Random(seed)
    fleet = build_fleet(rng)
    records: List[Dict[str, object]] = []
    for robot in fleet:
        for _ in range(EPISODES_PER_ROBOT):
            records.append(simulate_episode(rng, robot))
    records.sort(key=lambda r: (r["ts"], r["robot_id"]))
    return records


def write_jsonl(records: List[Dict[str, object]], path: Path) -> None:
    """Write records as JSONL, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, separators=(", ", ": ")) + "\n")


def summarize(records: List[Dict[str, object]]) -> str:
    """One-paragraph, spoiler-free summary for the console."""
    n = len(records)
    robots = {str(r["robot_id"]) for r in records}
    homes = {str(r["home_id"]) for r in records}
    ok = sum(1 for r in records if r["success"])
    return (
        "wrote {n} episodes | {nr} robots | {nh} homes | "
        "{d0}..{d1} | overall success {sr:.1%}".format(
            n=n,
            nr=len(robots),
            nh=len(homes),
            d0=str(records[0]["ts"])[:10],
            d1=str(records[-1]["ts"])[:10],
            sr=ok / n,
        )
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate fleet telemetry JSONL.")
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="output JSONL path (default: data/episodes.jsonl)",
    )
    parser.add_argument(
        "--seed", type=int, default=DEFAULT_SEED, help="RNG seed (default: %(default)s)"
    )
    args = parser.parse_args(argv)

    records = generate_episodes(seed=args.seed)
    write_jsonl(records, args.out)
    print("[generate_logs] " + summarize(records))
    print("[generate_logs] output: {}".format(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```




## test_triage.py

```python
#!/usr/bin/env python3
"""Plain-assert test suite for lab1_fleet_triage (no pytest).

Run:
    python test_triage.py

Covers:
    - deterministic generation (same seed -> byte-identical JSONL)
    - schema / shape of the generated dataset
    - root cause (a): v2.4 x carpet x dim cohort regression is detectable
    - root cause (b): the grip-drift robot is detectable by two signals
    - red herring (c): the "bad home" correlation collapses under control
    - end-to-end: triage report runs and its own asserts pass
"""

import hashlib
import sys
import tempfile
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB_DIR))

import generate_logs as gl  # noqa: E402
import triage  # noqa: E402


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _generate_dataset(tmp_dir: Path) -> Path:
    """Generate the canonical dataset into tmp_dir and return its path."""
    out = tmp_dir / "episodes.jsonl"
    gl.write_jsonl(gl.generate_episodes(seed=gl.DEFAULT_SEED), out)
    return out


def test_determinism(tmp_dir: Path) -> None:
    a, b = tmp_dir / "run_a.jsonl", tmp_dir / "run_b.jsonl"
    gl.write_jsonl(gl.generate_episodes(seed=gl.DEFAULT_SEED), a)
    gl.write_jsonl(gl.generate_episodes(seed=gl.DEFAULT_SEED), b)
    assert _sha256(a) == _sha256(b), "same seed must produce byte-identical output"

    c = tmp_dir / "run_c.jsonl"
    gl.write_jsonl(gl.generate_episodes(seed=gl.DEFAULT_SEED + 1), c)
    assert _sha256(a) != _sha256(c), "different seeds should differ"


def test_schema_and_shape(data_path: Path) -> None:
    episodes = triage.load_episodes(data_path)  # load_episodes validates schema
    assert len(episodes) == gl.N_ROBOTS * gl.EPISODES_PER_ROBOT, (
        "expected {} episodes, got {}".format(
            gl.N_ROBOTS * gl.EPISODES_PER_ROBOT, len(episodes)
        )
    )

    robots = {e.robot_id for e in episodes}
    assert len(robots) == gl.N_ROBOTS, "expected {} robots".format(gl.N_ROBOTS)

    assert {e.model_version for e in episodes} == {"v2.3", "v2.4"}
    assert {e.lighting for e in episodes} == {"bright", "dim"}
    assert {e.floor_type for e in episodes} == set(gl.FLOOR_TYPES)
    assert {e.task_type for e in episodes} == set(gl.TASK_TYPES)
    for ep in episodes:
        assert 0 <= ep.battery_pct <= 100, "battery_pct out of range"
        assert ep.grip_current > 0.0, "grip_current must be positive"
        assert ep.success or ep.error_code is not None, (
            "failed episodes must carry an error_code"
        )
        assert not (ep.success and ep.error_code is not None), (
            "successful episodes must not carry an error_code"
        )

    # Timestamps span the configured window.
    days = {e.ts.date() for e in episodes}
    assert len(days) == gl.N_DAYS, "expected {} distinct days".format(gl.N_DAYS)


def test_cohort_regression_detected(data_path: Path) -> None:
    episodes = triage.load_episodes(data_path)
    v24 = [e for e in episodes if e.model_version == gl.REGRESSED_MODEL_VERSION]
    v23 = [e for e in episodes if e.model_version == "v2.3"]

    tab24 = triage.crosstab(v24, lambda e: e.floor_type, lambda e: e.lighting)
    tab23 = triage.crosstab(v23, lambda e: e.floor_type, lambda e: e.lighting)

    cell, stat = triage.worst_cell(tab24, min_n=40)
    assert cell == (gl.REGRESSED_FLOOR_TYPE, gl.REGRESSED_LIGHTING), (
        "worst v2.4 cell should be (carpet, dim), got {}".format(cell)
    )
    assert stat.n >= 80, "broken cohort needs decent support, got n={}".format(stat.n)
    assert stat.rate < 0.45, "broken cohort rate {:.1%} not low enough".format(
        stat.rate
    )
    assert tab23[cell].rate > 0.75, "same cohort must be healthy on v2.3"
    for other, other_stat in tab24.items():
        if other != cell and other_stat.n >= 40:
            assert other_stat.rate > 0.75, (
                "v2.4 cell {} should be healthy, got {:.1%}".format(
                    other, other_stat.rate
                )
            )

    # OTA alignment: the same robots were fine on this cohort before upgrade.
    before, after = triage.before_after_upgrade(
        episodes,
        cohort_filter=lambda e: (
            e.floor_type == gl.REGRESSED_FLOOR_TYPE
            and e.lighting == gl.REGRESSED_LIGHTING
        ),
        new_version=gl.REGRESSED_MODEL_VERSION,
    )
    assert before.n >= 40 and after.n >= 40, "need support on both sides of OTA"
    assert before.rate > 0.75, "pre-OTA cohort should be healthy"
    assert after.rate < 0.45, "post-OTA cohort should be broken"


def test_bad_robot_detected(data_path: Path) -> None:
    episodes = triage.load_episodes(data_path)

    zscores = triage.robot_success_zscores(
        episodes, task_types=triage.GRIP_TASKS, min_n=8
    )
    suspect = min(zscores, key=lambda r: zscores[r])
    assert suspect == gl.BAD_ROBOT_ID, "z-score should flag {}, got {}".format(
        gl.BAD_ROBOT_ID, suspect
    )
    assert zscores[suspect] < -3.0, "suspect must be a hard outlier"

    slopes = triage.grip_current_slopes(episodes)
    ranked = sorted(slopes, key=lambda r: slopes[r], reverse=True)
    assert ranked[0] == gl.BAD_ROBOT_ID, "grip drift should flag {}, got {}".format(
        gl.BAD_ROBOT_ID, ranked[0]
    )
    assert slopes[ranked[0]] > 0.10, "planted drift is 0.13 A/day; must be visible"
    assert slopes[ranked[1]] < 0.05, "second-steepest robot should look flat"

    # The failure signature is mechanical (grip), not perception (vision).
    bad_failures = [
        e for e in episodes if e.robot_id == gl.BAD_ROBOT_ID and not e.success
    ]
    grip_coded = [
        e for e in bad_failures if e.error_code in ("GRIP_SLIP", "GRIP_STALL")
    ]
    assert len(grip_coded) >= 0.5 * len(bad_failures), (
        "the bad robot's failures should be dominated by grip error codes"
    )


def test_red_herring_rejected(data_path: Path) -> None:
    episodes = triage.load_episodes(data_path)

    homes = triage.slice_by(episodes, lambda e: e.home_id)
    big_homes = {h: st for h, st in homes.items() if st.n >= 80}
    worst_home, _ = triage.worst_cell(big_homes, min_n=80)
    assert worst_home == gl.RED_HERRING_HOME_ID, (
        "the planted home should look worst in raw slices, got {}".format(worst_home)
    )

    raw_gap, adjusted_gap = triage.raw_and_adjusted_gap(
        episodes,
        group_filter=lambda e: e.home_id == gl.RED_HERRING_HOME_ID,
        strata_key=lambda e: (e.model_version, e.floor_type, e.lighting),
    )
    assert raw_gap > 0.08, (
        "red herring must look real before control (raw gap {:+.1%})".format(raw_gap)
    )
    assert abs(adjusted_gap) < 0.05, (
        "home effect must vanish under stratification (adjusted {:+.1%})".format(
            adjusted_gap
        )
    )
    assert abs(adjusted_gap) < raw_gap / 2, "adjustment must collapse the gap"

    # Sanity: the home's robots are NOT hardware outliers -- their pick/place
    # success inside healthy strata is normal.
    healthy = [
        e
        for e in episodes
        if e.home_id == gl.RED_HERRING_HOME_ID
        and not (
            e.model_version == gl.REGRESSED_MODEL_VERSION
            and e.floor_type == gl.REGRESSED_FLOOR_TYPE
            and e.lighting == gl.REGRESSED_LIGHTING
        )
    ]
    assert triage.cohort_stat(healthy).rate > 0.75, (
        "outside the broken cohort the red-herring home is healthy"
    )


def test_end_to_end(data_path: Path) -> None:
    findings = triage.run_triage(data_path)
    triage.verify_findings(findings)  # raises AssertionError on any mismatch


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="lab1_fleet_triage_") as tmp:
        tmp_dir = Path(tmp)
        data_path = _generate_dataset(tmp_dir)

        tests = [
            ("determinism", lambda: test_determinism(tmp_dir)),
            ("schema_and_shape", lambda: test_schema_and_shape(data_path)),
            (
                "cohort_regression_detected",
                lambda: test_cohort_regression_detected(data_path),
            ),
            ("bad_robot_detected", lambda: test_bad_robot_detected(data_path)),
            ("red_herring_rejected", lambda: test_red_herring_rejected(data_path)),
            ("end_to_end", lambda: test_end_to_end(data_path)),
        ]
        for name, fn in tests:
            fn()
            print("PASS  {}".format(name))

    print("\nALL {} TESTS PASSED".format(len(tests)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```




## triage.py

```python
#!/usr/bin/env python3
"""Fleet triage toolkit -- reference solution for lab1_fleet_triage.

A small, reusable cohort-analysis library (numpy + stdlib only) plus a
``main()`` that runs the full triage workflow on ``data/episodes.jsonl``
and pins every conclusion with an ``assert``.

The workflow it demonstrates is the one to narrate in a fleet-debug
interview ("a batch of bots stopped working"):

    1. Aggregate first     -- overall success rate, is it really down?
    2. Slice by one dim    -- model / fw / task / floor / lighting / home.
    3. Cross two dims      -- interactions that single slices hide.
    4. Align with rollout  -- same robots before vs after their OTA.
    5. Per-robot outliers  -- z-scores + physical-signal trends (drift).
    6. Control confounders -- stratify before blaming a correlated dim.

Usage:
    python triage.py [--data PATH]
"""

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Hashable, List, Optional, Sequence, Tuple

import numpy as np

DEFAULT_DATA = Path(__file__).resolve().parent / "data" / "episodes.jsonl"

REQUIRED_FIELDS = (
    "robot_id",
    "fw_version",
    "model_version",
    "task_type",
    "home_id",
    "floor_type",
    "lighting",
    "battery_pct",
    "cpu_temp",
    "grip_current",
    "policy_latency_ms",
    "success",
    "error_code",
    "ts",
)

GRIP_TASKS = ("pick", "place")


# ---------------------------------------------------------------------------
# Data model & loading
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Episode:
    """Analysis-side view of one telemetry record."""

    robot_id: str
    fw_version: str
    model_version: str
    task_type: str
    home_id: str
    floor_type: str
    lighting: str
    battery_pct: int
    cpu_temp: float
    grip_current: float
    policy_latency_ms: float
    success: bool
    error_code: Optional[str]
    ts: datetime

    @property
    def day(self) -> int:
        """Absolute day ordinal (only differences between days matter)."""
        return self.ts.date().toordinal()


@dataclass(frozen=True)
class CohortStat:
    """Success statistics for one cohort of episodes."""

    n: int
    successes: int

    @property
    def rate(self) -> float:
        return self.successes / self.n if self.n else float("nan")

    def __str__(self) -> str:
        return "{:>5d} eps  {:6.1%}".format(self.n, self.rate)


def load_episodes(path: Path) -> List[Episode]:
    """Load and validate a JSONL telemetry file.

    Raises FileNotFoundError with a helpful hint, or ValueError with the
    offending line number for malformed records.
    """
    if not path.exists():
        raise FileNotFoundError(
            "{} not found -- run `python generate_logs.py` first".format(path)
        )
    episodes: List[Episode] = []
    with path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                missing = [k for k in REQUIRED_FIELDS if k not in raw]
                if missing:
                    raise KeyError("missing fields: {}".format(missing))
                episodes.append(
                    Episode(
                        robot_id=str(raw["robot_id"]),
                        fw_version=str(raw["fw_version"]),
                        model_version=str(raw["model_version"]),
                        task_type=str(raw["task_type"]),
                        home_id=str(raw["home_id"]),
                        floor_type=str(raw["floor_type"]),
                        lighting=str(raw["lighting"]),
                        battery_pct=int(raw["battery_pct"]),
                        cpu_temp=float(raw["cpu_temp"]),
                        grip_current=float(raw["grip_current"]),
                        policy_latency_ms=float(raw["policy_latency_ms"]),
                        success=bool(raw["success"]),
                        error_code=raw["error_code"],
                        ts=datetime.strptime(str(raw["ts"]), "%Y-%m-%dT%H:%M:%SZ"),
                    )
                )
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError(
                    "{}:{}: malformed record ({})".format(path, lineno, exc)
                ) from exc
    if not episodes:
        raise ValueError("{}: file contains no episodes".format(path))
    return episodes


# ---------------------------------------------------------------------------
# Generic cohort analytics
# ---------------------------------------------------------------------------

KeyFn = Callable[[Episode], Hashable]


def cohort_stat(episodes: Sequence[Episode]) -> CohortStat:
    """Aggregate success stats over a list of episodes."""
    return CohortStat(n=len(episodes), successes=sum(1 for e in episodes if e.success))


def slice_by(episodes: Sequence[Episode], key: KeyFn) -> Dict[Hashable, CohortStat]:
    """Success stats grouped by one key function."""
    groups: Dict[Hashable, List[Episode]] = defaultdict(list)
    for ep in episodes:
        groups[key(ep)].append(ep)
    return {k: cohort_stat(v) for k, v in groups.items()}


def crosstab(
    episodes: Sequence[Episode], key_a: KeyFn, key_b: KeyFn
) -> Dict[Tuple[Hashable, Hashable], CohortStat]:
    """Success stats grouped by the cross of two key functions."""
    return slice_by(episodes, lambda e: (key_a(e), key_b(e)))


def worst_cell(
    table: Dict[Hashable, CohortStat], min_n: int
) -> Tuple[Hashable, CohortStat]:
    """The lowest-success cell among cells with at least ``min_n`` episodes."""
    eligible = {k: v for k, v in table.items() if v.n >= min_n}
    if not eligible:
        raise ValueError("no cell has >= {} episodes".format(min_n))
    key = min(eligible, key=lambda k: eligible[k].rate)
    return key, eligible[key]


def before_after_upgrade(
    episodes: Sequence[Episode],
    cohort_filter: Callable[[Episode], bool],
    new_version: str,
) -> Tuple[CohortStat, CohortStat]:
    """Compare a cohort's success before vs after OTA, on the *same* robots.

    Only robots observed running ``new_version`` at least once are included,
    so fleet composition cannot confound the before/after comparison.
    """
    upgraded_robots = {e.robot_id for e in episodes if e.model_version == new_version}
    before = [
        e
        for e in episodes
        if e.robot_id in upgraded_robots
        and e.model_version != new_version
        and cohort_filter(e)
    ]
    after = [
        e
        for e in episodes
        if e.robot_id in upgraded_robots
        and e.model_version == new_version
        and cohort_filter(e)
    ]
    return cohort_stat(before), cohort_stat(after)


# ---------------------------------------------------------------------------
# Per-robot anomaly detection
# ---------------------------------------------------------------------------


def robot_success_zscores(
    episodes: Sequence[Episode],
    task_types: Optional[Sequence[str]] = None,
    min_n: int = 8,
) -> Dict[str, float]:
    """Z-score of each robot's success rate vs the fleet distribution.

    Robots with fewer than ``min_n`` qualifying episodes are excluded
    (their rates are too noisy to rank).
    """
    pool = [e for e in episodes if task_types is None or e.task_type in task_types]
    per_robot = slice_by(pool, lambda e: e.robot_id)
    rates = {str(rid): st.rate for rid, st in per_robot.items() if st.n >= min_n}
    if len(rates) < 3:
        raise ValueError("need >= 3 robots with >= {} episodes".format(min_n))
    values = np.array(list(rates.values()), dtype=np.float64)
    mean, std = float(values.mean()), float(values.std())
    if std == 0.0:
        return {rid: 0.0 for rid in rates}
    return {rid: (rate - mean) / std for rid, rate in rates.items()}


def grip_current_slopes(
    episodes: Sequence[Episode],
    task_types: Sequence[str] = GRIP_TASKS,
    min_points: int = 6,
) -> Dict[str, float]:
    """Per-robot linear trend (amps/day) of grip_current over time.

    Fits ``grip_current ~ day`` per robot on grip-loaded tasks. A healthy
    gripper trends flat; mechanical degradation shows as a positive slope.
    """
    by_robot: Dict[str, List[Episode]] = defaultdict(list)
    for ep in episodes:
        if ep.task_type in task_types:
            by_robot[ep.robot_id].append(ep)
    slopes: Dict[str, float] = {}
    for rid, eps in by_robot.items():
        days = np.array([e.day for e in eps], dtype=np.float64)
        amps = np.array([e.grip_current for e in eps], dtype=np.float64)
        if len(eps) < min_points or len(set(days.tolist())) < 3:
            continue
        slopes[rid] = float(np.polyfit(days, amps, 1)[0])
    return slopes


# ---------------------------------------------------------------------------
# Confounder control (red-herring analysis)
# ---------------------------------------------------------------------------


def raw_and_adjusted_gap(
    episodes: Sequence[Episode],
    group_filter: Callable[[Episode], bool],
    strata_key: KeyFn,
    min_stratum_n: int = 5,
) -> Tuple[float, float]:
    """How much worse the group is than the rest, raw vs stratified.

    Returns ``(raw_gap, adjusted_gap)`` where gap = rest_rate - group_rate.
    The adjusted gap is the within-stratum gap averaged with the *group's*
    stratum weights (direct standardization). A causal group effect
    survives adjustment; a confounded one collapses toward zero.
    """
    group = [e for e in episodes if group_filter(e)]
    rest = [e for e in episodes if not group_filter(e)]
    if not group or not rest:
        raise ValueError("group_filter must split episodes into two non-empty sets")
    raw_gap = cohort_stat(rest).rate - cohort_stat(group).rate

    group_by = slice_by(group, strata_key)
    rest_by = slice_by(rest, strata_key)
    weighted_sum, weight_total = 0.0, 0.0
    for stratum, g_stat in group_by.items():
        r_stat = rest_by.get(stratum)
        if r_stat is None or g_stat.n < min_stratum_n or r_stat.n < min_stratum_n:
            continue
        weighted_sum += g_stat.n * (r_stat.rate - g_stat.rate)
        weight_total += g_stat.n
    if weight_total == 0.0:
        raise ValueError("no stratum has enough support on both sides")
    return raw_gap, weighted_sum / weight_total


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def _print_table(title: str, table: Dict[Hashable, CohortStat]) -> None:
    print("\n  {}".format(title))
    for key in sorted(table, key=lambda k: table[k].rate):
        print("    {!s:<28} {}".format(key, table[key]))


def run_triage(data_path: Path) -> Dict[str, object]:
    """Run the full triage workflow, print the report, return the findings."""
    episodes = load_episodes(data_path)
    findings: Dict[str, object] = {}

    print("=" * 72)
    print(
        "FLEET TRIAGE REPORT  ({} episodes from {})".format(
            len(episodes), data_path.name
        )
    )
    print("=" * 72)

    # -- Step 1: aggregate ---------------------------------------------------
    overall = cohort_stat(episodes)
    findings["overall"] = overall
    print("\n[1] Overall: {}".format(overall))

    # -- Step 2: single-dimension slices --------------------------------------
    print("\n[2] Single-dimension slices (sorted worst-first)")
    for name, key in (
        ("model_version", lambda e: e.model_version),
        ("fw_version", lambda e: e.fw_version),
        ("task_type", lambda e: e.task_type),
        ("floor_type", lambda e: e.floor_type),
        ("lighting", lambda e: e.lighting),
    ):
        _print_table("by {}".format(name), slice_by(episodes, key))
    homes = slice_by(episodes, lambda e: e.home_id)
    big_homes = {h: st for h, st in homes.items() if st.n >= 80}
    _print_table("by home_id (only homes with >= 80 eps)", big_homes)
    worst_home, worst_home_stat = worst_cell(big_homes, min_n=80)
    findings["worst_home"] = worst_home
    print("    -> worst big home: {} ({})".format(worst_home, worst_home_stat))

    # -- Step 3: two-dimension crosstab, per model version --------------------
    print("\n[3] floor_type x lighting, split by model_version")
    v24 = [e for e in episodes if e.model_version == "v2.4"]
    v23 = [e for e in episodes if e.model_version == "v2.3"]
    tab24 = crosstab(v24, lambda e: e.floor_type, lambda e: e.lighting)
    tab23 = crosstab(v23, lambda e: e.floor_type, lambda e: e.lighting)
    _print_table("v2.4", tab24)
    _print_table("v2.3", tab23)
    bad_cell, bad_stat = worst_cell(tab24, min_n=40)
    findings["worst_v24_cell"] = bad_cell
    findings["worst_v24_rate"] = bad_stat.rate
    findings["v23_same_cell_rate"] = tab23[bad_cell].rate
    findings["other_v24_min_rate"] = min(
        st.rate for k, st in tab24.items() if k != bad_cell and st.n >= 40
    )
    print(
        "    -> worst v2.4 cell: {} at {:.1%} (same cell on v2.3: {:.1%})".format(
            bad_cell, bad_stat.rate, tab23[bad_cell].rate
        )
    )

    # -- Step 4: align with the OTA timeline ----------------------------------
    print("\n[4] Same-robot before/after OTA, inside the suspect cohort")
    floor, light = bad_cell
    before, after = before_after_upgrade(
        episodes,
        cohort_filter=lambda e: e.floor_type == floor and e.lighting == light,
        new_version="v2.4",
    )
    findings["cohort_before"] = before
    findings["cohort_after"] = after
    print(
        "    upgraded robots, {}+{} episodes: before {} | after {}".format(
            floor, light, before, after
        )
    )
    cohort_codes = sorted(
        slice_by(
            [
                e
                for e in v24
                if e.floor_type == floor and e.lighting == light and not e.success
            ],
            lambda e: e.error_code,
        ).items(),
        key=lambda kv: -kv[1].n,
    )
    print(
        "    top error codes in broken cohort: {}".format(
            [(code, st.n) for code, st in cohort_codes[:3]]
        )
    )

    # -- Step 5: per-robot outliers -------------------------------------------
    print("\n[5] Per-robot anomaly detection (grip-loaded tasks: pick/place)")
    zscores = robot_success_zscores(episodes, task_types=GRIP_TASKS, min_n=8)
    suspect_z = min(zscores, key=lambda r: zscores[r])
    slopes = grip_current_slopes(episodes)
    ranked = sorted(slopes, key=lambda r: slopes[r], reverse=True)
    suspect_slope, runner_up = ranked[0], ranked[1]
    findings["suspect_robot_z"] = suspect_z
    findings["suspect_z_value"] = zscores[suspect_z]
    findings["suspect_robot_slope"] = suspect_slope
    findings["suspect_slope_value"] = slopes[suspect_slope]
    findings["runner_up_slope_value"] = slopes[runner_up]
    print(
        "    lowest success z-score : {} (z = {:+.2f})".format(
            suspect_z, zscores[suspect_z]
        )
    )
    print(
        "    steepest grip drift    : {} ({:+.3f} A/day; runner-up {} {:+.3f})".format(
            suspect_slope, slopes[suspect_slope], runner_up, slopes[runner_up]
        )
    )
    suspect_fail_codes = slice_by(
        [e for e in episodes if e.robot_id == suspect_z and not e.success],
        lambda e: e.error_code,
    )
    print(
        "    suspect's failure codes: {}".format(
            sorted(
                ((c, st.n) for c, st in suspect_fail_codes.items()),
                key=lambda kv: -kv[1],
            )
        )
    )

    # -- Step 6: control the confounder ---------------------------------------
    print("\n[6] Red-herring check: is {} causally bad?".format(worst_home))
    raw_gap, adjusted_gap = raw_and_adjusted_gap(
        episodes,
        group_filter=lambda e: e.home_id == worst_home,
        strata_key=lambda e: (e.model_version, e.floor_type, e.lighting),
    )
    findings["raw_gap"] = raw_gap
    findings["adjusted_gap"] = adjusted_gap
    print("    raw gap vs rest of fleet      : {:+.1%}".format(raw_gap))
    print("    after stratifying on (model,  ")
    print("    floor, lighting)              : {:+.1%}".format(adjusted_gap))
    print(
        "    -> the home effect {} under stratification".format(
            "collapses" if abs(adjusted_gap) < raw_gap / 2 else "PERSISTS"
        )
    )

    print("\n" + "=" * 72)
    return findings


def verify_findings(findings: Dict[str, object]) -> None:
    """Pin the triage conclusions against the simulator's ground truth.

    A real on-call triage obviously has no ground truth to import; this
    block exists so the lab is self-checking.
    """
    import generate_logs as gt

    # (a) Cohort regression: v2.4 x carpet x dim.
    assert findings["worst_v24_cell"] == (
        gt.REGRESSED_FLOOR_TYPE,
        gt.REGRESSED_LIGHTING,
    ), "worst v2.4 cell should be (carpet, dim), got {}".format(
        findings["worst_v24_cell"]
    )
    assert findings["worst_v24_rate"] < 0.45, "broken cohort should be < 45% success"
    assert findings["v23_same_cell_rate"] > 0.75, (
        "same cohort on v2.3 should be healthy"
    )
    assert findings["other_v24_min_rate"] > 0.75, (
        "all other v2.4 cells should be healthy"
    )
    before = findings["cohort_before"]
    after = findings["cohort_after"]
    assert before.rate > 0.75 and after.rate < 0.45, (
        "same robots must be healthy pre-OTA and broken post-OTA "
        "(before {:.1%}, after {:.1%})".format(before.rate, after.rate)
    )

    # (b) Hardware fault: one robot, found by two independent signals.
    assert findings["suspect_robot_z"] == gt.BAD_ROBOT_ID, (
        "z-score suspect should be {}, got {}".format(
            gt.BAD_ROBOT_ID, findings["suspect_robot_z"]
        )
    )
    assert findings["suspect_robot_slope"] == gt.BAD_ROBOT_ID, (
        "grip-drift suspect should be {}, got {}".format(
            gt.BAD_ROBOT_ID, findings["suspect_robot_slope"]
        )
    )
    assert findings["suspect_z_value"] < -3.0, "suspect z should be a hard outlier"
    assert findings["suspect_slope_value"] > 0.10, "drift should be > 0.10 A/day"
    assert findings["runner_up_slope_value"] < 0.05, "healthy grippers should be flat"

    # (c) Red herring: the worst home is the planted one, and its effect
    #     disappears once the real drivers are controlled for.
    assert findings["worst_home"] == gt.RED_HERRING_HOME_ID, (
        "worst big home should be {}, got {}".format(
            gt.RED_HERRING_HOME_ID, findings["worst_home"]
        )
    )
    raw_gap = float(findings["raw_gap"])  # type: ignore[arg-type]
    adjusted_gap = float(findings["adjusted_gap"])  # type: ignore[arg-type]
    assert raw_gap > 0.08, "red herring must look real in raw data"
    assert abs(adjusted_gap) < 0.05, "home effect must vanish under stratification"
    assert abs(adjusted_gap) < raw_gap / 2, "adjustment must collapse the gap"

    print("[verify] all triage conclusions match planted ground truth")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run the fleet triage workflow.")
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA,
        help="episodes JSONL (default: data/episodes.jsonl)",
    )
    args = parser.parse_args(argv)
    findings = run_triage(args.data)
    verify_findings(findings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/labs/lab1_fleet_triage/README.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/labs/lab1_fleet_triage/README.md)。作者整理资料；许可和第三方来源范围见阅读指南。
