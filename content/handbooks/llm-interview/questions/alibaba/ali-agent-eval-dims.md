---
id: ali-agent-eval-dims
section: alibaba
order: 17
level: S
title: Agent 评估体系有哪些维度？如何衡量 planning vs hallucination？
quick: >-
  任务成功率、步数/成本、工具正确率、规划遵从、幻觉/忠实度、安全越权率、澄清率。Planning 看子目标分解与依赖；幻觉看无证据断言与错误 tool
  参数。
tags:
  - Alibaba
  - Agent
  - Eval
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>任务成功率、步数/成本、工具正确率、规划遵从、幻觉/忠实度、安全越权率、澄清率。Planning 看子目标分解与依赖；幻觉看无证据断言与错误 tool 参数。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>建议把指标拆开，避免只看最终 success：</p>
<ul>
<li><b>Outcome：</b>任务完成、业务 KPI；</li>
<li><b>Process：</b>平均工具轮次、无效调用、循环率；</li>
<li><b>Planning：</b>计划可执行性、关键步骤覆盖、是否过早结束；</li>
<li><b>Hallucination：</b>无依据事实、伪造引用、与工具结果矛盾；</li>
<li><b>Safety：</b>越权、不可逆操作未确认。</li>
</ul>
<p>最好有固定评测集 + trace 回归，而不是每次人工聊天感觉。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a></div>
