class Node:
    def __init__(self, edge=(), values=(), parent=None):
        self.edge, self.values, self.parent = tuple(edge), tuple(values), parent
        self.children = {}
        self.locks = 0
        self.used = 0


class RadixCache:
    """Token-granularity compressed edges. Values are opaque immutable KV handles."""
    def __init__(self):
        self.roots = {}
        self.clock = 0

    def root(self, namespace):
        return self.roots.setdefault(namespace, Node())

    def touch(self, node):
        self.clock += 1
        node.used = self.clock

    @staticmethod
    def split(child, length):
        if not 0 < length < len(child.edge):
            raise ValueError('split must be inside a nonempty edge')
        parent = child.parent
        mid = Node(child.edge[:length], child.values[:length], parent)
        # Existing live leases finish at stable node objects and release via parents.
        mid.locks, mid.used = child.locks, child.used
        parent.children[mid.edge[0]] = mid
        child.edge = child.edge[length:]
        child.values = child.values[length:]
        child.parent = mid
        mid.children[child.edge[0]] = child
        return mid

    def walk(self, tokens, namespace, split_boundary=False):
        tokens = tuple(tokens)
        node = self.root(namespace)
        offset, values = 0, []
        while offset < len(tokens):
            child = node.children.get(tokens[offset])
            if child is None:
                break
            count = 0
            while (count < len(child.edge) and offset+count < len(tokens)
                   and child.edge[count] == tokens[offset+count]):
                count += 1
            values.extend(child.values[:count])
            offset += count
            if count < len(child.edge):
                if count and split_boundary:
                    node = self.split(child, count)
                break
            node = child
        return offset, tuple(values), node

    def match(self, tokens, namespace='default'):
        length, values, _ = self.walk(tokens, namespace)
        return length, values

    def insert(self, tokens, values, namespace='default'):
        tokens, values = tuple(tokens), tuple(values)
        if len(tokens) != len(values):
            raise ValueError('one KV handle per token')
        node = self.root(namespace)
        offset = 0
        while offset < len(tokens):
            child = node.children.get(tokens[offset])
            if child is None:
                child = Node(tokens[offset:], values[offset:], node)
                node.children[child.edge[0]] = child
                self.touch(child)
                return offset  # caller can discard duplicated input handles[:offset]
            count = 0
            while (count < len(child.edge) and offset+count < len(tokens)
                   and child.edge[count] == tokens[offset+count]):
                count += 1
            if count < len(child.edge):
                child = self.split(child, count)
            offset += count
            node = child
            self.touch(node)
        return offset

    def validate(self):
        count = 0
        def visit(node):
            nonlocal count
            for first, child in node.children.items():
                assert child.parent is node and child.edge and first == child.edge[0]
                assert len(child.edge) == len(child.values)
                count += len(child.edge)
                visit(child)
        for root in self.roots.values():
            visit(root)
        return count

# === TESTS ===
def test():
    tree = RadixCache()
    assert tree.insert([1, 2, 3, 4], ['a', 'b', 'c', 'd']) == 0
    # Unlike a dictionary of terminal strings, every computed interior prefix hits.
    assert tree.match([1, 2, 9]) == (2, ('a', 'b'))
    assert tree.match([1, 2]) == (2, ('a', 'b'))
    assert tree.insert([1, 2, 8], ['dup-a', 'dup-b', 'x']) == 2
    assert tree.match([1, 2, 8, 7]) == (3, ('a', 'b', 'x'))
    assert tree.insert([1], ['duplicate']) == 1
    assert tree.validate() == 5
    assert tree.match([1], 'other') == (0, ())
    assert tree.insert([], []) == 0
    # Randomized oracle: union of all inserted prefixes, first payload wins.
    import random
    rng = random.Random(3)
    tree = RadixCache()
    oracle = {}
    for step in range(300):
        seq = tuple(rng.randrange(5) for _ in range(rng.randrange(1, 10)))
        payload = tuple((step, i) for i in range(len(seq)))
        tree.insert(seq, payload)
        for i in range(1, len(seq)+1):
            oracle.setdefault(seq[:i], payload[i-1])
        for _ in range(3):
            query = tuple(rng.randrange(5) for _ in range(rng.randrange(11)))
            length = 0
            while length < len(query) and query[:length+1] in oracle:
                length += 1
            expected = tuple(oracle[query[:i]] for i in range(1, length+1))
            assert tree.match(query) == (length, expected)
        assert tree.validate() == len(oracle)

if __name__ == '__main__':
    test()
