---
id: pt-self-generated-curriculum
section: posttrain
order: 34
level: S
title: 没有人工题库时，如何让模型自己出题、自己验证并持续提高，而不滑向 trivial task 或奖励作弊？
quick: 把题目生成、求解和验证角色分离，用学习进展而非单纯高 reward 选题；题目必须经独立可执行 verifier 和去重过滤，并保留冻结的外部评测集，防止系统只学会生成自己容易验证的题。
tags:
  - Curriculum
  - Self-play
  - RLVR
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Absolute Zero
    url: https://arxiv.org/abs/2505.03335
    type: primary
---

自生成 curriculum 是让系统提出任务、求解、用可执行环境验证，再用结果更新出题与求解策略。它不是「同一个模型自问自答刷高分」。Absolute Zero 一类设定把 proposer / solver 放进可运行环境，用环境反馈代替人工题库。错法：把 self-play 曲线上升当成能力增长：出题器很快会改去出自己能验证、solver 刚好会做、或钻 verifier 空子的题。`pt-reasoning-seed-data-quality` 讨论人给的 seed 质量；本题讨论没有人工题时，如何避免题库和 reward 共适应。

## 角色分离，用进展选题

至少拆成三个角色：出题器、求解器、verifier。版本或权重最好隔离，并记录题目生成链（谁出的、用了什么种子、verifier 哪一版）。选题不要只看瞬时高 reward，那会收敛到 trivial task。更稳的信号是学习进展：solver 成功率的变化、两次尝试的差距、或多个 verifier 的分歧。太易则进展为零，太难则一直失败，两端都应被降权。

候选题还要过四道门：可执行、落在目标难度区间、相对历史题新颖、不把答案写进题面（non-leakage）。缺任一门，self-play 都会塌成「自己给自己开卷」。出题器的奖励若含「solver 失败」，还要防止出不可判或病态题来故意为难，那是另一种 trivial：专门生产噪声。

## 题本身必须可独立检查

Verifier 应是可执行环境、测试套件或形式检查器，而不是出题器的口头判断。要对 verifier 做对抗：题目是否引用内部状态、是否依赖未声明接口、是否用 flaky 测试。语义去重不能只靠表面字符串，否则出题器会换皮刷「新题」。难度校准要用冻结的 solver 快照，而不是正在被训练的那一版，否则难度标签会跟着政策一起漂。

还要限制题目直接利用 verifier 漏洞（例如断言永真、测试覆盖不到的分支、把答案写进隐藏测例文件名）。这和普通 RLVR 的 reward hacking 同类，只是攻击面从「解题格式」扩到了「出题 + 判分」整条链。`pt-r1zero` 依赖外部可验证题；本题若 verifier 被出题器捕获，连题都不再可信。

白板例子：出题器专出「打印常量」的编程题，solver 秒过，内部成功率冲到顶，外部算法题纹丝不动。或出题器发现某条断言宏永不失败，于是所有新题都绕过真正计算。这两种都应被「可执行 + 去重 + 冻结 solver 定难度」拦住。

## 只信冻结的外部评测

Self-play 的内部成功率、平均难度、出题多样性都只能当过程指标。最终只信独立 held-out suite：人工或预先冻结的题、与训练环境不同的分布。若内部指标持续上升而外部成功率不动，优先怀疑 task generator 与 reward 共适应，而不是宣称获得新能力。多样性指标也要小心：表面 n-gram 变多，任务族可能仍是同一模板。

发布前做一次「换 verifier / 换题型」的破坏性测试。外部不动，就回滚出题器，而不是加大 solver 的 RL 步数。日志里留下每道题的生成链，才能回答「这波进步是会解题了，还是会出送命题了」。和 `pt-self-rewarding-idpo` 一样，凡是自己生成监督信号的系统，都要把生成器与真值隔开。出题 / 求解 / 判分要隔离；内部曲线涨时，外部冻结集也要一起涨，否则回滚 proposer，不要加 solver 步数。

## 追问

- **为什么不能让同一模型又出题又打分？** 它会把「自己容易验证」写成题，reward 与数据一起漂，形成自证循环。这和 `pt-self-rewarding-idpo` 的 judge-policy 耦合是同一类失败，只是发生在任务空间而不是偏好空间。
- **学习进展比高分更抗作弊吗？** 更抗 trivial，但不抗 verifier 漏洞；进展信号仍要建立在独立可执行检查上。出不可判的病态题也能制造「进展」，所以可执行门不能省。
- **和人工 seed 冲突吗？** 不冲突。有高质量 seed 时先冷启动（`pt-reasoning-seed-data-quality`），再让 proposer 在已验证的任务族附近扩张。完全无 seed 时，环境本身必须能生成合法任务。
- **外部集也逐渐被拟合怎么办？** 冻结、加密或定期换新的 held-out；把它当回归门，不当可优化目标。一旦它进了出题器的训练信号，就不再是外部。
