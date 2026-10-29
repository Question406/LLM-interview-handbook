---
id: drustz-ba426a8b4d7656c70b
section: anthropic
order: 76
level: A
title: Process Cat Images
quick: original-structured-preparation-guide · Process Cat Images
companies:
  - anthropic
tags:
  - DrustZ
  - original-structured-preparation-guide
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/a91f29c5-e919-47ed-b1fd-aa5470b62735
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Process Cat Images：先保证每张图的变换链独立

> “Cat”只说明样例图片主题。当前隐藏接口未逐字存档；下面依据本地图片处理同题族给出不虚构文件名的练习版本。

## 接口与例子

实现 `process_cats(image_paths, pipelines, output_path_for)`：对每张输入图分别应用每条 JSON 变换链并保存。例：`cat.jpg` 配置 `[flip_horizontal, blur(radius=2)]` 时，必须先镜像再模糊；另一条 `[grayscale]` 必须重新从原图开始，不能接着前一结果加工。

## 实现与收尾

启动时解析并校验所有配置；`apply_one(image, op)` 负责单步，`run_pipeline(source, ops)` 依次更新当前图。用 Pillow context manager 关闭文件句柄，处理 EXIF orientation 后再变换，并在保存前按格式处理 `RGB/RGBA`（JPEG 不能直接保存带 alpha 的模式）。先写到临时文件，成功后原子 rename，避免失败留下半张图；单任务异常应带上源图和 pipeline 名。

数据量小先串行；大图达到时间门槛后，用 `ProcessPoolExecutor` 并行不同图片或 `(图片, pipeline)`，不要把 Pillow 对象跨进程传递，只传路径和 JSON 数据。所有 future 被收集或结算后 executor 才能退出。若各步像素量为 `Pj`，时间 `O(ΣPj)`，峰值空间为最大中间图；总输出数为 `m×n`。覆盖坏图、空 pipeline、未知操作、重名输出、尺寸变为 0、旋转后画布、色彩模式、进程失败及磁盘空间不足。

测试时为每种操作准备一张极小、像素可人工核对的图，再加一组组合 pipeline 验证顺序；只肉眼看猫图很容易漏掉镜像方向或尺寸的一像素误差。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/a91f29c5-e919-47ed-b1fd-aa5470b62735)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
