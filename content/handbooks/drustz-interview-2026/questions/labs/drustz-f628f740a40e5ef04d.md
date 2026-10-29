---
id: drustz-f628f740a40e5ef04d
section: labs
order: 12
level: A
title: Feedback Agent — 从人类反馈中学习的个人助理（最小可跑演示）
quick: 作者完整文档 · Feedback Agent — 从人类反馈中学习的个人助理（最小可跑演示）
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/humansand/sample_code/README.md
    type: primary
---
# Feedback Agent — 从人类反馈中学习的个人助理（最小可跑演示）

单文件 mock-LLM 助理，展示一个完整的 human-in-the-loop 学习闭环：人类纠正 → distillation成规则（in-context 路径）+ 拟合微型 reward model（post-training 路径）→ 不确定时主动问人（mixed-initiative gate）。全部 stdlib + numpy，确定性，302 行，跑完 <1 秒。

## 一条命令怎么跑

```bash
cd ml_sys_prep/humansand/sample_code
/Users/mingrui/Documents/codes/interview/.venv/bin/python feedback_agent.py      # 演示 + 内置断言
/Users/mingrui/Documents/codes/interview/.venv/bin/python test_feedback_agent.py # 4 组测试
```



现场跑出来的硬数字（seed=13，永远一样）：

| 指标 | 数值 |
|---|---|
| 反馈前 held-out preference match | **5.0%** |
| 收集 54 次纠正 → 162 个偏好对 | |
| 仅注入distillation规则（in-context） | **45.0%** |
| Reward model held-out 成对准确率 | **96.7%** |
| 规则 + RM rerank | **87.5%** |
| Gate 总成本 14 vs 全问 40 / 全不问 25（问了 4/40 次） | **省 44–65%** |

## 2 分钟英文讲法（逐句稿）

> **开场（10 秒）**
> "This is a ~300-line demo I can run right now — it's a minimal system embodying my thesis: human feedback is a training signal, and knowing WHEN to ask is an interaction design problem."

> **设置（20 秒）**
> "A mock personal assistant drafts emails and schedules meetings. Each draft has style features — formality, brevity, emoji use. The user has a hidden preference the agent doesn't know, so out of the box it matches what the user wants only 5% of the time. That's the 'one model, many users' personalization gap."

> **两条学习路径（40 秒）**
> "When the user corrects a draft, I use that signal twice. First, corrections get distilled into human-readable rules — 'avoid emoji', 'prefer brevity' — and injected into later decisions. That's the in-context path: instant, auditable, but coarse — it gets us to 45%. Second, the same corrections become preference pairs for a tiny Bradley-Terry reward model — hand-rolled logistic regression, no sklearn — which reranks candidates. That's the post-training path in miniature: it generalizes to 97% pairwise accuracy on held-out tasks and lifts end-to-end match to 87.5%. The two paths are complementary: the rules actually missed formality, but the reward model caught it."

> **Gate — HCI 的部分（35 秒）**
> "The part I care most about: the agent knows when NOT to act. When the reward model's margin between the top two candidates is low, it asks the human instead. I price the trade-off explicitly — an interruption costs 1, an uncaught error costs 5 — and calibrate the ask threshold on a separate calibration split, never on the test set. On held-out tasks the gate asks only 4 times out of 40 and beats both degenerate policies: cost 14 versus 40 for always-ask and 25 for never-ask. That's the mixed-initiative insight from HCI, quantified."

> **收尾（15 秒）**
> "Everything is deterministic, assertion-pinned, and tested — same discipline I used shipping eval infrastructure at Reflection. Scale the mock LLM to a real one and the reward model to a fine-tune, and this is the architecture I'd build for an assistant that actually learns its user."

## 三个可被追问的设计决策与英文答法

**1. 为什么同一份反馈要走两条路径（rules + reward model）？**
> "They fail differently. Rules are instant and auditable — the user can read 'avoid emoji' and veto it — but they're coarse, direction-only. The reward model generalizes and captures magnitude — it learned that emoji matters 2x more than formality — but it's opaque. In the demo you can see the complementarity: rules alone get 45%, adding the RM gets 87.5%, and the RM caught the formality preference the rules missed. In a production system, rules are also what you can apply at inference time today, while pairs accumulate into training data for the next post-training run. Same signal, two time horizons."

