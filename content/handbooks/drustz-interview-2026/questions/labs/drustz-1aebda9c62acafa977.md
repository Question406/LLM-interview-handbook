---
id: drustz-1aebda9c62acafa977
section: labs
order: 4
level: A
title: lab2_ota_canary — 模型 OTA 金丝雀发布与自动回滚
quick: 作者完整文档 · lab2_ota_canary — 模型 OTA 金丝雀发布与自动回滚
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/labs/lab2_ota_canary/README.md
    type: primary
---
# lab2_ota_canary — 模型 OTA 金丝雀发布与自动回滚

对应考点：`bot_company/06_system_design_playbooks.md` 的 **Playbook B**（Robot Policy
Post-Training Pipeline：数据 → 训练 → 部署 → 回滚）。那道题的分数集中在部署侧
（registry 状态机、金丝雀放量、统计闸门、自动回滚），这个 lab 就是把 B 题架构图里
`Model Registry → 金丝雀 → 监控 → 回滚` 那一段真的写出来、跑起来。

面试里画完架构图后可以说这句：

> **"I've actually implemented this gate logic — a staged registry state machine plus a
> two-proportion z-test gate with Wilson intervals, and a simulated 10k-robot fleet where a
> cohort-masked regression gets shipped by the aggregate gate but caught by the per-cohort
> gate."**

## 文件

| 文件 | 内容 |
|---|---|
| `registry.py` | 极简 model registry：JSONL 事件日志持久化（append-only，重放重建状态 = 审计日志）；记录 lineage（train manifest id + 父版本）；状态机 `staged → canary_1pct → canary_10pct → fleet`，canary/fleet 可 `→ rolled_back`；非法转移一律 raise `IllegalTransitionError` |
| `gate.py` | 统计放行闸门：两比例 z 检验（显著更差 → ROLLBACK）+ Wilson 下界非劣性判据（→ PROMOTE），其余 HOLD；**样本量不足时强制 HOLD 而不是瞎判**；fleet 级决策 = 各 cohort 里最坏的那个 |
| `rollout.py` | 1 万台 fleet 模拟器 + rollout 控制器：按天累积观测、逐级放量、观察期用尽 fail-closed 回滚；内置三个场景（见下） |
| `test_ota.py` | 11 个测试，plain assert，无 pytest |

三个场景（固定种子，完全确定）：

1. **好模型**（真实 +3pp）：1% → 10% → fleet 逐级晋升；第 1 天 carpet 只有 100 条样本，闸门先 HOLD（演示"样本不足不判"）。
2. **坏模型**（carpet cohort −15pp，整体只 −4pp）：在 **1% canary 第 2 天**被 z 检验拦下自动回滚——blast radius 停在 100 台。
3. **整体持平但分 cohort 回归**（hardwood +2.7pp、carpet −8pp，加权 ≈ 0）：同一份数据，**聚合闸门会 PROMOTE**，分 cohort 闸门 ROLLBACK。这就是闸门必须分 cohort 看的理由（Simpson 式掩盖），对应 B 题"主指标 + 分层护栏指标"的讲法。

## 15–30 分钟熟悉路径

1. **先跑**（约 2 分钟）：

```bash
/usr/bin/python3 rollout.py  # 看三个场景的完整决策转录
/usr/bin/python3 test_ota.py # 11/11 PASS
```



   重点盯 rollout.py 输出里三处：好模型 day 1 的 `insufficient samples` HOLD；
   坏模型 day 2 的 `z=-3.80 <= -1.96` 自动回滚；场景 3 同一份数据两种闸门结论相反。
2. **再读 `gate.py`**（约 10 分钟，面试最可能被追问的文件）：
   记住决策顺序四步——样本不足 HOLD → z ≤ −1.96 ROLLBACK → (z ≥ +1.96 或 Wilson
   下界 ≥ control − 3pp 非劣) PROMOTE → 否则 HOLD；以及为什么用 Wilson 不用 Wald
   （小样本、rate 贴近 0/1 时 Wald 区间会塌掉，年轻 canary 恰好就在这个 regime）。
3. **然后读 `registry.py`**（约 5 分钟）：event-sourced JSONL（日志即审计轨迹）、
   promote 只走一步、rolled_back 是终态（坏版本不复活，重训重注册）、rollback 强制
   带 reason。
4. **最后扫 `rollout.py`**（约 5 分钟）：控制器的 fail-closed（观察期用尽 = 回滚而
   不是继续挂着）；`demo_cohort_masking` 怎么用 `merge_cohorts` 现场对比两种闸门。

## 面试话术锚点（对着 B 题深挖组件 2 讲）

- 分桶单位是 household 不是 request（本 lab 简化为 robot，口头点出来）；
- 1% canary = 100 台 → 样本天然稀缺 → min-sample HOLD 是一等公民，不是边角处理；
  真实系统还会加 shadow mode 来补小样本的坑；
- 主指标干预率比成功率更灵敏（本 lab 用成功率是为了让 z 检验直观，口头说明替换）；
- 聚合指标掩盖 cohort 回归 → 分层闸门 + fleet 决策取最坏；多 cohort 带来多重比较，
  可提 Bonferroni / 分层 alpha 作为 follow-up；
- 回滚执行端靠设备 A/B 双分区秒级切换，registry 只负责记录真相和挡住非法转移。

## 约束与运行环境

- 解释器固定 `/usr/bin/python3`（Python 3.9.6），纯标准库（math/random/json/dataclasses），
  无 pandas、无网络、无新依赖；固定种子，全套测试 + 主脚本 < 1 秒。

## gate.py

