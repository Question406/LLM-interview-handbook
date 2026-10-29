---
id: drustz-a3f1f76e6ccf4bc369
section: labs
order: 6
level: A
title: lab4_edge_uploader · 家用机器人边缘上传队列模拟器
quick: 作者完整文档 · lab4_edge_uploader · 家用机器人边缘上传队列模拟器
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/labs/lab4_edge_uploader/README.md
    type: primary
---
# lab4_edge_uploader · 家用机器人边缘上传队列模拟器

⏱ 熟悉 15–30 分钟 ｜ 纯标准库、零依赖 ｜ 全部测试 < 2 秒 ｜ 解释器：`/usr/bin/python3`（Python 3.9.6）

**对应考点**：[bot_company/06](?book=drustz-interview-2026&section=robotics&question=drustz-36784fe27814ef4267) Playbook A「家用机器人 Fleet 数据采集」——(a) 题**带宽受限数据采集**的可运行版本。06 里那句 hook——*"450 TB/day is neither feasible nor necessary"*——推出的结论是「设计重心在边缘侧决定不传什么」；这个 lab 就是把边缘侧那个「上传器」框图变成 ~400 行经得起 code review 的代码：优先级队列 + 每日 WiFi 配额 + 分块断点续传 + 指数退避 + aging 防饿死 + 环形缓冲区丢弃策略。

## 一、先跑什么（5 分钟）

```bash
/usr/bin/python3 simulate.py      # 7 天模拟：正常日 / 断网日 / OTA 风暴日
/usr/bin/python3 test_uploader.py # 9 条断言 = 9 个设计承诺
```



`simulate.py` 输出一张 7 天表格，读表顺序：

1. **budget% 列**：每天都 ≤ 100%——每日配额是硬约束，代码里不可能超支（chunk 放不进剩余预算就不发）；
2. **day 3 (outage)**：上传量掉到 ~65%，backlog 涨——16 小时断网；第二天从**已完成的 chunk** 继续，summary 里 `resume exactness -> True` 证明没有任何字节被重传；
3. **day 4 (storm)**：OTA 事故导致 failure 从 2/天 激增到 60/天 + 8 次人工接管。看 `done` 列：8 个 intervention 全部当天传完；`drop` 列：32 个 routine 视频被挤出缓冲区——**但 metadata 列 = 94，当天所有事件的元数据照样全部到云**；
4. **summary**：`intervention video lost: 0`——七天下来 14 个接管片段一个不丢、全部完整送达。

## 二、再读什么（15 分钟）

按这个顺序读 `uploader.py` 的三个函数（其它都是脚手架）：

| 函数 | 它回答的面试问题 |
|---|---|
| `effective_priority()` | 优先级怎么定？intervention > failure > novelty(嵌入距离加成) > routine；**aging 让等待者涨分但封顶在 intervention 楼下**——资历救得了 routine，救不过人工接管 |
| `_make_room()` | 缓冲区满了丢谁？丢「本来就最后才会传的」：routine 先走、novelty 其次、failure 最后，**intervention 永不被逐**；极端情况下宁可超容量收下 intervention 并报警（overflow_admit），也不丢 |
| `_upload_pass()` | 一个 tick 里发生什么？**先清 metadata（level 1），再按严格优先级发视频 chunk（level 2）**；chunk 不够预算就停（不许小文件插队——bypass 会重新引入饿死）；发失败按 2/4/8/16 tick 退避 |

然后扫一遍 `test_uploader.py` 的 9 个测试名——每个测试就是一条可以在面试里直接说出口的 invariant。

### Privacy-by-design 在代码里的三个落点（面试必讲）

06 的 privacy 要点「**元数据先行、视频按需拉取**」在这里不是口号，是三处代码结构：

1. `_upload_pass()` 里 level-1 metadata 队列**先于任何视频字节**清空（metadata 只有 2 KB、不含像素，只有任务 ID/结果/novelty 分）；
2. `_top_video_candidate()` 拒绝 metadata 未上传的事件——**级别 2 结构上不可能先于级别 1**；
3. `_evict_video()` 只丢视频、保留 metadata——即使风暴日视频被牺牲，云端仍知道「这个片段存在过」，可以事后下发 campaign 定向拉取。

测试 7 和测试 9(e) 把这个承诺变成断言：风暴日 routine 一个视频字节都没传，但 268/268 事件的 metadata 全部到云。

## 三、动手改参数（可选，10 分钟）

- 把 `UploaderConfig.aging_per_tick` 改成 `0`，重跑 sim：day 5–6 的 routine 完成数归零——这就是饿死（测试 8 的 control 分支就是它）；
- 把 `buffer_capacity_bytes` 减半：风暴日 drop 数翻倍，但 `intervention lost` 仍然是 0；
- 把风暴日 failure 提到 200：观察 overflow_admits 是否触发。

## 四、面试中怎么引用

> "To make the edge-side story concrete, I built a small simulator of the upload problem: a priority queue where teleop interventions preempt everything and are never dropped, a hard daily WiFi quota, chunked resumable uploads with exponential backoff, and an aging term so routine samples can't starve — the takeaway I'd defend is that on a bandwidth-starved fleet the upload policy IS the data strategy, and a metadata-first two-level upload is what keeps privacy and fleet visibility compatible."

### 追问预演

