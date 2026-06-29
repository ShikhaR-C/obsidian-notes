# Blockchain Theory Tutorial (from zero)

A structured, chapter-based learning path covering the theory behind blockchain systems. This file assumes you know almost nothing about cryptography or distributed systems and builds up step by step.

## What you'll learn

- The cryptographic primitives that make blockchains possible (hashes, keys, signatures, Merkle trees)
- How a blockchain actually works internally — you will build a toy one in JavaScript
- Consensus mechanisms: Proof-of-Work, Proof-of-Stake, finality, and forks
- The two major transaction models: UTXO (Bitcoin) and Accounts (Ethereum)
- What smart contracts are, the EVM, and Solidity basics
- Gas, fees, and the full transaction lifecycle
- How wallets, keys, addresses, and HD derivation work (BIP-32/39/44)
- Token standards: ERC-20, ERC-721, ERC-1155
- Oracles, bridges, and Layer-2 rollups
- Common smart contract vulnerabilities and how to avoid them

## Prerequisites

- Basic JavaScript (you can read a function, you know what `const` and `class` are)
- Node.js 18+ installed (`node -v` should print a version)
- A terminal and a text editor
- No prior blockchain knowledge required

Install one dependency we will use for crypto examples:

```bash
mkdir blockchain-theory && cd blockchain-theory
npm init -y
npm install elliptic
```

Node.js ships with a built-in `crypto` module, so we do not need anything else for hashes.

---

## Chapter 1: Cryptography Primer

Before blockchains can exist, four cryptographic tools must exist. We will cover each with a tiny runnable example.

### 1.1 Hash functions (SHA-256)

A hash function takes any input and returns a fixed-size fingerprint. For SHA-256, that fingerprint is always 256 bits (64 hex characters). Good hash functions have three properties:

1. **Deterministic** — the same input always produces the same output.
2. **One-way** — given the output, you cannot reverse it to get the input.
3. **Avalanche** — changing one bit of input completely changes the output.

Let us see this in action. Create `hash.js`:

```javascript
const crypto = require('crypto');

function sha256(input) {
  return crypto.createHash('sha256').update(input).digest('hex');
}

console.log(sha256('hello'));
console.log(sha256('hello!'));
console.log(sha256('hello'));
```

Run it:

```bash
node hash.js
```

You will see:

```
2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
ce06092fb948d9ffac7d1a376e404b26b7575bec38fe17c027452f1168f5ff20
2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
```

Notice: adding one character (`!`) produced a wildly different hash. The first and third calls are identical because the input is identical.

This is the property blockchains exploit: if you change any byte of any block, the hash changes, and every subsequent block breaks.

### 1.2 Public/private key cryptography

Symmetric encryption uses one key to encrypt and decrypt — which is useless when two strangers need to transact, because they would have to share the key first. Asymmetric cryptography solves this with **key pairs**:

- **Private key** — a large random number. Never share it. It proves ownership.
- **Public key** — derived from the private key using a one-way function. You share this freely.

Anything signed with the private key can be verified using the public key, without ever revealing the private key.

Bitcoin and Ethereum both use **ECDSA** (Elliptic Curve Digital Signature Algorithm) on the curve `secp256k1`. Create `keys.js`:

```javascript
const EC = require('elliptic').ec;
const ec = new EC('secp256k1');

const keyPair = ec.genKeyPair();
const privateKey = keyPair.getPrivate('hex');
const publicKey = keyPair.getPublic('hex');

console.log('Private key:', privateKey);
console.log('Public key: ', publicKey);
```

Run it a few times — you get a different pair each time. The public key is derived from the private key deterministically, but you cannot go the other direction.

### 1.3 Digital signatures

A digital signature proves two things:

1. The signer knew the private key.
2. The message has not been altered since it was signed.

Create `sign.js`:

```javascript
const crypto = require('crypto');
const EC = require('elliptic').ec;
const ec = new EC('secp256k1');

const keyPair = ec.genKeyPair();

const message = 'Send 10 coins to Bob';
const msgHash = crypto.createHash('sha256').update(message).digest();

const signature = keyPair.sign(msgHash);
const derSig = signature.toDER('hex');
console.log('Signature:', derSig);

const publicKey = keyPair.getPublic('hex');
const verifier = ec.keyFromPublic(publicKey, 'hex');
const isValid = verifier.verify(msgHash, signature);
console.log('Valid?', isValid);

const tamperedHash = crypto.createHash('sha256').update('Send 1000 coins to Bob').digest();
console.log('Tampered valid?', verifier.verify(tamperedHash, signature));
```

Expected output:

```
Signature: 3045...
Valid? true
Tampered valid? false
```

The verifier only needs the public key and the message — not the private key. If anyone changes the message after it is signed, verification fails. This is how blockchain transactions are authenticated: the sender signs with their private key, and every node on the network verifies using the sender's public key.

### 1.4 Merkle trees

A Merkle tree is a binary tree of hashes. You hash all the leaves, then hash pairs of hashes, then pairs of those, until you get one root hash. That single root commits to every leaf.

Why is this useful? Because you can prove that a specific transaction is in a block without downloading the entire block. You only need a handful of sibling hashes (a "Merkle proof"), and the block's Merkle root.

Create `merkle.js`:

```javascript
const crypto = require('crypto');

function sha256(x) {
  return crypto.createHash('sha256').update(x).digest('hex');
}

function merkleRoot(leaves) {
  let layer = leaves.map(sha256);
  while (layer.length > 1) {
    if (layer.length % 2 === 1) layer.push(layer[layer.length - 1]);
    const next = [];
    for (let i = 0; i < layer.length; i += 2) {
      next.push(sha256(layer[i] + layer[i + 1]));
    }
    layer = next;
  }
  return layer[0];
}

const txs = ['tx1', 'tx2', 'tx3', 'tx4'];
console.log('Root:', merkleRoot(txs));
```