```python
"""Statistical release gate for canary rollouts.

Given per-cohort success counts for a canary arm and a control arm, decide
one of three actions:

- ``ROLLBACK``: canary is *significantly worse* than control
  (one-sided two-proportion z-test, z <= -z_alpha).
- ``PROMOTE``: canary is *demonstrably non-inferior*: the Wilson lower bound
  of the canary success rate is at or above the control point estimate minus
  a non-inferiority margin (or canary is significantly better, z >= z_alpha).
- ``HOLD``: everything else -- including, crucially, **insufficient sample
  size**. A gate that answers before it has data is worse than no gate:
  underpowered "wins" promote bad models and underpowered "losses" roll back
  good ones. Below ``min_trials_per_arm`` we always HOLD and say why.

Cohorts
-------
The fleet-level decision is the *worst* decision across cohorts
(ROLLBACK > HOLD > PROMOTE). This is the whole point: an aggregate metric can
be flat while one cohort (e.g. carpet floors) regresses badly and another
improves -- Simpson's-paradox-style masking. ``rollout.py`` demonstrates this
failure mode end to end.

Pure stdlib (``math`` only), fully deterministic.
"""

import enum
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


class Decision(enum.Enum):
    """Gate decision, ordered by severity (see ``_SEVERITY``)."""

    PROMOTE = "promote"
    HOLD = "hold"
    ROLLBACK = "rollback"


_SEVERITY = {Decision.PROMOTE: 0, Decision.HOLD: 1, Decision.ROLLBACK: 2}


@dataclass(frozen=True)
class ArmCounts:
    """Success counts for one arm (canary or control) of one cohort."""

    successes: int
    trials: int

    def __post_init__(self) -> None:
        if self.trials < 0 or self.successes < 0:
            raise ValueError("counts must be non-negative")
        if self.successes > self.trials:
            raise ValueError(
                "successes (%d) cannot exceed trials (%d)"
                % (self.successes, self.trials)
            )

    @property
    def rate(self) -> float:
        """Point estimate of the success rate (0.0 when there are no trials)."""
        return self.successes / self.trials if self.trials > 0 else 0.0


@dataclass(frozen=True)
class GateConfig:
    """Tunable knobs of the gate.

    Attributes:
        min_trials_per_arm: below this, the cohort verdict is always HOLD.
        z_alpha: critical z value (1.96 ~= one-sided alpha 0.025).
        non_inferiority_margin: how much worse than control (in absolute
            success-rate points) the *pessimistic* canary estimate may be and
            still promote. Robots: a small regression on one floor type is an
            acceptable price for a fleet-wide win -- but it must be bounded.
    """

    min_trials_per_arm: int = 200
    z_alpha: float = 1.96
    non_inferiority_margin: float = 0.03

    def __post_init__(self) -> None:
        if self.min_trials_per_arm < 1:
            raise ValueError("min_trials_per_arm must be >= 1")
        if self.z_alpha <= 0:
            raise ValueError("z_alpha must be positive")
        if self.non_inferiority_margin < 0:
            raise ValueError("non_inferiority_margin must be >= 0")


@dataclass(frozen=True)
class CohortVerdict:
    """Per-cohort gate output, with enough detail to be auditable."""

    cohort: str
    decision: Decision
    reason: str
    z_score: Optional[float]
    canary_ci: Optional[Tuple[float, float]]
    control_ci: Optional[Tuple[float, float]]


@dataclass(frozen=True)
class GateReport:
    """Fleet-level decision plus the per-cohort verdicts behind it."""

    decision: Decision
    verdicts: List[CohortVerdict]

    def verdict_for(self, cohort: str) -> CohortVerdict:
        for verdict in self.verdicts:
            if verdict.cohort == cohort:
                return verdict
        raise KeyError("no verdict for cohort: %s" % cohort)


def wilson_interval(
    successes: int, trials: int, z: float = 1.96
) -> Tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    Preferred over the normal ("Wald") interval because it behaves sanely at
    small n and rates near 0/1 -- exactly the regime a young canary lives in.

    Raises:
        ValueError: invalid counts or ``trials == 0`` (no data, no interval).
    """
    if trials <= 0:
        raise ValueError("wilson_interval requires trials > 0")
    if successes < 0 or successes > trials:
        raise ValueError("successes must be within [0, trials]")
    p_hat = successes / trials
    z2 = z * z
    denom = 1.0 + z2 / trials
    center = (p_hat + z2 / (2.0 * trials)) / denom
    half = (
        z
        * math.sqrt(p_hat * (1.0 - p_hat) / trials + z2 / (4.0 * trials * trials))
        / denom
    )
    return (max(0.0, center - half), min(1.0, center + half))


def two_proportion_z(canary: ArmCounts, control: ArmCounts) -> float:
    """Pooled two-proportion z statistic for (canary rate - control rate).

    Positive z: canary better. Returns 0.0 when the pooled standard error is
    zero (both arms all-success or all-failure), i.e. "no evidence of a
    difference", which downstream logic treats as not-significant.

    Raises:
        ValueError: either arm has zero trials.
    """
    if canary.trials == 0 or control.trials == 0:
        raise ValueError("two_proportion_z requires trials > 0 in both arms")
    pooled = (canary.successes + control.successes) / (canary.trials + control.trials)
    se = math.sqrt(
        pooled * (1.0 - pooled) * (1.0 / canary.trials + 1.0 / control.trials)
    )
    if se == 0.0:
        return 0.0
    return (canary.rate - control.rate) / se


def evaluate_cohort(
    cohort: str,
    canary: ArmCounts,
    control: ArmCounts,
    config: GateConfig,
) -> CohortVerdict:
    """Gate one cohort. Decision order (first match wins):

    1. Either arm below ``min_trials_per_arm``  -> HOLD ("insufficient samples").
    2. z <= -z_alpha (significantly worse)      -> ROLLBACK.
    3. z >= +z_alpha (significantly better), or Wilson lower bound of canary
       >= control point estimate - margin       -> PROMOTE.
    4. Otherwise                                -> HOLD ("keep observing").
    """
    if canary.trials < config.min_trials_per_arm or (
        control.trials < config.min_trials_per_arm
    ):
        return CohortVerdict(
            cohort=cohort,
            decision=Decision.HOLD,
            reason=(
                "insufficient samples (canary=%d, control=%d, need %d/arm)"
                % (canary.trials, control.trials, config.min_trials_per_arm)
            ),
            z_score=None,
            canary_ci=None,
            control_ci=None,
        )

    z = two_proportion_z(canary, control)
    canary_ci = wilson_interval(canary.successes, canary.trials, config.z_alpha)
    control_ci = wilson_interval(control.successes, control.trials, config.z_alpha)

    if z <= -config.z_alpha:
        return CohortVerdict(
            cohort=cohort,
            decision=Decision.ROLLBACK,
            reason=(
                "canary significantly worse: rate %.3f vs %.3f (z=%.2f <= -%.2f)"
                % (canary.rate, control.rate, z, config.z_alpha)
            ),
            z_score=z,
            canary_ci=canary_ci,
            control_ci=control_ci,
        )

    non_inferior = canary_ci[0] >= control.rate - config.non_inferiority_margin
    if z >= config.z_alpha or non_inferior:
        return CohortVerdict(
            cohort=cohort,
            decision=Decision.PROMOTE,
            reason=(
                "non-inferior: canary Wilson lower %.3f >= control %.3f - %.3f"
                " (z=%.2f)"
                % (
                    canary_ci[0],
                    control.rate,
                    config.non_inferiority_margin,
                    z,
                )
            ),
            z_score=z,
            canary_ci=canary_ci,
            control_ci=control_ci,
        )

    return CohortVerdict(
        cohort=cohort,
        decision=Decision.HOLD,
        reason=(
            "inconclusive, keep observing: rate %.3f vs %.3f (z=%.2f)"
            % (canary.rate, control.rate, z)
        ),
        z_score=z,
        canary_ci=canary_ci,
        control_ci=control_ci,
    )


def evaluate(
    cohorts: Dict[str, Tuple[ArmCounts, ArmCounts]],
    config: GateConfig,
) -> GateReport:
    """Gate all cohorts; fleet decision = worst per-cohort decision.

    Args:
        cohorts: cohort name -> (canary counts, control counts).
        config: gate configuration.

    Raises:
        ValueError: ``cohorts`` is empty (a gate with no inputs must not
            silently promote).
    """
    if not cohorts:
        raise ValueError("evaluate requires at least one cohort")
    verdicts = [
        evaluate_cohort(name, canary, control, config)
        for name, (canary, control) in sorted(cohorts.items())
    ]
    worst = max(verdicts, key=lambda v: _SEVERITY[v.decision]).decision
    return GateReport(decision=worst, verdicts=verdicts)


def merge_cohorts(
    cohorts: Dict[str, Tuple[ArmCounts, ArmCounts]],
) -> Tuple[ArmCounts, ArmCounts]:
    """Collapse per-cohort counts into one aggregate (canary, control) pair.

    Exists so the demo can show what an aggregate-only gate *would* have
    decided -- i.e. the anti-pattern this module is designed to avoid.
    """
    canary_s = sum(c.successes for c, _ in cohorts.values())
    canary_t = sum(c.trials for c, _ in cohorts.values())
    control_s = sum(k.successes for _, k in cohorts.values())
    control_t = sum(k.trials for _, k in cohorts.values())
    return (
        ArmCounts(successes=canary_s, trials=canary_t),
        ArmCounts(successes=control_s, trials=control_t),
    )
```




