---
id: drustz-948ccbcca73ac19b1f
section: mlsd
order: 201
level: A
title: >-
  21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 4. Step 3：搭环境 —— **整条 pipeline 80%
  的工程量在这里**
quick: >-
  作者文档章节 · 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 4. Step 3：搭环境 —— **整条
  pipeline 80% 的工程量在这里**
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/21_swe_agent_data.md
    type: primary
---
## 4. Step 3：搭环境 —— **整条 pipeline 80% 的工程量在这里**

这是 SWE 数据和 math 数据最大的分岔口。math 没有对应物。

### 为什么这么难

- 每个仓库的依赖、构建系统、测试 runner 都不一样
- **同一个仓库的不同历史时点依赖也不一样**（三年前的 commit 装不上今天的依赖）
- 编译型语言打完补丁要**重新编译**，否则跑的是旧的二进制
- 测试输出格式各异，要解析成结构化结果

### 三代做法

**① 人工写 Dockerfile**（SWE-bench）—— 12 个仓库尚可，128 个就不行了。

**② Agent 搭环境**（SWE-smith / SWE-rebench V2 / SetUpAgent）：

> SWE-smith：让 **SWE-agent 在最新 commit 上跑最多 100 步**，
> 指令是「装好这个仓库并跑通测试套件」。然后人工核对安装与测试指令、
> 检查 **>80% 的已有测试能过**，最后固化成一个 Docker 镜像。
> **剩下的人工量：每个仓库约 7 分钟**（从 agent 轨迹里抠出正确的安装步骤）。

> SWE-rebench V2：用 **mini-SWE-agent + Qwen3-Coder-480B** 做交互式 setup agent，
> 闭环调试（读代码 → 试装 → 看报错 → 改脚本）。每种语言预建 base 镜像
> （Java 分 JDK 11/17/21 三个），**每个仓库只推断一次 setup，然后复用到该仓库的所有任务**。

**③ 关键的架构决策：环境按仓库复用，不按实例**

```text
❌ 每个 instance 一个镜像   → 存储爆炸（SWE-bench companion env 是 TB 级）
✅ 每个 repo 一个基础镜像   → 实例只存 (base_commit, patches)，运行时 checkout
```



**这也是 SWE-smith 「环境优先」路线的真正优势**：它把最贵的一步（搭环境）
从「每个实例一次」变成「每个仓库一次」。

### 一句可以直接引用的判据

> **能不能自动搭好环境，决定了你的数据规模上限。**
> 挖 PR 的产出率再高，卡在环境上就一条都出不来。
> 所以这条 pipeline 的正确投入顺序是：**先解决环境，再谈数据量**。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/21_swe_agent_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/21_swe_agent_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
