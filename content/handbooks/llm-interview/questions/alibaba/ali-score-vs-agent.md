---
id: ali-score-vs-agent
section: alibaba
order: 24
level: A
title: 单次 LLM 打分算不算 Agent？和多轮工具 Agent 的核心区别？
quick: 单次打分更像一次性推理/判别；Agent 强调多步决策、与环境交互、状态更新与终止条件。差别在控制回路，不在是否调用了一次模型。
tags:
  - Alibaba
  - Agent
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>单次打分更像一次性推理/判别；Agent 强调多步决策、与环境交互、状态更新与终止条件。差别在控制回路，不在是否调用了一次模型。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>可用定义对齐面试官：</p>
<ul>
<li><b>单次打分：</b>无环境反馈闭环，或只有一次 forward；</li>
<li><b>Agent：</b>observe→act→observe 循环，工具/用户/环境改变 state。</li>
</ul>
<p>不要把“用了 LLM”等同于 Agent；要讲清状态、动作空间、停止条件与责任边界。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f" target="_blank" rel="noopener noreferrer">↗ 淘天 Agent 社招一面</a></div>
