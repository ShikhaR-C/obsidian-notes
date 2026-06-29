# 07 — Where to Implement Blockchain: Platforms and Tools

## What you'll learn
- The major Layer 1 blockchains and what they're good at
- Layer 2 rollups and why most new Ethereum projects build on them
- Enterprise/permissioned platforms (Hyperledger, Corda, Quorum)
- Blockchain-as-a-Service (BaaS) offerings
- Developer platforms (Thirdweb, Moralis, Chainstack)
- How to actually pick one for your use case

---

## 1. The map of the territory

The blockchain landscape in 2026 is large but navigable. Chains fall into roughly four tiers:

```
  +--------------------------------------------+
  |           PUBLIC LAYER 1 CHAINS            |
  |   Ethereum  Bitcoin  Solana  Avalanche     |
  |   BNB  Cardano  Polkadot  Cosmos  Near     |
  |   Aptos  Sui                               |
  +--------------------------------------------+
                      |
  +--------------------------------------------+
  |             LAYER 2 ROLLUPS                |
  |   Arbitrum  Optimism  Base  Polygon zkEVM  |
  |   zkSync  StarkNet  Linea  Scroll          |
  +--------------------------------------------+
                      |
  +--------------------------------------------+
  |        PERMISSIONED / ENTERPRISE           |
  |   Hyperledger Fabric  R3 Corda             |
  |   Hyperledger Besu  Quorum                 |
  +--------------------------------------------+
                      |
  +--------------------------------------------+
  |      BaaS / DEVELOPER INFRASTRUCTURE       |
  |   Alchemy  Infura  QuickNode               |
  |   Thirdweb  Moralis  Chainstack            |
  |   AWS Managed Blockchain  IBM BP           |
  +--------------------------------------------+
```

The public L1s and L2s are where virtually all new permissionless applications live. The permissioned chains are for multi-party enterprise networks. The BaaS layer is the plumbing every developer uses regardless of which chain they target.

## 2. Layer 1 public chains

### Ethereum
- **Language:** Solidity (also Vyper)
- **Consensus:** Proof of Stake (post-2022)
- **TPS:** ~15 at L1, far more via rollups
- **Strengths:** Largest developer ecosystem, most tooling, most battle-tested, most institutional trust, most liquidity
- **Weaknesses:** Expensive and slow at L1 — you generally don't build new consumer apps on L1 anymore

**When to pick it:** Your project is L1-sensitive (cannot tolerate the assumptions of rollups), or you're building pure protocol-level infrastructure.

### Bitcoin
- **Language:** Script (limited), plus Taproot for richer scripts, Ordinals for NFT-like inscriptions, Runes for tokens
- **Consensus:** Proof of Work
- **TPS:** ~7
- **Strengths:** Strongest security budget, most decentralized, most widely held asset, most regulatory clarity (as a commodity in many jurisdictions)
- **Weaknesses:** Minimal smart-contract capabilities; scripting is intentionally limited

**When to pick it:** Digital gold use cases, Lightning Network payments, or Ordinals-based experiments. Not for rich dApps.

### Solana
- **Language:** Rust (and Anchor framework)
- **Consensus:** PoS + Proof of History (a clock primitive)
- **TPS:** 3,000–5,000 real, 65,000 theoretical
- **Strengths:** Very fast, very cheap, large consumer-app ecosystem, strong in memecoins and consumer trading
- **Weaknesses:** Historical downtime incidents, higher hardware requirements (less decentralization), newer tooling

**When to pick it:** High-throughput consumer apps, trading apps, payments, anywhere latency matters.

### Avalanche
- **Language:** Solidity (C-Chain is EVM-compatible), plus native subnets
- **Consensus:** Avalanche consensus (novel probabilistic)
- **TPS:** 4,500+
- **Strengths:** Subnets let you launch application-specific chains; institutional-friendly; good finality
- **Weaknesses:** Smaller DeFi TVL than Ethereum

**When to pick it:** When you want your own sidechain/subnet under a shared security umbrella.

