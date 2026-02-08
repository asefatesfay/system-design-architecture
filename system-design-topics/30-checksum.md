# Checksum

## Definition

**Checksum** is a small piece of data computed from a larger dataset to detect errors or verify data integrity. If data changes, checksum changes, indicating corruption or tampering.

## How It Works

```
Original Data: "Hello, World!"
↓
Hash Function (MD5, SHA-256, CRC32, etc.)
↓
Checksum: a1b2c3d4e5f6...

Verify:
1. Recompute checksum of received data
2. Compare with original checksum
3. Match → Data intact ✓
4. Mismatch → Data corrupted ❌
```

## Real-World Examples

### 1. File Downloads
```
Download Ubuntu ISO (4 GB)
Website provides SHA-256 checksum:
abc123def456...

After download:
$ sha256sum ubuntu-22.04.iso
abc123def456...  ✓ Match!

Ensures:
- Complete download
- No corruption
- No tampering
```

### 2. Git (Version Control)
```
Every commit has SHA-1 hash:
commit abc123def456...

Checksum of:
- File contents
- Commit message
- Author, timestamp
- Parent commit hash

Change one character → Completely different hash
Ensures integrity of entire repository history
```

### 3. AWS S3 (Cloud Storage)
```
Upload file to S3
→ S3 computes ETag (MD5 checksum)
→ Returns: "d41d8cd98f00b204e9800998ecf8427e"

Multipart upload:
→ S3 computes checksum per part
→ Combined checksum for entire file

Ensures:
- Upload completed successfully
- Data not corrupted during transfer
```

### 4. Blockchain (Bitcoin, Ethereum)
```
Block header includes:
- Timestamp
- Transactions
- Previous block hash (checksum)
- Nonce

Hash entire header → Block hash

Chain of hashes:
Block 1 (hash: abc) ← Block 2 (hash: def, prev: abc) ← Block 3

Change Block 1 → Hash changes → Block 2 invalid → Chain broken
Immutability through checksums ✓
```

### 5. TCP/IP (Network)
```
TCP packet includes checksum
1. Compute checksum of packet data
2. Include in header
3. Receiver recomputes checksum
4. Mismatch → Packet corrupted → Request retransmission

Ensures data integrity over unreliable networks
```

### 6. RAID (Disk Arrays)
```
RAID 5: Distribute data + parity across disks
Parity = XOR checksum of data

Disk fails → Reconstruct data using parity
Example:
Disk 1: 1010
Disk 2: 1100
Parity:  0110 (XOR)

Disk 2 fails → Recover: Disk 1 XOR Parity = Disk 2
```

### 7. Databases (PostgreSQL, MySQL)
```
Page-level checksums
Write data page → Compute checksum → Store with page
Read page → Verify checksum → Detect corruption

Example: PostgreSQL
initdb --data-checksums
```

### 8. Distributed Systems
```
Cassandra / DynamoDB: Merkle Trees for data sync
1. Divide data into chunks
2. Compute hash per chunk
3. Build tree of hashes

Compare Merkle trees between replicas
→ Identify which chunks differ
→ Sync only different chunks (efficient!)
```

## Common Checksum Algorithms

### 1. CRC32 (Cyclic Redundancy Check)
```python
import zlib

data = b"Hello, World!"
checksum = zlib.crc32(data)
print(hex(checksum))  # 0xec4ac3d0

# Fast, detects common errors
# Not cryptographically secure
# Used by: ZIP files, Ethernet, PNG
```

### 2. MD5
```python
import hashlib

data = b"Hello, World!"
checksum = hashlib.md5(data).hexdigest()
print(checksum)  # 65a8e27d8879283831b664bd8b7f0ad4

# Fast
# Not secure (collisions found)
# Still used for non-security purposes (file integrity)
```

### 3. SHA-256
```python
import hashlib

data = b"Hello, World!"
checksum = hashlib.sha256(data).hexdigest()
print(checksum)
# dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f

# Cryptographically secure
# No known collisions
# Used by: Git, Bitcoin, file verification
```

### 4. SHA-1
```
Faster than SHA-256
Collisions found (2017) → Deprecated for security
Still used in Git (transitioning to SHA-256)
```

### 5. xxHash (Fast Non-Cryptographic)
```python
import xxhash

data = b"Hello, World!"
checksum = xxhash.xxh64(data).hexdigest()

# Extremely fast
# Good distribution
# Not cryptographic
# Used by: Compression (zstd), databases
```

## Use Cases

### ✅ Data Integrity Verification
```python
# Before storage
original_checksum = hashlib.sha256(data).hexdigest()
save_to_disk(data)

# After retrieval
retrieved_data = load_from_disk()
new_checksum = hashlib.sha256(retrieved_data).hexdigest()

if original_checksum == new_checksum:
    print("Data intact ✓")
else:
    print("Data corrupted ❌")
```

### ✅ Duplicate Detection
```python
# Find duplicate files
checksums = {}
for file in files:
    checksum = compute_checksum(file)
    if checksum in checksums:
        print(f"Duplicate: {file} == {checksums[checksum]}")
    else:
        checksums[checksum] = file

# Used by: Dropbox, Google Photos
```

