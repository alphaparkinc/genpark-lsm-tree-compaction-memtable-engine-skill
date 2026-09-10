from client import LSMTreeEngine

def main():
    print("=== Testing LSM-Tree Engine ===")
    lsm = LSMTreeEngine(memtable_cap=3)
    lsm.put("user:101", "Alice")
    lsm.put("user:102", "Bob")
    lsm.put("user:103", "Charlie") # trigger flush to SSTable
    lsm.put("user:104", "Dave")
    lsm.put("user:105", "Eve")
    lsm.put("user:106", "Frank") # trigger another flush and compaction

    print("Lookup user:101:", lsm.get("user:101"))
    print("Lookup user:104:", lsm.get("user:104"))
    assert lsm.get("user:101") == "Alice"
    assert lsm.get("user:104") == "Dave"
    assert lsm.get("user:999") is None
    print("=== All tests passed successfully! ===")

if __name__ == "__main__":
    main()