### BNB Chain (BNB Smart Chain)
- **Language:** Solidity (EVM)
- **Consensus:** Proof of Staked Authority
- **TPS:** ~100
- **Strengths:** Cheap, fast, very large user base via Binance ecosystem
- **Weaknesses:** Much more centralized — 21 validators controlled by foundation-aligned parties

**When to pick it:** Mostly for reaching Binance's user base. Not ideal for decentralization-sensitive apps.

### Polygon PoS (sidechain, formerly Matic)
- **Language:** Solidity (EVM)
- **Consensus:** PoS
- **TPS:** ~7,000
- **Strengths:** Cheap, Ethereum-compatible, large ecosystem, many brand integrations (Starbucks, Reddit, Instagram NFTs)
- **Weaknesses:** Technically a sidechain with its own security, not an Ethereum rollup (Polygon is migrating toward Polygon 2.0/zkEVM)

**When to pick it:** Consumer applications where fees must be near-zero and you want EVM tooling.

### Cardano
- **Language:** Plutus (Haskell-based)
- **Consensus:** Ouroboros (PoS)
- **Strengths:** Academic rigor, formal verification culture
- **Weaknesses:** Slower development cycle, smaller ecosystem

### Polkadot and Cosmos
Not single chains but "chains of chains." They let you launch your own sovereign blockchain (a "parachain" on Polkadot, a "zone" on Cosmos) with shared security or interoperability.

- **Polkadot** — parachains share security with a central relay chain. Languages: Rust-based (ink!).
- **Cosmos** — zones are fully sovereign but communicate via IBC (Inter-Blockchain Communication). Languages: Go via Cosmos SDK.

**When to pick them:** You genuinely need your own chain with custom rules, governance, and economics, and want interoperability with others.

### Near, Aptos, Sui
Newer L1s with novel tech:
- **Near** — sharded PoS, focus on UX and account abstraction.
- **Aptos and Sui** — Move language (from the defunct Facebook Diem project), novel object model, high throughput, strong safety guarantees.

**When to pick them:** Experimenting with bleeding-edge languages and models; smaller but growing ecosystems.

## 3. Layer 2 rollups on Ethereum

Most new Ethereum development happens on rollups, not L1. A rollup executes transactions off-chain and posts proofs or data back to Ethereum L1 for security. You get Ethereum's security guarantees plus much lower fees.

### Optimistic rollups
Assume transactions are valid unless someone posts a fraud proof within a challenge window (usually 7 days).

- **Arbitrum** — largest L2 by TVL. Mature, EVM-equivalent.
- **Optimism** — smaller but influential (OP Stack powers many L3s including Base and World Chain).
- **Base** — Coinbase's L2 built on the OP Stack. Fastest growing in 2024-25 due to Coinbase integration.

### Zero-knowledge rollups (zk-rollups)
Prove transaction validity cryptographically — no challenge period needed. Harder to build, faster finality.

- **zkSync Era** — zk-EVM with native account abstraction.
- **StarkNet** — uses STARK proofs and the Cairo language (not EVM-compatible).
- **Polygon zkEVM** — zk-proved EVM chain.
- **Linea** — ConsenSys's zk-EVM.
- **Scroll** — bytecode-level zk-EVM.

**When to pick a rollup over L1:** Almost always, if you're deploying EVM apps in 2026. Only go to L1 directly if your use case demands it.

### Choosing between rollups
Small differences matter:
- **Arbitrum** if you want the largest existing DeFi liquidity.
- **Base** if you want the easiest path to Coinbase users.
- **Optimism** if you align with the Superchain ecosystem.
- **zkSync / Linea / Scroll** if finality speed (minutes instead of 7 days) matters.
- **StarkNet** if you want Cairo's formal guarantees and are willing to learn a new language.

## 4. Enterprise / permissioned platforms

For multi-party B2B networks where public-chain assumptions don't fit.