### ✅ Content Addressing
```python
# Git: Files identified by SHA-1 hash
file_content = "Hello, World!"
blob_hash = hashlib.sha1(file_content.encode()).hexdigest()
# Store as: objects/df/fd6021bb2bd5b0af676290809ec3a53191dd81

# Retrieve by hash (content-addressable storage)
```

### ✅ Cache Keys
```python
def cache_key(url, params):
    key = f"{url}:{json.dumps(params, sort_keys=True)}"
    return hashlib.md5(key.encode()).hexdigest()

# Same inputs → Same key → Cache hit
```

### ✅ Tamper Detection
```
Download software (binary)
Download signature (checksum signed by developer)
Verify checksum matches
→ Software not tampered with ✓
```

## Implementation Example

```python
import hashlib

class ChecksumVerifier:
    @staticmethod
    def compute_checksum(data, algorithm='sha256'):
        """Compute checksum using specified algorithm"""
        if algorithm == 'md5':
            return hashlib.md5(data).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(data).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(data).hexdigest()
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    @staticmethod
    def verify_file(file_path, expected_checksum, algorithm='sha256'):
        """Verify file integrity"""
        with open(file_path, 'rb') as f:
            data = f.read()
            actual_checksum = ChecksumVerifier.compute_checksum(data, algorithm)
            return actual_checksum == expected_checksum

# Usage
data = b"Important financial data"
checksum = ChecksumVerifier.compute_checksum(data)
print(f"Checksum: {checksum}")

# Later, verify
with open('file.dat', 'rb') as f:
    if ChecksumVerifier.verify_file('file.dat', checksum):
        print("File verified ✓")
    else:
        print("File corrupted ❌")
```

## Streaming Checksum (Large Files)

```python
import hashlib

def compute_checksum_streaming(file_path, algorithm='sha256'):
    """Compute checksum without loading entire file into memory"""
    hash_obj = hashlib.sha256() if algorithm == 'sha256' else hashlib.md5()
    
    with open(file_path, 'rb') as f:
        # Read in chunks
        while chunk := f.read(8192):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()

# Can handle multi-GB files efficiently
checksum = compute_checksum_streaming('large_video.mp4')
```

## Properties

### Good Checksum Algorithm Should:

✅ **Deterministic:** Same input → Same checksum
✅ **Fast to compute**
✅ **Uniform distribution:** Similar inputs → Different checksums
✅ **Avalanche effect:** 1 bit change → 50% checksum bits change
✅ **Collision resistant:** Hard to find different inputs with same checksum

### Cryptographic vs Non-Cryptographic

**Cryptographic (SHA-256, SHA-3):**
- Collision resistant
- Pre-image resistant (can't find input from checksum)
- Used for security (passwords, signatures, blockchain)

**Non-Cryptographic (CRC32, xxHash):**
- Much faster
- Detects accidental errors (not malicious)
- Used for data integrity (not security)

## Comparison

| Algorithm | Speed | Security | Use Case |
|-----------|-------|----------|----------|
| **CRC32** | Very Fast | None | Error detection (ZIP, Ethernet) |
| **MD5** | Fast | Weak | File integrity (non-security) |
| **SHA-1** | Medium | Weak | Legacy (Git, old systems) |
| **SHA-256** | Medium | Strong | Security (blockchain, signatures) |
| **xxHash** | Extremely Fast | None | High-speed integrity checks |

## Best Practices

✅ **Choose algorithm based on use case**
```
Security → SHA-256
Performance → xxHash, CRC32
General integrity → MD5 acceptable
```

✅ **Store checksums separately**
```
data.txt       (actual data)
data.txt.sha256 (checksum file)
```

✅ **Include metadata in checksum**
```
Checksum = Hash(data + filename + timestamp)
Prevents replay attacks
```

✅ **Use streaming for large files**
```
Don't load entire file into memory
Process in chunks
```

✅ **Verify on both write and read**
```
Write: Compute and store checksum
Read: Verify checksum matches
```

## Interview Tips

**Q: "What is checksum?"**

**A:** Small hash computed from data to verify integrity. If data changes, checksum changes. Example: Download Ubuntu ISO (4GB), website provides SHA-256 checksum, compute checksum of downloaded file, if matches → intact. Used by Git (commit hashes), S3 (ETags), TCP (packet checksums).

**Q: "How does Git use checksums?"**

**A:** Every commit has SHA-1 hash of contents (files, message, author, parent hash). Change one byte → completely different hash. Chain of hashes ensures repository integrity, can't modify history without detection. Transitioning to SHA-256 for better security.

**Q: "CRC vs SHA-256?"**

**A:** CRC (Cyclic Redundancy Check) fast, detects accidental errors (bit flips), not cryptographically secure. SHA-256 slower, cryptographically secure, collision resistant. Use CRC for performance (Ethernet, ZIP), SHA-256 for security (blockchain, digital signatures).

**Q: "How to verify file integrity in distributed system?"**

**A:** Compute checksum (SHA-256) when writing file, store with metadata. When reading, recompute checksum and compare. For large files, use streaming (read chunks). S3 returns ETag (MD5), DynamoDB uses Merkle trees to detect divergence between replicas.

**Key Takeaway:** Checksums detect corruption/tampering through hash comparison. Choose algorithm based on speed vs security needs!
