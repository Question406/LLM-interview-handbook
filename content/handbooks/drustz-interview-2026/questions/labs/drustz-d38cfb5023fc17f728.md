---
id: drustz-d38cfb5023fc17f728
section: labs
order: 9
level: A
title: Lab 6 — Buggy Training：训练循环 Debug 演习
quick: 作者完整文档 · Lab 6 — Buggy Training：训练循环 Debug 演习
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/labs/lab6_buggy_training/README.md
    type: primary
---
# Lab 6 — Buggy Training：训练循环 Debug 演习

## 对应什么考点

The Bot Company（及 Cruise/Tesla 系面试官）的实战 ML debug 轮：**给你一段「表面正经」
但不收敛/表现异常的训练代码，现场诊断并修复**。这轮考的不是算法，是：

1. 从症状到假设的分诊能力（loss 曲线形状、开环/闭环指标背离、评估不可重复各指向什么）；
2. PyTorch 肌肉记忆（`model.eval()`/`no_grad`、DataLoader shuffle、mask 掉 padding、normalization链路）——
   这正是你自评的最大风险点，本 lab 就是练这个；
3. 机器人语境的加分意识：train-serve skew（normalization stats 要跟 checkpoint 一起落盘到机上）、
   动作后处理链路（normalization空间 vs 物理单位）、fleet 数据按 task/session 分块带来的order bias。

场景：BC（行为克隆）训练一个 2-D reach 任务的小 MLP policy，4 个「家庭任务」的脚本专家演示，
变长轨迹 + padding，闭环 rollout 评估成功率。五个植入 bug 全部来自真实事故模式：

| # | Bug | 可观察症状 |
| --- | --- | --- |
| 1 | normalization stats 用全量数据算（split 前） | 无——靠 code review 抓（这正是考点） |
| 2 | 反normalization和 clip 顺序颠倒 | loss 低但 rollout 成功率 ~0.05 |
| 3 | 数据按 task 排序 + loader 不 shuffle | epoch 内 loss 周期性震荡（by-quarter 打印） |
| 4 | 变长 padding 没从 loss 里 mask | train loss 被稀释得好看，模型被拉向均值动作 |
| 5 | eval 没有 `model.eval()`/`no_grad` | 同一模型评估两次结果不同（val MSE 和成功率都抖） |

## 文件

- `buggy_train.py` — 埋了 5 个 bug 的 BC 训练脚本（无任何 bug 标记，当面试题用）
- `HINTS.md` — 三级提示阶梯（症状 → 定位手段 → 行号），自练时逐级揭开
- `SOLUTIONS.md` — 每个 bug 的症状/诊断路径/修复/英文面试叙述 + 数字总结
- `fixed_train.py` — 修复版，每处修复有 `FIX #n` 注释，可与 buggy 版直接 diff
- `test_fixed.py` — 断言修复版收敛、评估 bit 级可复现、成功率比 buggy 版高 ≥0.4（实际 0.875）

## 15–30 分钟熟悉路径

解释器固定用：`/Users/mingrui/Documents/codes/interview/.venv/bin/python3`（Python 3.9.6，torch 2.8 CPU）。

1. **跑 buggy（3 分钟）**：

```text
/Users/mingrui/Documents/codes/interview/.venv/bin/python3 buggy_train.py
```



   只看输出，写下至少 3 个异常：by-quarter 的周期形状、val MSE #1≠#2、
   success #1≠#2 且都 ~0.05、train loss 0.076 与成功率 0.05 的矛盾。
2. **盲修（10–15 分钟，核心环节）**：不开 HINTS，自己在 `buggy_train.py` 里找。计时。
   卡住了再按 HINTS 的 L1→L2→L3 逐级揭。目标：L2 内抓到 4 个（stats 泄漏那个允许靠 diff 发现）。
3. **对答案（5 分钟）**：`diff buggy_train.py fixed_train.py`，逐个对照 SOLUTIONS.md，
   重点背每个 bug 的「诊断路径」而不是修复本身——面试考的是路径。
4. **验证（2 分钟）**：

```text
/Users/mingrui/Documents/codes/interview/.venv/bin/python3 fixed_train.py
/Users/mingrui/Documents/codes/interview/.venv/bin/python3 test_fixed.py
```



   预期：fixed 成功率 0.925 且两次评估 bit-identical；测试全绿约 10–25 秒。
5. **复述（3 分钟）**：不看材料，口头把五个「症状→假设→验证→修复」各讲 30 秒英文。

## 面试中怎么引用这段经验

> *"I keep a personal drill of the five training-loop bugs I've actually hit — leaked normalization stats, clip-before-denormalize, unshuffled task-sorted data, unmasked padding loss, and eval without model.eval() — and for each one I can go from the observable symptom to the diagnosis in a couple of minutes, because the symptom signatures (periodic loss, non-reproducible eval, good loss but failed rollouts) are distinct."*

追问时的展开点见 `SOLUTIONS.md` 末尾的「30 秒方法论」。

## 测试命令

```text
/Users/mingrui/Documents/codes/interview/.venv/bin/python3 test_fixed.py
```



plain assert，无 pytest 依赖；CPU、全 seed，整套约 10–25 秒（视机器负载），三次连跑输出 bit 级一致。

## buggy_train.py