**2. Gate 的阈值怎么定的？为什么不用固定的置信度阈值？**
> "I tried the decision-theoretic threshold first — ask when expected error cost exceeds interruption cost, which gives tau = 1 − cost_ask/cost_error = 0.8. It lost to never-ask, because a freshly fit reward model's sigmoid confidence isn't calibrated. So I calibrate tau on a held-out calibration split of 20 tasks — never the test set. That's a general lesson: any ask-vs-act policy is only as good as its confidence calibration, and calibration is cheap to measure. Also, the costs themselves are the real product decision — interrupting a user in a group chat at 2am is not cost 1 — so I'd want them user- and context-dependent."

**3. Mock 环境会不会太简单，结论能迁移吗？**
> "The mock is deliberately the simplest environment where all three mechanisms are separable and measurable — that's an eval design choice, not a limitation I'm hiding. Linear features and a noise-free human mean I know ground truth, so I can pin every claim with an assertion. What transfers: the correction → pair → reward-model pipeline is exactly RLHF data collection; the gate logic is model-agnostic — it only needs a score margin; and the before/after evaluation discipline is the same one I used at Reflection and in my Anthropic take-home. What doesn't transfer: real preferences are noisy, contextual, and drift — that's why I'd add per-category rules, recency weighting, and periodic re-calibration before trusting it."

## 文件

- `feedback_agent.py` — 全部核心逻辑 + 演示主脚本（234 行）
- `test_feedback_agent.py` — 4 组 plain-assert 测试：反馈改变行为、RM 方向正确、gate 严格优于两个极端、逐字段确定性（68 行）

## feedback_agent.py

