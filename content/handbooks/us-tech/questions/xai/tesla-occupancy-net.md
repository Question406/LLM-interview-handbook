---
id: tesla-occupancy-net
section: xai
order: 5
level: S
title: Tesla：occupancy / BEV 类表示，评测用什么，和纯相机占用栅格差在哪
quick: >-
  Tesla 公开讲的 occupancy 是八路相机进 3D 体积占用加 occupancy flow，当几何底层，不靠检测框 ontology。评测先
  IoU / 可见区域，再下流规划碰撞；BEV 是 2D 压扁。别把学术 Occ3D 榜当成车内看板。
tags:
  - Tesla
  - Occupancy
  - BEV
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Tesla AI
    url: https://www.tesla.com/AI
    type: primary
  - title: Tesla AI Day 2022
    url: https://www.youtube.com/watch?v=ODSJsviD_SU
    type: primary
  - title: Tesla AI Day 2021
    url: https://www.youtube.com/watch?v=j0z4FweCy4M
    type: primary
  - title: Occ3D — A Large-Scale 3D Occupancy Prediction Benchmark for Autonomous Driving
    url: https://arxiv.org/abs/2304.14365
    type: primary
---

## 题怎么来的

Autopilot / FSD 相关 MLE 岗会问：你们不用 lidar 当主传感器，空间怎么表示、怎么评。这不是某一场能引用帖号的逐字题。公开锚点是 Tesla AI Day 2021/2022 和 tesla.com/AI：多相机进向量空间，occupancy network 当几何底层，上面再叠车道等语义头。学术侧 Occ3D 一类 benchmark 给 IoU / mIoU 语言，但那是公开数据集协议，**不是 Tesla 内部看板**。我会分开讲：表示是什么、评什么、和经典占用栅格差在哪。

## 表示：3D 占用，不是 2D BEV 也不是框

BEV 把世界压到地面网格，车道、可行驶区域好画，高度和悬空障碍会糊。Occupancy 是体积：对自车周围每个体素预测「有没有东西」，公开演讲里还带 **occupancy flow**（占用怎么动），用来处理遮挡和非常规形状（横着的卡车、塑料袋、施工围挡）。检测框要先有类别；占用可以在没有合适类别时仍挡住规划。Hydra 多头见 `tesla-hydra-nets`。

Shape 面试够用：相机特征 `[N_{\mathrm{cam}}, C, H, W]`，查询是 3D 位置编码，输出占用概率 `[X, Y, Z]` 加流场。不要编 Tesla 体素分辨率。融合方式公开讲过 transformer 式「每个输出位置去图像里找证据」，因为地面起伏和遮挡让固定投影对不齐。

和纯相机占用栅格的差别我会主动说：

| | 经典占用栅格 | 学出来的 occupancy |
| --- | --- | --- |
| 传感器 | 多为 lidar / 深度，log-odds 更新 | 多相机视频，端到端 |
| 遮挡 | 射线后是 unknown | 用多视和时间补 | 
| 运动 | 另做跟踪 | occupancy flow |
| 误差 | 标定和深度错了栅格就歪 | 深度误差进网络，但要有几何监督 |

「纯相机占用栅格」常见做法是单目/双目深度再 voxelize。没有时间、没有跨相机一致性时，远距离和反光地面会碎。Tesla 公开叙事是：离线用多相机、多帧、甚至更重的模型造几何监督，车上跑轻量网络。自动标注见 `tesla-autolabel`。

## 评测：先几何，再下游，不要只报一个 mIoU

我会拆层，避免「Occupancy 刷榜」空话：

1. **几何 IoU。** 占用 vs 空闲。空体素极多，要报告占用类 IoU，不要被空类撑起的准确率骗。Occ3D 还用相机可见 mask：当前相机看不到的体素不算 FN。面试要说这句，否则模型在墙后乱填会吃亏或钻空。
2. **语义 mIoU（若有类）。** 学术集常见。Tesla 公开更强调几何通用性；有类目时再报 mIoU，并和「未知障碍仍要占用」分开。
3. **Occupancy flow。** 未来占用 IoU 或端点误差。静止误成运动、运动漏掉，规划会不一样。
4. **遮挡切片。** 完全可见 / 半遮挡 / 刚出现。这是 occupancy 相对框的卖点，评测里要切开，否则平均 IoU 很好、加塞仍撞。
5. **规划下游。** 假占用把路堵死（过度保守），假空闲让规划穿过去（不安全）。车规更吃这条，而不是 Occ3D 名次。

错法：把 BEV 分割 IoU 当成 occupancy 评测；用 nuScenes 框 AP 替代体积占用；报一个无法核对的「车队分数」。延迟约束见 `tesla-latency-slo`：占用必须进规划周期，评测也要带延迟档，不能只看离线大模型。

## 追问

- **没有 lidar 金标怎么训？** 公开讲法是离线多相机、多帧重建和自动标注，车上不用 lidar 推理。金标协议要固定，否则 IoU 不可比。
- **BEV 还要不要？** 要。车道拓扑在 2D 更好说。Occupancy 补高度和通用障碍。两者是层，不是互相替换。
- **体素太大怎么办？** 薄障碍（栏杆）会消失。评测要按距离和物体尺度切片，不能只看粗网格 IoU。
- **和隐式表面 / NeRF？** AI Day 提过几何研究。车上要固定延迟的显式网格；隐式当离线监督或研究，不当默认车载输出。
