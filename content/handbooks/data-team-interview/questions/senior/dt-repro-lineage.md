---
id: dt-repro-lineage
section: senior
order: 9
level: A
title: Director：一周后这批数据还能复现吗，lineage 要记什么？
quick: "能不能复现，取决于每条样本能否追到来源和版本：来源 URL、许可集或研究协议，以及抽取器、过滤器、教师、验证器和 dataset_version。这样每次增益能对应固定评测与具体 mix，opt-out 也能按精确记录撤回。只有文件目录，没有来源与版本，不能说明数据可复现。"
companies:
  - apple
tags:
  - Apple
  - Lineage
  - Governance
  - Reproducibility
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
  - title: Applebot model training and individual privacy rights
    url: https://support.apple.com/en-us/120320
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

能不能复现，取决于每条样本和每次实验能否追溯到来源与版本。只说「文件都在 HDFS」，既复现不了，也解释不了增益来自数据还是随机波动。

## 为什么必须记

有两个直接用途。第一，飞轮每一圈的 $\Delta$ 都要能复现：同一个 `dataset_version`，同一个冻结评测集。不能复现的增益不能作为已确认的结果，见 `dt-data-flywheel`。第二，opt-out 要求能按 URL 撤回。如果答不出「怎么从 mix 里拿掉」，治理就落不了地。

## 最小字段

- 来源：URL、许可集 id、研究协议号。
- 抽取器和质量模型：版本、阈值、语言。
- 合成样本：教师 id、生成代数、prompt 模板、验证器版本和验证结果。
- 去重：是否命中评测指纹。
- 版本：`dataset_version`，以及进了哪一次 mix。

opt-out 和 PII 撤回要靠精确指纹加墓碑记录，Bloom 过滤器不够，见 `dt-exact-dedup-code`。

## 追问

- **合成数据没有 URL 怎么办？** 用教师、种子 id 和验证哈希当来源。缺这些记录的合成数据按高风险处理。
- **抽取用的 LLM 改写了正文，还算原页吗？** 算派生数据，原 URL 和抽取器版本都要记。评测重叠按派生后的正文来比。
- **要不要把 lineage 给面试官看？** 面试里讲字段，不讲内部表名。