```python
#!/usr/bin/env python3
"""Behavior-cloning trainer for the 2-D reach task.

Trains a small MLP policy on scripted expert demonstrations collected
across four household "tasks" (goal regions), then evaluates the policy
both on held-out MSE and on closed-loop rollout success rate.

Usage:
    python3 buggy_train.py
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EnvConfig:
    """Physical parameters of the planar reach environment."""

    workspace_low: float = -1.0
    workspace_high: float = 1.0
    max_action: float = 0.1  # actuator limit, per axis, per step
    success_radius: float = 0.08
    obs_dim: int = 4  # [ee_x, ee_y, goal_x, goal_y]
    action_dim: int = 2  # [dx, dy]


@dataclass(frozen=True)
class TaskSpec:
    """One data-collection task: a goal region plus expert controller gains."""

    task_id: int
    goal_center: Tuple[float, float]
    goal_jitter: float
    kp: float  # proportional gain of the scripted expert
    noise_std: float  # actuation noise during data collection


@dataclass(frozen=True)
class TrainConfig:
    """Hyper-parameters for behavior cloning."""

    seed: int = 0
    num_demos: int = 200
    max_demo_steps: int = 25
    val_every: int = 5  # every 5th trajectory is held out for validation
    batch_size: int = 16
    epochs: int = 15
    lr: float = 1e-3
    hidden_dim: int = 64
    dropout: float = 0.15
    eval_episodes: int = 40
    eval_max_steps: int = 40


def default_tasks() -> List[TaskSpec]:
    """The four goal regions used by the demo-collection fleet."""
    return [
        TaskSpec(0, (0.80, 0.75), 0.10, 0.50, 0.004),
        TaskSpec(1, (0.70, -0.70), 0.10, 0.65, 0.007),
        TaskSpec(2, (-0.75, 0.60), 0.10, 0.80, 0.010),
        TaskSpec(3, (0.65, 0.15), 0.10, 0.95, 0.013),
    ]


# ---------------------------------------------------------------------------
# Environment and expert
# ---------------------------------------------------------------------------


class ReachEnv:
    """Deterministic point-mass environment: move the end-effector to a goal."""

    def __init__(
        self, env_cfg: EnvConfig, task: TaskSpec, rng: np.random.Generator
    ) -> None:
        self._cfg = env_cfg
        self._task = task
        self._rng = rng
        self._pos = np.zeros(2, dtype=np.float32)
        self._goal = np.zeros(2, dtype=np.float32)

    @property
    def position(self) -> np.ndarray:
        return self._pos.copy()

    @property
    def goal(self) -> np.ndarray:
        return self._goal.copy()

    @property
    def distance_to_goal(self) -> float:
        return float(np.linalg.norm(self._goal - self._pos))

    def reset(self) -> np.ndarray:
        """Sample a new episode: jittered goal, start near the origin."""
        center = np.asarray(self._task.goal_center, dtype=np.float32)
        jitter = self._rng.uniform(
            -self._task.goal_jitter, self._task.goal_jitter, size=2
        )
        self._goal = np.clip(
            center + jitter.astype(np.float32),
            self._cfg.workspace_low,
            self._cfg.workspace_high,
        )
        start = self._rng.normal(0.0, 0.05, size=2).astype(np.float32)
        self._pos = np.clip(start, self._cfg.workspace_low, self._cfg.workspace_high)
        return self._observation()

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, bool]:
        """Apply one delta-position action. Returns (observation, done)."""
        action = np.asarray(action, dtype=np.float32)
        if action.shape != (self._cfg.action_dim,):
            raise ValueError(
                "expected action shape (%d,), got %s"
                % (self._cfg.action_dim, action.shape)
            )
        if not np.all(np.isfinite(action)):
            raise ValueError("non-finite action: %s" % action)
        action = np.clip(action, -self._cfg.max_action, self._cfg.max_action)
        self._pos = np.clip(
            self._pos + action, self._cfg.workspace_low, self._cfg.workspace_high
        )
        done = self.distance_to_goal < self._cfg.success_radius
        return self._observation(), done

    def _observation(self) -> np.ndarray:
        return np.concatenate([self._pos, self._goal]).astype(np.float32)


def expert_action(
    position: np.ndarray,
    goal: np.ndarray,
    task: TaskSpec,
    env_cfg: EnvConfig,
    rng: np.random.Generator,
) -> np.ndarray:
    """Scripted proportional controller with actuation noise."""
    raw = task.kp * (goal - position)
    noise = rng.normal(0.0, task.noise_std, size=2)
    return np.clip(raw + noise, -env_cfg.max_action, env_cfg.max_action).astype(
        np.float32
    )


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------


@dataclass
class Trajectory:
    """One expert demonstration (variable length)."""

    task_id: int
    observations: np.ndarray  # (T, obs_dim) float32
    actions: np.ndarray  # (T, action_dim) float32

    @property
    def length(self) -> int:
        return int(self.observations.shape[0])


def generate_demonstrations(
    env_cfg: EnvConfig,
    tasks: List[TaskSpec],
    num_demos: int,
    max_steps: int,
    rng: np.random.Generator,
) -> List[Trajectory]:
    """Roll out the scripted expert; tasks are interleaved round-robin."""
    trajectories: List[Trajectory] = []
    for demo_idx in range(num_demos):
        task = tasks[demo_idx % len(tasks)]
        env = ReachEnv(env_cfg, task, rng)
        obs = env.reset()
        obs_list: List[np.ndarray] = []
        act_list: List[np.ndarray] = []
        for _ in range(max_steps):
            action = expert_action(env.position, env.goal, task, env_cfg, rng)
            obs_list.append(obs)
            act_list.append(action)
            obs, done = env.step(action)
            if done:
                break
        if not obs_list:
            raise RuntimeError("expert produced an empty demonstration")
        trajectories.append(
            Trajectory(
                task_id=task.task_id,
                observations=np.stack(obs_list),
                actions=np.stack(act_list),
            )
        )
    return trajectories


@dataclass(frozen=True)
class NormStats:
    """Per-dimension normalization statistics for observations and actions."""

    obs_mean: np.ndarray
    obs_std: np.ndarray
    act_mean: np.ndarray
    act_std: np.ndarray

    @staticmethod
    def from_trajectories(trajectories: List[Trajectory]) -> "NormStats":
        if not trajectories:
            raise ValueError("cannot compute statistics from zero trajectories")
        all_obs = np.concatenate([t.observations for t in trajectories], axis=0)
        all_act = np.concatenate([t.actions for t in trajectories], axis=0)
        eps = 1e-6
        return NormStats(
            obs_mean=all_obs.mean(axis=0),
            obs_std=all_obs.std(axis=0) + eps,
            act_mean=all_act.mean(axis=0),
            act_std=all_act.std(axis=0) + eps,
        )


class TrajectoryDataset(Dataset):
    """Pads normalized variable-length trajectories to a common length."""

    def __init__(
        self,
        trajectories: List[Trajectory],
        stats: NormStats,
        pad_to: Optional[int] = None,
    ) -> None:
        if not trajectories:
            raise ValueError("dataset needs at least one trajectory")
        lengths = [t.length for t in trajectories]
        self.pad_to = int(pad_to) if pad_to is not None else max(lengths)
        if max(lengths) > self.pad_to:
            raise ValueError(
                "pad_to=%d smaller than longest trajectory %d"
                % (self.pad_to, max(lengths))
            )
        n = len(trajectories)
        obs_dim = trajectories[0].observations.shape[1]
        act_dim = trajectories[0].actions.shape[1]
        obs = np.zeros((n, self.pad_to, obs_dim), dtype=np.float32)
        act = np.zeros((n, self.pad_to, act_dim), dtype=np.float32)
        for i, traj in enumerate(trajectories):
            t_len = traj.length
            obs[i, :t_len] = (traj.observations - stats.obs_mean) / stats.obs_std
            act[i, :t_len] = (traj.actions - stats.act_mean) / stats.act_std
        self.observations = torch.from_numpy(obs)
        self.actions = torch.from_numpy(act)
        self.lengths = torch.tensor(lengths, dtype=torch.long)

    def __len__(self) -> int:
        return self.observations.shape[0]

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        return self.observations[idx], self.actions[idx], self.lengths[idx]


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


class PolicyNet(nn.Module):
    """MLP that maps a normalized observation to a normalized action."""

    def __init__(
        self, obs_dim: int, action_dim: int, hidden_dim: int, dropout: float
    ) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, action_dim),
        )

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        return self.net(obs)


# ---------------------------------------------------------------------------
# Training and evaluation
# ---------------------------------------------------------------------------


def _chunk_means(values: List[float], num_chunks: int) -> List[float]:
    """Mean of `values` split into `num_chunks` contiguous chunks."""
    if not values:
        return []
    chunks = np.array_split(np.asarray(values, dtype=np.float64), num_chunks)
    return [float(c.mean()) for c in chunks if c.size > 0]


def evaluate_mse(model: PolicyNet, loader: DataLoader) -> float:
    """Action-prediction MSE on a held-out set (normalized units)."""
    total = 0.0
    batches = 0
    for obs, act, _lengths in loader:
        pred = model(obs)
        total += F.mse_loss(pred, act).item()
        batches += 1
    if batches == 0:
        raise RuntimeError("validation loader is empty")
    return total / batches


def train_policy(
    model: PolicyNet,
    train_loader: DataLoader,
    val_loader: DataLoader,
    cfg: TrainConfig,
) -> Dict[str, List[float]]:
    """Run the BC optimization loop; returns loss history for inspection."""
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr)
    history: Dict[str, List[float]] = {"epoch_loss": [], "val_mse": []}
    for epoch in range(cfg.epochs):
        batch_losses: List[float] = []
        for obs, act, lengths in train_loader:
            pred = model(obs)
            loss = F.mse_loss(pred, act)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            batch_losses.append(loss.item())
        epoch_loss = float(np.mean(batch_losses))
        val_mse = evaluate_mse(model, val_loader)
        history["epoch_loss"].append(epoch_loss)
        history["val_mse"].append(val_mse)
        quarters = " ".join("%.4f" % q for q in _chunk_means(batch_losses, 4))
        print(
            "epoch %02d | train %.4f | by-quarter [%s] | val %.4f"
            % (epoch, epoch_loss, quarters, val_mse)
        )
    return history


def evaluate_rollout(
    model: PolicyNet,
    stats: NormStats,
    env_cfg: EnvConfig,
    tasks: List[TaskSpec],
    num_episodes: int,
    max_steps: int,
    seed: int,
) -> float:
    """Closed-loop evaluation: fraction of episodes that reach the goal."""
    rng = np.random.default_rng(seed)
    successes = 0
    for episode in range(num_episodes):
        task = tasks[episode % len(tasks)]
        env = ReachEnv(env_cfg, task, rng)
        obs = env.reset()
        done = False
        for _ in range(max_steps):
            obs_norm = (obs - stats.obs_mean) / stats.obs_std
            obs_t = torch.from_numpy(obs_norm.astype(np.float32)).unsqueeze(0)
            pred = model(obs_t).detach().squeeze(0).numpy()
            action = (
                np.clip(pred, -env_cfg.max_action, env_cfg.max_action) * stats.act_std
                + stats.act_mean
            )
            obs, done = env.step(action.astype(np.float32))
            if done:
                break
        if done:
            successes += 1
    return successes / float(num_episodes)


# ---------------------------------------------------------------------------
# Experiment driver
# ---------------------------------------------------------------------------


def run_experiment(cfg: TrainConfig) -> Dict[str, float]:
    """Train a BC policy end to end and return summary metrics."""
    if cfg.epochs <= 0 or cfg.batch_size <= 0:
        raise ValueError("epochs and batch_size must be positive")
    if cfg.num_demos < 4 * cfg.val_every:
        raise ValueError("num_demos too small for the validation split")

    torch.manual_seed(cfg.seed)
    rng = np.random.default_rng(cfg.seed)
    env_cfg = EnvConfig()
    tasks = default_tasks()

    trajectories = generate_demonstrations(
        env_cfg, tasks, cfg.num_demos, cfg.max_demo_steps, rng
    )
    # Keep the dataset grouped by task so per-task slices are easy to inspect.
    trajectories.sort(key=lambda t: t.task_id)

    stats = NormStats.from_trajectories(trajectories)

    val_trajs = trajectories[:: cfg.val_every]
    train_trajs = [t for i, t in enumerate(trajectories) if i % cfg.val_every != 0]

    train_ds = TrajectoryDataset(train_trajs, stats)
    val_ds = TrajectoryDataset(val_trajs, stats)
    train_loader = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=False)
    val_loader = DataLoader(val_ds, batch_size=cfg.batch_size, shuffle=False)

    model = PolicyNet(env_cfg.obs_dim, env_cfg.action_dim, cfg.hidden_dim, cfg.dropout)
    history = train_policy(model, train_loader, val_loader, cfg)

    # Repeatability sanity check: same model, same data, run twice.
    final_val_mse = evaluate_mse(model, val_loader)
    final_val_mse_recheck = evaluate_mse(model, val_loader)

    success_first = evaluate_rollout(
        model,
        stats,
        env_cfg,
        tasks,
        cfg.eval_episodes,
        cfg.eval_max_steps,
        seed=cfg.seed + 1,
    )
    success_second = evaluate_rollout(
        model,
        stats,
        env_cfg,
        tasks,
        cfg.eval_episodes,
        cfg.eval_max_steps,
        seed=cfg.seed + 1,
    )

    return {
        "first_epoch_train_loss": history["epoch_loss"][0],
        "final_epoch_train_loss": history["epoch_loss"][-1],
        "final_val_mse": final_val_mse,
        "final_val_mse_recheck": final_val_mse_recheck,
        "success_rate_first": success_first,
        "success_rate_second": success_second,
    }


def main() -> None:
    cfg = TrainConfig()
    print("== behavior cloning on 2-D reach (seed=%d) ==" % cfg.seed)
    start = time.time()
    metrics = run_experiment(cfg)
    print("-" * 60)
    print("final train loss      : %.4f" % metrics["final_epoch_train_loss"])
    print("final val MSE (#1)    : %.4f" % metrics["final_val_mse"])
    print("final val MSE (#2)    : %.4f" % metrics["final_val_mse_recheck"])
    print("rollout success (#1)  : %.3f" % metrics["success_rate_first"])
    print("rollout success (#2)  : %.3f" % metrics["success_rate_second"])
    print("wall time             : %.1fs" % (time.time() - start))


if __name__ == "__main__":
    main()
```




