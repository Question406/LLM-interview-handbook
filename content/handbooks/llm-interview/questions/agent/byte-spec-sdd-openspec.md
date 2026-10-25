---
id: byte-spec-sdd-openspec
section: agent
order: 201
level: A
title: 字节 Agent 一面：SDD、Spec-kit、OpenSpec 是什么，和 Harness 怎么配合？
quick: "SDD 先写可验收的规格再改实现。Spec-kit / OpenSpec 是把规格、任务和验证落成仓库约定的工具链，细节以你用过的为准。Harness 负责按规格执行验收和回放，没有规格时 Agent 只能靠观感。"
tags:
  - ByteDance
  - Spec-driven
  - SDD
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 字节跳动-Agent开发实习生 一面（45分钟）
    url: https://www.nowcoder.com/feed/main/detail/931a8a935a5e4b4f8d0b71cd4e818604
    type: candidate-first-hand
  - title: 字节AI Agent开发秋招一面面经
    url: https://www.nowcoder.com/feed/main/detail/7b1b40fda3244715a82bcb4a821ca887
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 岗位：Agent 开发实习 / 秋招一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“什么是SDD（规范驱动开发）”**；**“什么是Spec-kit”**；**“什么是OpenSpec”**；**“OpenSpec 和Spec-kit 的区别？”**；秋招帖还问 **“如何理解Spec Coding和Harness？”**

SDD（spec-driven development，规范驱动开发）就是先把需求写成能验收的规格，再让模型改实现；Spec-kit 和 OpenSpec 是把规格、任务和验证落成仓库约定的工具链，细节以你实际用过的为准；Harness 负责按规格跑验收、失败时回放和重试。规格让对错可判定，Harness 决定判定之后谁来执行，没有规格，Agent 只能靠观感。这面别背营销名，也别编一套没用过的 CLI。

先说 SDD。把需求写成测试、接口契约或验收清单，规格就提供了检查依据，程序能判断这一步过没过，用不着看结果像不像对的。没有规格，长任务会在中间步骤静默跑偏。规格要可执行，至少可检查，比如单测、类型、禁止改的路径、API 兼容断言。「做一个更好的登录」这种散文算不上 SDD，它没法告诉 Harness 什么时候停。举个例子，Coding Agent 里常见的落地是先补一个失败的测试或者 OpenAPI，再允许改业务代码；测试红着就合入，等于没有规格。

再说 Spec-kit 和 OpenSpec。两者都是规格工作流，本身不是模型。面试时按三个轴比，别背官网口号。一是规格存在哪，仓库里的 markdown / 结构化文件，还是任务系统里的工单。二是谁生成任务，人写规格再拆，还是工具从规格生成可勾选的子任务。三是怎么校验，跑测试、diff 策略、人工 review，还是只检查规格文档有没有更新。没亲手用过，就直说「同类物是规格文件 + 任务拆解 + 自动验证，我按这三轴理解，细节以实际仓库约定为准」，别假装跑过某条命令。编一条没跑过的 `openspec init`，比承认是「同类物」更容易被追穿。两者的区别原帖没有标准答案，别编「A 一定比 B 强」，讲清它们都在把 SDD 工程化就够了。

最后是和 Harness 的配合。Agent 读规格、改代码，Harness 跑验收、比较 diff，失败时按错误码决定重试还是升级，失败观察写回短记忆，再接着改。规格只写在输入提示里，就只是又一段话，模型照样可以忽略；写进测试和策略引擎，执行层才能拒掉「看起来能编译」的错误 patch。没有 Harness，规格只是文档；没有规格，Harness 只能管超时和权限，管不了正确性。Harness 的分工见 `byte-harness-engineering`，权限与沙箱仍在 Harness，见 `byte-team-agent-security`；工具失败分类见 `byte-tool-fail-retry`；同类的「先规格再编码」可以对照 `pdd-openclaw-spec-driven`。

## 追问

**没写过 Spec-kit 怎么办？**
用三个轴讲同类物，再举你仓库里真实的测试 / 验收例子，别虚构命令输出。

**规格和 prompt 不冲突吗？**
prompt 给策略提示，规格给可判定的约束。冲突时以可执行的验收为准，system prompt 写得再长也不算。

**规格过时了怎么办？**
和记忆过期一样处理，规格要绑定代码或测试哈希，实现变了规格必须一起改，不然 Harness 会拿旧预言机拒掉正确的改动。

**和普通 TDD 有什么差别？**
精神是一类的。SDD 强调给 Agent 的输入输出都是规格与验收，范围比人先写测试更大；工程上还是「红灯 → 改 → 绿灯」。
