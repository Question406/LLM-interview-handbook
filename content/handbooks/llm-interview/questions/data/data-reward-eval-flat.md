---
id: data-reward-eval-flat
section: data
order: 5
level: S
title: RL reward 涨但真正 Eval 不涨，怎么 Debug？
quick: >-
  按 Reward validity → Reward hacking → Train/Eval distribution → Policy drift →
  Optimization statistics → Eval reliability 六层排查，不要先盲调 learning rate。
tags:
  - Debug
  - Reward
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>按 Reward validity → Reward hacking → Train/Eval distribution → Policy drift → Optimization statistics → Eval reliability 六层排查，不要先盲调 learning rate。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><ol><li><b>Reward validity：</b>人工看 high-reward/low-reward trajectories，确认 proxy 真在测目标。</li><li><b>Reward hacking：</b>看 length、format、repetition、judge phrase、verifier exploit。</li><li><b>Distribution：</b>训练 prompts、rollout decoding 与 eval domain 是否一致？</li><li><b>Policy drift：</b>看 KL、SFT/general capability regression、language/style drift。</li><li><b>Optimization：</b>entropy、clip fraction、importance ratio、grad norm、advantage、zero-variance group rate、response length。</li><li><b>Eval reliability：</b>sample size、judge noise、temperature、max tokens、prompt template、benchmark contamination。</li></ol><p>一个实用 diagnostic 是把 reward 与 external success metric 做 scatter/分桶，找“reward 高但 external eval 低”的 cluster，再回溯共同特征。若训练 reward 继续升而 correlation 持续下降，往往是 proxy overoptimization 而不是 optimizer 没学会。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>怎么区分 reward overfit 与 catastrophic forgetting？</summary><div class="follow-answer"><p>前者通常在目标 reward 上过度优化并出现可解释 shortcut；后者会在与 reward 无关的 general capabilities 上也明显退化。需要 multi-benchmark retention。</p></div></details><details class="followup"><summary>如果 train/eval distribution 一样仍不涨？</summary><div class="follow-answer"><p>检查 reward metric 是否等价于 eval、decode config 是否一致、reward normalization/length bias、以及是否存在训练数据 leakage 让 reward 误高。</p></div></details></div>