| 追问 | 答 |
|---|---|
| aging 会不会让垃圾数据反超关键数据？ | aging 封顶（cap 55，ceiling 95）永远低于 intervention 的 100；它只保证 routine 在 failure/novelty 的**持续新流量**下不至于无限等待——而 routine 里是均匀random sampling，那是对冲 trigger selection bias 的数据，饿死它等于放弃分布calibration |
| 顶部大文件卡住预算尾巴，为什么不让小文件插队？ | 故意的。bypass 等于给低优先级开后门，饿死会换个形式回来；配额尾巴浪费几十 MB 是可预算的成本，优先级反转不是 |
| 真实系统和这个玩具差在哪？ | 至少五处：chunk 要 per-chunk checksum + 服务端去重；断点状态要 journal 到磁盘防掉电；多机器人共享家庭上行要 fairness；传输走 QUIC/S3 multipart；trigger 风暴防护应该在**入队前**做 per-class fire-rate 限额（本 lab 的丢弃策略是最后一道防线，不是第一道） |
| 为什么 novelty 用嵌入距离？ | `simulate.py` 里 novelty = 场景嵌入到运行中心的距离 `d/(1+d)`——这是 06 触发清单第 5 类「场景 embedding 与已采集分布距离大」的最小代理；真实版是设备端小模型对 fleet 分布的密度估计 |

## 五、诚实性提醒

这是**教学用最小复现**，不是生产系统、更不是项目经历。面试里的正确说法：「为了把 06 题边缘侧的框图变具体，我写了个可复现的模拟器验证这五条 invariant；它不能证明真实 fleet 规模下的表现，下一步是掉电持久化和多设备公平性。」

## 文件

```text
uploader.py        核心：EdgeUploader（优先级/配额/续传/退避/aging/丢弃）
simulate.py        7 天模拟（正常/断网/风暴），novelty 用嵌入距离代理
test_uploader.py   9 条 plain-assert 测试，/usr/bin/python3 test_uploader.py
```



## simulate.py

```python
"""7-day simulation of one home robot's edge upload queue.

Day schedule (1 tick = 1 hour, 24 ticks/day):
  * days 0-2, 5-6 : normal load, slightly oversubscribed vs. the daily quota
                    (so a small routine backlog builds up and aging matters);
  * day 3         : network outage 04:00-20:00 (home WiFi down) -- proves
                    chunked resume: files interrupted mid-upload finish later
                    without re-sending completed chunks;
  * day 4         : event storm -- a bad OTA push spikes FAILURE (and teleop
                    INTERVENTION) volume; ROUTINE video gets squeezed out of
                    the quota and partly evicted from the ring buffer, while
                    ROUTINE *metadata* still reaches the cloud (level 1).

Novelty is an embedding-distance proxy: each event carries an 8-dim scene
embedding; novelty = d / (1 + d) where d is the distance to the running
centroid of everything seen so far. Storm-day scenes are shifted, so they
score higher. Pure stdlib, deterministic under a fixed seed.

Run:  /usr/bin/python3 simulate.py
"""

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from uploader import (
    EdgeUploader,
    Event,
    EventType,
    MiB,
    UploaderConfig,
)

DAYS = 7
OUTAGE_DAY = 3
OUTAGE_TICKS = range(4, 20)  # 16 hours of dead uplink
STORM_DAY = 4
EMBED_DIM = 8

VIDEO_BYTES = {
    EventType.INTERVENTION: 128 * MiB,  # teleop takeover: all cams + actions
    EventType.FAILURE: 96 * MiB,
    EventType.NOVELTY: 64 * MiB,
    EventType.ROUTINE: 48 * MiB,
}

NORMAL_COUNTS = {
    EventType.ROUTINE: 22,
    EventType.NOVELTY: 4,
    EventType.FAILURE: 2,
    EventType.INTERVENTION: 1,
}

STORM_COUNTS = {
    EventType.ROUTINE: 22,
    EventType.NOVELTY: 4,
    EventType.FAILURE: 60,  # OTA regression: retry/timeout storm
    EventType.INTERVENTION: 8,  # operators taking over the failing robots
}


class NoveltyScorer:
    """Embedding-distance proxy: distance of a scene to the running centroid."""

    def __init__(self) -> None:
        self._centroid = [0.0] * EMBED_DIM
        self._count = 0

    def score(self, embedding: List[float]) -> float:
        if self._count == 0:
            distance = 0.0
        else:
            distance = math.sqrt(
                sum((e - c) ** 2 for e, c in zip(embedding, self._centroid))
            )
        self._count += 1
        alpha = 1.0 / self._count
        self._centroid = [
            (1 - alpha) * c + alpha * e for c, e in zip(self._centroid, embedding)
        ]
        return distance / (1.0 + distance)


@dataclass
class SimResult:
    uploader: EdgeUploader
    generated: Dict[EventType, int]
    day_kinds: List[str] = field(default_factory=list)
    backlog_bytes_eod: List[int] = field(default_factory=list)


def _make_embedding(rng: random.Random, day: int) -> List[float]:
    # Storm-day scenes come from a shifted distribution (robot stuck in
    # unfamiliar states after the bad OTA) -> larger centroid distance.
    shift = 3.0 if day == STORM_DAY else 0.0
    return [rng.gauss(shift, 1.0) for _ in range(EMBED_DIM)]


def _events_for_day(
    day: int,
    rng: random.Random,
    scorer: NoveltyScorer,
    next_id: int,
    ticks_per_day: int,
) -> Tuple[Dict[int, List[Event]], int]:
    """Return {tick_in_day: [events]} for one day, plus the next free id."""
    counts = STORM_COUNTS if day == STORM_DAY else NORMAL_COUNTS
    by_tick: Dict[int, List[Event]] = {}
    for etype, n in counts.items():
        for _ in range(n):
            if day == STORM_DAY and etype in (
                EventType.FAILURE,
                EventType.INTERVENTION,
            ):
                tick_in_day = rng.randrange(2, 9)  # burst right after the OTA
            else:
                tick_in_day = rng.randrange(ticks_per_day)
            novelty = 0.0
            if etype is EventType.NOVELTY:
                novelty = scorer.score(_make_embedding(rng, day))
            event = Event(
                event_id=next_id,
                etype=etype,
                created_tick=day * ticks_per_day + tick_in_day,
                video_bytes=VIDEO_BYTES[etype],
                novelty=novelty,
            )
            by_tick.setdefault(tick_in_day, []).append(event)
            next_id += 1
    for events in by_tick.values():
        events.sort(key=lambda e: e.event_id)  # deterministic offer order
    return by_tick, next_id


def run_simulation(
    seed: int = 42,
    config: Optional[UploaderConfig] = None,
    days: int = DAYS,
) -> SimResult:
    cfg = config if config is not None else UploaderConfig()
    gen_rng = random.Random(seed)
    net_rng = random.Random(seed + 1)
    # Flaky residential uplink: 3% of chunk sends fail -> exercises backoff.
    uploader = EdgeUploader(
        config=cfg,
        failure_model=lambda _e, _a, _t: net_rng.random() < 0.03,
    )
    scorer = NoveltyScorer()
    generated = {etype: 0 for etype in EventType}
    day_kinds: List[str] = []
    backlog_eod: List[int] = []
    next_id = 0

    for day in range(days):
        if day == OUTAGE_DAY:
            day_kinds.append("outage")
        elif day == STORM_DAY:
            day_kinds.append("storm")
        else:
            day_kinds.append("normal")
        by_tick, next_id = _events_for_day(
            day, gen_rng, scorer, next_id, cfg.ticks_per_day
        )
        for tick_in_day in range(cfg.ticks_per_day):
            for event in by_tick.get(tick_in_day, []):
                uploader.offer(event)
                generated[event.etype] += 1
            network_up = not (day == OUTAGE_DAY and tick_in_day in OUTAGE_TICKS)
            uploader.run_tick(network_up=network_up)
        backlog_eod.append(uploader.buffer_used)

    return SimResult(
        uploader=uploader,
        generated=generated,
        day_kinds=day_kinds,
        backlog_bytes_eod=backlog_eod,
    )


def _fmt_mb(n_bytes: int) -> str:
    return "%7.1f" % (n_bytes / MiB)


def print_report(result: SimResult) -> None:
    up = result.uploader
    cfg = up.config
    header = (
        "day  kind      up_MB  budget%  meta  done(i/f/n/r)  drop(r/n/f)  backlog_MB"
    )
    print(header)
    print("-" * len(header))
    for day in range(len(result.day_kinds)):
        stats = up.day_stats(day)
        done = stats.video_completed
        drop = stats.video_dropped
        pct = 100.0 * stats.bytes_uploaded / cfg.daily_budget_bytes
        print(
            "%3d  %-6s %s   %5.1f%%  %4d   %2d/%2d/%2d/%2d      %2d/%2d/%2d  %s"
            % (
                day,
                result.day_kinds[day],
                _fmt_mb(stats.bytes_uploaded),
                pct,
                stats.metadata_uploaded,
                done[EventType.INTERVENTION],
                done[EventType.FAILURE],
                done[EventType.NOVELTY],
                done[EventType.ROUTINE],
                drop[EventType.ROUTINE],
                drop[EventType.NOVELTY],
                drop[EventType.FAILURE],
                _fmt_mb(result.backlog_bytes_eod[day]),
            )
        )

    print()
    print("== 7-day summary ==")
    for etype in EventType:
        print(
            "  %-13s generated=%3d  video_completed=%3d  video_dropped=%3d"
            % (
                etype.value,
                result.generated[etype],
                up.completed_total(etype),
                up.dropped_total(etype),
            )
        )
    over_budget = [s.day for s in up.days if s.bytes_uploaded > cfg.daily_budget_bytes]
    print("  days over budget      : %s" % (over_budget or "none"))
    print(
        "  intervention video lost: %d (invariant: must be 0)"
        % up.dropped_total(EventType.INTERVENTION)
    )
    failures = sum(s.chunk_failures for s in up.days)
    print(
        "  chunk send failures    : %d (all retried with exponential backoff)"
        % failures
    )
    exact = all(e.bytes_sent == e.metadata_bytes + e.video_bytes for e in up.completed)
    print(
        "  resume exactness       : every completed event shipped exactly "
        "its size once -> %s" % exact
    )
    print()
    print("privacy-by-design: level-1 metadata (no pixels) reached the cloud for")
    meta_total = sum(s.metadata_uploaded for s in up.days)
    total_events = sum(result.generated.values())
    print(
        "  %d/%d events, including every clip whose video was dropped -- the"
        % (meta_total, total_events)
    )
    print("  cloud keeps full fleet visibility and pulls video on demand.")


def main() -> None:
    result = run_simulation(seed=42)
    print_report(result)


if __name__ == "__main__":
    main()
```




