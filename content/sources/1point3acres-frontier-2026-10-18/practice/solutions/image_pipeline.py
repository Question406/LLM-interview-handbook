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


def test():
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


if __name__ == "__main__":
    test()