## fixed_train.py

```python
#!/usr/bin/env python3
"""Fixed behavior-cloning trainer for the 2-D reach task.

Same structure as buggy_train.py with the five bugs repaired. Every fix
is marked with a `FIX #n` comment so you can diff the two files:

    FIX #1  normalization statistics computed on the TRAIN split only
    FIX #2  de-normalize the policy output BEFORE clipping to actuator limits
    FIX #3  do not sort by task; shuffle the DataLoader (seeded generator)
    FIX #4  mask padded timesteps out of the MSE loss
    FIX #5  model.eval() + torch.no_grad() on every evaluation path

Usage:
    python3 fixed_train.py
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EnvConfig:
    """Physical parameters of the planar reach environment."""

    workspace_low: float = -1.0
    workspace_high: float = 1.0
    max_action: float = 0.1  # actuator limit, per axis, per step
    success_radius: float = 0.08
    obs_dim: int = 4  # [ee_x, ee_y, goal_x, goal_y]
    action_dim: int = 2  # [dx, dy]


@dataclass(frozen=True)
class TaskSpec:
    """One data-collection task: a goal region plus expert controller gains."""

    task_id: int
    goal_center: Tuple[float, float]
    goal_jitter: float
    kp: float  # proportional gain of the scripted expert
    noise_std: float  # actuation noise during data collection