Change any transaction and the root changes. Bitcoin blocks store only the Merkle root of all transactions in the block header, which is why "light clients" can verify transactions without storing gigabytes of data.

### Chapter 1 quiz

1. If you SHA-256 the same string twice, do you get the same result?
2. Can you derive a private key from a public key?
3. What does a digital signature prove?
4. Why do Merkle trees allow "light clients" to exist?

**Answers:** 1) Yes, hashes are deterministic. 2) No, the derivation is one-way. 3) That the signer held the private key and the message has not been tampered with. 4) A light client can verify a single transaction is in a block using only a short path of sibling hashes, without storing the entire block.

---

## Chapter 2: How a Blockchain Actually Works Internally

Now that you have the primitives, we can assemble them into a real blockchain. We will build a toy blockchain in about 80 lines of JavaScript that has:

- Blocks containing data + a link to the previous block
- SHA-256 hashing of each block
- Proof-of-Work mining
- Full chain validation

### 2.1 What is a block?

A block is just a data structure with a few fields:

- `index` — its position in the chain
- `timestamp` — when it was created
- `data` — the transactions (or any payload)
- `previousHash` — the hash of the block before it
- `nonce` — a number miners change to find a valid hash
- `hash` — the SHA-256 of all of the above

The magic is that each block contains the hash of the previous one. If you tamper with block 5, its hash changes, which means block 6's `previousHash` field no longer matches, and the chain is broken. To fix the chain, you would have to re-mine every block from 5 onward — and with Proof-of-Work, that is computationally infeasible.

### 2.2 The full toy blockchain

Create `toy-blockchain.js`:

```javascript
const crypto = require('crypto');

class Block {
  constructor(index, timestamp, data, previousHash = '') {
    this.index = index;
    this.timestamp = timestamp;
    this.data = data;
    this.previousHash = previousHash;
    this.nonce = 0;
    this.hash = this.calculateHash();
  }

  calculateHash() {
    return crypto
      .createHash('sha256')
      .update(
        this.index +
          this.previousHash +
          this.timestamp +
          JSON.stringify(this.data) +
          this.nonce
      )
      .digest('hex');
  }

  mineBlock(difficulty) {
    const target = '0'.repeat(difficulty);
    while (this.hash.substring(0, difficulty) !== target) {
      this.nonce++;
      this.hash = this.calculateHash();
    }
    console.log(`Block ${this.index} mined: ${this.hash}`);
  }
}

class Blockchain {
  constructor() {
    this.chain = [this.createGenesisBlock()];
    this.difficulty = 4;
  }

  createGenesisBlock() {
    return new Block(0, Date.now(), 'Genesis Block', '0');
  }

  getLatestBlock() {
    return this.chain[this.chain.length - 1];
  }

  addBlock(data) {
    const previousBlock = this.getLatestBlock();
    const newBlock = new Block(
      previousBlock.index + 1,
      Date.now(),
      data,
      previousBlock.hash
    );
    newBlock.mineBlock(this.difficulty);
    this.chain.push(newBlock);
  }

  isValid() {
    for (let i = 1; i < this.chain.length; i++) {
      const current = this.chain[i];
      const previous = this.chain[i - 1];
      if (current.hash !== current.calculateHash()) return false;
      if (current.previousHash !== previous.hash) return false;
    }
    return true;
  }
}

const myChain = new Blockchain();

console.log('Mining block 1...');
myChain.addBlock({ from: 'Alice', to: 'Bob', amount: 50 });

console.log('Mining block 2...');
myChain.addBlock({ from: 'Bob', to: 'Carol', amount: 25 });

console.log('Chain valid?', myChain.isValid());

myChain.chain[1].data = { from: 'Alice', to: 'Eve', amount: 999 };
console.log('After tampering, valid?', myChain.isValid());
```

Run it:

```bash
node toy-blockchain.js
```

You will see each block being mined (it may take a second or two — that is the Proof-of-Work actually burning CPU). You will see the chain is valid, then invalid after we tamper with it.

### 2.3 What is actually happening

- `calculateHash` produces a fingerprint of the block's contents including the nonce.
- `mineBlock(difficulty)` loops, incrementing the nonce, until the hash starts with N leading zeros. There is no shortcut — the only way to find a nonce that produces N leading zeros is to try random nonces. That is what makes mining "work".
- `isValid()` walks the chain, recomputes each hash, and checks that each `previousHash` field matches the previous block's hash. Any tampering breaks this.

### 2.4 Tuning the difficulty

Change `this.difficulty = 4` to `5` and run it again — it will take noticeably longer. Each additional required leading zero makes mining roughly 16 times harder (because each hex character has 16 possible values). Real Bitcoin today has a difficulty corresponding to roughly 19 leading zeros, and it takes the entire global mining hash power about 10 minutes to find a valid nonce.

### 2.5 What our toy lacks

To keep it short, we left out:

- **Transactions and signatures** — real blocks contain signed transactions, not arbitrary JSON.
- **A mempool** — a pool of pending transactions waiting to be mined.
- **A peer-to-peer network** — our toy is single-process.
- **Dynamic difficulty adjustment** — real chains retarget difficulty every N blocks.
- **Merkle roots** — real blocks store a Merkle root of transactions in the header.

But the core idea — chained hashes + computational work to extend the chain — is complete.

