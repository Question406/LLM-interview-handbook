---
id: ml101-missing-mechanisms
section: data
order: 17
level: A
title: MCAR、MAR、MNAR 三种缺失机制有什么区别？
quick: MCAR 指缺失与观测值、未观测值都无关；MAR 指给定已观测信息后，缺失不再依赖缺失值本身；MNAR 则仍存在这种依赖。MAR 的 random 不表示完全随机，选择填补或推断方法时要说明条件变量与假设。仅凭已观测数据通常无法证实 MAR、排除 MNAR，需要业务信息与敏感性分析。
tags: [ML Fundamentals, Missing Data, Statistics]
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-23
sources:
  - title: Stef van Buuren, Flexible Imputation of Missing Data, MCAR MAR MNAR
    url: https://stefvanbuuren.name/fimd/sec-MCAR.html
    type: primary
  - title: scikit-learn Imputation of missing values
    url: https://scikit-learn.org/stable/modules/impute.html
    type: primary
---

这三个名称描述“为什么没观测到数据”，不是三种填补算法。判断机制时要说明哪些信息已经观测到，以及缺失概率是否还依赖没有观测到的值。

用单个可能缺失的收入 Y 举例，设 R=1 表示收入缺失，X 表示完全观测的辅助变量。MCAR 要求 $P(R=1\mid X,Y)$ 不随 X、Y 改变；MAR 要求 $P(R=1\mid X,Y)=P(R=1\mid X)$；若给定 X 后，缺失概率仍与 Y 有关，就是这个设定下的 MNAR。多变量缺失需要更完整的观测模式记号，但条件依赖的思路相同。

以下都是为说明机制设定的例子。若调查系统独立于用户信息随机丢失 10% 的收入记录，可视为 MCAR。若年轻用户更常跳过收入题，但给定已观测年龄后，是否跳过与收入无关，可视为 MAR。若同年龄下，高收入用户仍因隐私顾虑更少填写，收入缺失就可能是 MNAR。

机制依赖于可用信息。若年龄没有被记录，前一个 MAR 例子的条件信息就不再可用，不能沿用原假设。因此“缺失是随机的”应具体解释为对哪些变量、在什么条件下随机。

MCAR 下，完整记录通常仍是总体的随机子样本，删除会损失信息。MAR 下，可以在正确模型、足够辅助信息与相应可忽略性条件下考虑多重插补、似然或加权方法；仅把缺失项统一填均值，并不因为 MAR 就自动正确。MNAR 往往需要对缺失机制或未观测值的偏移额外建模，再比较假设变化时结论是否稳定。

**能从数据检验出是哪一种吗？**
可以寻找与 MCAR 不符的证据，例如已观测人群之间的缺失率不同。但即使没有发现差异，也不证明 MCAR；仅凭观测数据一般无法识别对缺失值本身的依赖，区分 MAR 与 MNAR 常需额外信息。

**多重插补怎样做才有意义？**
在合理的插补模型下生成多份可能的完整数据，并把估计中的数据缺失不确定性一起汇总。它依赖模型和机制假设，不能保证自动修复任意 MNAR。预测流水线中，插补器也必须仅在训练数据或训练折中拟合。

**做预测时缺失指示特征够了吗？**
它可以让模型利用缺失与目标的关联，但不解决总体统计推断中的所有 selection bias。若上线采集流程改变，模型依赖的缺失模式也会改变，需要单独监控和验证。
