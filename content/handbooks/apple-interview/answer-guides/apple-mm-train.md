---
id: apple-mm-train
kind: design
situation: 视觉训练受数据、算力与分辨率约束。
task: 决定冻结视觉塔还是联合训练。
approach: 先查缺口，再比较连接器、分辨率和更新范围。
result: 同预算视觉收益与语言回归支持取舍。
---

## 可以这样回答

视觉训练受数据、算力与分辨率约束。

我会先定任务需要的分辨率和视觉 token 数，再决定是否解冻视觉塔。MM1 的公开 ablation study 中，低分辨率时冻结更好，高分辨率或偏离 pre-training 分辨率时解冻更好；on-device 还要按 ANE 静态档位训练和导出，server-side 切块方案不能直接搬过去。
