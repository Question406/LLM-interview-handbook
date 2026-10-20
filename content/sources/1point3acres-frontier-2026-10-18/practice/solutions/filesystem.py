class Node:
    """文件或目录节点。text 为 None 表示目录；文件的 text 是字符串（空文件是 ""）。"""

    def __init__(self, text=None):
        self.text = text
        self.children = {}  # 只有目录使用：名字 -> Node

    @property
    def is_file(self):
        return self.text is not None


class FS:
    """内存里的 Unix 风格文件系统，只接受绝对路径，不支持链接和权限。"""

    def __init__(self):
        self.root = Node()

    def _parts(self, path):
        """把绝对路径规范化成名字列表：去掉空段和 "."，".." 回到上一级，根的上一级还是根。"""
        if not path.startswith("/"):
            raise ValueError(f"path must be absolute: {path!r}")
        parts = []
        for name in path.split("/"):
            if name in ("", "."):
                continue
            if name == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(name)
        return parts

    def _walk(self, parts):
        """沿 parts 走到目标节点；中途遇到文件或缺失的名字就报错。"""
        node = self.root
        for name in parts:
            if node.is_file:
                raise NotADirectoryError(name)
            if name not in node.children:
                raise FileNotFoundError(name)
            node = node.children[name]
        return node

    def mkdir(self, path, parents=False):
        """创建目录；目录已存在时什么也不做。parents=True 时顺带创建缺失的上级目录。"""
        parts = self._parts(path)
        node = self.root
        for depth, name in enumerate(parts):
            if node.is_file:
                raise NotADirectoryError(name)
            if name not in node.children:
                is_last = depth == len(parts) - 1
                if not is_last and not parents:
                    raise FileNotFoundError(name)
                node.children[name] = Node()
            node = node.children[name]
        if node.is_file:
            raise FileExistsError(path)

    def write(self, path, text, append=False):
        """写文件；文件不存在就创建。append=True 时接在原内容后面。上级目录必须已存在。"""
        parts = self._parts(path)
        if not parts:
            raise IsADirectoryError(path)
        parent = self._walk(parts[:-1])
        if parent.is_file:
            raise NotADirectoryError(path)
        name = parts[-1]
        old = parent.children.get(name)
        if old is not None and not old.is_file:
            raise IsADirectoryError(path)
        prefix = old.text if append and old is not None else ""
        parent.children[name] = Node(prefix + text)

    def read(self, path):
        node = self._walk(self._parts(path))
        if not node.is_file:
            raise IsADirectoryError(path)
        return node.text

    def ls(self, path):
        """文件返回 [自身名字]，目录返回排好序的子节点名字。"""
        parts = self._parts(path)
        node = self._walk(parts)
        if node.is_file:
            return [parts[-1]]
        return sorted(node.children)

    def remove(self, path, recursive=False):
        """删除文件或目录。非空目录必须 recursive=True；根目录不能删。"""
        parts = self._parts(path)
        if not parts:
            raise ValueError("cannot remove root")
        parent = self._walk(parts[:-1])
        node = self._walk(parts)
        if not node.is_file and node.children and not recursive:
            raise ValueError(f"directory not empty: {path}")
        # 从父目录断开整棵子树即可，子节点随之不可达
        del parent.children[parts[-1]]


def test():
    def expect_error(error, fn, *args):
        try:
            fn(*args)
        except error:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise {error.__name__}")

    # 写入、追加、带 "." 的路径
    fs = FS()
    fs.mkdir("/a")
    fs.write("/a/f", "hi")
    fs.write("/a/f", "!", True)
    assert fs.read("/a/./f") == "hi!"
    assert fs.ls("/a") == ["f"]
    assert fs.ls("/a/f") == ["f"]

    # 非空目录必须递归删除
    expect_error(ValueError, fs.remove, "/a")

    fs.mkdir("/b/c", True)
    fs.remove("/a", True)
    assert fs.ls("/") == ["b"]

    # ".." 回到上一级
    fs.write("/b/c/../x", "z")
    assert fs.read("/b/x") == "z"

    # 重复 mkdir 是幂等的；空文件仍然是文件
    fs.mkdir("/b/c")
    fs.write("/b/empty", "")
    assert fs.read("/b/empty") == ""
    assert fs.ls("/b") == ["c", "empty", "x"]

    expect_error(FileNotFoundError, fs.mkdir, "/p/q")      # 缺上级且没给 parents
    expect_error(FileExistsError, fs.mkdir, "/b/x")        # 同名文件已存在
    expect_error(NotADirectoryError, fs.read, "/b/x/y")    # 把文件当目录
    expect_error(IsADirectoryError, fs.write, "/b/c", "t")  # 往目录里写内容
    expect_error(ValueError, fs.remove, "/")               # 根目录不能删
    expect_error(ValueError, fs.ls, "b")                   # 只接受绝对路径


if __name__ == "__main__":
    test()
