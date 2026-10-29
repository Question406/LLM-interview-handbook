---
id: apple-vision-edge
kind: design
situation: 视觉 token 会挤占 on-device 内存和时延。
task: 在设备预算内保留必要信息。
approach: 按任务分辨率与静态形状控制 token。
result: 小字、图表与关键区域不因平均提速被牺牲。
---

## 可以这样回答

视觉 token 会挤占 on-device 内存和时延。

视觉 token 与文本、输出共享上下文和 KV，先按 $(H/P)\times(W/P)$ 算数量，再检查总数是否在 $S_{\max}$ 内。比如多张截图会挤占工具证据和生成空间；on-device 要预编译分辨率与切块档位，按任务选缩略图、ROI 或 PCC，并验证计算仍留在 ANE。