@dataclass(frozen=True)
class TrainConfig:
    """Hyper-parameters for behavior cloning."""

    seed: int = 0
    num_demos: int = 200
    max_demo_steps: int = 25
    val_every: int = 5  # every 5th trajectory is held out for validation
    batch_size: int = 16
    epochs: int = 15
    lr: float = 1e-3
    hidden_dim: int = 64
    dropout: float = 0.15
    eval_episodes: int = 40
    eval_max_steps: int = 40


def default_tasks() -> List[TaskSpec]:
    """The four goal regions used by the demo-collection fleet."""
    return [
        TaskSpec(0, (0.80, 0.75), 0.10, 0.50, 0.004),
        TaskSpec(1, (0.70, -0.70), 0.10, 0.65, 0.007),
        TaskSpec(2, (-0.75, 0.60), 0.10, 0.80, 0.010),
        TaskSpec(3, (0.65, 0.15), 0.10, 0.95, 0.013),
    ]


# ---------------------------------------------------------------------------
# Environment and expert (identical to buggy_train.py)
# ---------------------------------------------------------------------------


class ReachEnv:
    """Deterministic point-mass environment: move the end-effector to a goal."""

    def __init__(
        self, env_cfg: EnvConfig, task: TaskSpec, rng: np.random.Generator
    ) -> None:
        self._cfg = env_cfg
        self._task = task
        self._rng = rng
        self._pos = np.zeros(2, dtype=np.float32)
        self._goal = np.zeros(2, dtype=np.float32)

    @property
    def position(self) -> np.ndarray:
        return self._pos.copy()

    @property
    def goal(self) -> np.ndarray:
        return self._goal.copy()

    @property
    def distance_to_goal(self) -> float:
        return float(np.linalg.norm(self._goal - self._pos))

    def reset(self) -> np.ndarray:
        """Sample a new episode: jittered goal, start near the origin."""
        center = np.asarray(self._task.goal_center, dtype=np.float32)
        jitter = self._rng.uniform(
            -self._task.goal_jitter, self._task.goal_jitter, size=2
        )
        self._goal = np.clip(
            center + jitter.astype(np.float32),
            self._cfg.workspace_low,
            self._cfg.workspace_high,
        )
        start = self._rng.normal(0.0, 0.05, size=2).astype(np.float32)
        self._pos = np.clip(start, self._cfg.workspace_low, self._cfg.workspace_high)
        return self._observation()

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, bool]:
        """Apply one delta-position action. Returns (observation, done)."""
        action = np.asarray(action, dtype=np.float32)
        if action.shape != (self._cfg.action_dim,):
            raise ValueError(
                "expected action shape (%d,), got %s"
                % (self._cfg.action_dim, action.shape)
            )
        if not np.all(np.isfinite(action)):
            raise ValueError("non-finite action: %s" % action)
        action = np.clip(action, -self._cfg.max_action, self._cfg.max_action)
        self._pos = np.clip(
            self._pos + action, self._cfg.workspace_low, self._cfg.workspace_high
        )
        done = self.distance_to_goal < self._cfg.success_radius
        return self._observation(), done

    def _observation(self) -> np.ndarray:
        return np.concatenate([self._pos, self._goal]).astype(np.float32)


