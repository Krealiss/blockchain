import hashlib
import json


def sha256(s: str) -> str:
    #Simple SHA-256 helper: string -> hex hash.
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def hash_tx(tx: dict) -> str:
    #Hash a transaction object using JSON with sorted keys.
    tx_str = json.dumps(tx, sort_keys=True)
    return sha256(tx_str)


def build_merkle_tree(txs):
   
   #Build Merkle tree levels from list of transactions.
   #Returns list of levels, where:
   #   levels[0] = leaf hashes (tx hashes)
   #   levels[-1][0] = merkle root
   #If odd number of nodes -> duplicate last hash.
   
    if not txs:
        leaves = [sha256("")]  # empty block
    else:
        leaves = [hash_tx(tx) for tx in txs]

    levels = [leaves]
    current = leaves

    while len(current) > 1:
        next_level = []
        for i in range(0, len(current), 2):
            left = current[i]
            if i + 1 < len(current):
                right = current[i + 1]
            else:
                right = left  # duplicate last if odd
            parent = sha256(left + right)
            next_level.append(parent)
        levels.append(next_level)
        current = next_level

    return levels


def getMerkleProof(txId: str, merkle_levels):
    
    #Build Merkle proof for given txId (leaf hash).
    #Returns a list of {"hash": sibling_hash, "position": "left"/"right"}.
    #- "left"  means: sibling is on the left, so parent = H(sibling + current)
    #- "right" means: sibling is on the right, so parent = H(current + sibling)
    #If txId not found in leaves -> returns None.
    
    leaves = merkle_levels[0]
    if txId not in leaves:
        return None

    index = leaves.index(txId)
    proof = []

    # Go up from leaves to root
    for level in merkle_levels[:-1]:  # skip last (root) level
        # sibling index: if index is even -> sibling = index+1, else index-1
        if index % 2 == 0:  # left node
            if index + 1 < len(level):
                sibling_index = index + 1
            else:
                sibling_index = index  # duplicated node
            sibling_hash = level[sibling_index]
            proof.append({"hash": sibling_hash, "position": "right"})
        else:  # right node
            sibling_index = index - 1
            sibling_hash = level[sibling_index]
            proof.append({"hash": sibling_hash, "position": "left"})

        # move index to next level up
        index = index // 2

    return proof


def verifyProof(txId: str, proof, merkleRoot: str) -> bool:
    
    #Verify Merkle proof using only:
    #- txId (leaf hash),
    #- proof (list of sibling hashes with position),
    #- merkleRoot.
    #No access to full list of txs.
    
    current = txId
    for step in proof:
        sibling = step["hash"]
        pos = step["position"]
        if pos == "left":
            current = sha256(sibling + current)
        else:  # "right"
            current = sha256(current + sibling)

    return current == merkleRoot


#SIMPLE BLOCK

class Block:
    def __init__(self, index, txs, prev_hash):
        self.index = index
        self.txs = txs
        self.prev_hash = prev_hash
        # build Merkle tree
        self.merkle_levels = build_merkle_tree(self.txs)
        self.merkle_root = self.merkle_levels[-1][0]
        # very simple header hash (no PoW)
        header_str = f"{self.prev_hash}|{self.merkle_root}"
        self.hashHeader = sha256(header_str)


# LIGHT CLIENT WITH MERKLE PROOF

if __name__ == "__main__":
    # 1. full node: create a block with some transactions
    txs = [
        {"from": "Alice", "to": "Bob", "amount": 10},
        {"from": "Bob", "to": "Charlie", "amount": 5},
        {"from": "Charlie", "to": "Dave", "amount": 2},
        {"from": "Dave", "to": "Alice", "amount": 1},
    ]

    prev_hash = "0" * 64  # dummy previous hash
    block = Block(1, txs, prev_hash)

    print("Block header (full node)")
    print("prevHash  :", block.prev_hash)
    print("merkleRoot:", block.merkle_root)
    print("hashHeader:", block.hashHeader)
    print()

    # Choose one real transaction and compute its txId (leaf hash)
    real_tx = txs[1]  # Bob -> Charlie
    real_txId = hash_tx(real_tx)

    # Full node computes Merkle proof for this txId
    proof = getMerkleProof(real_txId, block.merkle_levels)

    # "Light client" only knows:
    # - txId
    # - proof
    # - merkleRoot from block header
    # It runs verifyProof(...)

    def print_proof(p):
        arr = []
        for step in p:
            arr.append({
                "hash": step["hash"][:12] + "...",
                "pos": step["position"]
            })
        return arr

    # 1) tx exists in block -> verification = true
    print("Case 1: real tx in block")
    print("txId:", real_txId[:24] + "...")
    print("proof:", print_proof(proof))
    result1 = verifyProof(real_txId, proof, block.merkle_root)
    print("verifyProof ->", result1)
    print()

    # 2) tampered proof (one hash changed) -> verification = false 
    print("Case 2: proof is TAMPERED")
    fake_proof = [step.copy() for step in proof]
    # change first sibling hash
    fake_proof[0]["hash"] = sha256("some random fake hash")
    print("txId:", real_txId[:24] + "...")
    print("fake proof:", print_proof(fake_proof))
    result2 = verifyProof(real_txId, fake_proof, block.merkle_root)
    print("verifyProof ->", result2)
    print()

    # 3) tx that is NOT in the block -> verification = false 
    print("Case 3: tx NOT in block")
    fake_tx = {"from": "X", "to": "Y", "amount": 999}
    fake_txId = hash_tx(fake_tx)
    # attacker reuses proof from real tx, but txId is different
    print("txId (not in block):", fake_txId[:24] + "...")
    print("proof (for other tx):", print_proof(proof))
    result3 = verifyProof(fake_txId, proof, block.merkle_root)
    print("verifyProof ->", result3)
