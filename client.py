import hashlib

class MemTable:
    def __init__(self, capacity=4):
        self.capacity = capacity
        self.data = {}

    def put(self, key, value):
        self.data[key] = value
        return len(self.data) >= self.capacity

    def get(self, key):
        return self.data.get(key)

class SSTable:
    def __init__(self, level, entries):
        self.level = level
        self.entries = sorted(entries, key=lambda x: x[0])
        self.keys = [k for k, v in self.entries]
        self.bloom = 0
        for k, _ in self.entries:
            h = int(hashlib.md5(k.encode()).hexdigest(), 16)
            self.bloom |= (1 << (h % 64))

    def may_contain(self, key):
        h = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return (self.bloom & (1 << (h % 64))) != 0

    def get(self, key):
        if not self.may_contain(key):
            return None
        low, high = 0, len(self.entries) - 1
        while low <= high:
            mid = (low + high) // 2
            k, v = self.entries[mid]
            if k == key:
                return v
            elif k < key:
                low = mid + 1
            else:
                high = mid - 1
        return None

class LSMTreeEngine:
    """
    Log-Structured Merge Tree Engine with in-memory MemTable,
    immutable SSTables, Bloom filters, and compaction.
    """
    def __init__(self, memtable_cap=4):
        self.memtable = MemTable(memtable_cap)
        self.levels = {0: [], 1: []}
        self.wal = []

    def put(self, key, value):
        self.wal.append((key, value))
        is_full = self.memtable.put(key, value)
        if is_full:
            self.flush()

    def flush(self):
        entries = list(self.memtable.data.items())
        sst = SSTable(level=0, entries=entries)
        self.levels[0].append(sst)
        self.memtable = MemTable(self.memtable.capacity)
        if len(self.levels[0]) >= 2:
            self.compact(0, 1)

    def compact(self, src_level, dst_level):
        merged = {}
        for sst in self.levels[src_level]:
            for k, v in sst.entries:
                merged[k] = v
        for sst in self.levels[dst_level]:
            for k, v in sst.entries:
                if k not in merged:
                    merged[k] = v
        new_sst = SSTable(dst_level, list(merged.items()))
        self.levels[src_level] = []
        self.levels[dst_level] = [new_sst]

    def get(self, key):
        v = self.memtable.get(key)
        if v is not None:
            return v if v != "__TOMBSTONE__" else None
        for sst in reversed(self.levels[0]):
            val = sst.get(key)
            if val is not None:
                return val if val != "__TOMBSTONE__" else None
        for sst in self.levels[1]:
            val = sst.get(key)
            if val is not None:
                return val if val != "__TOMBSTONE__" else None
        return None
