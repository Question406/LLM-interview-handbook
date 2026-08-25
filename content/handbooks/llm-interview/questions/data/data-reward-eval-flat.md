---
id: data-reward-eval-flat
section: data
order: 5
level: S
title: RL reward 涨但真正 Eval 不涨，怎么 Debug？
quick: >-
  按 Reward 是否成立、有没有 hacking、Train/Eval 分布、Policy drift、优化统计、Eval
  可不可靠这六层排查。别一上来盲调 learning rate。
tags:
  - Debug
  - Reward
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>按 Reward 是否成立、有没有 hacking、Train/Eval 分布、Policy drift、优化统计、Eval 可不可靠这六层排查。别一上来盲调 learning rate。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><ol><li><b>Reward validity：</b>人工看 high-reward/low-reward trajectories，确认 proxy 真在测目标。</li><li><b>Reward hacking：</b>看 length、format、repetition、judge phrase、verifier exploit。</li><li><b>Distribution：</b>训练 prompts、rollout decoding 与 eval domain 是否一致？</li><li><b>Policy drift：</b>看 KL、SFT/general capability regression、language/style drift。</li><li><b>Optimization：</b>entropy、clip fraction、importance ratio、grad norm、advantage、zero-variance group rate、response length。</li><li><b>Eval reliability：</b>sample size、judge noise、temperature、max tokens、prompt template、benchmark contamination。</li></ol><p>一个能用的 diagnostic：把 reward 和外部 success metric 做 scatter 或分桶，找「reward 高但外部 eval 低」的 cluster，再回溯共同特征。若训练 reward 还在涨、correlation 持续掉，往往是 proxy 被 overoptimize，不是 optimizer 没学会。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>怎么区分 reward overfit 与 catastrophic forgetting？</summary><div class="follow-answer"><p>前者通常在目标 reward 上优化过头，还能讲出 shortcut。后者会在跟 reward 无关的通用能力上也明显退化。需要 multi-benchmark retention。</p></div></details><details class="followup"><summary>如果 train/eval distribution 一样仍不涨？</summary><div class="follow-answer"><p>检查 reward metric 是不是和 eval 一回事、decode config 是否一致、reward normalization 和 length bias，以及训练数据有没有 leakage 把 reward 抬假了。</p></div></details></div>
