---
id: ali-qwen-finetune-loss
section: alibaba
order: 18
level: A
title: 微调 Qwen 时，训练阶段和 Loss 如何选择？
quick: >-
  先定目标：指令遵循用 SFT（只对 assistant/action token 计 loss）；偏好用 DPO；可验证目标用 GRPO。阶段不要跳，数据与
  mask 必须匹配部署协议。
tags:
  - Alibaba
  - Qwen
  - SFT
realInterview: true
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
  - title: ↗ Qwen GSPO paper
    url: 'https://arxiv.org/abs/2507.18071'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>先定目标：指令遵循用 SFT（只对 assistant/action token 计 loss）；偏好用 DPO；可验证目标用 GRPO。阶段不要跳，数据与 mask 必须匹配部署协议。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>淘天校招原题常见追问：</p>
<ul>
<li>为何先 SFT 再对齐：先学会格式/工具协议，再优化偏好或成功率；</li>
<li>Loss mask：user/tool response 通常不进 policy loss；</li>
<li>LoRA vs 全参：数据少/多任务隔离用 LoRA；要大幅改行为再考虑更大更新；</li>
<li>用 Qwen 系列时关注其 chat template、tool schema 与官方 post-train 实践（含 GSPO）。</li>
</ul></div>
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://www.nowcoder.com/discuss/911218249889480704" target="_blank" rel="noopener noreferrer">↗ 淘天大模型 Agent 校招面经</a><a href="https://arxiv.org/abs/2507.18071" target="_blank" rel="noopener noreferrer">↗ Qwen GSPO paper</a></div>
