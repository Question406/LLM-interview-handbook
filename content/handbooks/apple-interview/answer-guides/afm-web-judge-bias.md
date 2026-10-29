---
id: afm-web-judge-bias
kind: concept
situation: Judge 偏好更长、更像自己风格的回答，可能把风格当正确性。
task: 验证 judge 是否真正测量目标质量，并决定哪些标签可用于训练。
approach: 用对照 pairs 分离内容、顺序和长度，结合 blind human labels calibration。
result: 判断稳定且与独立正确性相符，保留 disagreement 和不确定样本。
---

## 可以这样回答

我会先定义 judge 要评什么。代码能否运行可以先用测试检查；是否解释清楚可以用 rubric。把所有维度合成一个看起来权威的总分，很容易掩盖问题。

我会做几组有控制的 pairs：交换两个答案的顺序，比较同一正确答案的长短版本，再比较正确但简洁与流畅却错误的答案。如果顺序一换 winner 就变了，或者总是更长的获胜，我们就知道标签里混入了与目标无关的偏好。

然后用不显示模型来源的 human labels calibration，并检查不同任务的 agreement。Judge 自己生成的解释不能替代 calibration；换一个 model family 也不是自动消除 bias。

如果这些标签要进入 reward model 或 DPO，我会保留 judge 版本、rubric、顺序和置信信息。对不稳定或 human disagreement 高的样本先审核，不强行输出 winner。最终还是用独立任务质量验证训练收益，避免 judge 的偏好在数据迭代里被不断放大。
