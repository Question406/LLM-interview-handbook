from collections import defaultdict
import hashlib
import os
from pathlib import Path

BLOCK_SIZE = 64 * 1024


def same_content(path_a, path_b):
    """逐块比较两个文件的字节，用来排除哈希碰撞。"""
    with open(path_a, "rb") as file_a, open(path_b, "rb") as file_b:
        while True:
            block_a = file_a.read(BLOCK_SIZE)
            block_b = file_b.read(BLOCK_SIZE)
            if block_a != block_b:
                return False
            if not block_a:
                return True


def sha256_of(path):
    """流式计算 SHA-256，不把整个文件读进内存。"""
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for block in iter(lambda: file.read(BLOCK_SIZE), b""):
            digest.update(block)
    return digest.digest()


def group_by_size(root):
    """递归收集普通文件，按字节数分组；不跟随符号链接（目录和文件都跳过）。"""
    by_size = defaultdict(list)
    for directory, subdirs, files in os.walk(root, followlinks=False):
        subdirs[:] = [name for name in subdirs if not (Path(directory) / name).is_symlink()]
        for name in files:
            path = Path(directory) / name
            if path.is_file() and not path.is_symlink():
                by_size[path.stat().st_size].append(str(path))
    return by_size


def split_by_bytes(candidates):
    """把哈希相同的候选按真实内容分组。内容相等是等价关系，所以只需和每组第一个比。"""
    groups = []
    for path in sorted(candidates):
        for group in groups:
            if same_content(path, group[0]):
                group.append(path)
                break
        else:
            groups.append([path])
    return groups


def duplicates(root):
    """返回内容相同的普通文件路径组：每组至少两个，组内和组间都排序。"""
    result = []
    for paths in group_by_size(root).values():
        if len(paths) < 2:
            continue  # 大小唯一的文件不可能有重复，不用读内容
        by_hash = defaultdict(list)
        for path in paths:
            by_hash[sha256_of(path)].append(path)
        for candidates in by_hash.values():
            result.extend(group for group in split_by_bytes(candidates) if len(group) > 1)
    return sorted(result)


def test():
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        contents = [("a", b"abc"), ("b", b"abc"), ("c", b"xyz"), ("d", b""), ("e", b"")]
        for name, data in contents:
            (root / name).write_bytes(data)

        # 同大小不同内容的 c 不应和 a/b 并组；两个空文件互为重复
        groups = duplicates(directory)
        names = sorted(sorted(Path(path).name for path in group) for group in groups)
        assert names == [["a", "b"], ["d", "e"]]

        # 符号链接不算一份文件
        (root / "link").symlink_to(root / "a")
        assert duplicates(directory) == groups

        # 子目录里的文件也会被找到；指向目录的符号链接不跟随
        (root / "sub").mkdir()
        (root / "sub" / "f").write_bytes(b"xyz")
        (root / "sub_link").symlink_to(root / "sub")
        names = sorted(sorted(Path(path).name for path in group) for group in duplicates(directory))
        assert names == [["a", "b"], ["c", "f"], ["d", "e"]]

    # 逐块比较：差异落在第二块里也能发现
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "x").write_bytes(b"1" * (BLOCK_SIZE + 1))
        (root / "y").write_bytes(b"1" * BLOCK_SIZE + b"2")
        assert not same_content(root / "x", root / "y")
        assert same_content(root / "x", root / "x")


if __name__ == "__main__":
    test()