## registry.py

```python
"""Minimal model registry with JSONL event-sourced persistence.

Responsibilities
----------------
1. Track every model version with full lineage: which training-data manifest
   produced it and which parent version it was fine-tuned from. Any production
   model must be able to answer "what data, what parent" (blast-radius analysis
   when a bad data batch is discovered).
2. Enforce the rollout state machine:

       staged -> canary_1pct -> canary_10pct -> fleet
                     |               |            |
                     +---------------+------------+--> rolled_back

   Promotion only moves one step forward along the path. Rollback is only
   legal from an in-flight or fully deployed stage (never from ``staged``,
   which has nothing running, and never twice). Every illegal transition
   raises :class:`IllegalTransitionError` -- the registry is the last line of
   defence against a buggy rollout controller.
3. Persist as an append-only JSONL event log. State is rebuilt by replaying
   the log, so the file is also a complete audit trail (who promoted what,
   when, and why).

Deliberate simplifications (call these out in an interview):
- No auth / no concurrent-writer locking (single-writer assumption).
- Promoting a new version to ``fleet`` does not auto-deprecate the previous
  fleet version; ``current_fleet_version`` simply returns the most recent one.
"""

import enum
import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class Stage(enum.Enum):
    """Lifecycle stage of a model version."""

    STAGED = "staged"
    CANARY_1PCT = "canary_1pct"
    CANARY_10PCT = "canary_10pct"
    FLEET = "fleet"
    ROLLED_BACK = "rolled_back"


#: The only legal forward path. promote() moves exactly one step to the right.
PROMOTION_PATH: List[Stage] = [
    Stage.STAGED,
    Stage.CANARY_1PCT,
    Stage.CANARY_10PCT,
    Stage.FLEET,
]

#: Stages from which a rollback is legal (something is actually running).
ROLLBACK_SOURCES = frozenset([Stage.CANARY_1PCT, Stage.CANARY_10PCT, Stage.FLEET])


class RegistryError(Exception):
    """Base class for all registry errors."""


class IllegalTransitionError(RegistryError):
    """Raised when a state transition violates the rollout state machine."""


class UnknownVersionError(RegistryError):
    """Raised when an operation references a version that was never registered."""


class DuplicateVersionError(RegistryError):
    """Raised when registering a version_id that already exists."""


@dataclass
class ModelVersion:
    """A single model version and its lineage.

    Attributes:
        version_id: Unique id, e.g. ``policy-2026-08-08-a``.
        train_manifest_id: Content-addressed id of the dataset manifest the
            model was trained on (episode-id list + processing-code hash).
        parent_version: Version this one was fine-tuned from, or ``None`` for
            a from-scratch train.
        stage: Current lifecycle stage.
        created_at: Unix timestamp of registration.
        history: Ordered transition records
            (``{"from": ..., "to": ..., "reason": ..., "ts": ...}``).
    """

    version_id: str
    train_manifest_id: str
    parent_version: Optional[str]
    stage: Stage = Stage.STAGED
    created_at: float = 0.0
    history: List[Dict[str, Any]] = field(default_factory=list)


class ModelRegistry:
    """JSONL-backed model registry.

    The on-disk format is one JSON event per line:

        {"event": "register",   "version_id": ..., "train_manifest_id": ...,
         "parent_version": ..., "ts": ...}
        {"event": "transition", "version_id": ..., "from": ..., "to": ...,
         "reason": ..., "ts": ...}

    Loading replays the log through the same validation code as live calls,
    so a corrupted/hand-edited log that encodes an illegal transition fails
    loudly at load time instead of silently poisoning state.
    """

    def __init__(self, path: str) -> None:
        """Open (or create) the registry backed by the JSONL file at ``path``."""
        self._path = path
        self._versions: Dict[str, ModelVersion] = {}
        if os.path.exists(path):
            self._replay()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(
        self,
        version_id: str,
        train_manifest_id: str,
        parent_version: Optional[str] = None,
    ) -> ModelVersion:
        """Register a new version in ``staged``. Lineage fields are mandatory.

        Raises:
            DuplicateVersionError: ``version_id`` already exists.
            UnknownVersionError: ``parent_version`` given but never registered.
            ValueError: empty ``version_id`` or ``train_manifest_id``.
        """
        if not version_id or not train_manifest_id:
            raise ValueError("version_id and train_manifest_id must be non-empty")
        if version_id in self._versions:
            raise DuplicateVersionError("version already registered: %s" % version_id)
        if parent_version is not None and parent_version not in self._versions:
            raise UnknownVersionError("unknown parent version: %s" % parent_version)
        event = {
            "event": "register",
            "version_id": version_id,
            "train_manifest_id": train_manifest_id,
            "parent_version": parent_version,
            "ts": time.time(),
        }
        self._apply(event)
        self._append(event)
        return self._versions[version_id]

    def promote(self, version_id: str, reason: str = "") -> Stage:
        """Advance ``version_id`` exactly one step along the promotion path.

        Returns the new stage.

        Raises:
            UnknownVersionError: version was never registered.
            IllegalTransitionError: version is at ``fleet`` (nothing above it)
                or ``rolled_back`` (dead versions never come back -- retrain
                and re-register instead).
        """
        version = self._get_or_raise(version_id)
        if version.stage not in PROMOTION_PATH or version.stage == Stage.FLEET:
            raise IllegalTransitionError(
                "cannot promote %s from stage %s" % (version_id, version.stage.value)
            )
        next_stage = PROMOTION_PATH[PROMOTION_PATH.index(version.stage) + 1]
        return self._transition(version, next_stage, reason)

    def rollback(self, version_id: str, reason: str) -> Stage:
        """Move ``version_id`` to ``rolled_back``.

        A reason is required: rollbacks are incidents and must be auditable.

        Raises:
            UnknownVersionError: version was never registered.
            IllegalTransitionError: version is ``staged`` (nothing deployed)
                or already ``rolled_back``.
            ValueError: empty reason.
        """
        if not reason:
            raise ValueError("rollback requires a non-empty reason")
        version = self._get_or_raise(version_id)
        if version.stage not in ROLLBACK_SOURCES:
            raise IllegalTransitionError(
                "cannot roll back %s from stage %s" % (version_id, version.stage.value)
            )
        return self._transition(version, Stage.ROLLED_BACK, reason)

    def get(self, version_id: str) -> ModelVersion:
        """Return the :class:`ModelVersion` for ``version_id``."""
        return self._get_or_raise(version_id)

    def lineage(self, version_id: str) -> List[str]:
        """Return ``[version, parent, grandparent, ...]`` following parents."""
        chain: List[str] = []
        cursor: Optional[str] = version_id
        while cursor is not None:
            version = self._get_or_raise(cursor)
            chain.append(version.version_id)
            cursor = version.parent_version
        return chain

    def current_fleet_version(self) -> Optional[str]:
        """Most recently promoted version currently at ``fleet``, if any."""
        best_id: Optional[str] = None
        best_ts = float("-inf")
        for version in self._versions.values():
            if version.stage is not Stage.FLEET:
                continue
            ts = version.history[-1]["ts"] if version.history else version.created_at
            if ts >= best_ts:
                best_ts = ts
                best_id = version.version_id
        return best_id

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _get_or_raise(self, version_id: str) -> ModelVersion:
        try:
            return self._versions[version_id]
        except KeyError:
            raise UnknownVersionError("unknown version: %s" % version_id)

    def _transition(self, version: ModelVersion, to: Stage, reason: str) -> Stage:
        event = {
            "event": "transition",
            "version_id": version.version_id,
            "from": version.stage.value,
            "to": to.value,
            "reason": reason,
            "ts": time.time(),
        }
        self._apply(event)
        self._append(event)
        return to

    def _apply(self, event: Dict[str, Any]) -> None:
        """Mutate in-memory state from a (pre-validated) event."""
        if event["event"] == "register":
            self._versions[event["version_id"]] = ModelVersion(
                version_id=event["version_id"],
                train_manifest_id=event["train_manifest_id"],
                parent_version=event["parent_version"],
                stage=Stage.STAGED,
                created_at=event["ts"],
            )
        elif event["event"] == "transition":
            version = self._versions[event["version_id"]]
            version.stage = Stage(event["to"])
            version.history.append(
                {
                    "from": event["from"],
                    "to": event["to"],
                    "reason": event["reason"],
                    "ts": event["ts"],
                }
            )
        else:
            raise RegistryError("unknown event type: %r" % event.get("event"))

    def _append(self, event: Dict[str, Any]) -> None:
        with open(self._path, "a") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
            handle.flush()

    def _replay(self) -> None:
        """Rebuild state by replaying the JSONL log through validation."""
        with open(self._path, "r") as handle:
            for line_no, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    raise RegistryError(
                        "corrupt registry log %s at line %d" % (self._path, line_no)
                    )
                self._validate_replayed(event, line_no)
                self._apply(event)

    def _validate_replayed(self, event: Dict[str, Any], line_no: int) -> None:
        kind = event.get("event")
        if kind == "register":
            if event["version_id"] in self._versions:
                raise RegistryError("duplicate register in log at line %d" % line_no)
        elif kind == "transition":
            version = self._versions.get(event["version_id"])
            if version is None:
                raise RegistryError(
                    "transition for unknown version at line %d" % line_no
                )
            to = Stage(event["to"])
            legal_promote = (
                version.stage in PROMOTION_PATH
                and version.stage is not Stage.FLEET
                and PROMOTION_PATH[PROMOTION_PATH.index(version.stage) + 1] is to
            )
            legal_rollback = (
                to is Stage.ROLLED_BACK and version.stage in ROLLBACK_SOURCES
            )
            if not (legal_promote or legal_rollback):
                raise RegistryError(
                    "illegal transition %s->%s in log at line %d"
                    % (version.stage.value, to.value, line_no)
                )
        else:
            raise RegistryError("unknown event type at line %d" % line_no)
```




