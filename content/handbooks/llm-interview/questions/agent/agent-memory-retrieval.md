---
id: agent-memory-retrieval
section: agent
order: 12
level: A
title: Memory Retrieval 怎么评估？
quick: >-
  不能只看 Recall@K。要同时测“该记忆是否应该被召回”“召回后是否改善任务”“错误/过期 memory 是否造成伤害”，并分 read/write
  两个子问题评估。
tags:
  - Memory
  - Eval
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>不能只看 Recall@K。要同时测“该记忆是否应该被召回”“召回后是否改善任务”“错误/过期 memory 是否造成伤害”，并分 read/write 两个子问题评估。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>Memory 系统至少有 <b>write policy、storage/compaction、retrieval、usage</b> 四步。Eval 可以构造：需要 memory 的任务、不需要 memory 的 distractor、冲突 memory、过期 memory、敏感 memory。</p><p>指标：retrieval recall/precision、downstream success delta、false-memory harm、token overhead、freshness accuracy、privacy violation rate。一个 recall 很高但总把无关历史塞 context 的系统可能更差。</p></div>