### Chapter 2 quiz

1. What happens if you change `data` in an old block?
2. What does the nonce do?
3. Why is mining slow?
4. What does `previousHash` enforce?

**Answers:** 1) The old block's hash changes, every subsequent block's `previousHash` no longer matches, and validation fails. 2) It is the only field miners change to search for a hash below the difficulty target. 3) Because the only way to find a matching hash is brute-force guessing. 4) It chains blocks together so you cannot modify history without redoing all the work.

---

## Chapter 3: Consensus Mechanisms Deep Dive

A blockchain is a distributed database. Thousands of nodes each have a copy of it. The hard problem is: when two nodes disagree about what happened, how do they decide? That is consensus.

### 3.1 Proof-of-Work (PoW)

Used by Bitcoin, Litecoin, Dogecoin, and Ethereum before The Merge (September 2022).

**The rule:** nodes accept the longest valid chain, where "longest" means the most cumulative work.

Miners race to find a nonce such that `SHA256(block) < target`. The target is a huge number; the smaller it is, the harder the puzzle. Whoever finds a valid nonce first broadcasts the block, and everyone else verifies and extends it.

**The math:** if the target allows 1 in 2^70 nonces to succeed, and you have a hash rate of 2^40 hashes per second, on average you will find a block every 2^30 seconds (~34 years). A million such miners combined would find one every ~17 minutes. Bitcoin retargets difficulty every 2,016 blocks so that block times stay near 10 minutes.

**Why it works:** an attacker who wants to rewrite history must out-mine the entire honest network. As long as honest miners have more than 50% of the hash power, they will extend the honest chain faster than the attacker can build a rival.

**Downsides:**
- Massive energy consumption.
- Probabilistic finality — your transaction can be reversed if a longer chain appears. Convention is to wait 6 confirmations for Bitcoin (~1 hour).

### 3.2 Proof-of-Stake (PoS)

Used by Ethereum (post-Merge), Solana, Cardano, Cosmos, and most new chains.

**The rule:** validators lock up ("stake") tokens as collateral. The protocol randomly selects validators to propose and attest to blocks, weighted by stake. If a validator signs two conflicting blocks or misbehaves, their stake is **slashed** — destroyed or partially confiscated.

**The economics:** an attacker needs to control a supermajority (typically 2/3) of the total stake. On Ethereum that is tens of billions of dollars. Any attempted attack destroys the attacker's own capital via slashing, which is much more aligned with good behavior than PoW (where an attacker's hardware is unaffected).

**Ethereum's specific design:**
- Validators deposit 32 ETH each.
- Time is divided into 12-second slots; one validator is chosen to propose each slot.
- Slots are grouped into 32-slot epochs.
- After ~2 epochs (~12 minutes) a block becomes **finalized** — it cannot be reverted without 1/3 of all stake being slashed.

### 3.3 Why finality matters

In PoW, there is no moment when a block is "final". A longer chain can always appear. In PoS with explicit finality (like Ethereum), once a block is finalized, reverting it is economically impossible. This matters for:

- **Exchanges** accepting deposits — finality means you can credit a user safely.
- **Bridges** between chains — they need to know when they can trust a source-chain state.
- **DeFi liquidations** — must execute on a known-final state.

### 3.4 Forks

A fork happens when two miners/validators produce valid blocks at nearly the same height. The network temporarily disagrees. Types:

- **Soft fork** — backwards-compatible rule tightening. Old nodes still accept new blocks.
- **Hard fork** — incompatible rule change. Old nodes reject new blocks. Requires all participants to upgrade. Famous examples: Bitcoin Cash (forked from Bitcoin, 2017), Ethereum Classic (forked from Ethereum after the DAO hack, 2016).
- **Temporary fork** — accidental, resolved when one chain extends faster and becomes canonical. Orphaned blocks are discarded.

### 3.5 Other consensus mechanisms (briefly)

- **Delegated Proof-of-Stake (DPoS)** — token holders vote for a small set of validators. Fast but more centralized. Used by EOS, Tron.
- **Proof-of-Authority (PoA)** — a fixed set of trusted validators. Used for private/consortium chains.
- **Practical Byzantine Fault Tolerance (PBFT)** — used in Cosmos and Hyperledger. Validators vote in rounds; consensus in one round gives instant finality.

### Chapter 3 quiz

1. What incentivizes miners to behave honestly in PoW?
2. What incentivizes validators to behave honestly in PoS?
3. What is a hard fork?
4. Why does finality matter for exchanges?

**Answers:** 1) Block rewards plus the sunk cost of hardware and electricity. 2) Staked collateral that can be slashed. 3) An incompatible protocol change requiring all nodes to upgrade. 4) Because they cannot safely credit a user until the deposit cannot be reverted.

---

## Chapter 4: Accounts vs UTXO Models

There are two fundamentally different ways to track who owns what.

### 4.1 The UTXO model (Bitcoin)

UTXO stands for **Unspent Transaction Output**. Imagine cash: if you pay for a $7 coffee with a $20 bill, you get $13 in change. You do not modify the $20 bill; you destroy it and create a $7 payment and a $13 change note.

In Bitcoin, your wallet does not have a single balance. It has a collection of UTXOs — previous outputs sent to your addresses. When you pay someone:

1. You select one or more UTXOs that total at least the amount you want to send.
2. You create a transaction that spends (destroys) those UTXOs and creates new ones:
   - One output to the recipient's address.
   - One output back to yourself as change.
3. You sign the transaction with the private keys of the UTXOs you are spending.

Example: Alice has two UTXOs, 0.5 BTC and 0.3 BTC. She wants to send 0.6 BTC to Bob. She creates:

