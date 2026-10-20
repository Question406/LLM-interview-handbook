from dataclasses import dataclass, asdict
import hashlib
import json


@dataclass(frozen=True)
class Context:
    model: str
    adapter: str
    tokenizer: str
    position_and_mask: str
    tenant: str
    multimodal: str = ''


class BlockHashCache:
    def __init__(self, block_size=4, hash_fn=None):
        if type(block_size) is not int or block_size < 1:
            raise ValueError('block size')
        self.block_size = block_size
        self.hash_fn = hash_fn or (lambda data: hashlib.sha256(data).hexdigest())
        self.blocks = {}

    def chain(self, tokens, context):
        tokens = tuple(tokens)
        if not isinstance(context, Context) or any(type(t) is not int or t < 0 for t in tokens):
            raise ValueError('context or tokens')
        # The complete exact key is retained too: a digest collision is not a hit.
        parent_hash = None
        for offset in range(0, len(tokens)-self.block_size+1, self.block_size):
            block = tokens[offset:offset+self.block_size]
            exact = (context, tokens[:offset], block)
            encoded = json.dumps([asdict(context), self.block_size, parent_hash, block],
                                 sort_keys=True, separators=(',', ':')).encode()
            digest = self.hash_fn(encoded)
            yield digest, exact
            parent_hash = digest

    def put(self, tokens, values, context):
        keys = list(self.chain(tokens, context))
        values = tuple(values)
        if len(keys) != len(values):
            raise ValueError('one immutable value per full block')
        # Check all collisions before publishing any newly computed blocks.
        for digest, exact in keys:
            if digest in self.blocks and self.blocks[digest][0] != exact:
                raise ValueError('hash collision: refuse to reuse')
        if len({d for d, _ in keys}) != len(keys):
            raise ValueError('intra-request hash collision')
        for (digest, exact), value in zip(keys, values):
            self.blocks.setdefault(digest, (exact, value))

    def match(self, tokens, context):
        values = []
        for digest, exact in self.chain(tokens, context):
            entry = self.blocks.get(digest)
            if entry is None:
                break
            if entry[0] != exact:
                raise ValueError('hash collision: refuse to reuse')
            values.append(entry[1])
        return len(values)*self.block_size, tuple(values)

# === TESTS ===
def test():
    from dataclasses import replace
    context = Context('weights-v1', 'lora-A', 'tok-v1', 'rope0-causal', 'tenant-A')
    cache = BlockHashCache(2)
    cache.put([1, 2, 3, 4, 5], ['AB', 'CD'], context)
    assert cache.match([1, 2, 3, 4, 9], context) == (4, ('AB', 'CD'))
    assert cache.match([1, 2, 3], context) == (2, ('AB',))
    assert cache.match([9, 2, 3, 4], context) == (0, ())
    assert cache.match([3, 4], context) == (0, ())  # suffix block needs its full ancestry
    for field in asdict(context):
        other = replace(context, **{field: getattr(context, field)+'-changed'})
        assert cache.match([1, 2], other) == (0, ())
    cache.put([1, 2], ['duplicate-handle'], context)
    assert cache.match([1, 2], context)[1] == ('AB',)
    collision = BlockHashCache(2, hash_fn=lambda _: 'constant')
    collision.put([1, 2], ['AB'], context)
    try:
        collision.match([3, 4], context)
    except ValueError:
        pass
    else:
        raise AssertionError('collision became a false hit')

if __name__ == '__main__':
    test()
