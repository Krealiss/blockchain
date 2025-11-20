import hashlib
import time
import json


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def hash_tx(tx: dict) -> str:
    tx_str = json.dumps(tx, sort_keys=True)
    return sha256(tx_str)


def build_merkle_tree(txs):
    if not txs:
        # if block has no txs
        first_level = [sha256("")]   # hash of empty string
    else:
        first_level = [hash_tx(tx) for tx in txs]

    levels = [first_level]
    current = first_level

    while len(current) > 1:
        next_level = []
        for i in range(0, len(current), 2):
            left = current[i]
            if i + 1 < len(current):
                right = current[i + 1]
            else:
                right = left  # duplicate last if odd number of nodes
            parent = sha256(left + right)
            next_level.append(parent)
        levels.append(next_level)
        current = next_level

    return levels  # levels[-1][0] is merkle root


class Block:
    def __init__(self, index, txs, prev_hash):
        self.index = index
        self.timestamp = int(time.time())
        self.transactions = txs
        self.prev_hash = prev_hash

        # build Merkle tree and root
        self.merkle_levels = build_merkle_tree(self.transactions)
        self.merkle_root = self.merkle_levels[-1][0]

        # no real PoW, just hash header once
        self.hash = self.calculate_hash()

    def header_string(self):
        # header fields: prevHash | timestamp | merkleRoot
        return f"{self.prev_hash}|{self.timestamp}|{self.merkle_root}"

    def calculate_hash(self):
        return sha256(self.header_string())


def create_genesis_block():
    txs = [{"from": "GENESIS", "to": "GENESIS", "amount": 0}]
    return Block(0, txs, "0" * 64)


def is_chain_valid(chain):
    for i in range(1, len(chain)):
        block = chain[i]
        prev_block = chain[i - 1]

        # check prevHash
        if block.prev_hash != prev_block.hash:
            print(f"[ERROR] Block {block.index}: prev_hash mismatch")
            return False

        # recompute merkle root
        new_levels = build_merkle_tree(block.transactions)
        new_root = new_levels[-1][0]
        if block.merkle_root != new_root:
            print(f"[ERROR] Block {block.index}: merkleRoot mismatch")
            return False

        # recompute block hash
        new_hash = sha256(f"{block.prev_hash}|{block.timestamp}|{block.merkle_root}")
        if block.hash != new_hash:
            print(f"[ERROR] Block {block.index}: hash mismatch")
            return False

    return True


# 1. create simple "blockchain"
chain = []
genesis = create_genesis_block()
chain.append(genesis)

# block 1 with some txs
txs1 = [
    {"from": "Alice", "to": "Bob", "amount": 10},
    {"from": "Bob", "to": "Charlie", "amount": 5},
    {"from": "Charlie", "to": "Dave", "amount": 2},
    {"from": "Dave", "to": "Alice", "amount": 1},
]

block1 = Block(1, txs1, genesis.hash)
chain.append(block1)

# 2. print tx list and merkle tree
print("=== Block 1 transactions ===")
for t in block1.transactions:
    print(t)
print()

print("=== Merkle tree levels (0 = leaves) ===")
for i, level in enumerate(block1.merkle_levels):
    # show first 12 chars to keep output short
    short_level = [h[:12] + "..." for h in level]
    print(f"Level {i}: {short_level}")
print()

print("Merkle root:", block1.merkle_root)
print("Block 1 hash:", block1.hash)
print("Chain valid before tamper?:", is_chain_valid(chain))

# 3. change one transaction (minimal change)
print("\n--- Tampering: change amount in first tx ---")
print("Old tx[0]:", block1.transactions[0])
block1.transactions[0]["amount"] = 999  # changed from 10 to 999
print("New tx[0]:", block1.transactions[0])

print("\nChain valid after tamper?:", is_chain_valid(chain))

# 4. show how merkleRoot and block hash WOULD change if we recompute them
new_levels = build_merkle_tree(block1.transactions)
new_root = new_levels[-1][0]
new_hash = sha256(f"{block1.prev_hash}|{block1.timestamp}|{new_root}")

print("\n--- Recomputed values (not saved in block) ---")
print("Old merkleRoot:", block1.merkle_root)
print("New merkleRoot:", new_root)
print("Old block hash:", block1.hash)
print("New block hash:", new_hash)

# 5. "remine" / fix block manually (just recalc root + hash)
print("\n--- Fix block (\"re-mining\" without PoW) ---")
block1.merkle_levels = new_levels
block1.merkle_root = new_root
block1.hash = block1.calculate_hash()

print("New stored merkleRoot:", block1.merkle_root)
print("New stored block hash:", block1.hash)
print("Chain valid after recompute?:", is_chain_valid(chain))