```
Inputs:  UTXO A (0.5 BTC, owned by Alice)
         UTXO B (0.3 BTC, owned by Alice)
Outputs: 0.6 BTC to Bob
         0.19 BTC to Alice (change)
         (0.01 BTC implicit fee — inputs minus outputs)
```

After this transaction, UTXOs A and B no longer exist. Two new UTXOs exist. Your wallet's "balance" is just the sum of all UTXOs it owns.

**Pros:**
- Highly parallelizable — independent UTXOs can be validated in parallel.
- Better privacy — each transaction can use different addresses.
- Simpler state model — just a set of unspent outputs.

**Cons:**
- Complex for stateful applications (e.g., smart contracts that track user balances).
- Wallet software must track many UTXOs.

### 4.2 The account model (Ethereum)

Ethereum works more like a bank. Each address has a persistent account with:

- **Balance** (in wei)
- **Nonce** (transaction count — prevents replay)
- **Code hash** (for contract accounts)
- **Storage root** (for contract state)

When Alice sends 0.6 ETH to Bob:

```
Before: Alice.balance = 0.8,  Bob.balance = 0.0
Tx:     Alice -> Bob : 0.6
After:  Alice.balance = 0.2,  Bob.balance = 0.6
```

No UTXOs are consumed; balances are just updated.

**Two account types on Ethereum:**

1. **Externally Owned Accounts (EOAs)** — controlled by a private key. Humans and wallets use these.
2. **Contract accounts** — controlled by code. No private key. Triggered when another account sends them a transaction.

**Pros:**
- Trivial to build smart contracts with mutable state (balances, mappings, etc.).
- Simple mental model for developers.

**Cons:**
- Harder to parallelize — two transactions touching the same account must be ordered.
- Privacy is weaker — your address is reused.
- Requires a nonce to prevent replay attacks (a signed transaction for nonce 5 can only be executed once, then nonce becomes 6).

### 4.3 Concrete comparison

Sending 10 tokens of balance across three addresses:

**UTXO (Bitcoin-style):** Each transaction produces new outputs, consumes old ones. Chain state is a set of outputs.

**Accounts (Ethereum-style):** Each transaction mutates state. Chain state is a mapping from address to balance.

Both produce the same economic result, but the underlying data structures and how you reason about concurrency are totally different.

### Chapter 4 quiz

1. In UTXO, what is "change"?
2. How does the account model prevent replay attacks?
3. Which model is easier for smart contracts?
4. What are the two account types on Ethereum?

**Answers:** 1) The portion of an input UTXO that the sender returns to themselves because the UTXO was larger than needed. 2) Each account has a nonce that increments with every transaction; a signed transaction for a given nonce can only execute once. 3) The account model. 4) Externally Owned Accounts (EOAs) and contract accounts.

---

## Chapter 5: Smart Contracts

A smart contract is a program stored on-chain that runs exactly as written, without a trusted third party. Anyone can call it; the rules are enforced by the network.

### 5.1 The Ethereum Virtual Machine (EVM)

The EVM is a stack-based virtual machine that executes contract bytecode. Key properties:

- **Deterministic** — same input, same output on every node (no network calls, no random sources, no filesystem).
- **Gas-metered** — every opcode has a gas cost; execution halts if gas runs out.
- **Isolated** — contracts cannot reach outside the EVM state.
- **256-bit words** — the native integer size is 256 bits, optimized for cryptographic operations.

Bytecode is too hard to write by hand, so we use higher-level languages that compile to EVM bytecode. The dominant one is **Solidity**.

### 5.2 Solidity in five minutes

Solidity looks like JavaScript mixed with C++. Here is a complete, minimal contract:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Counter {
    uint256 public count;
    address public owner;

    event Incremented(address indexed by, uint256 newCount);

    constructor() {
        owner = msg.sender;
    }

    function increment() external {
        count += 1;
        emit Incremented(msg.sender, count);
    }

    function reset() external {
        require(msg.sender == owner, "Not owner");
        count = 0;
    }
}
```

Line-by-line:

- `SPDX-License-Identifier` — a comment declaring the license. Required by convention.
- `pragma solidity ^0.8.20;` — compile with Solidity 0.8.20 or any compatible 0.8.x version.
- `contract Counter { ... }` — declares a contract.
- `uint256 public count;` — a state variable. `public` auto-generates a getter function.
- `address public owner;` — Ethereum addresses are 20-byte values.
- `event Incremented(...)` — events are emitted to a log; frontends listen to them.
- `constructor()` — runs once at deployment.
- `msg.sender` — the address that called this function.
- `external` — callable from outside the contract (cheaper than `public` for externally-called functions).
- `require(condition, "error")` — revert the transaction if the condition is false.
- `emit` — writes the event to the log.

### 5.3 State, storage, memory, calldata

Solidity distinguishes data locations:

- **Storage** — persistent on-chain state. Very expensive to read (~2,100 gas cold), extremely expensive to write (~20,000 gas for a fresh slot).
- **Memory** — temporary, per-transaction. Cheap.
- **Calldata** — read-only input to a function. Cheapest.
- **Stack** — EVM stack, automatic for primitives.

Writing Solidity that minimizes storage access is the main way to lower gas costs.

### 5.4 A slightly richer example

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Bank {
    mapping(address => uint256) private balances;

    event Deposit(address indexed from, uint256 amount);
    event Withdraw(address indexed to, uint256 amount);

    function deposit() external payable {
        require(msg.value > 0, "Zero deposit");
        balances[msg.sender] += msg.value;
        emit Deposit(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient");
        balances[msg.sender] -= amount;
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "Transfer failed");
        emit Withdraw(msg.sender, amount);
    }

    function balanceOf(address user) external view returns (uint256) {
        return balances[user];
    }
}
```

