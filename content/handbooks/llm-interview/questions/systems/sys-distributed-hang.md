---
id: sys-distributed-hang
section: systems
order: 20
level: S
title: 分布式训练卡住没有报错，怎样判断是 NCCL 问题还是代码路径不一致？
quick: >-
  Collective 要求所有 rank 以相同顺序、相同 shape 参与。某个 rank 提前异常、数据耗尽、条件分支跳过通信，就会让其他 rank
  看起来像“卡在 NCCL”；先定位最早发生分歧的 rank 和 collective。
tags:
  - NCCL
  - Distributed Training
  - Debugging
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: NCCL communicator guide
    url: >-
      https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>“NCCL hang”是现象，不一定是网络故障。最常见的可复现原因是 rank divergence。</p><ol><li>为每个 collective 记录 rank、step、操作类型、tensor shape、sequence number 和前后的关键状态；</li><li>检查 dataloader 长度、OOM/exception、条件分支、gradient accumulation、unused parameter 和 checkpoint restore 是否在所有 rank 一致；</li><li>用 watchdog/timeout 获取堆栈，比较最早停止前进的 rank，而不是只盯最后超时的 rank；</li><li>确认代码路径一致后，再排查 communicator、网卡、拓扑与驱动版本。</li></ol><p>barrier 可以帮助缩小范围，但在错误位置额外插 barrier 也可能掩盖或制造死锁，不能当根治方案。</p><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html" target="_blank" rel="noreferrer">NCCL communicator guide</a></div></div>
