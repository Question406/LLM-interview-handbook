from threading import RLock

class Database:
    def __init__(self):
        self.data = {}
        self.versions = {}
        self.clock = 0
        self.lock = RLock()

    def begin(self):
        with self.lock:
            return Transaction(self, self.data.copy(), self.versions.copy())

class Transaction:
    def __init__(self, db, snapshot, versions):
        self.db, self.snapshot, self.versions = db, snapshot, versions
        self.reads, self.writes, self.closed = set(), {}, False

    def _check(self):
        if self.closed:
            raise RuntimeError("transaction closed")

    def get(self, key):
        self._check()
        self.reads.add(key)
        return self.writes.get(key, self.snapshot.get(key))

    def put(self, key, value):
        self._check()
        if not isinstance(value, str):
            raise ValueError("values must be strings")
        self.writes[key] = value

    def delete(self, key):
        self._check()
        self.writes[key] = None

    def commit(self):
        self._check()
        with self.db.lock:
            touched = self.reads | self.writes.keys()
            self.closed = True
            if any(self.db.versions.get(k, 0) != self.versions.get(k, 0)
                   for k in touched):
                return False
            if self.writes:
                self.db.clock += 1
                for key, value in self.writes.items():
                    if value is None:
                        self.db.data.pop(key, None)
                    else:
                        self.db.data[key] = value
                    self.db.versions[key] = self.db.clock
            return True

    def rollback(self):
        self._check()
        self.closed = True
        self.writes.clear()

db = Database()
t = db.begin(); t.put("a", "1"); assert t.commit()
x, y = db.begin(), db.begin()
x.put("a", "2"); assert x.get("a") == "2" and x.commit()
assert y.get("a") == "1"
y.put("b", "3"); assert not y.commit()
assert db.begin().get("b") is None
x, y = db.begin(), db.begin()
x.put("c", "x"); y.put("d", "y")
assert x.commit() and y.commit()
old = db.begin(); assert old.get("ghost") is None
x = db.begin(); x.put("ghost", "x"); assert x.commit()
x = db.begin(); x.delete("ghost"); assert x.commit()
assert not old.commit()  # creation then deletion must still conflict
x = db.begin(); x.delete("a"); x.rollback()
assert db.begin().get("a") == "2"
try: x.get("a")
except RuntimeError: pass
else: raise AssertionError("closed transaction reused")
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
barrier = Barrier(2)
def compete(value):
    t = db.begin(); t.put("same", value); barrier.wait(); return t.commit()
with ThreadPoolExecutor(2) as pool:
    assert sum(pool.map(compete, ["x", "y"])) == 1
