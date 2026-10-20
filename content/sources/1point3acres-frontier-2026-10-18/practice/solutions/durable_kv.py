import hashlib
import json
import os
import struct
import uuid
from pathlib import Path

MAGIC = b"KVS1"
COUNT = struct.Struct(">Q")         # 条目数，8 字节大端
LENGTHS = struct.Struct(">QQ")      # 每条的 key 长度、value 长度


def encode(data):
    """把 dict[bytes, bytes] 编码成 MAGIC + 条目数 + (key 长, value 长, key, value)*。"""
    parts = [MAGIC, COUNT.pack(len(data))]
    for key, value in data.items():
        if not isinstance(key, bytes) or not isinstance(value, bytes):
            raise ValueError("keys and values must be bytes")
        parts.extend([LENGTHS.pack(len(key), len(value)), key, value])
    return b"".join(parts)


def decode(data):
    """encode 的逆操作；截断、魔数错误、重复 key 或尾部多余数据都抛 ValueError。"""
    pos = 0

    def take(size):
        nonlocal pos
        if pos + size > len(data):
            raise ValueError("truncated payload")
        chunk = data[pos:pos + size]
        pos += size
        return chunk

    if take(len(MAGIC)) != MAGIC:
        raise ValueError("bad magic")
    (count,) = COUNT.unpack(take(COUNT.size))
    result = {}
    for _ in range(count):
        key_len, value_len = LENGTHS.unpack(take(LENGTHS.size))
        key = take(key_len)
        value = take(value_len)
        if key in result:
            raise ValueError(f"duplicate key: {key!r}")
        result[key] = value
    if pos != len(data):
        raise ValueError("trailing bytes after last entry")
    return result


def write_durably(path, content):
    """写入并 fsync，保证返回时内容已落盘。"""
    mode = "wb" if isinstance(content, bytes) else "w"
    with open(path, mode) as file:
        file.write(content)
        file.flush()
        os.fsync(file.fileno())


def dump_chunks(data, directory, limit=1024):
    """把快照切成每个不超过 limit 字节的文件，最后原子替换 manifest.json 来发布。"""
    if limit <= 0:
        raise ValueError("limit must be positive")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    payload = encode(data)
    version = uuid.uuid4().hex  # 新快照的文件名带版本号，不会覆盖旧快照
    names = []
    for start in range(0, len(payload), limit):
        name = f"{version}-{start // limit}.bin"
        write_durably(directory / name, payload[start:start + limit])
        names.append(name)

    manifest = {"files": names, "sha": hashlib.sha256(payload).hexdigest()}
    tmp = directory / f"{version}.manifest"
    write_durably(tmp, json.dumps(manifest))
    os.replace(tmp, directory / "manifest.json")  # 发布点：之前失败则旧 manifest 不变


def load_chunks(directory):
    """按 manifest 拼回 payload，校验 SHA-256 后解码。"""
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    if any(Path(name).name != name for name in manifest["files"]):
        raise ValueError("manifest file names must not contain paths")
    payload = b"".join((directory / name).read_bytes() for name in manifest["files"])
    if hashlib.sha256(payload).hexdigest() != manifest["sha"]:
        raise ValueError("checksum mismatch")
    return decode(payload)


def test():
    import tempfile

    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__} should raise ValueError")

    # 任意字节都能往返，包括空 key、\x00 和换行
    sample = {b"a\x00": b"x\ny", b"": bytes(range(256)) * 8}
    assert decode(encode(sample)) == sample
    assert decode(encode({})) == {}

    # 损坏的输入
    encoded = encode(sample)
    expect_value_error(decode, encoded[:-1])          # 截断
    expect_value_error(decode, encoded + b"\x00")     # 尾部多余数据
    expect_value_error(decode, b"XXXX" + encoded[4:])  # 魔数错误
    expect_value_error(encode, {"text": b"v"})         # key 不是 bytes

    # 分片落盘：每个数据文件不超过 limit，加载后完全一致
    with tempfile.TemporaryDirectory() as tmp:
        dump_chunks(sample, tmp, 100)
        assert load_chunks(tmp) == sample
        assert all(path.stat().st_size <= 100 for path in Path(tmp).glob("*.bin"))

        # 再发布一版，读者只会看到新版本
        dump_chunks({b"k": b"v2"}, tmp, 100)
        assert load_chunks(tmp) == {b"k": b"v2"}

        # 分片被篡改时校验失败
        manifest = json.loads((Path(tmp) / "manifest.json").read_text())
        (Path(tmp) / manifest["files"][0]).write_bytes(b"corrupt")
        expect_value_error(load_chunks, tmp)


if __name__ == "__main__":
    test()
