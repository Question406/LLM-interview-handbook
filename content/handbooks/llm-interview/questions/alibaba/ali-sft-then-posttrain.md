---
id: ali-sft-then-posttrain
section: alibaba
order: 13
level: S
title: SFT 核心流程与数据构建？之后 Post-Training 各自解决什么？
quick: >-
  SFT：定任务分布→采/合成指令数据→清洗配比→监督学习。其后 DPO 解决偏好排序；PPO/RLHF 解决复杂主观目标；GRPO 等 RL
  解决可验证/探索目标。
tags:
  - Alibaba
  - SFT
  - Post-Training
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
<div class="quick"><div class="mini-title">30 秒回答</div><p>SFT：定任务分布→采/合成指令数据→清洗配比→监督学习。其后 DPO 解决偏好排序；PPO/RLHF 解决复杂主观目标；GRPO 等 RL 解决可验证/探索目标。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p><b>SFT：</b>定义场景与格式 → 采集/合成 instruction-response → 去重、安全过滤、难度与任务配比 → 设 loss mask → 用离线评测+人工评查看是否真变好。</p>
<p><b>之后：</b></p>
<ul>
<li><b>DPO：</b>成对偏好，学“更好 vs 更差”；</li>
<li><b>RLHF/PPO：</b>RM + 强化学习，拟合更复杂的人类偏好；</li>
<li><b>GRPO 等：</b>可验证奖励或 group 相对优化，强化推理/工具成功率。</li>
</ul>
<p>强调它们不是堆 buzzword，而是针对不同监督信号。</p></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a></div>
