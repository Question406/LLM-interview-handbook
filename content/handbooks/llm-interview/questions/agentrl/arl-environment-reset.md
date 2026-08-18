---
id: arl-environment-reset
section: agentrl
order: 17
level: S
title: Agent RL 里的 Environment Reset 为什么比普通文本 RL 更难？
quick: >-
  网页、数据库、文件和外部 API 都是有状态的。若 reset 不彻底，后一个 episode 会看到前一个轨迹留下的订单、缓存或权限，reward 和
  observation 被污染，训练与 eval 都不再可比较。
tags:
  - Agent RL
  - Environment
  - Reproducibility
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: WebArena
    url: 'https://arxiv.org/abs/2307.13854'
    type: legacy-reference
  - title: OSWorld
    url: 'https://arxiv.org/abs/2404.07972'
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>文本 completion 通常可近似成独立样本；Agent episode 会改变环境。reset 是定义 MDP 初始状态分布的一部分，而不是测试基础设施细节。</p><ul><li><b>隔离状态：</b>为每个 episode 建独立账号/目录/数据库 snapshot，或能原子恢复到相同初始状态。</li><li><b>控制随机性：</b>记录 seed、任务版本、工具版本、网络 mock 与 observation 截止时间；但不要误以为“完全 deterministic”就等于真实。</li><li><b>处理副作用：</b>写操作必须 cleanup 或回滚；不可逆的外部行为应使用 sandbox 或 human gate。</li></ul><p>否则模型可能学会利用上一个 episode 遗留的捷径，offline reward 很高但部署立即失效。</p><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://arxiv.org/abs/2307.13854" target="_blank" rel="noreferrer">WebArena</a><a href="https://arxiv.org/abs/2404.07972" target="_blank" rel="noreferrer">OSWorld</a></div></div>