### Hyperledger Fabric
- **Type:** Permissioned, modular, pluggable consensus
- **Language:** Go, Node.js, Java (chaincode)
- **Governance:** Channel-based privacy, MSP identities
- **Used by:** Walmart's food trust, De Beers' diamond network, IBM deployments
- **Strengths:** Enterprise-grade, fine-grained privacy, established
- **Weaknesses:** Complex, heavy tooling, IBM-leaning ecosystem

### R3 Corda
- **Type:** Permissioned, DLT (no block structure — point-to-point ledger)
- **Language:** Kotlin, Java
- **Used by:** Banks, insurers, trade finance networks
- **Strengths:** Designed for financial services, strong privacy model
- **Weaknesses:** Narrower ecosystem than Fabric

### Hyperledger Besu
- **Type:** Permissioned Ethereum client (runs on public or private networks)
- **Language:** Solidity (EVM)
- **Used by:** Banks wanting EVM tooling in private settings
- **Strengths:** Bridges EVM ecosystem to enterprise needs

### Quorum (now part of ConsenSys)
- **Type:** Permissioned Ethereum fork with privacy enhancements
- **Used by:** JPMorgan's Onyx platform originally built on Quorum

**When to pick permissioned:** Regulated consortiums, sensitive data, known participants. Not for anything public-facing.

## 5. Blockchain-as-a-Service (BaaS)

Managed infrastructure so you don't run nodes yourself.

| Provider | What they offer |
|---|---|
| **Alchemy** | RPC endpoints, SDKs, analytics, NFT API, enhanced data |
| **Infura** (ConsenSys) | RPC endpoints, IPFS gateway, historical queries |
| **QuickNode** | Multi-chain RPC, marketplace of addons |
| **Chainstack** | Managed nodes on many chains, including private |
| **IBM Blockchain Platform** | Managed Hyperledger Fabric |
| **AWS Managed Blockchain** | Managed Fabric + Ethereum (partial) |
| **Oracle Blockchain Platform** | Managed Fabric |
| **Azure Blockchain** | **Discontinued** in 2021 — don't plan around it |

For most teams, Alchemy, Infura, and QuickNode are the three defaults. Pick one based on price, features, and the chains you care about.

## 6. Developer platforms

Higher-level SDKs that abstract away common tasks.

- **Thirdweb** — pre-built contracts, deployment tools, SDK for frontends. Great for rapid prototyping.
- **Moralis** — backend-as-a-service with Web3 auth, NFT data, streaming APIs.
- **OpenZeppelin** — not a platform but *the* reference Solidity contract library. Always use these instead of writing your own ERC-20/ERC-721 from scratch.
- **WalletConnect** — the connect-any-wallet-to-any-dapp protocol. Effectively a standard.
- **RainbowKit** — pre-built wallet connection UI for React apps.
- **wagmi + viem** — the modern TypeScript hook library for Ethereum front-ends. Default choice for new React dApps.
- **Hardhat / Foundry** — development frameworks. Hardhat is JS-based, Foundry is Rust-based and faster.
- **The Graph** — decentralized indexing protocol. Write subgraphs to query chain state via GraphQL.

## 7. Comparison table

| Chain | Lang | Consensus | TPS | Finality | Cost | Ecosystem | Notable use |
|---|---|---|---|---|---|---|---|
| Ethereum L1 | Solidity | PoS | 15 | ~15 min | High | Largest | DeFi, institutional |
| Bitcoin | Script | PoW | 7 | ~60 min | Medium | Largest value | Store of value |
| Solana | Rust | PoH+PoS | 3k–5k | ~2 sec | Very low | Large | Consumer, trading |
| Avalanche | Solidity | Avalanche | 4.5k | ~2 sec | Low | Medium | Subnets, DeFi |
| BNB Chain | Solidity | PoSA | 100 | ~3 sec | Low | Large | Binance ecosystem |
| Polygon PoS | Solidity | PoS | 7k | ~2 sec | Very low | Large | Consumer apps |
| Arbitrum | Solidity | Optimistic | 4k | 7 days (strong) | Low | Largest L2 | DeFi on L2 |
| Optimism | Solidity | Optimistic | 2k | 7 days (strong) | Low | Large | OP Stack chains |
| Base | Solidity | Optimistic | 2k | 7 days (strong) | Low | Growing | Coinbase users |
| zkSync | Solidity | zk-rollup | 2k+ | Minutes | Low | Growing | Fast finality |
| StarkNet | Cairo | zk-rollup | 2k+ | Minutes | Low | Smaller | Novel language |
| Hyperledger Fabric | Go/Node | Pluggable | Thousands | Instant | N/A | Enterprise | Supply chain |
| Corda | Kotlin/Java | Notary | Medium | Instant | N/A | Financial | Banking |