```python
"""Minimal runnable demo: a personal-assistant agent that learns from human feedback.

Three ideas, one file (mock LLM, numpy only, fully deterministic):
  (a) human corrections -> distilled preference RULES injected into later
      decisions (the in-context learning path)
  (b) the same corrections as preference pairs -> a tiny Bradley-Terry reward
      model (hand-rolled logistic regression) used to RERANK candidate
      responses (the post-training path, in miniature)
  (c) an uncertainty GATE: when the reward margin is low, ASK the human
      instead of acting (mixed-initiative HCI: interruption cost vs error
      cost, quantified)

Run:  python feedback_agent.py
"""

import numpy as np

SEED = 13
FEATURES = ["formality", "brevity", "warmth", "emoji", "structure"]
D = len(FEATURES)

# What THIS user actually wants. Hidden from the agent; only used to simulate
# human feedback (likes formal, brief, structured drafts; dislikes emoji).
HUMAN_W = np.array([2.0, 1.5, 0.5, -2.5, 1.0])

# Generic pretrained-assistant prior: chatty, emoji-happy. Mismatched on
# purpose -- this is the "one model, many users" personalization gap.
BASE_W = np.array([0.0, -1.0, 1.5, 1.5, 0.0])

CATEGORIES = [
    "email_to_manager",
    "reschedule_meeting",
    "status_update",
    "intro_message",
]
N_TRAIN, N_CALIB, N_HELDOUT, N_CANDS = 60, 20, 40, 4
RULE_STRENGTH = 2.0  # how hard an injected rule biases scoring
RM_SCALE = 3.0  # weight of the reward model at rerank time
ASK_COST = 1.0  # cost of interrupting the human with a question
ERROR_COST = 5.0  # cost of confidently acting and being wrong
TAU_GRID = np.arange(0.55, 0.96, 0.05)  # candidate ask thresholds


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def make_tasks(n_tasks, n_cands, rng):
    """Mock LLM: for each assistant task, propose n_cands drafts. A draft is
    represented only by its style features in [0,1]^D (text elided)."""
    tasks = []
    for i in range(n_tasks):
        tasks.append(
            {
                "id": i,
                "category": CATEGORIES[i % len(CATEGORIES)],
                "candidates": rng.rand(n_cands, D),
            }
        )
    return tasks


def human_pick(task):
    """Which draft the human actually prefers (simulator ground truth)."""
    return int(np.argmax(task["candidates"] @ HUMAN_W))


class Agent:
    """Mock-LLM assistant. Score = frozen base prior + injected rules
    (in-context path) + reward-model rerank (post-training path)."""

    def __init__(self):
        self.rules = []  # [(feature_idx, direction)] distilled from corrections
        self.rm_w = None  # Bradley-Terry reward model weights

    def scores(self, cands, use_rules=True, use_rm=True):
        s = cands @ BASE_W
        if use_rules:
            for j, direction in self.rules:
                s = s + RULE_STRENGTH * direction * cands[:, j]
        if use_rm and self.rm_w is not None:
            s = s + RM_SCALE * (cands @ self.rm_w)
        return s

    def pick(self, cands, use_rules=True, use_rm=True):
        return int(np.argmax(self.scores(cands, use_rules, use_rm)))

    def distill_rules(self, pairs, threshold=0.12):
        """Compress corrections into human-readable, retrievable rules: any
        feature whose mean (preferred - rejected) gap is consistent enough."""
        diffs = np.array([p - r for p, r in pairs])
        mean_gap = diffs.mean(axis=0)
        self.rules = [
            (j, 1.0 if mean_gap[j] > 0 else -1.0)
            for j in range(D)
            if abs(mean_gap[j]) > threshold
        ]

    def rule_texts(self):
        return [
            ("PREFER more %s" if d > 0 else "AVOID %s") % FEATURES[j]
            for j, d in self.rules
        ]


def collect_corrections(agent, tasks):
    """Human reviews the agent's pick; when it is not what they wanted, they
    point at the draft they DID want. One choose-1-of-k correction yields
    (k-1) preference pairs: (wanted, each other draft)."""
    pairs, n_corrections = [], 0
    for t in tasks:
        a = agent.pick(t["candidates"])
        h = human_pick(t)
        if a != h:
            n_corrections += 1
            for j in range(len(t["candidates"])):
                if j != h:
                    pairs.append((t["candidates"][h], t["candidates"][j]))
    return pairs, n_corrections


def fit_reward_model(pairs, lr=0.5, epochs=2000, l2=1e-4):
    """Bradley-Terry: maximize sum log sigmoid(w . (f_pref - f_rej)).
    Hand-rolled gradient ascent; no sklearn."""
    X = np.array([p - r for p, r in pairs])
    w = np.zeros(D)
    for _ in range(epochs):
        grad = X.T @ (1.0 - sigmoid(X @ w)) / len(X)
        w = w + lr * (grad - l2 * w)
    return w


def match_rate(agent, tasks, use_rules=True, use_rm=True):
    """Fraction of tasks where the agent's pick equals the human's pick."""
    hits = [
        agent.pick(t["candidates"], use_rules, use_rm) == human_pick(t) for t in tasks
    ]
    return float(np.mean(hits))


def rm_heldout_accuracy(rm_w, tasks):
    """Pairwise accuracy of the reward model on unseen tasks."""
    correct, total = 0, 0
    for t in tasks:
        h = human_pick(t)
        for j in range(len(t["candidates"])):
            if j != h:
                total += 1
                correct += int((t["candidates"][h] - t["candidates"][j]) @ rm_w > 0)
    return correct / total


def gate_policy_costs(agent, tasks, tau):
    """Ask-vs-act. Confidence = RM's P(top beats runner-up). Compare the gate
    against the two degenerate policies: always-ask and never-ask."""
    gate = always = never = 0.0
    n_ask = n_act_errors = 0
    for t in tasks:
        s = agent.scores(t["candidates"])
        order = np.argsort(-s)
        top, second = int(order[0]), int(order[1])
        conf = sigmoid((t["candidates"][top] - t["candidates"][second]) @ agent.rm_w)
        wrong = top != human_pick(t)
        always += ASK_COST
        never += ERROR_COST if wrong else 0.0
        if conf < tau:  # low margin: interrupt the human
            gate += ASK_COST
            n_ask += 1
        else:  # confident: act autonomously
            gate += ERROR_COST if wrong else 0.0
            n_act_errors += int(wrong)
    return {
        "gate": gate,
        "always_ask": always,
        "never_ask": never,
        "n_ask": n_ask,
        "n_act_errors": n_act_errors,
        "n_tasks": len(tasks),
    }


def calibrate_gate_tau(agent, calib_tasks):
    """Pick the ask threshold that minimizes total cost on a calibration split
    (not hand-set, and never tuned on the held-out set)."""
    best_tau, best_cost = None, None
    for tau in TAU_GRID:
        cost = gate_policy_costs(agent, calib_tasks, tau)["gate"]
        if best_cost is None or cost < best_cost:
            best_tau, best_cost = float(tau), cost
    return best_tau


def run_demo(seed=SEED):
    rng = np.random.RandomState(seed)
    train = make_tasks(N_TRAIN, N_CANDS, rng)
    calib = make_tasks(N_CALIB, N_CANDS, rng)
    heldout = make_tasks(N_HELDOUT, N_CANDS, rng)
    agent = Agent()

    before = match_rate(agent, heldout)  # generic prior, no feedback
    pairs, n_corr = collect_corrections(agent, train)  # human corrects the agent
    agent.distill_rules(pairs)  # path (a): rules
    rules_only = match_rate(agent, heldout, use_rm=False)
    agent.rm_w = fit_reward_model(pairs)  # path (b): reward model
    rm_acc = rm_heldout_accuracy(agent.rm_w, heldout)
    after = match_rate(agent, heldout)  # rules + RM rerank
    tau = calibrate_gate_tau(agent, calib)  # path (c): ask-vs-act gate
    costs = gate_policy_costs(agent, heldout, tau)

    return {
        "before": before,
        "rules_only": rules_only,
        "after": after,
        "rm_acc": rm_acc,
        "n_pairs": len(pairs),
        "n_corrections": n_corr,
        "rules": agent.rule_texts(),
        "rm_w": agent.rm_w,
        "tau": tau,
        "costs": costs,
        "agent": agent,
        "heldout": heldout,
    }


def main():
    m = run_demo()
    c = m["costs"]
    print("== Personal assistant that learns from human feedback (mock LLM, numpy) ==")
    print(
        "train tasks: %d | calibration tasks: %d | held-out tasks: %d | drafts per task: %d"
        % (N_TRAIN, N_CALIB, N_HELDOUT, N_CANDS)
    )
    print()
    print(
        "[1] BEFORE feedback  held-out preference match: %5.1f%%" % (100 * m["before"])
    )
    print(
        "[2] %d corrections -> %d preference pairs" % (m["n_corrections"], m["n_pairs"])
    )
    print("[3a] distilled rules (injected in-context):")
    for r in m["rules"]:
        print("      - " + r)
    print(
        "     rules only          held-out preference match: %5.1f%%"
        % (100 * m["rules_only"])
    )
    print(
        "[3b] reward model (Bradley-Terry LR)  held-out pairwise acc: %5.1f%%"
        % (100 * m["rm_acc"])
    )
    print(
        "     rules + RM rerank   held-out preference match: %5.1f%%"
        % (100 * m["after"])
    )
    print(
        "[4] ask-vs-act gate: ask iff P(top beats runner-up) < %.2f"
        " (calibrated; ask=%.0f, error=%.0f)" % (m["tau"], ASK_COST, ERROR_COST)
    )
    print(
        "     always-ask cost: %5.1f | never-ask cost: %5.1f | gate cost: %5.1f"
        % (c["always_ask"], c["never_ask"], c["gate"])
    )
    print(
        "     asked %d/%d tasks; errors while acting: %d"
        % (c["n_ask"], c["n_tasks"], c["n_act_errors"])
    )

    # Pin the headline claims.
    assert m["after"] >= m["before"] + 0.30, "feedback must lift match rate by >=30pts"
    assert m["rules_only"] > m["before"], "rules alone must already help"
    assert m["rm_acc"] >= 0.90, "reward model must generalize to held-out pairs"
    assert c["gate"] < c["always_ask"], "gate must beat always-ask"
    assert c["gate"] < c["never_ask"], "gate must beat never-ask"
    assert 0 < c["n_ask"] < c["n_tasks"], "gate must be selective, not degenerate"
    print()
    print("all main-script assertions passed")


if __name__ == "__main__":
    main()
```




