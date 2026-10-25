---
id: swe-run-contract
section: swe-agent
order: 1
level: S
title: 怎样定义一个可复现的 issue-to-patch run contract？
quick: "我会先把一次 attempt 的输入输出写成一份合同：输入固定 repo base commit、依赖和镜像 digest、issue、模型与 sampling、工具版本、时间和费用预算、评测命令；输出交 patch、完整 trace 和机器可读的 verdict。缺任何一项，结果都难复现，也没法和别人比。"
tags:
  - SWE Agent
  - Reproducibility
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: SWE-bench Multimodal
    url: https://arxiv.org/abs/2505.23419
    type: primary
---

我会先把输入输出写成一份 run contract，再去比模型。输入要固定 repo base commit、依赖和镜像 digest、issue、模型和 sampling、工具版本、预算和评测命令；输出要有 patch、完整 trace 和由冻结 evaluator 给出的 verdict。没有这份合同，resolve rate 之间没法比。

举个例子，两个人都说「跑了同一个 issue」，一个用的 base commit 比另一个新，依赖也没锁，超时一个设得紧一个不设，一个允许联网一个不允许，最后分数差了一截，谁也说不清是模型的差别还是环境的差别。所以分数对不上的时候，我会先查环境有没有漂，再去查模型。

输入这边，一份 attempt 至少要固定：issue 文本和附件的 hash、repo base SHA、评测用的 test commit、容器和依赖 lock 的 digest、网络与权限策略、模型 snapshot、系统提示的 hash、工具字段和类型规范（schema）的版本、sampling 参数和 seed，以及时间、调用次数、token、费用的预算。持续更新的 benchmark 还要写明 freshness cutoff 和任务版本号。仓库更新、依赖漂移、模型已经见过这个 issue，都会让数字失去对照。缺 seed 或镜像 digest，就别说可复现。这些字段我会写成一份 YAML，和 artifact 存在一起，光说一句「我们用的官方镜像」不算数。评测命令本身也要版本化，免得 evaluator 哪天静默升级。

输出这边，目标是让第二个人在同样的环境里能 replay，并且判断得出失败是模型、工具、依赖还是评测器造成的。最低要交：统一 diff、逐步 trace（每次 tool 的请求和响应）、测试日志、机器可读的 verdict（`resolved` / `failed` / `timeout` / `policy_denied` / `env_error`）、退出原因和资源消耗。verdict 必须由冻结的 evaluator 产生，模型自己说「已修复」不算。artifact 和 trace 版本化存放，和任务 ID、attempt ID 绑在一起。没有 trace 的成功没法审计，你证明不了它没改测试、没检索 gold PR。预算耗尽也要单独计数，别并进「模型不会修」。

评测上能刷分的缺口也就出在这些地方：不冻依赖，环境碰巧能编过；评测时允许上网，把 gold PR 检索回来；预算不封顶，靠无限 retry 堆成功率；只交最终 patch 不交 trace；环境崩了算成模型失败，或者反过来全推给环境。所以报告里我会同时给成功定义、预算耗尽率、不可复现率和多次重跑的方差。最小可发表的一组东西是任务版本、镜像 digest、模型 snapshot、patch、evaluator verdict 和完整 trace。

落地的时候，把 run contract 存成和 patch 同目录的机器可读文件，当成实验的 schema 用：CI 拒绝缺 digest、缺 verdict、缺 trace 的提交，缺字段的运行结果进不了对比表，只有合同字段完全一致的两次运行才拿来对比。这样别人按同一份 YAML 能重跑出同一个 verdict，剩下的误差只来自模型的随机性。口头上对齐了环境，和真的可复现是两回事。

## 追问

**为什么你们的分数和官方不一致？**
先拿运行约定里的字段一条条核对，base commit、镜像 digest、预算、是否联网，都对上了再谈模型。

**有了 seed，LLM 就能复现吗？**
不能完全复现。seed 只是必要项，还要冻住模型版本和 decoding，并且多次重跑报方差。

**live 仓库的结果能和 frozen 的放进同一个数字吗？**
不能。frozen 和 live 要分开列，见 `swe-contamination-resistance`。

**timeout 算失败还是算无效？**
算预算内的失败，但单独列一栏，别和 oracle fail 混成一个 error rate。

**prompt 改了，任务版本要不要跟着换？**
要。prompt 和 tool schema 都是输入合同的一部分，静默改掉会让历史分数没法比。