## test_uploader.py

```python
"""Executable invariants for the edge upload queue. Plain asserts, no pytest.

Run:  /usr/bin/python3 test_uploader.py

Each test states the fleet-learning invariant it encodes:
  1. priority + two-level upload   metadata (level 1) always precedes video
  2. intervention zero loss        never evicted, even when the buffer is full
  3. drop order                    routine -> novelty -> failure, never intervention
  4. budget never exceeded         hard daily WiFi quota (scripted + 7-day sim)
  5. resume after outage           completed chunks survive, no byte re-sent
  6. exponential backoff           retry gaps double: 2, 4, 8, then cap at 16
  7. storm squeezes routine        routine video yields, routine metadata flows
  8. aging beats starvation        an old routine clip overtakes fresh failures
  9. 7-day sim invariants          everything above holds end-to-end + determinism
"""

import logging
from typing import List

from uploader import (
    BASE_PRIORITY,
    EdgeUploader,
    Event,
    EventType,
    MiB,
    UploaderConfig,
)
from simulate import OUTAGE_DAY, STORM_DAY, run_simulation

KB = 1024


def _cfg(**overrides) -> UploaderConfig:
    """Small deterministic config for scripted tests."""
    base = dict(
        ticks_per_day=24,
        chunk_bytes=4 * MiB,
        link_bytes_per_tick=50 * MiB,
        daily_budget_bytes=10240 * MiB,
        buffer_capacity_bytes=10240 * MiB,
        aging_per_tick=0.0,  # aging off unless a test opts in
        aging_cap=55.0,
        backoff_base_ticks=2,
        backoff_cap_ticks=16,
    )
    base.update(overrides)
    return UploaderConfig(**base)


def _event(
    event_id: int, etype: EventType, video_mib: int, tick: int = 0, novelty: float = 0.0
) -> Event:
    return Event(
        event_id=event_id,
        etype=etype,
        created_tick=tick,
        video_bytes=video_mib * MiB,
        novelty=novelty,
    )


# ---------------------------------------------------------------------- 1
def test_priority_order_and_two_level_upload() -> None:
    up = EdgeUploader(config=_cfg(link_bytes_per_tick=12 * MiB))
    up.offer(_event(0, EventType.ROUTINE, 8))
    up.offer(_event(1, EventType.NOVELTY, 8, novelty=0.9))
    up.offer(_event(2, EventType.FAILURE, 8))
    up.offer(_event(3, EventType.INTERVENTION, 8))

    up.run_tick()
    # Level 1 drained for *all* events before level 2 got a third chunk.
    assert all(e.metadata_done for e in up.pending_events() + up.completed), (
        "metadata of every event must upload before video saturates the tick"
    )
    # Highest priority video went first.
    assert up.completed and up.completed[0].etype is EventType.INTERVENTION

    for _ in range(8):
        up.run_tick()
    order = [e.etype for e in up.completed]
    assert order == [
        EventType.INTERVENTION,
        EventType.FAILURE,
        EventType.NOVELTY,
        EventType.ROUTINE,
    ], order
    print("PASS 1: priority order + metadata-first two-level upload")


# ---------------------------------------------------------------------- 2
def test_intervention_never_dropped() -> None:
    cfg = _cfg(buffer_capacity_bytes=100 * MiB)
    up = EdgeUploader(config=cfg)
    for i in range(5):
        assert up.offer(_event(i, EventType.ROUTINE, 20))
    assert up.buffer_used == 100 * MiB

    # Intervention evicts exactly enough routine video.
    assert up.offer(_event(10, EventType.INTERVENTION, 60))
    assert up.dropped_total(EventType.ROUTINE) == 3
    assert up.dropped_total(EventType.INTERVENTION) == 0

    # Buffer now: 2 routine (40) + 1 intervention (60). Two more interventions:
    # the first (40) evicts the remaining routines and fits exactly, the
    # second (60) finds nothing evictable and is admitted OVER capacity --
    # never lost, surfaced as an overflow in stats.
    assert up.offer(_event(11, EventType.INTERVENTION, 40))
    assert up.dropped_total(EventType.ROUTINE) == 5
    assert up.day_stats(0).overflow_admits == 0
    assert up.offer(_event(12, EventType.INTERVENTION, 60))
    assert up.dropped_total(EventType.INTERVENTION) == 0
    assert up.day_stats(0).overflow_admits == 1
    assert up.buffer_used > cfg.buffer_capacity_bytes  # logged overflow

    # Incoming routine while the buffer holds only interventions: the incoming
    # video is rejected (metadata still queued), interventions untouched.
    admitted = up.offer(_event(13, EventType.ROUTINE, 20))
    assert not admitted
    assert up.dropped_total(EventType.ROUTINE) == 6  # 3 + 2 evicted + 1 rejected
    assert up.dropped_total(EventType.INTERVENTION) == 0
    rejected = [e for e in up.pending_events() if e.event_id == 13][0]
    assert rejected.video_dropped and not rejected.metadata_done
    print("PASS 2: intervention video is never dropped (overflow-admit path incl.)")


# ---------------------------------------------------------------------- 3
def test_drop_order_routine_then_novelty_then_failure() -> None:
    up = EdgeUploader(config=_cfg(buffer_capacity_bytes=100 * MiB))
    up.offer(_event(0, EventType.ROUTINE, 30))
    up.offer(_event(1, EventType.NOVELTY, 30, novelty=0.5))
    up.offer(_event(2, EventType.FAILURE, 30))

    up.offer(_event(3, EventType.INTERVENTION, 40))  # needs 30 MiB freed
    assert up.dropped_total(EventType.ROUTINE) == 1, "routine must go first"
    assert up.dropped_total(EventType.NOVELTY) == 0
    assert up.dropped_total(EventType.FAILURE) == 0

    up.offer(_event(4, EventType.INTERVENTION, 60))  # needs 60 MiB freed
    assert up.dropped_total(EventType.NOVELTY) == 1, "novelty before failure"
    assert up.dropped_total(EventType.FAILURE) == 1, "failure only as last resort"
    assert up.dropped_total(EventType.INTERVENTION) == 0
    print("PASS 3: eviction order routine -> novelty -> failure, never intervention")


# ---------------------------------------------------------------------- 4
def test_budget_never_exceeded_scripted() -> None:
    cfg = _cfg(
        daily_budget_bytes=10 * MiB, chunk_bytes=4 * MiB, link_bytes_per_tick=50 * MiB
    )
    up = EdgeUploader(config=cfg)
    up.offer(_event(0, EventType.FAILURE, 40))  # 10 chunks, needs 4+ days
    for _ in range(5 * cfg.ticks_per_day):
        up.run_tick()
    for stats in up.days:
        assert stats.bytes_uploaded <= cfg.daily_budget_bytes, (
            "day %d used %d > budget" % (stats.day, stats.bytes_uploaded)
        )
    # Quota really bites: exactly 2 chunks/day fit next to the metadata.
    assert up.days[0].bytes_uploaded == 2 * cfg.chunk_bytes + 2 * KB
    assert up.completed_total(EventType.FAILURE) == 1
    print("PASS 4: daily budget is a hard cap (chunk denied when it would overshoot)")


# ---------------------------------------------------------------------- 5
def test_resume_after_network_outage() -> None:
    cfg = _cfg(link_bytes_per_tick=8 * MiB + 8 * KB)
    up = EdgeUploader(config=cfg)
    event = _event(0, EventType.FAILURE, 40)  # 10 chunks of 4 MiB
    up.offer(event)

    for _ in range(3):  # tick 0: meta+1 chunk; ticks 1-2: 2 chunks
        up.run_tick(network_up=True)
    chunks_before_outage = event.chunks_done
    assert 0 < chunks_before_outage < event.total_chunks(cfg.chunk_bytes)

    for _ in range(4):  # WiFi down: state must be preserved
        up.run_tick(network_up=False)
    assert event.chunks_done == chunks_before_outage
    assert event.bytes_sent == chunks_before_outage * cfg.chunk_bytes + 2 * KB

    for _ in range(10):  # link back: finish from where we stopped
        up.run_tick(network_up=True)
    assert event.video_done(cfg.chunk_bytes)
    assert up.completed == [event]
    # THE resume invariant: exactly file size + metadata crossed the wire.
    assert event.bytes_sent == 40 * MiB + 2 * KB, (
        "re-uploaded bytes detected: %d" % event.bytes_sent
    )
    print("PASS 5: chunked upload resumes after outage, zero bytes re-sent")


# ---------------------------------------------------------------------- 6
def test_exponential_backoff() -> None:
    failure_ticks: List[int] = []

    def flaky(_event: Event, attempts: int, tick: int) -> bool:
        if attempts < 4:  # first 4 sends fail, 5th succeeds
            failure_ticks.append(tick)
            return True
        return False

    cfg = _cfg()
    up = EdgeUploader(config=cfg, failure_model=flaky)
    event = _event(0, EventType.FAILURE, 4)  # single chunk
    up.offer(event)
    for _ in range(40):
        up.run_tick()

    # Retry schedule: fail@0 -> +2 -> fail@2 -> +4 -> fail@6 -> +8 ->
    # fail@14 -> +16 (capped) -> success@30.
    assert failure_ticks == [0, 2, 6, 14], failure_ticks
    gaps = [b - a for a, b in zip(failure_ticks, failure_ticks[1:])]
    assert gaps == [2, 4, 8], "retry gaps must double: %s" % gaps
    assert up.completed == [event]
    assert event.attempts == 0, "success must reset the backoff counter"
    assert event.bytes_sent == 4 * MiB + 2 * KB
    print("PASS 6: exponential backoff 2/4/8 then cap, state resets on success")


# ---------------------------------------------------------------------- 7
def test_storm_squeezes_routine_video_not_metadata() -> None:
    cfg = _cfg(daily_budget_bytes=200 * MiB, aging_per_tick=0.5)
    up = EdgeUploader(config=cfg)
    eid = 0
    for _ in range(5):
        up.offer(_event(eid, EventType.ROUTINE, 20))
        eid += 1
    for _ in range(20):  # OTA incident: failure storm
        up.offer(_event(eid, EventType.FAILURE, 40))
        eid += 1
    for _ in range(2):
        up.offer(_event(eid, EventType.INTERVENTION, 40))
        eid += 1

    for _ in range(cfg.ticks_per_day):
        up.run_tick()
    day = up.day_stats(0)
    # Routine shipped ONLY its level-1 metadata; every video byte of the quota
    # went to interventions and failures.
    assert day.bytes_by_type[EventType.ROUTINE] == 5 * 2 * KB, (
        "routine video should be fully squeezed out on storm day"
    )
    assert day.metadata_uploaded == 27, "cloud must still see all 27 events"
    assert day.video_completed[EventType.INTERVENTION] == 2
    assert day.bytes_uploaded <= cfg.daily_budget_bytes
    print("PASS 7: storm day squeezes routine video out; metadata still flows")


# ---------------------------------------------------------------------- 8
def test_aging_prevents_starvation() -> None:
    def run(aging_per_tick: float, horizon: int) -> EdgeUploader:
        cfg = _cfg(
            aging_per_tick=aging_per_tick,
            link_bytes_per_tick=9 * MiB,
            chunk_bytes=4 * MiB,
        )
        up = EdgeUploader(config=cfg)
        up.offer(_event(0, EventType.ROUTINE, 8))  # the clip at risk
        for tick in range(horizon):  # endless fresh failures
            up.offer(_event(1 + tick, EventType.FAILURE, 8, tick=tick))
            up.run_tick()
        return up

    # Control: no aging -> the routine clip starves forever.
    control = run(aging_per_tick=0.0, horizon=60)
    assert control.completed_total(EventType.ROUTINE) == 0, (
        "without aging the routine clip should starve (control)"
    )

    # With aging 2.0/tick the routine clip overtakes fresh failures
    # (30 + 55 cap = 85 > 80) at ~tick 28 and completes.
    aged = run(aging_per_tick=2.0, horizon=60)
    assert aged.completed_total(EventType.ROUTINE) == 1, (
        "aging must eventually push the routine clip through"
    )
    routine_done_index = next(
        i for i, e in enumerate(aged.completed) if e.etype is EventType.ROUTINE
    )
    assert routine_done_index > 0, "routine must NOT jump the queue immediately"

    # Aging never crosses the intervention floor.
    old_routine = Event(
        event_id=999, etype=EventType.ROUTINE, created_tick=0, video_bytes=MiB
    )
    assert (
        aged.effective_priority(old_routine, now=10_000)
        < BASE_PRIORITY[EventType.INTERVENTION]
    )
    print("PASS 8: aging rescues routine from starvation, control run starves")


# ---------------------------------------------------------------------- 9
def test_seven_day_simulation_invariants() -> None:
    result = run_simulation(seed=42)
    up = result.uploader
    cfg = up.config

    # (a) intervention: zero loss, all videos fully delivered.
    assert up.dropped_total(EventType.INTERVENTION) == 0
    assert (
        up.completed_total(EventType.INTERVENTION)
        == result.generated[EventType.INTERVENTION]
    )

    # (b) hard quota, every single day.
    for stats in up.days:
        assert stats.bytes_uploaded <= cfg.daily_budget_bytes, (
            "day %d over budget" % stats.day
        )

    # (c) outage day uploads less; backlog carried over and resumed without
    #     re-sending: every completed event shipped exactly its size once.
    assert up.day_stats(OUTAGE_DAY).bytes_uploaded < up.day_stats(0).bytes_uploaded
    for e in up.completed:
        assert e.bytes_sent == e.metadata_bytes + e.video_bytes, (
            "event %d re-uploaded bytes" % e.event_id
        )

    # (d) storm day: routine video evicted (never intervention/failure here),
    #     intervention took the lion's share of the quota.
    storm = up.day_stats(STORM_DAY)
    assert storm.video_dropped[EventType.ROUTINE] > 0
    assert storm.video_dropped[EventType.INTERVENTION] == 0
    assert (
        storm.bytes_by_type[EventType.INTERVENTION]
        > storm.bytes_by_type[EventType.ROUTINE]
    )
    assert storm.bytes_by_type[EventType.ROUTINE] < 0.25 * cfg.daily_budget_bytes

    # (e) privacy-by-design: level-1 metadata reached the cloud for EVERY
    #     generated event, including all dropped-video clips.
    meta_total = sum(s.metadata_uploaded for s in up.days)
    assert meta_total == sum(result.generated.values())

    # (f) backoff was actually exercised by the flaky link.
    assert sum(s.chunk_failures for s in up.days) > 0

    # (g) determinism: identical rerun.
    rerun = run_simulation(seed=42)
    assert [s.bytes_uploaded for s in rerun.uploader.days] == [
        s.bytes_uploaded for s in up.days
    ]
    print(
        "PASS 9: 7-day sim -- zero intervention loss, quota held, resume exact,"
        " storm triage correct, deterministic"
    )


def main() -> None:
    # The overflow-admit path in test 2 intentionally triggers a WARNING log;
    # keep the assertion output clean.
    logging.disable(logging.WARNING)
    test_priority_order_and_two_level_upload()
    test_intervention_never_dropped()
    test_drop_order_routine_then_novelty_then_failure()
    test_budget_never_exceeded_scripted()
    test_resume_after_network_outage()
    test_exponential_backoff()
    test_storm_squeezes_routine_video_not_metadata()
    test_aging_prevents_starvation()
    test_seven_day_simulation_invariants()
    print("\nALL 9 TESTS PASSED")


if __name__ == "__main__":
    main()
```