Key ideas:

- `payable` marks functions that can receive ETH.
- `msg.value` is the amount of ETH sent with the call.
- `mapping(address => uint256)` is a hash map from address to balance.
- `.call{value: amount}("")` sends ETH to an address (the modern preferred pattern).
- `view` marks a function that reads state but does not modify it — free to call from outside.

Note: this `withdraw` has a subtle reentrancy bug we will fix in Chapter 10.

### 5.5 What else Solidity gives you

- Inheritance: `contract Child is Parent { ... }`
- Interfaces: `interface IERC20 { function transfer(...) external returns (bool); }`
- Modifiers: `modifier onlyOwner() { require(msg.sender == owner); _; }`
- Libraries: reusable code linked at compile time
- Custom errors: `error InsufficientBalance(uint256 have, uint256 need);` (cheaper than `require` strings)
- Enums, structs, arrays

We will use many of these in the practical tutorial in the next file.

### Chapter 5 quiz

1. What does `msg.sender` return?
2. Why is storage expensive?
3. What does `payable` do?
4. What is an event used for?

**Answers:** 1) The address that called the current function. 2) Because state is persisted on every node and indexed in a Merkle Patricia Trie. 3) It allows a function to receive ETH along with the call. 4) Events are written to the transaction log; off-chain applications (frontends, indexers) subscribe to them to react to on-chain activity.

---

## Chapter 6: Gas, Fees, and the Transaction Lifecycle

Every EVM computation costs gas. Understanding gas is essential.

### 6.1 What is gas?

Gas is a measure of computational work. Each EVM opcode has a fixed gas cost:

- `ADD` — 3 gas
- `MUL` — 5 gas
- `SLOAD` (cold storage read) — 2,100 gas
- `SSTORE` (fresh storage slot) — 20,000 gas
- `KECCAK256` (hash) — 30 gas + 6 per word

A complex contract function might use 100,000 gas. A simple ETH transfer uses 21,000 gas (a fixed base cost).

### 6.2 Gas price

You also set a **gas price** (in gwei, where 1 gwei = 10^-9 ETH). The total fee is:

```
fee = gasUsed * gasPrice
```

Example: 100,000 gas at 30 gwei = 3,000,000 gwei = 0.003 ETH. At $2,000/ETH that is $6.

### 6.3 EIP-1559 (the modern fee model)

Since August 2021 (Ethereum London upgrade), fees are split into:

- **Base fee** — set by the protocol, adjusted per block based on demand. **Burned** (destroyed).
- **Priority fee (tip)** — goes to the validator, incentivizes inclusion.
- **Max fee** — the highest total you are willing to pay.

Transaction uses `min(maxFee, baseFee + priorityFee)`. If blocks get full, base fee rises exponentially, pricing out low-urgency transactions.

### 6.4 Gas limit

You set a **gas limit** — the maximum amount of gas you allow your transaction to consume. If execution runs out of gas, the transaction **reverts** but you still pay for the gas used up to that point. Wallets estimate a reasonable limit automatically.

### 6.5 The full transaction lifecycle

1. **Sign** — user signs the transaction with their private key, producing `{from, to, value, data, nonce, gasLimit, maxFeePerGas, maxPriorityFeePerGas, chainId, v, r, s}`.
2. **Broadcast** — the wallet sends it to an RPC endpoint (Infura, Alchemy, your own node).
3. **Mempool** — the transaction waits in the pending pool along with others. Validators rank them by priority fee.
4. **Included** — a validator selects the transaction for the next block.
5. **Executed** — the EVM runs the transaction. State is updated. Gas is consumed. Logs are emitted.
6. **Confirmed** — the block is propagated. Subsequent blocks build on top.
7. **Finalized** — after ~12 minutes on Ethereum PoS, the block is finalized and cannot be reverted.

### 6.6 Reading a block explorer

On Etherscan, a transaction has:

- **Status** — success or failed
- **Block** — which block included it
- **From / To** — accounts
- **Value** — ETH transferred
- **Transaction fee** — actual ETH burned + tipped
- **Gas price** — effective price per unit
- **Gas used** — actual units consumed
- **Input data** — calldata (function selector + arguments)
- **Logs** — events emitted

Spending time reading random transactions on Etherscan is one of the best ways to build intuition.

### Chapter 6 quiz

1. What happens if a transaction runs out of gas?
2. What happens to the base fee in EIP-1559?
3. What does the priority fee do?
4. What are the main steps of the transaction lifecycle?

**Answers:** 1) It reverts, but the sender still pays for gas used up to the revert point. 2) It is burned. 3) It is a tip to the validator to prioritize inclusion. 4) Sign, broadcast, mempool, included, executed, confirmed, finalized.

---

## Chapter 7: Wallets, Keys, Addresses, HD Wallets

A wallet does not hold coins. A wallet holds **keys**. Coins live on the chain, and the keys prove who can spend them.

### 7.1 From private key to address (Ethereum)

1. Generate a 256-bit random number — this is the **private key**.
2. Apply `secp256k1` elliptic curve multiplication to get the **public key** (64 bytes).
3. Hash the public key with Keccak-256.
4. Take the last 20 bytes of the hash — this is the **address**.

Example in JavaScript:

