---
id: dt-gui-agent-rl
section: posttrain-data
order: 26
level: S
title: GUI / 电脑使用的 Agent RL 数据，和写代码的环境差在哪？
quick: "GUI RL 的一条任务包括指令、初始桌面快照和状态检查器。模型读取截图及无障碍树，执行点击、键入和滚动；奖励检查文件、窗口或单元格等最终状态。检查器要与 agent 工作区隔离，不能把用户屏幕默认当训练环境池。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - GUI
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks"
    url: https://arxiv.org/abs/2404.07972
    type: primary
  - title: "ComputerRL: Scaling End-to-End Online Reinforcement Learning for Computer Use Agents"
    url: https://arxiv.org/abs/2508.14040
    type: primary
  - title: SkyRL-Agent
    url: https://arxiv.org/abs/2511.16108
    type: primary
  - title: Computer use (Anthropic)
    url: https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

GUI 强化学习（RL）的任务应包含任务指令、初始快照和执行检查器，由检查器根据最终状态计算奖励。监督微调（SFT） 轨迹门在 `dt-gui-traj`。没有检查器的「点这里」标注，不能当 $r$。

常见误区是：拿点击示范或和金补丁的像素差当奖励。漏金补丁、对着过期帧点，见 `dt-webarena-traj`。

OSWorld 是公开锚点：真实桌面，369 题，每题有初始状态配置和执行检查脚本（他们标了 134 种检查函数）。人能做七成以上，早期 VLM 只有一成出头。

## 和 SWE 环境的差别

SWE 的 observation 包括 stdout，奖励依据测试。GUI 的 observation 包括屏幕像素和无障碍树，动作则是点击、键入和滚动。检查器看文件是否改对、窗口状态、表格单元格。

Anthropic 的 computer use 是产品形态：截图进、动作出。训练数据仍要自己的沙箱和检查器，不能把用户桌面当环境池。

## 公开怎么扩

ComputerRL（清华 / Z.AI）：Docker + gRPC 拉起上千并行 Ubuntu 桌面；API 调用和 GUI 动作混用；Entropulse 在 RL 和 SFT 之间轮换，缓解长训熵崩。他们报 OSWorld 上 RL 贡献很大一截，数字随版本变，现场记「并行桌面 + 状态检查器 + 轮换 SFT」，别背榜。

SkyRL-Agent 用 OSWorld 当 tool：PyAutoGUI 动作，a11y 树反馈，虚机当 Ray 任务，CPU 环境和 GPU 生成拆开。32 个桌面副本就能开始训，不必先喊 2 万。

## 数据组交什么

任务指令、初始快照哈希、检查脚本、分辨率模式。端侧 AFM 有 tiling / overview / rapid，如果训练只覆盖高清模式，在 rapid 模式下模型就可能点错按钮，见 `dt-multimodal-data`。检查脚本放只读镜像，agent 工作区碰不到。

苹果：许可或合成桌面、隔离虚机。用户屏幕、点击日志默认不进基础模型。

## 追问

- **只有成功演示视频？** 我会当行为克隆，上限就是教师。ComputerRL 写了人标贵、蒸馏吃教师天花板，才上在线 RL。
- **检查脚本会不会被改？** 会。我会让脚本在只读镜像里跑，agent 工作区和检查器隔离。
- **和工具 JSON agent？** 动作格式符合 schema 还不够，GUI 任务还必须通过最终状态检查。
