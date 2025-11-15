import hashlib
import time

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def find_prefix_collision(base="student_test", n=4, max_attempts=2_000_000, verbose_every=100_000):
    assert 1 <= n <= 64, "n must be within the range of 1..64 hex characters"
    seen = {}  # prefix -> (nonce, full_hash)
    start = time.time()

    for nonce in range(max_attempts):
        s = f"{base}{nonce}"
        h = sha256_hex(s)
        prefix = h[:n]

        if prefix in seen:
            prev_nonce, prev_hash = seen[prefix]
            if prev_nonce != nonce:
                elapsed = time.time() - start
                return {
                    "attempts": nonce + 1,
                    "elapsed_sec": elapsed,
                    "base": base,
                    "n": n,
                    "a": {"nonce": prev_nonce, "string": f"{base}{prev_nonce}", "hash": prev_hash},
                    "b": {"nonce": nonce, "string": s, "hash": h},
                }
        else:
            seen[prefix] = (nonce, h)

        if verbose_every and nonce % verbose_every == 0 and nonce > 0:
            print(f"[info] Verified {nonce:,} nonce... (unique prefixes: {len(seen):,})")

    return None  # not found within max_attempts

if __name__ == "__main__":
    # Settings
    BASE = "student_test"
    N = 5              # change 1-5 to set the prefix length
    MAX_ATTEMPTS = 5_000_000

    res = find_prefix_collision(base=BASE, n=N, max_attempts=MAX_ATTEMPTS)
    print("\nResult")
    if res is None:
        print(f"Collision by prefix with n={N} not found within {MAX_ATTEMPTS:,} attempts.")
    else:
        print(f"A collision was found for the length prefix n={res['n']}!")
        print(f"Number of attempts: {res['attempts']:,}")
        print(f"Search time: {res['elapsed_sec']:.3f} c")
        print("\n— Line A:")
        print(f"   nonce:  {res['a']['nonce']}")
        print(f"   value:  {res['a']['string']}")
        print(f"   hash:   {res['a']['hash']}")
        print("\n— Line B:")
        print(f"   nonce:  {res['b']['nonce']}")
        print(f"   value:  {res['b']['string']}")
        print(f"   hash:   {res['b']['hash']}")
        print(f"\nCommon prefix: {res['a']['hash'][:N]} (first {N} hex-symbols)")
