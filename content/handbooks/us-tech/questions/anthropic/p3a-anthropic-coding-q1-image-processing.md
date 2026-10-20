---
id: p3a-anthropic-coding-q1-image-processing
section: anthropic
order: 601
level: A
title: "Anthropic：图片流水线：批量变换与并行性能"
quick: "先写顺序版本作为基准，定清变换顺序和输出尺寸，测出解码、变换和写盘各自耗时，再按瓶颈选线程或多进程，并限制并发数。"
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · coding-q1-image-processing"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/coding-q1-image-processing
    type: secondary
---

## 题目

对一个目录里的图片批量做变换，比如灰度、翻转、缩放、模糊或旋转，先写出能用的版本，再优化整体耗时。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

先写一个顺序执行的版本作为基准，把变换的执行顺序和输出尺寸定清楚，比如先缩放再旋转和先旋转再缩放，得到的尺寸不一样。然后分别测量解码、变换和写盘各花了多少时间，再决定怎么优化。

并行化时要按瓶颈选工具：

- 线程适合 I/O，以及 Pillow 里会释放 GIL 的 C 实现操作。纯 Python 的逐像素循环用线程不会变快。
- 多进程适合 CPU 密集的步骤，但图片要在进程间传递，序列化和拷贝有成本。
- 并发数要受内存和磁盘吞吐限制。每个 worker 同时持有一张解码后的大图，开太多会把内存撑爆；磁盘写满带宽后再加线程只会更慢。

还要处理好工程细节：输出文件名冲突时开工前就报错，不能覆盖源文件，读完图片及时关闭文件句柄。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `process_image(path, steps)`：读入一张图片，按顺序执行 `steps`，返回新的 `Image`。`steps` 是 `(操作, 参数)` 的列表：
  - `("grayscale", None)`：转成 L 模式灰度图；
  - `("flip", None)`：左右镜像；
  - `("resize", (width, height))`：双线性插值缩放，宽高至少为 1；
  - `("rotate", degrees)`：逆时针旋转，画布扩大以容纳整张图（`expand=True`）。
- `pipeline(paths, outdir, steps, workers=4)`：用线程池并行处理多张图，每张输出为 `outdir/<原文件名>.png`，按输入顺序返回输出路径。
- 输入文件名（去掉扩展名后）必须唯一，输出不能覆盖源文件，这两项在开工前检查。未知操作、非法参数都抛 `ValueError`。
- 最多 1000 张图，每张不超过 $4096^2$ 像素，依赖 Pillow。练习的测试只用 PNG。

### 输入输出示例

```text
a.png: 2×1 的 RGB 红色图
pipeline(["a.png"], "out", [("grayscale", None), ("resize", (4, 2))], workers=2)
  -> ["out/a.png"]，输出为 L 模式、尺寸 4×2；源文件仍是 2×1 的 RGB
```

### 解题思路与正确性

每张图独立执行同一串有序变换。线程池只改变不同图片之间的执行先后，单张图内部的变换顺序不变，所以并行结果和顺序执行一致；`pool.map` 也保证返回顺序和输入顺序相同。

`process_image` 读图后先 `copy()` 再关闭文件，处理完的图在保存后 `close()`，并发时不会堆积打开的文件。输出路径冲突在提交任何任务之前就检查，不会出现两个线程写同一个文件。

### 完整参考实现（Python 3）

```python
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageOps


def apply_step(image, operation, argument):
    if operation == "grayscale":
        return ImageOps.grayscale(image)  # 输出 L 模式
    if operation == "flip":
        return ImageOps.mirror(image)  # 左右镜像
    if operation == "resize":
        if len(argument) != 2 or min(argument) < 1:
            raise ValueError(f"resize needs (width, height) >= 1: {argument!r}")
        return image.resize(tuple(argument), Image.Resampling.BILINEAR)
    if operation == "rotate":
        return image.rotate(argument, expand=True)  # 逆时针，画布扩大以容纳整张图
    raise ValueError(f"unknown operation: {operation!r}")


def process_image(path, steps):
    """读入一张图，按顺序执行 steps，返回新的 Image。"""
    with Image.open(path) as source:
        image = source.copy()  # copy 后立即关闭文件句柄，并发时不会堆积打开的文件
    for operation, argument in steps:
        image = apply_step(image, operation, argument)
    return image


def pipeline(paths, outdir, steps, workers=4):
    """并行处理多张图，输出 outdir/<原文件名>.png，按输入顺序返回输出路径。"""
    if workers < 1:
        raise ValueError(f"workers must be at least 1: {workers}")
    paths = [Path(path) for path in paths]
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # 开工前检查冲突，避免两个线程写同一个目标或覆盖源文件
    targets = [outdir / (path.stem + ".png") for path in paths]
    if len(set(targets)) != len(targets):
        raise ValueError("input basenames must be unique")
    for path, target in zip(paths, targets):
        if target.resolve() == path.resolve():
            raise ValueError(f"output would overwrite source: {path}")

    def run(path, target):
        image = process_image(path, steps)
        try:
            image.save(target, format="PNG")
        finally:
            image.close()
        return str(target)

    with ThreadPoolExecutor(workers) as pool:
        return list(pool.map(run, paths, targets))
```

### 可执行测试

```python
import tempfile

def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    red = root / "a.png"
    Image.new("RGB", (2, 1), (255, 0, 0)).save(red)

    # 先灰度再缩放；源文件不被修改
    result = pipeline([red], root / "out", [("grayscale", None), ("resize", (4, 2))], 2)
    with Image.open(result[0]) as output:
        assert output.mode == "L"
        assert output.size == (4, 2)
    with Image.open(red) as source:
        assert source.mode == "RGB"
        assert source.size == (2, 1)

    # 多张图并行，结果按输入顺序返回；左右镜像、旋转 90 度
    striped = root / "b.png"
    image = Image.new("RGB", (2, 1), (0, 0, 0))
    image.putpixel((0, 0), (255, 255, 255))
    image.save(striped)
    results = pipeline([red, striped], root / "out2", [("flip", None), ("rotate", 90)], 2)
    assert [Path(path).name for path in results] == ["a.png", "b.png"]
    with Image.open(results[1]) as output:
        assert output.size == (1, 2)
        assert output.getpixel((0, 0)) == (255, 255, 255)   # 镜像后白点在右，逆时针转 90 度到上方

    # 非法输入
    expect_value_error(pipeline, [red, root / "x" / "a.png"], root / "out3", [])
    expect_value_error(pipeline, [red], root, [])           # 会覆盖源文件
    expect_value_error(process_image, red, [("blur", 2)])
```

### 复杂度与追问

设总像素数为 P、变换步数为 s。像素处理大约是 O(P·s)；同一时刻最多有 `workers` 张图在内存里，峰值内存约为 `workers` 乘以单张图的大小。

- 多线程一定更快吗？不一定。Pillow 的一部分操作在 C 层释放了 GIL，可以并行；另一部分不释放，就只能并发等待 I/O。需要实测，I/O 带宽饱和后继续加线程反而变慢。
- 要加模糊这类 CPU 很重的操作呢？在 `apply_step` 里加一个分支（比如 `ImageFilter.GaussianBlur`）即可。如果实测发现它成了瓶颈，可以把 `ThreadPoolExecutor` 换成 `ProcessPoolExecutor`，让每个子进程自己读写文件，只在进程间传路径，不传图片数据。
- 某一张图损坏怎么办？这个实现会让整个 `pipeline` 抛异常。生产版可以按图片捕获异常，返回每张图的成功或失败状态，不让一张坏图拖垮整批。
