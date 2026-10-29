---
id: drustz-8b9dad60a590dbb018
section: mlsd
order: 120
level: A
title: 16 · Case：设计 RL（post-training）数据流水线 · 17. 常见追问 + 应答要点
quick: 作者文档章节 · 16 · Case：设计 RL（post-training）数据流水线 · 17. 常见追问 + 应答要点
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md
    type: primary
---
## 17. 常见追问 + 应答要点

1. **「为什么不干脆全都在训练循环里做 dynamic sampling？」**
   → 因为我会为「对任何近期 checkpoint 都退化」的那批题反复付 rollout 费用，且每个实验重付一遍。而且在线过滤让每步耗时可变，分布式下同步开销明显。离线负责大头（可复用、可抢占、可错峰），在线负责漂移残差。

2. **「16 条探测的统计功效够吗？」**
   → 如果目标是估计 p，不够（SE≈0.12）。但我的判据不是估 p，是**判别退化**——`p^16+(1−p)^16` 在 p∈[0.2,0.8] 上小于 3%，在 p>0.95 上大于 44%。这个判据恰好在我需要它敏感的地方敏感。要更精细的 curriculum 分桶才需要更大的 n，那时我会按域设不同的  $n_{probe}$ 。

3. **「模型变强之后数据不就没用了吗？」**
   → 对，这正是要点。所以①难度标注绑 checkpoint 并会 stale；②too_hard 池必须保留、定期回捞；③训练本身的 rollout 免费提供当前 p̂，不用额外探测；④长期看供给侧必须持续产出更难的题，否则 RL 会撞天花板——这是「合成能不能超过教师」的问题，也是我认为原始语料转换比合成更有战略价值的原因。

4. **「怎么证明你这批数据真的有用？」**
   → 固定算力的 A/B：同一 checkpoint、同一超参、同样的总 rollout 预算，加这批 vs 不加，比下游 eval。**不能用「训练 pass rate 涨了」证明**，那可能是难度筛松了或者 verifier 被 hack 了。方法论同 [07 §13](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573) 的 data ablation ladder。

5. **「verifier 假阳性怎么主动找，而不是等它出问题？」**
   → 三条：①对 reward=满分的样本做**分层人工抽检**，报假阳性率作为 guardrail 指标；②准备一批**对抗样本**（枚举式答案、hard-code 的代码解、格式合规但内容空洞的回答），当作 verifier 的单元测试，每次改 verifier 跑一遍；③监控「pass rate 跨 checkpoint 突然跳变」的 prompt。

6. **「judge 一致性差，多 judge 投票不就行了？」**
   → 投票是最后手段。它成本翻倍，而且**共享盲区不会被投票消除**——三个同源模型会在同一个地方一起错。我优先缩小 judge 的作用域：能抽答案就别让它读全文，能拆 claim 就别让它整体打分。我有对照数据支持这个排序（0.569 → 0.844）。

7. **「多域混合，怎么防止模型只在最容易验证的域上变强？」**
   → 三点：①配比设**比例下限**，不让 yield 驱动的机制饿死难验证的域；②eval 必须**分域报**，总均值会掩盖；③警惕 yield 驱动的自我强化——可验证性和产出量正相关，任性地按产出配比会一路滑向数学。

8. **「合成数据能不能超过teacher model的水平？」**
   → 单纯distillation式合成不能，天花板就是教师。能超过的路径是：①**逆向构造**（先造答案/结构再造题，难度不受教师解题能力限制）；②**组合难化**（把多个已验证的子问题组合，验证器仍然可靠）；③**从人类语料挖**（竞赛题、研究性问题的难度上界是人类，不是教师）——这也是我把原始语料转换当主线的原因。

9. **「不可验证的领域怎么办？这套还成立吗？」**
   → 核心机制（探测难度、丢退化样本）依赖的是「reward 有区分度」，不依赖「reward 可程序化」。judge-based reward 同样可以做组内方差探测。但**假阳性风险高一个量级**，所以我会：把难度带收窄（更保守）、增加人工抽检比例、并且优先做 §6 的可验证化改造，而不是直接上 judge。

10. **「RL 之前需要 SFT 吗？数据 pipeline 要不要顺便产 SFT 数据？」**
    → 需要，但用途不同：SFT 负责把格式、工具协议、基本行为教会，让策略在 RL 的探索空间里有一个非零起点。如果基座连答案格式都不稳，所有题的 p 都接近 0，整个难度筛选机制会失效（全部落进 too_hard）。**顺便产 SFT 数据是可以的**——被丢弃的「太简单」样本加上它们的正确 rollout，正好是高质量 SFT/rejection-sampling 语料。这是一个很自然的副产品回收。

11. **「怎么处理部分正确（partial credit）？二元 reward 是不是太粗？」**
    → 连续 reward 让组内方差更容易非零，看起来能缓解退化问题，但它把假阳性风险变成了连续谱——「答对一半」的判定比「对/错」更依赖 judge，更容易被 hack。我的取向是：**能二元就二元，需要 partial credit 时用可程序化的分解**（比如代码题按测试用例通过数），而不是让 judge 给 0–1 的连续分。

12. **「探测的 rollout 能不能顺便用作训练数据？」**
    → 探测的 16 条是 on-policy 的，理论上可以进训练 batch，但要小心：①它们来自探测时的 checkpoint，训练开始后就 off-policy 了，需要重要性修正或严格限制滞后；②被丢弃的样本的 rollout 不能进（那些组的 advantage 是 0，进去只是稀释 batch）。**更有价值的复用是拿它们做解法骨架去重（§8.2）和 SFT 语料回收**，那两个用途没有 on-policy 要求。

13. **「如果只给你一周，先做什么？」**
    → 先做**难度探测**这一件事，接在现有的开源数据集后面。理由：它不需要新的数据供给、不需要新的 verifier，改动最小，但能立刻给出「我现在有多少算力在空转」这个数字——有了这个数字，后面所有投资（改供给、改 verifier、改配比）才有 ROI 论证的分母。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/16_case_rl_data_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
