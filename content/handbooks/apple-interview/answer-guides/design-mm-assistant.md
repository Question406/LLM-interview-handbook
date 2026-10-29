---
id: "design-mm-assistant"
kind: "design"
situation: "助手需将答案绑定到实际图像位置。"
task: "设计证据引用和视觉预算。"
approach: "区域选择与生成分开，预算由任务信息需求决定。"
result: "区域正确、内容受支持且端到端成本可接受。"
---

## 可以这样回答

助手需将答案绑定到实际图像位置。

回答要能指回图上的框或屏幕区域，引用对不上就删句，尚未到达的模态不能当证据。视觉 token 按 patch 占上下文，高分辨率图先粗定位、再裁剪细看；模态延迟状态机见 `design-multimodal-prod`。