## test_feedback_agent.py

```python
"""Plain-assert tests for feedback_agent.py (no pytest required).

Run:  python test_feedback_agent.py
"""

import time
import numpy as np
import feedback_agent as fa


def test_feedback_changes_behavior(m):
    """After corrections, the agent behaves differently -- and better."""
    assert len(m["rules"]) >= 2, "should distill at least two rules"
    assert "AVOID emoji" in m["rules"], "the strongest preference must surface"
    assert m["rules_only"] > m["before"], "rules alone must already help"
    assert m["after"] >= m["before"] + 0.30, "full loop must lift match >=30pts"
    # Concrete flip: two drafts identical except one uses emoji.
    plain = np.array([0.6, 0.6, 0.5, 0.0, 0.5])
    emoji = np.array([0.6, 0.6, 0.5, 1.0, 0.5])
    cands = np.stack([plain, emoji])
    assert fa.Agent().pick(cands) == 1, "generic prior prefers the emoji draft"
    assert m["agent"].pick(cands) == 0, "after feedback, it should not"


def test_reward_model_direction(m):
    """RM learned from pairs must point the same way as the hidden preference."""
    w = m["rm_w"]
    assert w[0] > 0, "formality: human likes it, RM must too"
    assert w[1] > 0, "brevity: human likes it, RM must too"
    assert w[3] < 0, "emoji: human dislikes it, RM must too"
    assert w[4] > 0, "structure: human likes it, RM must too"
    assert int(np.argmax(np.abs(w))) == 3, "emoji is the dominant preference"
    assert m["rm_acc"] >= 0.90, "RM must generalize to held-out pairs"


def test_gate_between_extremes(m):
    """The calibrated gate must strictly beat both degenerate policies."""
    c = m["costs"]
    assert c["gate"] < c["always_ask"], "gate must beat always-ask"
    assert c["gate"] < c["never_ask"], "gate must beat never-ask"
    assert 0 < c["n_ask"] < c["n_tasks"], "gate must be selective"
    assert 0.5 < m["tau"] < 1.0, "threshold must be a real interior choice"
    # Degenerate taus reproduce the two baselines exactly.
    agent, heldout = m["agent"], m["heldout"]
    all_ask = fa.gate_policy_costs(agent, heldout, tau=1.01)
    no_ask = fa.gate_policy_costs(agent, heldout, tau=0.0)
    assert all_ask["n_ask"] == len(heldout) and all_ask["gate"] == c["always_ask"]
    assert no_ask["n_ask"] == 0 and no_ask["gate"] == c["never_ask"]


def test_deterministic():
    """Same seed, same story: every reported number reproduces exactly."""
    a, b = fa.run_demo(), fa.run_demo()
    for key in [
        "before",
        "rules_only",
        "after",
        "rm_acc",
        "tau",
        "rules",
        "n_pairs",
        "n_corrections",
        "costs",
    ]:
        assert a[key] == b[key], "non-deterministic field: %s" % key
    assert np.array_equal(a["rm_w"], b["rm_w"])


if __name__ == "__main__":
    t0 = time.time()
    m = fa.run_demo()
    test_feedback_changes_behavior(m)
    test_reward_model_direction(m)
    test_gate_between_extremes(m)
    test_deterministic()
    elapsed = time.time() - t0
    assert elapsed < 30.0, "tests must finish in under 30s"
    print("4/4 test groups passed in %.2fs" % elapsed)
```

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/humansand/sample_code/README.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/humansand/sample_code/README.md)。作者整理资料；许可和第三方来源范围见阅读指南。