```javascript
const crypto = require('crypto');
const EC = require('elliptic').ec;
const ec = new EC('secp256k1');
const { keccak256 } = require('ethereum-cryptography/keccak');

const key = ec.genKeyPair();
const publicKey = key.getPublic('hex').slice(2); // strip leading 04
const address = '0x' + Buffer.from(keccak256(Buffer.from(publicKey, 'hex'))).slice(-20).toString('hex');
console.log(address);
```

### 7.2 The problem with random keys

If every new address needs a fresh random private key, users have to back up many different keys. That is terrible UX. Hierarchical Deterministic (HD) wallets solve this.

### 7.3 BIP-39: mnemonic seeds

BIP-39 (Bitcoin Improvement Proposal 39) defines a way to encode a random seed as a human-readable phrase. A 128-bit entropy becomes a 12-word phrase from a fixed 2,048-word dictionary:

```
abandon ability able about above absent absorb abstract absurd abuse access accident
```

A 256-bit entropy becomes a 24-word phrase. A checksum is embedded in the last word, so typos are usually caught.

The phrase is hashed (PBKDF2 with 2,048 iterations) to produce a **512-bit seed**.

### 7.4 BIP-32: hierarchical derivation

BIP-32 takes the seed and lets you derive an entire tree of keys. Each node can have 2^31 children. Paths look like:

```
m / 44' / 60' / 0' / 0 / 0
```

- `m` — master key
- `44'` — purpose (BIP-44)
- `60'` — coin type (Ethereum = 60, Bitcoin = 0)
- `0'` — account index
- `0` — change (0 = external, 1 = internal)
- `0` — address index

The apostrophe means "hardened" derivation (an extra safety property; hardened child keys cannot be derived from the parent public key alone).

### 7.5 BIP-44: coin-aware accounts

BIP-44 standardizes the path structure above so that the same seed can generate separate addresses for Bitcoin, Ethereum, Litecoin, etc., all from the same 12 words.

### 7.6 What this means for you

- Your wallet shows you **one seed phrase**. Back it up on paper. Never type it into a website. Never take a screenshot that syncs to the cloud.
- From that seed phrase, you can derive unlimited addresses, restore in any BIP-39 compatible wallet, and deterministically generate child accounts.
- Losing the seed phrase = losing the funds forever.

### 7.7 Hot vs cold wallets

- **Hot wallet** — keys stored on an internet-connected device (MetaMask, Phantom). Convenient, exposed to malware.
- **Cold wallet / hardware wallet** — keys stored on a dedicated offline device (Ledger, Trezor). Sign transactions on the device itself; the private key never touches your computer. Much safer for significant holdings.

### Chapter 7 quiz

1. What does a wallet actually store?
2. What is a BIP-39 seed phrase for?
3. Why is a hardware wallet safer than MetaMask?
4. What does the `60` in `m/44'/60'/0'/0/0` mean?

**Answers:** 1) Private keys (or a seed phrase from which keys are derived). 2) A human-readable backup of the master entropy, from which all child keys are derived. 3) Because the private key never leaves the device; even a compromised computer cannot exfiltrate it. 4) Coin type 60 = Ethereum.

---

## Chapter 8: Tokens — ERC-20, ERC-721, ERC-1155

"ERC" means Ethereum Request for Comments. These are standards — interfaces that contracts can implement so that wallets, exchanges, and other contracts can interact with them uniformly.

### 8.1 ERC-20: fungible tokens

"Fungible" means interchangeable — 1 USDC is equal to any other 1 USDC, the same way dollar bills are interchangeable.

The ERC-20 interface:

```solidity
interface IERC20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}
```

A minimal implementation:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MiniToken {
    string public name = "Mini";
    string public symbol = "MIN";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    constructor(uint256 _initialSupply) {
        totalSupply = _initialSupply;
        balanceOf[msg.sender] = _initialSupply;
        emit Transfer(address(0), msg.sender, _initialSupply);
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        require(balanceOf[msg.sender] >= amount, "Insufficient");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(balanceOf[from] >= amount, "Insufficient");
        require(allowance[from][msg.sender] >= amount, "Not approved");
        allowance[from][msg.sender] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        emit Transfer(from, to, amount);
        return true;
    }
}
```

Why `approve` + `transferFrom`? Because if Alice wants a DEX contract to trade tokens on her behalf, she cannot give the DEX her private key. Instead she approves an allowance, and the DEX pulls tokens via `transferFrom`.

In production, always use **OpenZeppelin's** audited ERC-20 — do not hand-roll these primitives.

### 8.2 ERC-721: non-fungible tokens (NFTs)

NFT = Non-Fungible Token. Each token has a unique ID and unique properties.

Key interface additions over ERC-20:

```solidity
function ownerOf(uint256 tokenId) external view returns (address);
function safeTransferFrom(address from, address to, uint256 tokenId) external;
function tokenURI(uint256 tokenId) external view returns (string memory);
```

`tokenURI` typically points to a JSON metadata file (often on IPFS) describing the NFT:

```json
{
  "name": "CryptoKitten #42",
  "description": "A mischievous kitten",
  "image": "ipfs://bafy.../42.png",
  "attributes": [
    {"trait_type": "Color", "value": "Orange"},
    {"trait_type": "Rarity", "value": "Legendary"}
  ]
}
```

A minimal ERC-721 using OpenZeppelin:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyNFT is ERC721, Ownable {
    uint256 public nextId;

    constructor() ERC721("MyNFT", "MNFT") Ownable(msg.sender) {}

    function mint(address to) external onlyOwner {
        _safeMint(to, nextId);
        nextId++;
    }

    function _baseURI() internal pure override returns (string memory) {
        return "ipfs://bafy.../";
    }
}
```

### 8.3 ERC-1155: multi-token standard