def expert_action(
    position: np.ndarray,
    goal: np.ndarray,
    task: TaskSpec,
    env_cfg: EnvConfig,
    rng: np.random.Generator,
) -> np.ndarray:
    """Scripted proportional controller with actuation noise."""
    raw = task.kp * (goal - position)
    noise = rng.normal(0.0, task.noise_std, size=2)
    return np.clip(raw + noise, -env_cfg.max_action, env_cfg.max_action).astype(
        np.float32
    )


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------


@dataclass
class Trajectory:
    """One expert demonstration (variable length)."""

    task_id: int
    observations: np.ndarray  # (T, obs_dim) float32
    actions: np.ndarray  # (T, action_dim) float32

    @property
    def length(self) -> int:
        return int(self.observations.shape[0])


def generate_demonstrations(
    env_cfg: EnvConfig,
    tasks: List[TaskSpec],
    num_demos: int,
    max_steps: int,
    rng: np.random.Generator,
) -> List[Trajectory]:
    """Roll out the scripted expert; tasks are interleaved round-robin."""
    trajectories: List[Trajectory] = []
    for demo_idx in range(num_demos):
        task = tasks[demo_idx % len(tasks)]
        env = ReachEnv(env_cfg, task, rng)
        obs = env.reset()
        obs_list: List[np.ndarray] = []
        act_list: List[np.ndarray] = []
        for _ in range(max_steps):
            action = expert_action(env.position, env.goal, task, env_cfg, rng)
            obs_list.append(obs)
            act_list.append(action)
            obs, done = env.step(action)
            if done:
                break
        if not obs_list:
            raise RuntimeError("expert produced an empty demonstration")
        trajectories.append(
            Trajectory(
                task_id=task.task_id,
                observations=np.stack(obs_list),
                actions=np.stack(act_list),
            )
        )
    return trajectories


