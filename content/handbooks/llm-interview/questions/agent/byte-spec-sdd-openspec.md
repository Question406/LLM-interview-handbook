---
id: byte-spec-sdd-openspec
section: agent
order: 201
level: A
title: 字节 Agent 一面：SDD、Spec-kit、OpenSpec 是什么，和 Harness 怎么配合？
quick: >-
  SDD 先写可验收规格再改实现。Spec-kit / OpenSpec
  是把规格、任务和验证落成仓库约定的工具链，细节以你用过的为准。Harness
  负责按规格执行与回放；没有规格时 Agent 只能靠观感。
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

错法：背营销名、编一套没用过的 CLI。这面要的是：规格先于实现、对错可判定；工具链只是把规格、任务、验证落成仓库约定。没亲手用过就说「同类物是规格文件 + 任务拆解 + 自动验证」，不要假装跑过某条命令。和 Harness 的分工见 `byte-harness-engineering`；同类「先规格再编码」也可对照 `pdd-openclaw-spec-driven`。

## SDD：先写可验收规格再改代码

SDD（spec-driven development）把需求写成测试、接口契约或验收清单，再让模型改实现。规格是预言机：这一步过不过，不靠「看起来对」。没有规格时 Agent 只能靠观感，长任务会在中间步骤静默跑偏。

规格要可执行或至少可检查：单测、类型、禁止改的路径、API 兼容断言。纯散文「做一个更好的登录」不是 SDD，因为它不能告诉 Harness 何时停。Coding Agent 里常见落地是：先补失败测试或 OpenAPI，再允许改业务代码；测试红着合入等于没有规格。

## Spec-kit 和 OpenSpec：按「存在哪、谁拆任务、如何校验」比

两者都是规格工作流，不是模型本身。面试按三个轴比，而不是背官网口号：

- **规格存在哪**：仓库里的 markdown / 结构化文件，还是任务系统里的工单。
- **谁生成任务**：人写规格再拆，还是工具从规格生成可勾选子任务。
- **如何校验**：跑测试、diff 策略、人工 review，还是只检查规格文档有没有更新。

没用过具体工具时，明确说「我按这三轴理解，细节以实际仓库约定为准」。编 `openspec init` 之类没跑过的命令，比承认「同类物」更容易被追穿。区别若原帖没有标准答案，不要编「A 一定比 B 强」；能讲清它们都在把 SDD 工程化即可。

## Spec 判定对错，Harness 负责执行

Spec Coding 解决「对错可判定」；Harness 解决「判定之后谁执行、失败怎么回放」。Harness 吃的是规格：跑测试、比 diff、失败按错误码重试或升级。规格写在 prompt 里只是又一段话，模型仍可忽略；规格写进测试和策略引擎，执行层才能拒绝「看起来能编译」的错误 patch。

配合方式：Agent 读规格 → 改代码 → Harness 跑验收 → 失败观察写回短记忆 → 再改。没有 Harness，规格只是文档；没有规格，Harness 只能做超时和权限，不能做正确性。权限与沙箱仍在 Harness，见 `byte-team-agent-security`；工具失败分类见 `byte-tool-fail-retry`。

## 追问

- **没写过 Spec-kit 怎么办？** 用三轴讲同类物，并举你仓库里真实的测试/验收例子。不要虚构命令输出。
- **规格和 prompt 不冲突吗？** prompt 给策略提示；规格给可判定约束。冲突时以可执行验收为准，而不是以更长的 system prompt 为准。
- **规格过时了怎么办？** 和记忆过期一样：规格要绑定代码或测试哈希，实现变了规格必须一起改，否则 Harness 会用旧预言机拒绝正确改动。
- **和普通 TDD 的差别？** 精神同类。SDD 强调给 Agent 的输入输出都是规格与验收，而不仅是人先写测试。工程上仍是「红灯 → 改 → 绿灯」。
