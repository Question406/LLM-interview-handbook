---
id: ali-modular-agent-plan
section: alibaba
order: 16
level: A
title: Modular Agent 如何实现多步规划？工具链路调度与 fallback 怎么设计？
quick: 规划器产出步骤/子目标，执行器按状态机调用工具；每步有输入输出契约、超时重试、幂等与降级。fallback：换工具、缩任务、澄清用户、转人工。
tags:
  - Alibaba
  - Agent
  - Harness
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>规划器产出步骤/子目标，执行器按状态机调用工具；每步有输入输出契约、超时重试、幂等与降级。fallback：换工具、缩任务、澄清用户、转人工。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>工业界回答要落到控制面：</p>
<ul>
<li><b>规划：</b>Plan-and-Execute / ReAct；关键业务可用确定性工作流包住 LLM 规划。</li>
<li><b>调度：</b>工具白名单、并行/串行依赖、参数 schema 校验。</li>
<li><b>fallback：</b>瞬时错误重试；逻辑错误换策略；超预算终止；高风险 Human-in-the-loop。</li>
<li><b>可观测：</b>trace、tool 指纹、重复调用检测防死循环。</li>
</ul></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a></div>