@dataclass(frozen=True)
class NormStats:
    """Per-dimension normalization statistics for observations and actions."""

    obs_mean: np.ndarray
    obs_std: np.ndarray
    act_mean: np.ndarray
    act_std: np.ndarray

    @staticmethod
    def from_trajectories(trajectories: List[Trajectory]) -> "NormStats":
        if not trajectories:
            raise ValueError("cannot compute statistics from zero trajectories")
        all_obs = np.concatenate([t.observations for t in trajectories], axis=0)
        all_act = np.concatenate([t.actions for t in trajectories], axis=0)
        eps = 1e-6
        return NormStats(
            obs_mean=all_obs.mean(axis=0),
            obs_std=all_obs.std(axis=0) + eps,
            act_mean=all_act.mean(axis=0),
            act_std=all_act.std(axis=0) + eps,
        )


class TrajectoryDataset(Dataset):
    """Pads normalized variable-length trajectories to a common length."""

    def __init__(
        self,
        trajectories: List[Trajectory],
        stats: NormStats,
        pad_to: Optional[int] = None,
    ) -> None:
        if not trajectories:
            raise ValueError("dataset needs at least one trajectory")
        lengths = [t.length for t in trajectories]
        self.pad_to = int(pad_to) if pad_to is not None else max(lengths)
        if max(lengths) > self.pad_to:
            raise ValueError(
                "pad_to=%d smaller than longest trajectory %d"
                % (self.pad_to, max(lengths))
            )
        n = len(trajectories)
        obs_dim = trajectories[0].observations.shape[1]
        act_dim = trajectories[0].actions.shape[1]
        obs = np.zeros((n, self.pad_to, obs_dim), dtype=np.float32)
        act = np.zeros((n, self.pad_to, act_dim), dtype=np.float32)
        for i, traj in enumerate(trajectories):
            t_len = traj.length
            obs[i, :t_len] = (traj.observations - stats.obs_mean) / stats.obs_std
            act[i, :t_len] = (traj.actions - stats.act_mean) / stats.act_std
        self.observations = torch.from_numpy(obs)
        self.actions = torch.from_numpy(act)
        self.lengths = torch.tensor(lengths, dtype=torch.long)

    def __len__(self) -> int:
        return self.observations.shape[0]

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        return self.observations[idx], self.actions[idx], self.lengths[idx]


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


class PolicyNet(nn.Module):
    """MLP that maps a normalized observation to a normalized action."""

    def __init__(
        self, obs_dim: int, action_dim: int, hidden_dim: int, dropout: float
    ) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, action_dim),
        )

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        return self.net(obs)


# ---------------------------------------------------------------------------
# Training and evaluation
# ---------------------------------------------------------------------------


def _chunk_means(values: List[float], num_chunks: int) -> List[float]:
    """Mean of `values` split into `num_chunks` contiguous chunks."""
    if not values:
        return []
    chunks = np.array_split(np.asarray(values, dtype=np.float64), num_chunks)
    return [float(c.mean()) for c in chunks if c.size > 0]


def masked_mse(
    pred: torch.Tensor, target: torch.Tensor, lengths: torch.Tensor
) -> torch.Tensor:
    """MSE over valid (non-padded) timesteps only.

    FIX #4: padded timesteps are all-zero targets; averaging over them both
    dilutes the reported loss and biases the policy toward the mean action.
    """
    if pred.shape != target.shape:
        raise ValueError(
            "pred shape %s != target shape %s" % (pred.shape, target.shape)
        )
    max_len = pred.shape[1]
    # (B, T, 1) validity mask built from true lengths.
    mask = (torch.arange(max_len)[None, :] < lengths[:, None]).float().unsqueeze(-1)
    num_valid = mask.sum() * pred.shape[-1]
    if num_valid.item() == 0:
        raise RuntimeError("batch contains no valid timesteps")
    return ((pred - target) ** 2 * mask).sum() / num_valid


def evaluate_mse(model: PolicyNet, loader: DataLoader) -> float:
    """Action-prediction MSE on a held-out set (normalized units)."""
    was_training = model.training
    model.eval()  # FIX #5: deterministic eval (dropout off)
    total = 0.0
    batches = 0
    with torch.no_grad():  # FIX #5: no autograd graph during evaluation
        for obs, act, lengths in loader:
            pred = model(obs)
            total += masked_mse(pred, act, lengths).item()  # FIX #4
            batches += 1
    if was_training:
        model.train()
    if batches == 0:
        raise RuntimeError("validation loader is empty")
    return total / batches


def train_policy(
    model: PolicyNet,
    train_loader: DataLoader,
    val_loader: DataLoader,
    cfg: TrainConfig,
) -> Dict[str, List[float]]:
    """Run the BC optimization loop; returns loss history for inspection."""
    optimizer = torch.optim.Adam(model.parameters(), lr=cfg.lr)
    history: Dict[str, List[float]] = {"epoch_loss": [], "val_mse": []}
    for epoch in range(cfg.epochs):
        model.train()
        batch_losses: List[float] = []
        for obs, act, lengths in train_loader:
            pred = model(obs)
            loss = masked_mse(pred, act, lengths)  # FIX #4
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            batch_losses.append(loss.item())
        epoch_loss = float(np.mean(batch_losses))
        val_mse = evaluate_mse(model, val_loader)
        history["epoch_loss"].append(epoch_loss)
        history["val_mse"].append(val_mse)
        quarters = " ".join("%.4f" % q for q in _chunk_means(batch_losses, 4))
        print(
            "epoch %02d | train %.4f | by-quarter [%s] | val %.4f"
            % (epoch, epoch_loss, quarters, val_mse)
        )
    return history