## rollout.py

```python
"""Fleet rollout simulator: OTA canary with automatic rollback.

Simulates a 10,000-robot home fleet receiving a new policy over the air:

    staged -> canary_1pct (100 robots) -> canary_10pct (1,000 robots) -> fleet

Each canary stage runs day-sized observation windows. Robots execute tasks in
two cohorts (floor types) with different baseline success rates; a matched
control arm of equal size keeps running the incumbent policy. After every day
the statistical gate (``gate.py``) reads the *accumulated* counts and says
PROMOTE / HOLD / ROLLBACK; the rollout controller translates that into
registry transitions (``registry.py``). If a stage exhausts its observation
budget without a decision, the controller **fails closed** and rolls back.

Three scenarios (fixed seeds, fully deterministic):

1. good   -- true +3pp everywhere       -> promotes step by step to fleet.
2. bad    -- carpet -15pp, overall -4pp -> caught at the 1% canary, rolled back.
3. masked -- overall ~flat, but carpet -8pp masked by a hardwood win.
             An aggregate-only gate PROMOTES this model; the per-cohort gate
             rolls it back. This is why the gate slices by cohort.

Run: ``/usr/bin/python3 rollout.py``
"""

import random
import tempfile
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from gate import (
    ArmCounts,
    Decision,
    GateConfig,
    GateReport,
    evaluate,
    merge_cohorts,
)
from registry import ModelRegistry, Stage

# ----------------------------------------------------------------------
# Fleet / cohort model
# ----------------------------------------------------------------------

FLEET_SIZE = 10_000
TASKS_PER_ROBOT_PER_DAY = 4
MAX_DAYS_PER_STAGE = 12

#: Robots assigned to the canary arm at each gated stage (control arm is a
#: matched set of the same size running the incumbent policy).
STAGE_ARM_SIZE: Dict[Stage, int] = {
    Stage.CANARY_1PCT: FLEET_SIZE // 100,  # 100 robots
    Stage.CANARY_10PCT: FLEET_SIZE // 10,  # 1,000 robots
}

#: Stages that require a gate decision, in rollout order.
GATED_STAGES: List[Stage] = [Stage.CANARY_1PCT, Stage.CANARY_10PCT]


@dataclass(frozen=True)
class CohortSpec:
    """A task cohort with its share of daily tasks and baseline success rate."""

    name: str
    weight: float
    baseline_rate: float


COHORTS: List[CohortSpec] = [
    CohortSpec(name="hardwood", weight=0.75, baseline_rate=0.90),
    CohortSpec(name="carpet", weight=0.25, baseline_rate=0.70),
]


@dataclass(frozen=True)
class ModelProfile:
    """Ground-truth behaviour of a candidate model (unknown to the gate).

    ``deltas`` maps cohort name -> true change in success rate vs baseline.
    """

    name: str
    deltas: Dict[str, float]

    def true_rate(self, cohort: CohortSpec) -> float:
        rate = cohort.baseline_rate + self.deltas.get(cohort.name, 0.0)
        return min(1.0, max(0.0, rate))


GOOD_MODEL = ModelProfile(name="good", deltas={"hardwood": +0.03, "carpet": +0.03})
# carpet -15pp, weighted overall = 0.75*(-0.005) + 0.25*(-0.15) ~= -4pp
BAD_MODEL = ModelProfile(name="bad", deltas={"hardwood": -0.005, "carpet": -0.15})
# overall = 0.75*(+0.027) + 0.25*(-0.08) ~= +0.03pp: flat in aggregate,
# badly regressed on carpet.
MASKED_MODEL = ModelProfile(name="masked", deltas={"hardwood": +0.027, "carpet": -0.08})


# ----------------------------------------------------------------------
# Simulator
# ----------------------------------------------------------------------


class FleetSimulator:
    """Draws daily per-cohort task outcomes for a canary arm and its control.

    Deterministic given the seed. Pure stdlib ``random`` -- sample sizes are
    small enough that O(n) Bernoulli draws are instant.
    """

    def __init__(self, seed: int) -> None:
        self._rng = random.Random(seed)

    def sample_day(
        self, arm_robots: int, candidate: ModelProfile
    ) -> Dict[str, Tuple[ArmCounts, ArmCounts]]:
        """One observation day; returns cohort -> (canary, control) counts."""
        total_tasks = arm_robots * TASKS_PER_ROBOT_PER_DAY
        day: Dict[str, Tuple[ArmCounts, ArmCounts]] = {}
        remaining = total_tasks
        for i, cohort in enumerate(COHORTS):
            if i == len(COHORTS) - 1:
                n_tasks = remaining  # keep the split exact
            else:
                n_tasks = int(round(total_tasks * cohort.weight))
                remaining -= n_tasks
            canary = self._binomial(n_tasks, candidate.true_rate(cohort))
            control = self._binomial(n_tasks, cohort.baseline_rate)
            day[cohort.name] = (
                ArmCounts(successes=canary, trials=n_tasks),
                ArmCounts(successes=control, trials=n_tasks),
            )
        return day

    def _binomial(self, n: int, p: float) -> int:
        rng = self._rng
        return sum(1 for _ in range(n) if rng.random() < p)


def _accumulate(
    total: Dict[str, Tuple[ArmCounts, ArmCounts]],
    day: Dict[str, Tuple[ArmCounts, ArmCounts]],
) -> Dict[str, Tuple[ArmCounts, ArmCounts]]:
    """Merge one day of counts into the running per-cohort totals."""
    merged: Dict[str, Tuple[ArmCounts, ArmCounts]] = dict(total)
    for name, (canary_day, control_day) in day.items():
        canary_old, control_old = merged.get(name, (ArmCounts(0, 0), ArmCounts(0, 0)))
        merged[name] = (
            ArmCounts(
                successes=canary_old.successes + canary_day.successes,
                trials=canary_old.trials + canary_day.trials,
            ),
            ArmCounts(
                successes=control_old.successes + control_day.successes,
                trials=control_old.trials + control_day.trials,
            ),
        )
    return merged


# ----------------------------------------------------------------------
# Rollout controller
# ----------------------------------------------------------------------


@dataclass
class RolloutResult:
    """Outcome of one candidate rollout, with a full decision audit trail."""

    version_id: str
    terminal_stage: Stage
    decision_log: List[Dict[str, object]] = field(default_factory=list)

    def had_insufficient_sample_hold(self) -> bool:
        """True if any HOLD was caused by the minimum-sample guard."""
        for entry in self.decision_log:
            reasons: Dict[str, str] = entry["reasons"]  # type: ignore[assignment]
            if entry["decision"] == Decision.HOLD.value and any(
                "insufficient" in reason for reason in reasons.values()
            ):
                return True
        return False


def run_rollout(
    candidate: ModelProfile,
    registry: ModelRegistry,
    version_id: str,
    train_manifest_id: str,
    parent_version: Optional[str],
    seed: int,
    gate_config: Optional[GateConfig] = None,
    log: Callable[[str], None] = print,
) -> RolloutResult:
    """Drive one candidate through the staged rollout under gate control.

    Returns a :class:`RolloutResult`; the registry ends at ``fleet`` or
    ``rolled_back`` (never stuck mid-canary: budget exhaustion fails closed).
    """
    config = gate_config if gate_config is not None else GateConfig()
    simulator = FleetSimulator(seed=seed)
    result = RolloutResult(version_id=version_id, terminal_stage=Stage.STAGED)

    registry.register(version_id, train_manifest_id, parent_version)
    registry.promote(version_id, reason="start 1%% canary for %s" % candidate.name)
    log(
        "[%s] registered (manifest=%s, parent=%s) -> canary_1pct"
        % (version_id, train_manifest_id, parent_version)
    )

    for stage in GATED_STAGES:
        arm_robots = STAGE_ARM_SIZE[stage]
        counts: Dict[str, Tuple[ArmCounts, ArmCounts]] = {}
        decided = False
        for day in range(1, MAX_DAYS_PER_STAGE + 1):
            counts = _accumulate(counts, simulator.sample_day(arm_robots, candidate))
            report = evaluate(counts, config)
            _log_report(result, log, stage, day, report)
            if report.decision is Decision.PROMOTE:
                new_stage = registry.promote(
                    version_id,
                    reason="gate promote at %s day %d" % (stage.value, day),
                )
                log("  -> PROMOTE to %s" % new_stage.value)
                decided = True
                break
            if report.decision is Decision.ROLLBACK:
                registry.rollback(
                    version_id,
                    reason="gate rollback at %s day %d" % (stage.value, day),
                )
                log("  -> ROLLBACK (auto)")
                result.terminal_stage = Stage.ROLLED_BACK
                return result
            # HOLD: keep observing.
        if not decided:
            registry.rollback(
                version_id,
                reason="no decision within %d days at %s (fail closed)"
                % (MAX_DAYS_PER_STAGE, stage.value),
            )
            log("  -> ROLLBACK (observation budget exhausted, fail closed)")
            result.terminal_stage = Stage.ROLLED_BACK
            return result

    result.terminal_stage = registry.get(version_id).stage
    log("[%s] terminal stage: %s" % (version_id, result.terminal_stage.value))
    return result


def _log_report(
    result: RolloutResult,
    log: Callable[[str], None],
    stage: Stage,
    day: int,
    report: GateReport,
) -> None:
    reasons = {v.cohort: v.reason for v in report.verdicts}
    result.decision_log.append(
        {
            "stage": stage.value,
            "day": day,
            "decision": report.decision.value,
            "reasons": reasons,
        }
    )
    log("  %s day %d: %s" % (stage.value, day, report.decision.value.upper()))
    for verdict in report.verdicts:
        log(
            "      %-8s %-8s %s"
            % (verdict.cohort, verdict.decision.value, verdict.reason)
        )


# ----------------------------------------------------------------------
# Scenario 3: why the gate must slice by cohort
# ----------------------------------------------------------------------


def demo_cohort_masking(
    registry: ModelRegistry,
    version_id: str,
    parent_version: Optional[str],
    seed: int,
    days: int = 6,
    log: Callable[[str], None] = print,
) -> Tuple[GateReport, GateReport]:
    """Run the masked model at the 1% canary and gate it two ways.

    Returns ``(aggregate_report, cohort_report)`` computed on the *same*
    accumulated counts. The aggregate gate promotes; the per-cohort gate
    rolls back, and the registry records the rollback.
    """
    config = GateConfig()
    simulator = FleetSimulator(seed=seed)
    registry.register(version_id, "manifest-masked-001", parent_version)
    registry.promote(version_id, reason="start 1% canary (masking demo)")

    counts: Dict[str, Tuple[ArmCounts, ArmCounts]] = {}
    arm_robots = STAGE_ARM_SIZE[Stage.CANARY_1PCT]
    for _ in range(days):
        counts = _accumulate(counts, simulator.sample_day(arm_robots, MASKED_MODEL))

    agg_canary, agg_control = merge_cohorts(counts)
    aggregate_report = evaluate({"all_tasks": (agg_canary, agg_control)}, config)
    cohort_report = evaluate(counts, config)

    log("[%s] %d days at 1%% canary, same data, two gates:" % (version_id, days))
    log("  aggregate-only gate: %s" % aggregate_report.decision.value.upper())
    for verdict in aggregate_report.verdicts:
        log(
            "      %-8s %-8s %s"
            % (verdict.cohort, verdict.decision.value, verdict.reason)
        )
    log("  per-cohort gate:     %s" % cohort_report.decision.value.upper())
    for verdict in cohort_report.verdicts:
        log(
            "      %-8s %-8s %s"
            % (verdict.cohort, verdict.decision.value, verdict.reason)
        )

    if cohort_report.decision is Decision.ROLLBACK:
        registry.rollback(version_id, reason="per-cohort gate: carpet regression")
        log("  -> ROLLBACK recorded (aggregate gate would have shipped this)")
    return aggregate_report, cohort_report


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------


def _setup_baseline(registry: ModelRegistry) -> str:
    """Register + fully promote the incumbent policy; return its version id."""
    baseline = "policy-v1"
    registry.register(baseline, "manifest-base-000", None)
    registry.promote(baseline, reason="baseline bootstrap")
    registry.promote(baseline, reason="baseline bootstrap")
    registry.promote(baseline, reason="baseline bootstrap")
    return baseline


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        registry = ModelRegistry(tmp + "/registry.jsonl")
        baseline = _setup_baseline(registry)
        print("incumbent fleet version: %s" % registry.current_fleet_version())

        print("\n=== scenario 1: good model (+3pp everywhere) ===")
        good = run_rollout(
            GOOD_MODEL,
            registry,
            "policy-v2-good",
            "manifest-good-001",
            parent_version=baseline,
            seed=11,
        )
        print("terminal: %s\n" % good.terminal_stage.value)

        print("=== scenario 2: bad model (carpet -15pp, overall -4pp) ===")
        bad = run_rollout(
            BAD_MODEL,
            registry,
            "policy-v2-bad",
            "manifest-bad-001",
            parent_version=baseline,
            seed=13,
        )
        print("terminal: %s\n" % bad.terminal_stage.value)

        print("=== scenario 3: flat overall, carpet regression (masking) ===")
        demo_cohort_masking(
            registry, "policy-v2-masked", parent_version=baseline, seed=17
        )

        print(
            "\nfleet version after all three rollouts: %s"
            % registry.current_fleet_version()
        )
        print(
            "lineage of policy-v2-good: %s"
            % " <- ".join(registry.lineage("policy-v2-good"))
        )


if __name__ == "__main__":
    main()
```