ERC-1155 lets one contract manage many token types — both fungible and non-fungible — in a single contract. Originally designed for games where you might have 10,000 "sword" tokens and 1 unique "legendary sword" NFT.

```solidity
function balanceOf(address account, uint256 id) external view returns (uint256);
function safeTransferFrom(
    address from,
    address to,
    uint256 id,
    uint256 amount,
    bytes calldata data
) external;
function safeBatchTransferFrom(
    address from,
    address to,
    uint256[] calldata ids,
    uint256[] calldata amounts,
    bytes calldata data
) external;
```

The big win is **batch transfers**: you can send 5 swords + 1 helmet + 10 potions in a single transaction, saving a lot of gas.

### Chapter 8 quiz

1. What does "fungible" mean?
2. Why does ERC-20 have `approve` and `transferFrom`?
3. What is stored at a `tokenURI`?
4. When would you use ERC-1155 instead of ERC-721?

**Answers:** 1) Interchangeable — each unit is identical to every other. 2) So users can authorize contracts (like DEXes) to move tokens on their behalf without sharing private keys. 3) A JSON metadata file describing the NFT (name, image, attributes). 4) When a single application needs many token types, especially a mix of fungible and non-fungible, with batch operations.

---

## Chapter 9: Oracles, Bridges, Rollups

### 9.1 Oracles

Smart contracts cannot call external APIs. If you want to know "what is the ETH/USD price right now?" inside a contract, you need an oracle.

**Oracles** are services that push off-chain data onto the chain. The most widely used is **Chainlink**, which runs a decentralized network of nodes that aggregate data from many sources and publish the median on-chain.

Reading a Chainlink price feed:

```solidity
interface AggregatorV3Interface {
    function latestRoundData() external view returns (
        uint80, int256 answer, uint256, uint256, uint80
    );
}

contract PriceReader {
    AggregatorV3Interface public feed;

    constructor(address _feed) {
        feed = AggregatorV3Interface(_feed);
    }

    function getPrice() external view returns (int256) {
        (, int256 answer, , , ) = feed.latestRoundData();
        return answer;
    }
}
```

**The oracle problem:** your contract is only as trustworthy as your oracle. A compromised oracle can cause a DeFi protocol to execute trades or liquidations at wrong prices. This has caused numerous hacks.

### 9.2 Bridges

Different blockchains are disconnected. To move USDC from Ethereum to Polygon you need a **bridge**. Bridges come in two main flavors:

- **Lock-and-mint** — tokens are locked on chain A, a wrapped version is minted on chain B. Reversed on withdrawal.
- **Burn-and-mint** — tokens are burned on chain A, minted on chain B. Requires a trusted supply authority.

**Bridges have been the single biggest source of hacks in crypto history** — Ronin ($625M), Wormhole ($325M), Nomad ($190M), and more. Cross-chain messaging is extremely hard to secure because you have two security domains and a bridge operator in between.

### 9.3 Rollups and L2s

Ethereum mainnet can process ~15 transactions per second. For a global financial system, this is not enough. **Layer 2** scaling moves execution off-mainnet while still relying on mainnet for security.

**Optimistic rollups** (Arbitrum, Optimism, Base):
- Bundle thousands of transactions off-chain, post the compressed result to L1.
- Assume it is valid by default.
- Allow a 7-day "challenge period" during which anyone can submit a fraud proof.
- Withdrawals to L1 take 7 days (unless you use a third-party bridge).

**ZK rollups** (zkSync, StarkNet, Polygon zkEVM, Scroll):
- Bundle thousands of transactions off-chain, post the result to L1 along with a **zero-knowledge proof** that the execution was valid.
- No challenge period — the proof is verified on-chain immediately.
- Withdrawals are fast, but proof generation is computationally expensive.

Both models inherit Ethereum's security while offering 10-100x cheaper transactions and much higher throughput. This is where most user activity on Ethereum is shifting.

### 9.4 State channels and sidechains (briefly)

- **State channels** (e.g., the Lightning Network on Bitcoin) — two parties open a channel, exchange millions of updates off-chain, only settle the final state on-chain.
- **Sidechains** (e.g., Polygon PoS) — a separate chain with its own consensus, connected to Ethereum via a bridge. Not technically an L2 because they have their own security, not Ethereum's.

### Chapter 9 quiz

1. Why can't a smart contract call an external API directly?
2. What is the difference between an optimistic rollup and a ZK rollup?
3. Why have bridges been the biggest source of hacks?
4. What is a "sidechain"?

**Answers:** 1) Because contract execution must be deterministic across all nodes; external APIs can return different answers at different times. 2) Optimistic rollups assume validity and allow fraud proofs during a 7-day window; ZK rollups post a cryptographic proof of validity with every batch. 3) Because they span two security domains and typically hold enormous value, making them high-value targets with a large attack surface. 4) A separate blockchain with its own consensus that is connected to a main chain via a bridge.

---

## Chapter 10: Security — Common Vulnerabilities

Smart contracts are immutable once deployed. A bug can cost millions of dollars and cannot be patched after the fact (unless you designed upgradeability in). Here are the most common classes of vulnerability.

### 10.1 Reentrancy

The classic. If your contract calls an external contract before updating its own state, the external contract can call back into you and exploit the stale state.

**Vulnerable:**

```solidity
mapping(address => uint256) public balances;

function withdraw() external {
    uint256 amount = balances[msg.sender];
    (bool ok, ) = msg.sender.call{value: amount}("");
    require(ok);
    balances[msg.sender] = 0;
}
```

An attacker contract's `fallback()` calls `withdraw` again before `balances[msg.sender] = 0` runs. It can drain the contract.

