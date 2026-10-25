---
id: tesla-occupancy-net
section: xai
order: 5
level: S
title: Tesla：occupancy / BEV 类表示，评测用什么，和纯相机占用栅格差在哪
quick: "Occupancy 在 3D 体素上预测占用与 flow，给规划提供通用几何；BEV 把高度压到 2D，检测框还依赖类别。评测先看可见区域的占用 IoU，再看运动、遮挡与下游安全，Occ3D 协议只能作公开参考，不能代替 Tesla 内部指标。"
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

Occupancy 给规划提供带高度的 3D 占用几何，并用 flow 描述它如何运动。比如悬空障碍或没有合适检测类别的围挡，单靠 2D BEV 或类别框不够，体积占用仍可提醒规划避开。

这里依据 Tesla AI Day 2021/2022 和 tesla.com/AI 对多相机向量空间、occupancy 几何底层及车道语义头的公开介绍讨论表示与评测，并非有帖号的逐字真题。Occ3D 的 IoU / mIoU 是公开数据集协议，不能据此称为 Tesla 内部看板。

BEV 把世界压到地面网格，车道、可行驶区域好画，难以区分高度和悬空障碍。Occupancy 是体积：对自车周围每个体素预测「有没有东西」，公开演讲里还带 occupancy flow（占用怎么动），用来处理遮挡和非常规形状（横着的卡车、塑料袋、施工围挡）。检测框要先有类别；占用可以在没有合适类别时仍挡住规划。Hydra 多头见 `tesla-hydra-nets`。

形状上，相机特征是 `[N_{\mathrm{cam}}, C, H, W]`，3D 位置编码作为查询，输出 `[X, Y, Z]` 的占用概率及流场。公开介绍过 transformer 式的融合，让输出位置去图像特征中找证据，处理地面起伏与遮挡下固定投影对不齐的问题；未公开的体素分辨率不补写。

可以按传感器、遮挡、运动和误差来源比较这两类表示：

| | 经典占用栅格 | 学出来的 occupancy |
| --- | --- | --- |
| 传感器 | 多为 lidar / 深度，log-odds 更新 | 多相机视频，端到端 |
| 遮挡 | 射线后是 unknown | 用多视和时间补 | 
| 运动 | 另做跟踪 | occupancy flow |
| 误差 | 标定和深度错了栅格就歪 | 深度误差进网络，但要有几何监督 |

「纯相机占用栅格」常见做法是单目/双目深度再 voxelize。没有时间、没有跨相机一致性时，远距离和反光地面会碎。Tesla 公开叙事是：离线用多相机、多帧、甚至更重的模型造几何监督，车上跑轻量网络。自动标注见 `tesla-autolabel`。

评测按几何、语义、运动、遮挡和规划分别看：

1. 几何 IoU。占用 vs 空闲。空体素极多，要报告占用类 IoU，不要被空类撑起的准确率骗。Occ3D 还用相机可见 mask：当前相机看不到的体素不算 FN。这样就把相机看不到的区域与已观测区域分开计分。
2. 语义 mIoU（若有类）。学术集常见。Tesla 公开更强调几何通用性；有类目时再报 mIoU，并和「未知障碍仍要占用」分开。
3. Occupancy flow。未来占用 IoU 或端点误差。静止误成运动、运动漏掉，规划会不一样。
4. 遮挡切片。完全可见 / 半遮挡 / 刚出现。这是 occupancy 相对框该切开评的地方，否则平均 IoU 很好、加塞仍撞。
5. 规划下游。假占用把路堵死（过度保守），假空闲让规划穿过去（不安全）。车载应用更重视这一项，Occ3D 名次次之。

BEV 分割 IoU、nuScenes 框 AP 和体积占用衡量的对象不同，不能互相代替，也不能补报无来源的车队分数。占用还必须进入规划周期，所以要同时报告延迟档，见 `tesla-latency-slo`。

## 追问

**没有 lidar 金标怎么训？**
公开讲法是离线多相机、多帧重建和自动标注，车上不用 lidar 推理。金标协议要固定，否则 IoU 不可比。
**BEV 还要不要？**
要。车道拓扑在 2D 更好说。Occupancy 补高度和通用障碍。两者是层，不是互相替换。
**体素太大怎么办？**
薄障碍（栏杆）会消失。评测要按距离和物体尺度切片，不能只看粗网格 IoU。
**和隐式表面 / NeRF？**
AI Day 提过几何研究。车上要固定延迟的显式网格；隐式当离线监督或研究，不当默认车载输出。