## 8. Decision framework: which chain should you use?

Ask yourself these questions in order:

### Q1: Public or permissioned?
- **Public** → continue to Q2.
- **Permissioned** → go to Hyperledger Fabric (general), Corda (financial), or Besu (if you want EVM tooling).

### Q2: EVM or not?
- **EVM** (you want the largest tooling ecosystem) → continue to Q3.
- **Non-EVM** → Solana (consumer, fast), Near (UX focus), Aptos/Sui (Move language), StarkNet (Cairo/ZK).

### Q3: L1 or L2?
- **L1 only** (you need the full L1 security assumption, or are building protocol infrastructure) → Ethereum L1.
- **L2 is fine** (99% of cases) → continue to Q4.

### Q4: Which L2?
- **Maximum DeFi liquidity** → Arbitrum
- **Coinbase user base** → Base
- **Superchain / OP Stack ecosystem** → Optimism
- **Fast withdrawals and ZK proofs** → zkSync, Linea, Scroll, or Polygon zkEVM
- **Novel cryptography and Cairo** → StarkNet

### Q5: What about non-EVM public chains?
- **Gaming or consumer apps with sub-second UX** → Solana
- **Application-specific chain with shared security** → Avalanche subnets, Polygon CDK, OP Stack, or Arbitrum Orbit
- **Sovereign chain with interoperability** → Cosmos or Polkadot
- **Novel object model and Move** → Aptos or Sui

## 9. Getting started with each (generic pointers)

- **Ethereum / L2s:** Install MetaMask, get testnet ETH from a Sepolia or L2 testnet faucet, deploy with Hardhat or Foundry, interact via wagmi + viem.
- **Solana:** Install Phantom, get devnet SOL from a faucet, write programs in Rust via Anchor, interact via @solana/web3.js.
- **Aptos / Sui:** Install the official wallet, use the Move CLI, deploy modules, interact via the respective TypeScript SDKs.
- **Hyperledger Fabric:** Use the test-network scripts in the Fabric samples repo, write chaincode in Go.
- **Corda:** Use the official Kotlin template repo.

Each ecosystem has extensive official documentation. Always prefer the official docs over third-party tutorials — they're typically well-maintained.

## 10. Common newbie mistakes

- **Picking a chain by hype cycle.** Popular chains change every year. Pick by use case fit.
- **Building for a chain with no users or liquidity.** Launching on a ghost-town L2 and hoping liquidity follows rarely works.
- **Assuming EVM everywhere.** Solana, Move chains, and Cairo all have different mental models.
- **Ignoring tooling maturity.** Brand new L2s may have beautiful marketing but broken debuggers. Tooling maturity is a real cost.
- **Starting on mainnet.** Always build, test, and burn bugs on a testnet first.
- **Trusting "blockchain-as-a-service" to hide the abstraction forever.** Eventually you'll hit the ceiling and need to understand the underlying chain.

## Further reading
- L2BEAT (l2beat.com) — the canonical tracker for L2 decentralization and TVL
- DefiLlama (defillama.com) — TVL and activity across chains
- Messari research reports — institutional-grade chain comparisons
- Each chain's official documentation

## Next file to read
`08-theory-tutorial.md` — the theory tutorial, or if you prefer hands-on: `09-practical-tutorial-5-domains.md`.