## test_ota.py

```python
"""Tests for the OTA canary lab. Plain asserts, no pytest.

Run: /usr/bin/python3 test_ota.py
"""

import os
import tempfile

from gate import (
    ArmCounts,
    Decision,
    GateConfig,
    evaluate,
    evaluate_cohort,
    merge_cohorts,
    two_proportion_z,
    wilson_interval,
)
from registry import (
    DuplicateVersionError,
    IllegalTransitionError,
    ModelRegistry,
    Stage,
    UnknownVersionError,
)
from rollout import (
    BAD_MODEL,
    GOOD_MODEL,
    demo_cohort_masking,
    run_rollout,
)


def _quiet(_msg: str) -> None:
    """Silent logger for rollout runs inside tests."""


# ----------------------------------------------------------------------
# registry.py
# ----------------------------------------------------------------------


def test_registry_happy_path_and_lineage() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "reg.jsonl")
        reg = ModelRegistry(path)
        reg.register("v1", "manifest-a", None)
        assert reg.get("v1").stage is Stage.STAGED
        assert reg.promote("v1") is Stage.CANARY_1PCT
        assert reg.promote("v1") is Stage.CANARY_10PCT
        assert reg.promote("v1") is Stage.FLEET
        assert reg.current_fleet_version() == "v1"

        reg.register("v2", "manifest-b", parent_version="v1")
        assert reg.lineage("v2") == ["v2", "v1"]
        assert reg.get("v2").train_manifest_id == "manifest-b"

        # Persistence: replaying the JSONL reproduces identical state.
        reg2 = ModelRegistry(path)
        assert reg2.get("v1").stage is Stage.FLEET
        assert reg2.get("v2").stage is Stage.STAGED
        assert reg2.lineage("v2") == ["v2", "v1"]
        assert len(reg2.get("v1").history) == 3


def test_registry_illegal_transitions_raise() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        reg = ModelRegistry(os.path.join(tmp, "reg.jsonl"))
        reg.register("v1", "manifest-a", None)

        # Rollback from staged: nothing is deployed -> illegal.
        try:
            reg.rollback("v1", "nope")
            assert False, "expected IllegalTransitionError"
        except IllegalTransitionError:
            pass

        # Promote past fleet -> illegal.
        reg.promote("v1")
        reg.promote("v1")
        reg.promote("v1")
        try:
            reg.promote("v1")
            assert False, "expected IllegalTransitionError"
        except IllegalTransitionError:
            pass

        # rolled_back is terminal: no promote, no second rollback.
        reg.rollback("v1", "post-mortem: bad release")
        assert reg.get("v1").stage is Stage.ROLLED_BACK
        try:
            reg.promote("v1")
            assert False, "expected IllegalTransitionError"
        except IllegalTransitionError:
            pass
        try:
            reg.rollback("v1", "again")
            assert False, "expected IllegalTransitionError"
        except IllegalTransitionError:
            pass

        # Duplicate register / unknown version / unknown parent.
        try:
            reg.register("v1", "manifest-x", None)
            assert False, "expected DuplicateVersionError"
        except DuplicateVersionError:
            pass
        try:
            reg.promote("ghost")
            assert False, "expected UnknownVersionError"
        except UnknownVersionError:
            pass
        try:
            reg.register("v2", "manifest-b", parent_version="ghost")
            assert False, "expected UnknownVersionError"
        except UnknownVersionError:
            pass

        # Rollback must carry a reason.
        reg.register("v3", "manifest-c", None)
        reg.promote("v3")
        try:
            reg.rollback("v3", "")
            assert False, "expected ValueError"
        except ValueError:
            pass


# ----------------------------------------------------------------------
# gate.py
# ----------------------------------------------------------------------


def test_wilson_interval_sanity() -> None:
    low, high = wilson_interval(85, 100)
    assert 0.0 <= low < 0.85 < high <= 1.0
    # Tighter with more data.
    low2, high2 = wilson_interval(850, 1000)
    assert (high2 - low2) < (high - low)
    # Sane at the edges (Wald would collapse to a zero-width interval).
    low0, high0 = wilson_interval(0, 20)
    assert low0 == 0.0 and high0 > 0.0
    lowN, highN = wilson_interval(20, 20)
    assert highN == 1.0 and lowN < 1.0
    try:
        wilson_interval(1, 0)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_two_proportion_z_signs() -> None:
    better = two_proportion_z(ArmCounts(90, 100), ArmCounts(80, 100))
    worse = two_proportion_z(ArmCounts(80, 100), ArmCounts(90, 100))
    assert better > 0 and worse < 0
    assert abs(better + worse) < 1e-12  # antisymmetric
    # Degenerate pooled rate -> "no evidence", not a crash.
    assert two_proportion_z(ArmCounts(100, 100), ArmCounts(100, 100)) == 0.0


def test_arm_counts_validation() -> None:
    try:
        ArmCounts(successes=5, trials=3)
        assert False, "expected ValueError"
    except ValueError:
        pass
    try:
        ArmCounts(successes=-1, trials=3)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_gate_insufficient_samples_holds() -> None:
    config = GateConfig(min_trials_per_arm=200)
    # 50 trials of catastrophic regression: still HOLD, never a verdict on noise.
    verdict = evaluate_cohort("carpet", ArmCounts(10, 50), ArmCounts(45, 50), config)
    assert verdict.decision is Decision.HOLD
    assert "insufficient" in verdict.reason
    # Same rates with real sample size -> ROLLBACK.
    verdict2 = evaluate_cohort(
        "carpet", ArmCounts(200, 1000), ArmCounts(900, 1000), config
    )
    assert verdict2.decision is Decision.ROLLBACK


def test_gate_promote_hold_rollback() -> None:
    config = GateConfig()
    # Clearly better -> promote.
    up = evaluate_cohort("hardwood", ArmCounts(930, 1000), ArmCounts(900, 1000), config)
    assert up.decision is Decision.PROMOTE
    # Clearly worse -> rollback.
    down = evaluate_cohort("carpet", ArmCounts(550, 1000), ArmCounts(700, 1000), config)
    assert down.decision is Decision.ROLLBACK
    # Slightly worse, inconclusive at this n -> hold, keep observing.
    mid = evaluate_cohort("carpet", ArmCounts(158, 250), ArmCounts(175, 250), config)
    assert mid.decision is Decision.HOLD
    assert "insufficient" not in mid.reason
    # Empty input must not silently promote.
    try:
        evaluate({}, config)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_gate_cohort_masking_deterministic_counts() -> None:
    """Aggregate flat -> aggregate gate promotes; carpet cohort -> rollback."""
    config = GateConfig()
    cohorts = {
        "hardwood": (ArmCounts(1667, 1800), ArmCounts(1620, 1800)),  # +2.6pp
        "carpet": (ArmCounts(372, 600), ArmCounts(420, 600)),  # -8pp
    }
    agg_canary, agg_control = merge_cohorts(cohorts)
    assert agg_canary.trials == 2400 and agg_control.trials == 2400
    aggregate = evaluate({"all": (agg_canary, agg_control)}, config)
    assert aggregate.decision is Decision.PROMOTE  # the trap
    sliced = evaluate(cohorts, config)
    assert sliced.decision is Decision.ROLLBACK
    assert sliced.verdict_for("carpet").decision is Decision.ROLLBACK
    assert sliced.verdict_for("hardwood").decision is Decision.PROMOTE


# ----------------------------------------------------------------------
# rollout.py -- the three scenarios, end to end
# ----------------------------------------------------------------------


def test_scenario_good_model_reaches_fleet() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        reg = ModelRegistry(os.path.join(tmp, "reg.jsonl"))
        result = run_rollout(
            GOOD_MODEL,
            reg,
            "v-good",
            "manifest-good",
            None,
            seed=11,
            log=_quiet,
        )
        assert result.terminal_stage is Stage.FLEET
        assert reg.get("v-good").stage is Stage.FLEET
        # Day 1 at the 1% canary has only ~100 carpet trials/arm: the gate
        # must have HELD for insufficient samples instead of guessing.
        assert result.had_insufficient_sample_hold()
        # It went through both canary stages (no stage skipping).
        stages = [e["stage"] for e in result.decision_log]
        assert "canary_1pct" in stages and "canary_10pct" in stages


def test_scenario_bad_model_rolled_back_at_canary() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        reg = ModelRegistry(os.path.join(tmp, "reg.jsonl"))
        result = run_rollout(
            BAD_MODEL,
            reg,
            "v-bad",
            "manifest-bad",
            None,
            seed=13,
            log=_quiet,
        )
        assert result.terminal_stage is Stage.ROLLED_BACK
        assert reg.get("v-bad").stage is Stage.ROLLED_BACK
        # Caught at the FIRST canary stage: blast radius stayed at 1%.
        stages = {e["stage"] for e in result.decision_log}
        assert stages == {"canary_1pct"}
        # The audit trail shows why.
        last = result.decision_log[-1]
        assert last["decision"] == Decision.ROLLBACK.value
        assert "significantly worse" in last["reasons"]["carpet"]


def test_scenario_masked_regression_needs_cohort_gate() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        reg = ModelRegistry(os.path.join(tmp, "reg.jsonl"))
        aggregate, sliced = demo_cohort_masking(
            reg,
            "v-masked",
            parent_version=None,
            seed=17,
            log=_quiet,
        )
        # The trap: aggregate-only gate would NOT have rolled this back.
        assert aggregate.decision is not Decision.ROLLBACK
        # The per-cohort gate catches the carpet regression.
        assert sliced.decision is Decision.ROLLBACK
        assert sliced.verdict_for("carpet").decision is Decision.ROLLBACK
        assert reg.get("v-masked").stage is Stage.ROLLED_BACK


def main() -> None:
    tests = [
        test_registry_happy_path_and_lineage,
        test_registry_illegal_transitions_raise,
        test_wilson_interval_sanity,
        test_two_proportion_z_signs,
        test_arm_counts_validation,
        test_gate_insufficient_samples_holds,
        test_gate_promote_hold_rollback,
        test_gate_cohort_masking_deterministic_counts,
        test_scenario_good_model_reaches_fleet,
        test_scenario_bad_model_rolled_back_at_canary,
        test_scenario_masked_regression_needs_cohort_gate,
    ]
    for test in tests:
        test()
        print("PASS %s" % test.__name__)
    print("\n%d/%d tests passed" % (len(tests), len(tests)))


if __name__ == "__main__":
    main()
```

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/labs/lab2_ota_canary/README.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/labs/lab2_ota_canary/README.md)。作者整理资料；许可和第三方来源范围见阅读指南。
