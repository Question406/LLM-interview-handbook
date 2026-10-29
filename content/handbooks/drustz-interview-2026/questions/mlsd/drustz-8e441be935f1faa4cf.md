---
id: drustz-8e441be935f1faa4cf
section: mlsd
order: 139
level: A
title: 17 · Case：设计合成数据生成系统 · 13. 10 分钟口述稿
quick: 作者文档章节 · 17 · Case：设计合成数据生成系统 · 13. 10 分钟口述稿
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md
    type: primary
---
## 13. 10 分钟口述稿

> 我先确认三件事：**合成数据要解决的是哪个问题**——总量不足、长尾覆盖、隐私替代、标注成本还是难度控制；**有没有 verifier**；以及**这批数据用在训练的哪一段**。第一个问题最关键，因为这五个目的对"和真实分布的差距"的要求是相反的：补长尾时我故意要分布偏移，做隐私替代时同样的偏移就是缺陷。
>
> 指标上我只认一件事：**在固定算力、固定其他变量的 ablation 下，加了这批数据的模型在纯真实 held-out 上更好**。generator 的自评、judge 的平均分、"看起来很像真的"都不是证据——它们只说明生成端和评判端有共同偏好。我会在开工前写一份验收合同：主指标、guardrail、污染阈值、多样性下限、provenance 字段、成本上限，还有失败判据。
>
> 生成范式我会混着用。种子来自真实语料——**多样性来自 seed，不来自 prompt**，在 prompt 里写"请多样一点"基本无效。然后跑多阶段流水线：question rewriting、把不可验证的题转成可验证形式、answer rewriting、质量特征打分。我在 Reflection 做 math/STEM 数据就是这条路径，其中**"不可验证转可验证"这一步价值最高**，因为它把下游从"只能靠 judge"变成"可以靠程序"，直接决定了筛选的成本结构。
>
> 筛选是三级漏斗，不是加一个 judge：规则先挡垃圾，verifier 挡硬错误，模型 judge 判语义质量，人工只做分层抽检来calibration前三级。judge 我会拆成一组二元判定——是否自包含、是否含矛盾信息、解题假设是否给足——而不是打 1 到 10 分，因为**同一条标准 judge 在不同题目上判得不一致**，这个我实际遇到过。我会给 judge 建一套固定的人工锚点集当回归测试。
>
> 难度这块是我做得最深的。**难度不是题目的属性，是模型的函数**，所以必须在线筛。我们的做法是：正式 rollout 之前先用 16 条小批量探测可解率，全对或全错的直接丢——没有梯度信号，纯烧算力——保留的再跑 128 条。筛选大约占 12% 的算力。这个思想和 DAPO 的 dynamic sampling 是一致的。副作用要主动防：如果某类题的 verifier 有 bug，它们会全部落在"全错"被静默丢掉，所以要按类别统计丢弃率。
>
> 多样性和质量的张力上，温度不是多样性旋钮——它主要在"生成成本"和"筛选成本"之间做交换。真正的杠杆是 seed 多样性和条件维度的笛卡尔积。去重上，合成数据的重复是模式重复不是字符串重复，所以除了 MinHash 还要做 embedding 近邻去重和"骨架去重"，把数字和实体normalization后再比。覆盖度我会做成 taxonomy 网格看板而不是标量分数，因为标量分数不能告诉团队下一批该生成什么。
>
> 模型坍塌我会主动讲。反复自产自销会让分布的尾部先消失，而这时整体指标可能还在涨——这是最危险的阶段。关键的工程结论是 **replace 会坍塌、accumulate 不会**：每代必须保留真实数据，合成只做增量。加上代际标签和比例上限，用一个冻结的reference model监控分布，再留一个永不参与生成的真实锚定集。这里我要诚实：跨多代自训练的长期实验我没跑过，我遇到过的是单代内的模式坍塌。
>
> 分布偏移我用判别器二样本检验来量——训个分类器区分真实和合成，AUC 接近 0.5 说明不可区分；更有用的是看分类器最看重哪些特征，那就是 artifact 清单，可以直接回去修 prompt。隐私上，**合成不等于匿名**：要做 canary 记忆测试，要防准标识符组合重识别；需要形式保证时用 DP 训练 generator，靠差分隐私的后处理免疫性，sampling多少条都不额外消耗隐私预算。
>
> 成本我看的是**每条通过闸门的样本成本**，不是每千 token 单价——一个便宜但通过率 10% 的 pipeline 比贵一倍通过率 60% 的更贵。降本靠分层生成（便宜模型量产、贵模型只做精修和边界仲裁）、批处理接口（约五折）、prompt caching（rubric 前缀固定，缓存读约 0.1 倍）。基础设施上这类任务throughput敏感、延迟不敏感、可中断，适合跑在抢占式资源上——我自建过 pause/resume 框架和 TCP 式的自适应并发调节。
>
> 最后我会说什么时候不该做：真实数据便宜时、分布极难建模时、没有 verifier 也没有人评预算时、以及要建 eval 集时。**合成数据是信息的重新分配，不是信息的创造**——所以判断一个 pipeline 值不值得做，只要问一句：新信息从哪里进来？

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/17_case_synthetic_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