## uploader.py

```python
"""Edge upload queue for a home-robot fleet (Playbook A, bandwidth-starved collection).

Models the on-device uploader of a home robot that must ship event clips to the
cloud over a residential WiFi uplink with a hard daily quota. Design invariants:

  1. Priority order: INTERVENTION > FAILURE > NOVELTY (embedding-distance proxy)
     > ROUTINE. Interventions are teleop takeovers -- the highest-value training
     data -- and are never dropped, ever.
  2. Two-level, privacy-by-design upload: a tiny metadata record (task id,
     outcome, novelty score -- no pixels) always uploads BEFORE any video bytes
     of the same event. Video is level 2 and competes under the quota. The
     cloud therefore has full fleet visibility even when video is triaged out,
     and can decide which video to pull. This is enforced structurally:
     ``_video_candidates`` refuses events whose metadata is not yet uploaded.
  3. Daily bandwidth budget is a hard cap: a chunk is only sent if it fits in
     the remaining budget, so the quota can never be exceeded.
  4. Large files upload in fixed-size chunks; completed chunks survive network
     outages and process restarts (resume = continue from ``chunks_done``).
  5. Transfer failures back off exponentially (base * 2^(attempts-1), capped).
  6. Aging: non-intervention events gain priority as they wait, so ROUTINE
     clips cannot starve forever behind a steady FAILURE stream. Aging is
     capped below the INTERVENTION floor: seniority never outranks a takeover.
  7. Ring buffer: when local storage is full, evict the lowest-effective-
     priority non-intervention video first (in practice: youngest ROUTINE).
     Evicting a video keeps its metadata queued -- the cloud still learns the
     clip existed. Interventions are never evicted; if only interventions
     remain, an incoming intervention is admitted over capacity (logged), and
     an incoming non-intervention is rejected instead.

Pure standard library, Python 3.9 compatible, fully deterministic (any
randomness is injected by the caller through ``failure_model``).
"""

import enum
import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

logger = logging.getLogger("edge_uploader")

MiB = 1024 * 1024


class EventType(enum.Enum):
    """Trigger classes, ordered by training value (see 06 Playbook A)."""

    INTERVENTION = "intervention"  # teleop takeover: labelled correction
    FAILURE = "failure"  # task retry / timeout / abort
    NOVELTY = "novelty"  # scene embedding far from fleet distribution
    ROUTINE = "routine"  # uniform random sample (anti selection-bias)


#: Base priority per class. INTERVENTION sits above the non-intervention
#: ceiling (see UploaderConfig) so no amount of aging or novelty bonus can
#: outrank it.
BASE_PRIORITY = {
    EventType.INTERVENTION: 100.0,
    EventType.FAILURE: 80.0,
    EventType.NOVELTY: 50.0,
    EventType.ROUTINE: 30.0,
}

# FailureModel(event, attempts_so_far, tick) -> True if this chunk send fails.
FailureModel = Callable[["Event", int, int], bool]


@dataclass(frozen=True)
class UploaderConfig:
    """Tuning knobs. Defaults model one robot on a home broadband uplink."""

    ticks_per_day: int = 24  # 1 tick = 1 hour
    chunk_bytes: int = 4 * MiB  # resumable-upload chunk size
    link_bytes_per_tick: int = 128 * MiB  # physical uplink per tick
    daily_budget_bytes: int = 1536 * MiB  # WiFi upload quota per day
    buffer_capacity_bytes: int = 6144 * MiB  # local NVMe ring buffer
    aging_per_tick: float = 0.5  # priority points per waiting tick
    aging_cap: float = 55.0  # max seniority bonus
    non_intervention_ceiling: float = 95.0  # aging can never cross this
    novelty_bonus_max: float = 15.0  # scales with embedding distance
    backoff_base_ticks: int = 2  # first retry delay
    backoff_cap_ticks: int = 16  # max retry delay

    def __post_init__(self) -> None:
        if self.chunk_bytes <= 0 or self.daily_budget_bytes <= 0:
            raise ValueError("chunk_bytes and daily_budget_bytes must be positive")
        if self.chunk_bytes > self.daily_budget_bytes:
            raise ValueError("a single chunk must fit inside the daily budget")
        if self.chunk_bytes > self.link_bytes_per_tick:
            raise ValueError("a single chunk must fit inside one tick of link capacity")
        if self.non_intervention_ceiling >= BASE_PRIORITY[EventType.INTERVENTION]:
            raise ValueError("ceiling must stay below the INTERVENTION floor")
        if self.aging_per_tick < 0 or self.aging_cap < 0:
            raise ValueError("aging parameters must be non-negative")
        if (
            self.backoff_base_ticks < 1
            or self.backoff_cap_ticks < self.backoff_base_ticks
        ):
            raise ValueError("invalid backoff configuration")


@dataclass
class Event:
    """One triggered clip: a small metadata record plus a chunked video blob."""

    event_id: int
    etype: EventType
    created_tick: int
    video_bytes: int
    metadata_bytes: int = 2048
    novelty: float = 0.0  # embedding-distance proxy in [0, 1]

    # -- mutable upload state -------------------------------------------------
    chunks_done: int = 0
    metadata_done: bool = False
    video_dropped: bool = False  # evicted from ring buffer (metadata kept)
    attempts: int = 0  # consecutive failed chunk sends
    next_retry_tick: int = 0  # earliest tick the next send may happen
    bytes_sent: int = 0  # exact bytes shipped (proves no re-upload)

    def __post_init__(self) -> None:
        if self.video_bytes < 0 or self.metadata_bytes <= 0:
            raise ValueError("invalid event sizes")
        if not 0.0 <= self.novelty <= 1.0:
            raise ValueError("novelty must be in [0, 1]")

    def total_chunks(self, chunk_bytes: int) -> int:
        return (self.video_bytes + chunk_bytes - 1) // chunk_bytes

    def video_done(self, chunk_bytes: int) -> bool:
        return self.chunks_done >= self.total_chunks(chunk_bytes)

    def next_chunk_size(self, chunk_bytes: int) -> int:
        remaining = self.video_bytes - self.chunks_done * chunk_bytes
        return min(chunk_bytes, remaining)


def _type_counter() -> Dict[EventType, int]:
    return {etype: 0 for etype in EventType}


@dataclass
class DayStats:
    """Per-day accounting; the budget invariant is checked against this."""

    day: int
    bytes_uploaded: int = 0
    bytes_by_type: Dict[EventType, int] = field(default_factory=_type_counter)
    metadata_uploaded: int = 0
    video_completed: Dict[EventType, int] = field(default_factory=_type_counter)
    video_dropped: Dict[EventType, int] = field(default_factory=_type_counter)
    chunk_failures: int = 0
    overflow_admits: int = 0


class EdgeUploader:
    """Priority upload queue with quota, resume, backoff, aging and eviction.

    Usage: ``offer()`` events as triggers fire, then call ``run_tick()`` once
    per tick with the current link state. All scheduling decisions are made
    with an O(n) scan over pending events -- deliberate: n is bounded by the
    ring buffer, and aging makes priorities time-varying, which would leave a
    heap permanently stale.
    """

    def __init__(
        self,
        config: Optional[UploaderConfig] = None,
        failure_model: Optional[FailureModel] = None,
    ) -> None:
        self.config = config if config is not None else UploaderConfig()
        self._failure_model: FailureModel = (
            failure_model if failure_model is not None else (lambda _e, _a, _t: False)
        )
        self.now: int = 0
        self._events: List[Event] = []
        self._day_stats: Dict[int, DayStats] = {}
        self.completed: List[Event] = []
        self._seen_ids: set = set()

    # ------------------------------------------------------------------ admit

    def offer(self, event: Event) -> bool:
        """Admit an event, evicting lower-priority video if the buffer is full.

        Returns True if the event's *video* was admitted. The metadata record
        is queued unconditionally (it is ~5 orders of magnitude smaller than
        video and is the level-1 privacy artifact the cloud triages with).
        """
        if event.event_id in self._seen_ids:
            raise ValueError("duplicate event_id %d" % event.event_id)
        self._seen_ids.add(event.event_id)
        day = self._stats_for(self.now)

        admitted = self._make_room(event, day)
        if not admitted:
            event.video_dropped = True
            day.video_dropped[event.etype] += 1
            logger.info(
                "buffer full: rejected video of %s #%d (metadata kept)",
                event.etype.value,
                event.event_id,
            )
        self._events.append(event)
        return admitted

    def _make_room(self, incoming: Event, day: DayStats) -> bool:
        """Ring-buffer eviction. Never touches INTERVENTION video."""
        needed = incoming.video_bytes
        if self.buffer_used + needed <= self.config.buffer_capacity_bytes:
            return True

        incoming_prio = self.effective_priority(incoming)
        victims = [
            e
            for e in self._events
            if e.etype is not EventType.INTERVENTION
            and not e.video_dropped
            and not e.video_done(self.config.chunk_bytes)
            and self.effective_priority(e) < incoming_prio
        ]
        # Evict cheapest-to-lose first: lowest effective priority, then newest.
        victims.sort(
            key=lambda e: (self.effective_priority(e), -e.created_tick, -e.event_id)
        )
        freed = 0
        chosen: List[Event] = []
        for victim in victims:
            if self.buffer_used - freed + needed <= self.config.buffer_capacity_bytes:
                break
            chosen.append(victim)
            freed += victim.video_bytes

        if self.buffer_used - freed + needed <= self.config.buffer_capacity_bytes:
            for victim in chosen:
                self._evict_video(victim, day)
            return True

        if incoming.etype is EventType.INTERVENTION:
            # Nothing evictable is enough: admit over capacity rather than
            # ever losing a takeover. Bounded in practice (interventions are
            # rare); the overflow is surfaced in stats for fleet monitoring.
            for victim in chosen:
                self._evict_video(victim, day)
            day.overflow_admits += 1
            logger.warning(
                "buffer overflow-admit for intervention #%d", incoming.event_id
            )
            return True
        return False

    def _evict_video(self, event: Event, day: DayStats) -> None:
        event.video_dropped = True
        day.video_dropped[event.etype] += 1
        logger.info(
            "evicted video of %s #%d (metadata kept)", event.etype.value, event.event_id
        )

    # -------------------------------------------------------------- scheduling

    def effective_priority(self, event: Event, now: Optional[int] = None) -> float:
        """Base priority + novelty bonus + capped seniority (aging)."""
        tick = self.now if now is None else now
        base = BASE_PRIORITY[event.etype]
        if event.etype is EventType.INTERVENTION:
            return base  # never modified, never outranked
        if event.etype is EventType.NOVELTY:
            base += self.config.novelty_bonus_max * event.novelty
        age = max(0, tick - event.created_tick)
        aging = min(age * self.config.aging_per_tick, self.config.aging_cap)
        return min(base + aging, self.config.non_intervention_ceiling)

    def run_tick(self, network_up: bool = True) -> None:
        """Advance one tick; upload as much as quota/link/network allow."""
        day = self._stats_for(self.now)
        if network_up:
            self._upload_pass(day)
        self.now += 1

    def _upload_pass(self, day: DayStats) -> None:
        budget_left = self.config.daily_budget_bytes - day.bytes_uploaded
        link_left = self.config.link_bytes_per_tick

        # Level 1: metadata-first (privacy-by-design). Tiny, drains before any
        # video byte moves, still charged against the quota (honest accounting).
        pending_meta = sorted(
            (e for e in self._events if not e.metadata_done),
            key=lambda e: (-self.effective_priority(e), e.created_tick, e.event_id),
        )
        for event in pending_meta:
            cost = event.metadata_bytes
            if cost > budget_left or cost > link_left:
                break
            event.metadata_done = True
            event.bytes_sent += cost
            day.bytes_uploaded += cost
            day.bytes_by_type[event.etype] += cost
            day.metadata_uploaded += 1
            budget_left -= cost
            link_left -= cost
            self._maybe_finish(event, day)

        # Level 2: video chunks, strict priority. If the top candidate's chunk
        # does not fit the remaining quota we stop rather than bypass it with a
        # smaller low-priority file -- bypass would reintroduce starvation.
        while True:
            candidate = self._top_video_candidate()
            if candidate is None:
                break
            chunk = candidate.next_chunk_size(self.config.chunk_bytes)
            if chunk > budget_left or chunk > link_left:
                break
            if self._failure_model(candidate, candidate.attempts, self.now):
                candidate.attempts += 1
                delay = min(
                    self.config.backoff_base_ticks * (2 ** (candidate.attempts - 1)),
                    self.config.backoff_cap_ticks,
                )
                candidate.next_retry_tick = self.now + delay
                day.chunk_failures += 1
                logger.info(
                    "chunk send failed for #%d, retry in %d ticks",
                    candidate.event_id,
                    delay,
                )
                continue  # backoff excludes it; scan for the next candidate
            candidate.chunks_done += 1
            candidate.attempts = 0  # success resets backoff
            candidate.bytes_sent += chunk
            day.bytes_uploaded += chunk
            day.bytes_by_type[candidate.etype] += chunk
            budget_left -= chunk
            link_left -= chunk
            if candidate.video_done(self.config.chunk_bytes):
                day.video_completed[candidate.etype] += 1
            self._maybe_finish(candidate, day)

    def _top_video_candidate(self) -> Optional[Event]:
        best: Optional[Event] = None
        best_key = None
        for event in self._events:
            if event.video_dropped or event.video_done(self.config.chunk_bytes):
                continue
            if not event.metadata_done:  # level 2 never precedes level 1
                continue
            if event.next_retry_tick > self.now:  # still backing off
                continue
            key = (self.effective_priority(event), -event.created_tick, -event.event_id)
            if best_key is None or key > best_key:
                best, best_key = event, key
        return best

    def _maybe_finish(self, event: Event, day: DayStats) -> None:
        video_settled = event.video_dropped or event.video_done(self.config.chunk_bytes)
        if event.metadata_done and video_settled:
            self._events.remove(event)
            if not event.video_dropped:
                self.completed.append(event)

    # ------------------------------------------------------------------ stats

    @property
    def buffer_used(self) -> int:
        return sum(
            e.video_bytes
            for e in self._events
            if not e.video_dropped and not e.video_done(self.config.chunk_bytes)
        )

    def _stats_for(self, tick: int) -> DayStats:
        day = tick // self.config.ticks_per_day
        if day not in self._day_stats:
            self._day_stats[day] = DayStats(day=day)
        return self._day_stats[day]

    def day_stats(self, day: int) -> DayStats:
        if day not in self._day_stats:
            self._day_stats[day] = DayStats(day=day)
        return self._day_stats[day]

    @property
    def days(self) -> List[DayStats]:
        return [self._day_stats[d] for d in sorted(self._day_stats)]

    def dropped_total(self, etype: EventType) -> int:
        return sum(stats.video_dropped[etype] for stats in self._day_stats.values())

    def completed_total(self, etype: EventType) -> int:
        return sum(1 for e in self.completed if e.etype is etype)

    def pending_events(self) -> List[Event]:
        return list(self._events)
```

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/labs/lab4_edge_uploader/README.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/labs/lab4_edge_uploader/README.md)。作者整理资料；许可和第三方来源范围见阅读指南。
