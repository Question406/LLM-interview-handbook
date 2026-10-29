---
id: drustz-d2b6ba2e76548c2bb6
section: anthropic
order: 84
level: A
title: Image Transformation using Python Libraries
quick: >-
  original-structured-preparation-guide · Image Transformation using Python
  Libraries
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
      https://www.1point3acres.com/interview/problems/d5535584-0980-47fb-862d-6f9f7569791d
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 用 Python 图片库完成六种 Transformation

> 证据边界：四目录、六类操作、顺序执行和大图限时均由当前 UUID 的公开 description 直接确认；下文为中文重写和原创方案。

## 完整题面与接口

输入四个目录：`small_images`、`big_images`、`transformations`、`out`。每个 JSON 含一条或多条按顺序执行的操作：无参数的 `grayscale`、`flip_horizontal`、`flip_vertical`，以及 `scale(factor)`、`blur(radius)`、`rotate(angle)`。实现 `process_images(image_paths, transform_files, output_dir, get_output_path)`，先让所有小图结果正确，再在规定时间内处理大图；每张图片与每个配置组合都要单独输出。

例：`[{type:grayscale},{type:scale,factor:0.5},{type:rotate,angle:90}]` 必须依次灰度、缩小、旋转；另一份配置要重新从原图开始，不能承接前一结果。

## 解法、复杂度与测试

用 Pillow 时可映射到 `ImageOps.grayscale/mirror/flip`、`resize`、`GaussianBlur`、`rotate`。先验证 JSON schema 和参数，再让 `apply_one(image,op)` 返回新图，pipeline 循环串接；用 context manager 关闭源图，输出路径只由 helper 生成。正确性通过后，把独立的 `(image,config)` 任务交给 `ProcessPoolExecutor`；worker 必须是顶层可 pickle 函数，只传路径和普通字典，不跨进程传 Image 对象。

若各步处理像素数为 `P_j`，单任务约 `O(ΣP_j)`，峰值内存与最大中间图成正比，总输出数 `m×n`。测试未知 type、缺参数、factor≤0、尺寸取整到至少 1、空 pipeline、损坏文件、PNG alpha 转 JPEG、EXIF 方向、rotate 是否扩展画布、同名输出、一个 worker 失败仍能定位任务，以及进程开销/磁盘瓶颈使并行不一定更快。

性能阶段要分别计时decoding、变换和编码，并先在相同输入上校验串并行输出尺寸与像素近似一致。若磁盘已饱和，增加进程只会争抢 I/O；若 CPU 变换占主导，多进程才可能绕过 GIL 获益。输出先写临时文件再 rename，可避免失败后留下看似成功的半文件。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/d5535584-0980-47fb-862d-6f9f7569791d)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
