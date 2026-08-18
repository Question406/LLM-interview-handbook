---
id: ali-prompt-optimize
section: alibaba
order: 19
level: B
title: Prompt 自动推荐/压缩可用哪些策略？
quick: 模板分层、示例检索、embedding 聚类选示范、摘要压缩、关键槽位结构化；效果要用任务指标验证，不只看更短。
tags:
  - Alibaba
  - Prompt
  - Context
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>模板分层、示例检索、embedding 聚类选示范、摘要压缩、关键槽位结构化；效果要用任务指标验证，不只看更短。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>常见路线：</p>
<ul>
<li>按意图路由到短模板；</li>
<li>用 embedding 检索相似成功 case 作 few-shot；</li>
<li>长历史摘要 + 结构化 state，避免全文拼接；</li>
<li>对工具说明做裁剪，只暴露当前任务相关 tools。</li>
</ul></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a></div>
