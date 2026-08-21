---
id: data-mix-curriculum
section: data
order: 212
level: S
title: SFT / RL 的多源数据配比与 Curriculum 怎么定，如何证明没有过拟合某一源？
quick: >-
  先按任务价值与难度分桶设配额，再用温度采样或 mixing law 做小规模配比 sweep；Curriculum 从高通过率短轨迹抬到长程难例。证明没过拟合某一源要靠按来源 held-out、leave-one-source-out 和近重复污染率，而不是总 loss 下降。
tags:
  - Data Mix
  - Curriculum
  - SFT
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: Data Mixing Laws
    url: https://arxiv.org/abs/2403.16952
    type: primary
---

陷阱是把配比讲成「经验 $1:1:1$」或「难例越多越好」。评委要的是可回放的配额实验：每源独立 held-out、配比变更可版本化，以及增益来自泛化而不是背诵主数据源。快手题（`kuaishou-sft-source-mix`）是 SFT 来源配比的场景版；阶跃题（`stepfun-agent-data-mix`）是 Agent RL 的场景版。本题是通用方法：先分桶，再拟合或扫配比，最后用切片证明没有过拟合某一源。

## 配比是优化问题，不是审美

质量过滤后按领域、任务、难度配额抽样，再用温度采样调节长尾：$p_i \propto n_i^{\alpha}$，$\alpha$ 越小越抬长尾。Data Mixing Laws 指出，固定模型规模与步数时，域 $i$ 的验证损失可写成

$$
L_i(r)=c_i+k_i\exp\Big(\sum_j t_{ij} r_j\Big),
$$

其中 $r_j$ 是训练域比例，$t_{ij}\lt 0$ 表示域 $j$ 帮域 $i$。小规模配比 sweep 拟合后再预测大规模 mix，比盲扫更省。SFT 还要看遗忘：主源升、锚点（通用指令、安全、格式）掉，就是挤占而不是补洞。条数不等于有效梯度，短模板会淹没可验证难例。

## Curriculum 避免梯度稀疏

Curriculum 不是「先简单后难」的口号。SFT 先格式与高置信短样本，再提高难例温度。RL 从高通过率、短轨迹到低通过率、长程 agent，避免一开始全是不可能成功的题导致组内全错、advantage 全零。只加难例、无 verifier、无课程，会学噪声。各桶要盯非零 advantage 比例：全对或全错都该调采样，而不是加条数。配比变更必须绑定 `dataset_version`，能回放才能归因。

## 怎么证明没有过拟合某一源

1. 每源留 held-out，且与训练集做近重复去污（`data-contamination`），否则「该源 holdout 涨」只是背诵。
2. leave-one-source-out 或配比 sweep：拿掉主源后邻域是否塌；只涨主源、邻域与私有变体不动，就是过拟合。
3. 报告近重复污染率、各桶 $\Delta$ 能力 / $\Delta$ token，而不是总 loss。
4. 对照至少：等比例、按缺口加权、按质量加权、curriculum。过拟合防护与 `meituan-sft-overfit` 同一套：模板重复会把配比实验变成背数据。

Mixing law 拟合的是预训练域损失，不能直接当 SFT win-rate 或 RL 成功率的预言机：后训练目标更稀疏、标签更噪，仍要按任务 held-out 做小规模真实 sweep，定律只提供初值和哪些域互相伤害的先验。RL 配比还有一层动态：用当前 actor 估各桶 pass@$1$ 与非零 advantage 率，难度标签每周更新，静态 $r$ 会在政策变强后变成全对。面试收口：比例是实验结果，不是出发假设；没有按源切片和 leave-one-source-out，任何 mix 都只是口味。难例必须落在当前政策可探索区间，否则课程只是在灌噪声。

## 追问

- **为什么不用固定 $1:1:1$？** 条数不等于有效梯度。短模板会淹没难例；要用 holdout 缺口、token 效率和 mixing law 预测，而不是拍整数比。
- **只加难例会怎样？** 无课程、无 verifier 时 RL 组内全错、SFT 学噪声。先保证各桶非零 advantage / 可验证标签，再抬难度温度。
- **怎么向评委证明没背主源？** 按源 held-out + leave-one-source-out + 近重复污染率三件套；缺任何一件都只是总榜好看。
- **和快手 / 阶跃那两题怎么分？** 那两题是场景约束（SFT 来源、Agent 工具桶）；本题是通用流程：分桶、拟合/扫配比、切片证明。场景题里的数字是本方法的实例，不是另一套哲学。
- **配比一周一变如何归因？** 一次只动一维，绑定 `dataset_version` 与环境 hash；同时动奖励、过滤和 mix，分不清是谁在涨。
