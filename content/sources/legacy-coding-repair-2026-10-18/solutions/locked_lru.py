from threading import RLock

class Node:
    def __init__(self, key=None, value=None, weight=0):
        self.key, self.value, self.weight = key, value, weight
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity):
        if type(capacity) is not int or capacity < 0:
            raise ValueError("capacity")
        self.capacity, self.used = capacity, 0
        self.nodes = {}
        self.head, self.tail = Node(), Node()
        self.head.next, self.tail.prev = self.tail, self.head
        self.lock = RLock()

    def _unlink(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _recent(self, node):
        node.prev, node.next = self.tail.prev, self.tail
        self.tail.prev.next = node
        self.tail.prev = node

    def get(self, key):
        with self.lock:
            node = self.nodes.get(key)
            if node is None:
                return None
            self._unlink(node)
            self._recent(node)
            return node.value

    def put(self, key, value, weight=1):
        if type(weight) is not int or weight <= 0 or value is None:
            raise ValueError("weight/value")
        with self.lock:
            if weight > self.capacity:
                return False
            old = self.nodes.get(key)
            if old is not None:
                self._unlink(old)
                self.used -= old.weight
            node = Node(key, value, weight)
            self.nodes[key] = node
            self._recent(node)
            self.used += weight
            while self.used > self.capacity:
                victim = self.head.next
                self._unlink(victim)
                del self.nodes[victim.key]
                self.used -= victim.weight
            return True

c = LRUCache(5)
assert c.put("a", "A", 3) and c.put("b", "B", 2)
assert c.get("a") == "A"
assert c.put("c", "C", 2) and c.get("b") is None
assert not c.put("a", "X", 6) and c.get("a") == "A"
assert c.put("a", "new", 1) and c.used == 3
assert not LRUCache(0).put("x", 1)
# Randomized state-machine comparison with a standard-library oracle.
from collections import OrderedDict
import random
rng = random.Random(3); c = LRUCache(7); oracle = OrderedDict()
for _ in range(500):
    key = rng.randrange(8)
    if rng.random() < .4:
        expected = oracle[key][0] if key in oracle else None
        if key in oracle: oracle.move_to_end(key)
        assert c.get(key) == expected
    else:
        weight, value = rng.randrange(1, 10), rng.randrange(100)
        assert c.put(key, value, weight) == (weight <= 7)
        if weight <= 7:
            oracle.pop(key, None); oracle[key] = (value, weight)
            while sum(w for _, w in oracle.values()) > 7: oracle.popitem(last=False)
    order = []; node = c.head.next
    while node is not c.tail:
        assert node.next.prev is node and node.prev.next is node
        order.append(node.key); node = node.next
    assert order == list(oracle) and c.used == sum(w for _,w in oracle.values())
from concurrent.futures import ThreadPoolExecutor
c = LRUCache(100)
with ThreadPoolExecutor(8) as pool:
    assert all(pool.map(lambda i: c.put(i, i), range(100)))
assert c.used == 100 and all(c.get(i) == i for i in range(100))
