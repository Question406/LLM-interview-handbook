---
id: dt-repro-lineage
section: senior
order: 9
level: A
title: Director：一周后这批数据还能复现吗，lineage 要记什么？
quick: "记录来源 URL、许可集或研究协议，以及抽取器、过滤器、教师、验证器和 dataset_version。每次增益能对应固定评测与具体 mix，opt-out 能按精确记录撤回。只有文件目录，没有来源与版本，不能说明数据可复现。"
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

数据血缘（lineage）要让每条样本和每次实验能追溯到来源与版本。只有「文件都在 HDFS」无法复现；要解释增益来自数据而非随机波动，需要下面这些记录。

不这么选的理由：opt-out 还要求能按 URL 撤回。答不出「怎么从 mix 里拿掉」，治理是空的。飞轮的每一圈 $\Delta$ 要能复现：同一 `dataset_version`、同一冻结集。不能复现的增益不能作为已确认结果，见 `dt-data-flywheel`。

## 最小字段

来源是 URL、许可集 id、研究协议号。用户日志默认没有这个字段，因为不该在表里。抽取器和质量模型记录版本、阈值和语言。合成样本另记教师 id、生成代数、prompt 模板、验证器版本和结果。去重记是否命中评测指纹。最后是 `dataset_version` 和进了哪一次 mix。

opt-out 和 PII 撤回依赖精确指纹加墓碑，Bloom 不够，见 `dt-exact-dedup-code`。Applebot 支持页给了个人对 URL 提出异议的路径。

## 追问

- **合成没有 URL？** 用教师 + 种子 id + 验证哈希当来源。没有这些的合成当高风险。
- **抽取 LLM 改写了正文，还算原页吗？** 算派生。原 URL 和抽取器版本都要。评测重叠按派生正文比。
- **要不要把 lineage 给人看？** 面试讲字段，不讲内部表名。
