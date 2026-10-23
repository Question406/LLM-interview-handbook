---
id: dt-gui-agent-rl
section: posttrain-data
order: 26
level: S
title: GUI / 电脑使用的 Agent RL 数据，和写代码的环境差在哪？
quick: "差在观测、动作和奖励检查的对象。代码环境看 stdout、靠测试给奖励；GUI 任务是指令加初始桌面快照加状态检查器，模型读截图和无障碍树，点击、键入、滚动，奖励看文件、窗口、单元格这些最终状态。检查器要放在只读镜像里，和 agent 工作区隔离。"
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

差别在观测、动作和奖励检查的对象。写代码的环境里，模型看 stdout，奖励靠测试；GUI 强化学习（RL）的一条任务包含任务指令、初始桌面快照和执行检查器，模型看截图和无障碍树，做点击、键入、滚动，检查器根据最终状态算奖励。

举个例子，任务是把一份表格里某一列改成另一种格式。检查器在任务结束后打开保存的文件，看那一列单元格的值对不对，至于模型是用菜单还是快捷键改的，它不管。如果手里只有「点这里、再点那里」这类标注，没有检查器，就算不出 $r$。

奖励为什么非要看最终状态，可以看另外两种做法会怎样。拿点击示范当奖励，会漏掉金补丁之外的正确路径；拿和金标准结果的像素差当奖励，模型会对着过期的帧去点，见 `dt-webarena-traj`。监督微调（SFT）轨迹的门禁是另一回事，见 `dt-gui-traj`。

公开的参照是 OSWorld：真实桌面，369 道题，每题都有初始状态配置和执行检查脚本，他们一共标了 134 种检查函数。人能完成七成以上，早期 VLM 只有一成出头。Anthropic 的 computer use 是产品形态，截图进、动作出，训练仍然要有自己的沙箱和检查器。

## 公开方案怎么扩规模

ComputerRL（清华 / Z.AI）用 Docker + gRPC 拉起上千个并行 Ubuntu 桌面，API 调用和 GUI 动作混用，再用 Entropulse 在 RL 和 SFT 之间轮换，缓解长时间训练的熵崩。他们报告 RL 在 OSWorld 上贡献了很大一截提升，但数字随版本变，现场记住「并行桌面 + 状态检查器 + 轮换 SFT」就够了，不用背榜。

SkyRL-Agent 把 OSWorld 当作工具接入，动作用 PyAutoGUI，反馈用 a11y 树，虚机作为 Ray 任务运行，CPU 环境和 GPU 生成拆开。32 个桌面副本就能开始训，不必一上来就要 2 万。

## 数据组交付什么

环境用许可或合成的桌面，跑在隔离虚机里。每条任务交任务指令、初始快照哈希、检查脚本和分辨率模式，检查脚本放在只读镜像里，agent 的工作区碰不到。

## 追问

**只有成功演示视频怎么办？**
我会把它当行为克隆，上限就是教师。ComputerRL 也写了，人工标注贵，蒸馏又受限于教师的天花板，所以才上在线 RL。

**检查脚本会不会被 agent 改掉？**
会。所以脚本要在只读镜像里跑，agent 工作区和检查器隔离。

**分辨率模式为什么要单独记？**
同一个视觉编码器可能有多种输入模式，AFM 2025 报告里就有 tiling / overview / rapid 三种。训练只覆盖高清模式，模型到 rapid 模式下就可能点错按钮，见 `dt-multimodal-data`。

**和工具 JSON 类的 agent 有什么区别？**
对 GUI 任务来说，动作格式符合 schema 只是前提，奖励要看最终状态检查。

相关：`dt-webarena-traj`、`dt-gui-traj`、`dt-multimodal-data`