**Fix (checks-effects-interactions pattern):**

```solidity
function withdraw() external {
    uint256 amount = balances[msg.sender];
    balances[msg.sender] = 0;
    (bool ok, ) = msg.sender.call{value: amount}("");
    require(ok);
}
```

Or use OpenZeppelin's `ReentrancyGuard`:

```solidity
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract Vault is ReentrancyGuard {
    function withdraw() external nonReentrant { /* ... */ }
}
```

This bug cost Ethereum $60M in the 2016 DAO hack, which led to the Ethereum/Ethereum Classic fork.

### 10.2 Integer overflow / underflow

Before Solidity 0.8, `uint256(0) - 1` wrapped around to `2^256 - 1`. Since 0.8, overflow/underflow automatically reverts, so this class is mostly solved — but if you explicitly use `unchecked { }` blocks for gas optimization, the danger returns.

```solidity
unchecked {
    balance -= amount;
}
```

Only use `unchecked` when you have independently proven the operation cannot overflow.

### 10.3 Front-running / MEV

Transactions sit in the public mempool before being included. A bot can see your pending trade on a DEX, submit the same trade with a higher gas price (getting included first), let your trade execute at a worse price, then sell for a profit. This is called a **sandwich attack**, and the general category is **MEV** (Maximal Extractable Value).

Defenses:
- Set a strict `slippage` limit on trades.
- Use private mempools (Flashbots Protect, MEV-Share).
- For protocols: use commit-reveal schemes so that bids/actions are hidden until committed.

### 10.4 Access control bugs

Forgetting to restrict sensitive functions is surprisingly common:

```solidity
// BUG: anyone can mint!
function mint(address to, uint256 amount) external {
    _mint(to, amount);
}
```

Fix with a modifier:

```solidity
modifier onlyOwner() {
    require(msg.sender == owner, "Not owner");
    _;
}

function mint(address to, uint256 amount) external onlyOwner {
    _mint(to, amount);
}
```

Or use OpenZeppelin's `Ownable` or `AccessControl`.

### 10.5 Price oracle manipulation

If you read a price from a DEX that can be manipulated within a single transaction (via a flash loan), attackers can temporarily skew the price and exploit your contract. Use time-weighted average prices (TWAPs) or Chainlink feeds. Never read spot prices directly.

### 10.6 Signature replay

If you accept signed messages, include a nonce and the contract's address in the signed data. Otherwise a valid signature can be replayed on another chain or another deployment of the contract.

### 10.7 Denial of service via unbounded loops

```solidity
// BUG: if array grows large, this runs out of gas forever
for (uint256 i = 0; i < recipients.length; i++) {
    payable(recipients[i]).transfer(amounts[i]);
}
```

Use pull-based patterns (let each recipient withdraw their own share) instead of pushing to many addresses.

### 10.8 Delegatecall danger

`delegatecall` executes another contract's code in the context of the caller's storage. If the target is attacker-controlled or the storage layouts do not match, it can corrupt state or steal funds. This bug cost Parity wallet users around $30M in 2017 and permanently froze another ~$280M.

### 10.9 Defense in depth

- **Use audited libraries** (OpenZeppelin) for standard functionality.
- **Write tests** with Hardhat or Foundry — unit tests, fuzz tests, invariant tests.
- **Static analysis** — Slither and Mythril catch many classes of bugs automatically.
- **Get audits** from reputable firms before deploying anything holding real value.
- **Deploy on a testnet first** — Sepolia, Holesky.
- **Use bug bounties** — Immunefi is the standard.
- **Consider upgradeability carefully** — proxies let you fix bugs but add their own risks.

### Chapter 10 quiz

1. What is the fix for reentrancy?
2. When is integer overflow still a danger in Solidity 0.8+?
3. What is a sandwich attack?
4. Why is reading a DEX spot price dangerous?

**Answers:** 1) Apply checks-effects-interactions (update state before external calls) or use a reentrancy guard. 2) Inside `unchecked { }` blocks. 3) A MEV attack where a bot inserts transactions before and after yours to profit from the price movement your trade causes. 4) Because it can be manipulated within a single transaction using a flash loan, temporarily skewing the price your contract reads.

---

## What to build next

You now have the conceptual foundation. Pick one of these to deepen your understanding:

1. **Extend the toy blockchain** in Chapter 2 to support signed transactions and a mempool. Add dynamic difficulty adjustment.
2. **Deploy your first contract** to a testnet using Hardhat. Start with the `Counter` contract from Chapter 5. Use a Sepolia faucet to get test ETH.
3. **Write a simple ERC-20** using OpenZeppelin and deploy it. Send some to a friend.
4. **Mint your first NFT** by deploying an ERC-721 contract and uploading metadata to IPFS.
5. **Build a frontend** with viem or ethers.js that reads and writes a contract you deployed.
6. **Read Etherscan daily** — pick random transactions and try to understand what they are doing. This is surprisingly effective.
7. **Do the Ethernaut CTF** — a set of progressively harder smart contract security puzzles maintained by OpenZeppelin. Start at level 1.
8. **Read one audit report** from a firm like Trail of Bits, OpenZeppelin, or ConsenSys Diligence. Learn what auditors actually look for.

---

## Next file to read

**`09-practical-tutorial-5-domains.md`** — "Build 5 Small Blockchain Apps Across Different Domains". That file is the hands-on counterpart to this theory tutorial. You will build a DeFi vault, a supply chain tracker, a medical consent registry, an on-chain certificate issuer, and a simple DAO — with complete Solidity code, deployment scripts, and frontend snippets for each.