def evaluate_rollout(
    model: PolicyNet,
    stats: NormStats,
    env_cfg: EnvConfig,
    tasks: List[TaskSpec],
    num_episodes: int,
    max_steps: int,
    seed: int,
) -> float:
    """Closed-loop evaluation: fraction of episodes that reach the goal."""
    rng = np.random.default_rng(seed)
    was_training = model.training
    model.eval()  # FIX #5: dropout must be off when driving the robot
    successes = 0
    with torch.no_grad():  # FIX #5
        for episode in range(num_episodes):
            task = tasks[episode % len(tasks)]
            env = ReachEnv(env_cfg, task, rng)
            obs = env.reset()
            done = False
            for _ in range(max_steps):
                obs_norm = (obs - stats.obs_mean) / stats.obs_std
                obs_t = torch.from_numpy(obs_norm.astype(np.float32)).unsqueeze(0)
                pred = model(obs_t).squeeze(0).numpy()
                # FIX #2: de-normalize back to physical units FIRST, then clip
                # to the actuator limit. Clipping the normalized output (std
                # ~1) at max_action (~0.1) collapses every saturated action.
                action = np.clip(
                    pred * stats.act_std + stats.act_mean,
                    -env_cfg.max_action,
                    env_cfg.max_action,
                )
                obs, done = env.step(action.astype(np.float32))
                if done:
                    break
            if done:
                successes += 1
    if was_training:
        model.train()
    return successes / float(num_episodes)


# ---------------------------------------------------------------------------
# Experiment driver
# ---------------------------------------------------------------------------


def run_experiment(cfg: TrainConfig) -> Dict[str, float]:
    """Train a BC policy end to end and return summary metrics."""
    if cfg.epochs <= 0 or cfg.batch_size <= 0:
        raise ValueError("epochs and batch_size must be positive")
    if cfg.num_demos < 4 * cfg.val_every:
        raise ValueError("num_demos too small for the validation split")

    torch.manual_seed(cfg.seed)
    rng = np.random.default_rng(cfg.seed)
    env_cfg = EnvConfig()
    tasks = default_tasks()

    trajectories = generate_demonstrations(
        env_cfg, tasks, cfg.num_demos, cfg.max_demo_steps, rng
    )
    # FIX #3: keep generation order (task-interleaved); no sort by task.

    val_trajs = trajectories[:: cfg.val_every]
    train_trajs = [t for i, t in enumerate(trajectories) if i % cfg.val_every != 0]

    # FIX #1: normalization statistics come from the TRAIN split only, and
    # these exact arrays are what would ship to the robot with the checkpoint.
    stats = NormStats.from_trajectories(train_trajs)

    train_ds = TrajectoryDataset(train_trajs, stats)
    val_ds = TrajectoryDataset(val_trajs, stats)
    # FIX #3: shuffle every epoch with a seeded generator for reproducibility.
    loader_gen = torch.Generator()
    loader_gen.manual_seed(cfg.seed)
    train_loader = DataLoader(
        train_ds, batch_size=cfg.batch_size, shuffle=True, generator=loader_gen
    )
    val_loader = DataLoader(val_ds, batch_size=cfg.batch_size, shuffle=False)

    model = PolicyNet(env_cfg.obs_dim, env_cfg.action_dim, cfg.hidden_dim, cfg.dropout)
    history = train_policy(model, train_loader, val_loader, cfg)

    # Repeatability sanity check: same model, same data, run twice.
    # With FIX #5 in place both numbers must be bit-identical.
    final_val_mse = evaluate_mse(model, val_loader)
    final_val_mse_recheck = evaluate_mse(model, val_loader)

    success_first = evaluate_rollout(
        model,
        stats,
        env_cfg,
        tasks,
        cfg.eval_episodes,
        cfg.eval_max_steps,
        seed=cfg.seed + 1,
    )
    success_second = evaluate_rollout(
        model,
        stats,
        env_cfg,
        tasks,
        cfg.eval_episodes,
        cfg.eval_max_steps,
        seed=cfg.seed + 1,
    )

    return {
        "first_epoch_train_loss": history["epoch_loss"][0],
        "final_epoch_train_loss": history["epoch_loss"][-1],
        "final_val_mse": final_val_mse,
        "final_val_mse_recheck": final_val_mse_recheck,
        "success_rate_first": success_first,
        "success_rate_second": success_second,
    }


def main() -> None:
    cfg = TrainConfig()
    print("== behavior cloning on 2-D reach, FIXED (seed=%d) ==" % cfg.seed)
    start = time.time()
    metrics = run_experiment(cfg)
    print("-" * 60)
    print("final train loss      : %.4f" % metrics["final_epoch_train_loss"])
    print("final val MSE (#1)    : %.4f" % metrics["final_val_mse"])
    print("final val MSE (#2)    : %.4f" % metrics["final_val_mse_recheck"])
    print("rollout success (#1)  : %.3f" % metrics["success_rate_first"])
    print("rollout success (#2)  : %.3f" % metrics["success_rate_second"])
    print("wall time             : %.1fs" % (time.time() - start))


if __name__ == "__main__":
    main()
