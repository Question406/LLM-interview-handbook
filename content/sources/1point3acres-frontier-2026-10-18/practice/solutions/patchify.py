import numpy as np


def patchify(images, ph, pw):
    """[B, H, W, C] -> [B * (H/ph) * (W/pw), C, ph, pw]，patch 顺序为 batch、patch 行、patch 列。"""
    images = np.asarray(images)
    if images.ndim != 4 or ph <= 0 or pw <= 0:
        raise ValueError("images must be [B, H, W, C] and patch size positive")
    B, H, W, C = images.shape
    if H % ph or W % pw:
        raise ValueError(f"image {H}x{W} is not divisible by patch {ph}x{pw}")
    grid = images.reshape(B, H // ph, ph, W // pw, pw, C)  # 拆出 patch 网格轴和 patch 内轴
    grid = grid.transpose(0, 1, 3, 5, 2, 4)                # [B, 行, 列, C, ph, pw]
    return grid.reshape(-1, C, ph, pw)


def unpatchify(patches, B, H, W, C):
    """patchify 的逆变换：[P, C, ph, pw] -> [B, H, W, C]。"""
    patches = np.asarray(patches)
    if patches.ndim != 4:
        raise ValueError("patches must be [P, C, ph, pw]")
    ph, pw = patches.shape[-2:]
    if H % ph or W % pw:
        raise ValueError(f"image {H}x{W} is not divisible by patch {ph}x{pw}")
    expected = (B * (H // ph) * (W // pw), C, ph, pw)
    if patches.shape != expected:
        raise ValueError(f"expected patches of shape {expected}, got {patches.shape}")
    grid = patches.reshape(B, H // ph, W // pw, C, ph, pw)
    grid = grid.transpose(0, 1, 4, 2, 5, 3)  # [B, 行, ph, 列, pw, C]
    return grid.reshape(B, H, W, C)


def conv1x1(patches, weight, bias):
    """在每个 patch 上做 1x1 卷积：patches [P, C, ph, pw]，weight [O, C]，bias [O] -> [P, O, ph, pw]。"""
    patches = np.asarray(patches)
    weight = np.asarray(weight)
    bias = np.asarray(bias)
    if patches.ndim != 4 or weight.ndim != 2 or weight.shape[1] != patches.shape[1]:
        raise ValueError("weight must be [O, C] matching the patch channels")
    if bias.shape != (weight.shape[0],):
        raise ValueError("bias must be [O]")
    return np.einsum("pchw,oc->pohw", patches, weight) + bias[None, :, None, None]


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__} should raise ValueError")

    # 单张 4x4 单通道图，2x2 patch：首个 patch 是左上角
    image = np.arange(16).reshape(1, 4, 4, 1)
    patches = patchify(image, 2, 2)
    assert patches.shape == (4, 1, 2, 2)
    assert patches[0, 0].tolist() == [[0, 1], [4, 5]]
    assert patches[1, 0].tolist() == [[2, 3], [6, 7]]  # 第二个是同一行右边那块
    assert np.array_equal(unpatchify(patches, 1, 4, 4, 1), image)

    # 1x1 卷积：输出通道 0 = 2 * 输入 + 1
    out = conv1x1(patches, np.array([[2], [3]]), np.array([1, 0]))
    assert out.shape == (4, 2, 2, 2)
    assert np.array_equal(out[:, 0], patches[:, 0] * 2 + 1)
    assert np.array_equal(out[:, 1], patches[:, 0] * 3)

    # 多 batch、多通道、非正方形 patch、非连续输入都能往返
    images = np.arange(2 * 4 * 6 * 3).reshape(2, 4, 6, 3)[:, ::-1]
    assert np.array_equal(unpatchify(patchify(images, 2, 3), 2, 4, 6, 3), images)

    # 不整除和形状不符
    expect_value_error(patchify, image, 3, 2)
    expect_value_error(unpatchify, patches, 2, 4, 4, 1)
    expect_value_error(conv1x1, patches, np.ones((2, 3)), np.zeros(2))


if __name__ == "__main__":
    test()
