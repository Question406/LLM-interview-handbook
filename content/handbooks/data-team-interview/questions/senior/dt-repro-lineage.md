---
id: dt-repro-lineage
section: senior
order: 9
level: A
title: Director：一周后这批数据还能复现吗，lineage 要记什么？
quick: "能不能复现，看每条样本能不能追到来源和版本：来源 URL、许可集或研究协议，加上抽取器、过滤器、教师、验证器和 dataset_version。这样每次增益都能对应固定评测和具体 mix，opt-out 也能按精确记录撤回。只有文件目录、没有来源和版本，说明不了数据可复现。"
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

能不能复现，取决于每条样本和每次实验能不能追到来源与版本。只说「文件都在 HDFS」，既复现不了，也解释不了增益来自数据还是随机波动。

举个例子，飞轮这一圈目标任务涨了，一周后有人问是哪批数据带来的。要答得上来，得有同一个 `dataset_version`、同一个冻结评测集把它重跑出来，复现不了的增益不能算已确认的结果，见 `dt-data-flywheel`。另一头是 opt-out：用户要求按 URL 撤回，你得答得出「怎么从 mix 里拿掉」，不然治理落不了地。

所以每条样本至少记这几样。来源记 URL、许可集 id 或研究协议号；抽取器和质量模型记版本、阈值和语言；合成样本记教师 id、生成代数、prompt 模板、验证器版本和验证结果；去重记有没有命中评测指纹；最后是 `dataset_version`，以及它进了哪一次 mix。

## 追问

**opt-out 撤回能靠 Bloom 过滤器吗？**
不够。opt-out 和 PII 撤回要靠精确指纹加墓碑记录，见 `dt-exact-dedup-code`。

**合成数据没有 URL 怎么办？**
用教师、种子 id 和验证哈希当来源。缺这些记录的合成数据按高风险处理。

**抽取用的 LLM 改写了正文，还算原页吗？**
算派生数据，原 URL 和抽取器版本都要记，评测重叠按派生后的正文来比。

**要不要把 lineage 给面试官看？**
面试里讲字段就行，不讲内部表名。