```




## test_fixed.py

```python
#!/usr/bin/env python3
"""Tests for lab6: the fixed BC trainer must converge, evaluate
deterministically, and beat the buggy trainer by a wide margin.

Run:
    python3 test_fixed.py

Plain asserts only -- no pytest dependency. Everything is seeded, so all
comparisons (including exact float equality for determinism checks) are
stable on this pinned environment (CPU, torch 2.8, numpy 2.0.2).
"""

import contextlib
import io
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch

import buggy_train
import fixed_train


def run_silently(module) -> dict:
    """Run a module's experiment while swallowing its per-epoch prints."""
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        metrics = module.run_experiment(module.TrainConfig())
    return metrics


def main() -> None:
    start = time.time()

    print("[1/4] training buggy_train ...")
    buggy = run_silently(buggy_train)
    print("[2/4] training fixed_train ...")
    fixed = run_silently(fixed_train)
    print("[3/4] re-training fixed_train (determinism check) ...")
    fixed_again = run_silently(fixed_train)
    print("[4/4] asserting ...")

    # --- 1. fixed trainer converges -------------------------------------
    assert fixed["final_epoch_train_loss"] < 0.5 * fixed["first_epoch_train_loss"], (
        "fixed loss did not drop: first=%.4f final=%.4f"
        % (fixed["first_epoch_train_loss"], fixed["final_epoch_train_loss"])
    )
    assert fixed["final_epoch_train_loss"] < 0.15, (
        "fixed final loss too high: %.4f" % fixed["final_epoch_train_loss"]
    )

    # --- 2. fixed policy actually reaches goals -------------------------
    assert fixed["success_rate_first"] >= 0.90, (
        "fixed success rate too low: %.3f" % fixed["success_rate_first"]
    )

    # --- 3. fixed evaluation is repeatable (model.eval + no_grad) -------
    assert fixed["success_rate_first"] == fixed["success_rate_second"], (
        "fixed rollout eval not repeatable: %.3f vs %.3f"
        % (fixed["success_rate_first"], fixed["success_rate_second"])
    )
    assert fixed["final_val_mse"] == fixed["final_val_mse_recheck"], (
        "fixed val MSE not repeatable: %.6f vs %.6f"
        % (fixed["final_val_mse"], fixed["final_val_mse_recheck"])
    )

    # --- 4. buggy policy is far worse in closed loop --------------------
    buggy_best = max(buggy["success_rate_first"], buggy["success_rate_second"])
    assert buggy_best <= 0.5, "buggy success unexpectedly high: %.3f" % buggy_best
    gap = fixed["success_rate_first"] - buggy_best
    assert gap >= 0.4, "success gap too small: fixed=%.3f buggy=%.3f gap=%.3f" % (
        fixed["success_rate_first"],
        buggy_best,
        gap,
    )

    # --- 5. buggy evaluation is NOT repeatable (dropout left on) --------
    assert buggy["final_val_mse"] != buggy["final_val_mse_recheck"], (
        "buggy val MSE should jitter (dropout active during eval)"
    )
    assert buggy["success_rate_first"] != buggy["success_rate_second"], (
        "buggy rollout success should jitter (dropout active during eval)"
    )

    # --- 6. direct probe: train-mode forward pass is stochastic ---------
    torch.manual_seed(123)
    net = buggy_train.PolicyNet(obs_dim=4, action_dim=2, hidden_dim=32, dropout=0.15)
    net.train()
    x = torch.randn(16, 4)
    out_a = net(x).detach()
    out_b = net(x).detach()
    assert not torch.equal(out_a, out_b), (
        "two train-mode forward passes matched; dropout probe is broken"
    )

    # --- 7. masked_mse ignores padded timesteps -------------------------
    pred = torch.zeros(2, 3, 2)
    target = torch.zeros(2, 3, 2)
    lengths = torch.tensor([1, 3])
    pred[0, 1:] = 5.0  # garbage on sample 0's PADDED steps only
    masked = fixed_train.masked_mse(pred, target, lengths).item()
    unmasked = torch.nn.functional.mse_loss(pred, target).item()
    assert masked == 0.0, "masked_mse leaked padding: %.4f" % masked
    assert unmasked > 0.0, "unmasked control should be nonzero"

    # --- 8. fixed pipeline is fully deterministic across runs -----------
    for key in fixed:
        assert fixed[key] == fixed_again[key], (
            "fixed run not reproducible for %s: %r vs %r"
            % (key, fixed[key], fixed_again[key])
        )

    elapsed = time.time() - start
    assert elapsed < 60.0, "test suite too slow: %.1fs" % elapsed

    print("-" * 64)
    print(
        "buggy : success #1=%.3f #2=%.3f | val MSE #1=%.4f #2=%.4f"
        % (
            buggy["success_rate_first"],
            buggy["success_rate_second"],
            buggy["final_val_mse"],
            buggy["final_val_mse_recheck"],
        )
    )
    print(
        "fixed : success #1=%.3f #2=%.3f | val MSE #1=%.4f #2=%.4f"
        % (
            fixed["success_rate_first"],
            fixed["success_rate_second"],
            fixed["final_val_mse"],
            fixed["final_val_mse_recheck"],
        )
    )
    print("gap   : %.3f (assert >= 0.4)" % gap)
    print("ALL TESTS PASSED in %.1fs" % elapsed)


if __name__ == "__main__":
    main()
```

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/labs/lab6_buggy_training/README.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/labs/lab6_buggy_training/README.md)。作者整理资料；许可和第三方来源范围见阅读指南。
