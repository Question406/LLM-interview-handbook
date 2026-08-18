---
id: ali-memory-conflict
section: alibaba
order: 22
level: A
title: Agent 记忆如何迭代？新旧经验冲突时怎样取舍？
quick: 分短/长期：短期窗口+摘要；长期结构化写入要带时间戳/来源/置信度。冲突时按时间、权威来源、用户显式更正优先，并支持遗忘与审计。
tags:
  - Alibaba
  - Memory
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
  - title: ↗ 淘宝闪购 Agent 算法一面
    url: 'https://www.nowcoder.com/discuss/879393838081597440'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>分短/长期：短期窗口+摘要；长期结构化写入要带时间戳/来源/置信度。冲突时按时间、权威来源、用户显式更正优先，并支持遗忘与审计。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>可落地策略：</p>
<ul>
<li>写入前做冲突检测（同实体不同值）；</li>
<li>保留 provenance：谁说的、何时、哪次工具结果；</li>
<li>用户更正 &gt; 工具权威数据 &gt; 模型推断；</li>
<li>定期衰减低置信记忆，防记忆污染。</li>
</ul>
<p>闪购等面经还会问长周期对话的分层压缩：近详远略 + 关键事件入库检索。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 社招一面</a><a href="https://www.nowcoder.com/discuss/879393838081597440" target="_blank" rel="noopener noreferrer">↗ 淘宝闪购 Agent 算法一面</a></div>
