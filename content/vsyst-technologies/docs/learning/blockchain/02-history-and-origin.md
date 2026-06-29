# 02 — How Blockchain Originated

## What you'll learn
- The 30-year cryptographic lineage that made blockchain possible
- Why the 2008 financial crisis was the ignition moment
- What Satoshi Nakamoto actually invented (and what they didn't)
- How Ethereum turned a payment network into a world computer
- The rough post-2015 timeline: DAO hack, ICOs, DeFi, NFTs, L2s, PoS merge

---

## 1. Blockchain is older than you think

A common myth is that Satoshi Nakamoto invented blockchain from scratch in 2008. The truth is that every technical ingredient of Bitcoin had been worked on for decades. Satoshi's breakthrough was in *assembly*, not invention.

Here is the full chain of influences:

### 1979 — Merkle trees (Ralph Merkle)
Merkle's PhD work gave us a way to summarize a large collection of data with a single hash, while still letting you prove any individual item was in the set. Every modern blockchain uses Merkle trees to compress transaction lists.

### 1982 — Byzantine Generals Problem (Lamport, Shostak, Pease)
A seminal paper asking: how can distributed processes agree on a value if some of them might lie? The formal framing of "consensus under malicious actors" that all blockchains eventually had to solve.

### 1982 — Digital cash, blind signatures (David Chaum)
Chaum proposed **DigiCash**, the first serious electronic cash system, based on cryptographic blind signatures. DigiCash was centralized (a bank issued the tokens) and eventually went bankrupt, but it planted the flag: *digital money with cryptographic guarantees can exist*.

### 1991 — Timestamped document chains (Stuart Haber and W. Scott Stornetta)
Their paper "How to Time-Stamp a Digital Document" is arguably the earliest direct ancestor of Bitcoin's design. They proposed linking documents via cryptographic hashes so that altering any one would invalidate the chain. Satoshi's whitepaper explicitly cites them.

### 1997 — Hashcash (Adam Back)
An anti-spam proof-of-work scheme: to send email, your computer had to compute a hash with certain properties, imposing a small cost. Useless for spammers, negligible for individuals. Bitcoin uses essentially the same mechanism for mining.

### 1998 — b-money (Wei Dai)
Wei Dai described a distributed electronic cash system with most of the modern blockchain properties: a distributed ledger, proof-of-work for issuance, and contracts enforceable by the network. It was a proposal, not an implementation.

### 2005 — Bit Gold (Nick Szabo)
Nick Szabo — who also coined the term *smart contract* back in 1994 — proposed "Bit Gold," a decentralized digital currency where PoW puzzles would produce chain-linked tokens. He never deployed it, but the resemblance to Bitcoin is strong enough that many people suspected Szabo *was* Satoshi (he denies it).

**Takeaway:** By 2007, all the pieces existed. What nobody had done was *wire them together into a working system* that solved the final missing problem — **double-spending without a trusted central issuer**.

## 2. The 2008 catalyst

In September 2008, Lehman Brothers collapsed. Governments bailed out major banks. Public trust in the financial system hit a generational low. The question "why does money have to flow through institutions we can't audit?" was suddenly not academic.

On **October 31, 2008**, an unknown author calling themselves **Satoshi Nakamoto** posted a nine-page paper to a cryptography mailing list:

> *Bitcoin: A Peer-to-Peer Electronic Cash System*

The paper was not long. It was not hype. It was a calm, technical proposal for an electronic cash system that would work without a trusted intermediary. The abstract is the clearest two paragraphs ever written about blockchain, and worth reading in full at least once.

### What Satoshi actually solved
Prior digital-cash proposals all broke on the **double-spend problem**: how do you stop someone from spending the same digital dollar twice? Traditional solutions required a central server. Satoshi's answer:

1. Broadcast every transaction to the whole network.
2. Order transactions into blocks.
3. Chain blocks together via hashes.
4. Make block production costly (proof-of-work).
5. Define "the real history" as the chain with the most accumulated work.

An attacker who wanted to double-spend would have to out-compute every honest miner combined, not for a moment, but for the length of the chain. As long as more than half of mining power is honest, the honest chain wins. That was the *Nakamoto consensus*.

### January 3, 2009 — The Genesis Block
Satoshi mined Bitcoin block 0 with a coded message in its coinbase transaction:

> *"The Times 03/Jan/2009 Chancellor on brink of second bailout for banks."*

That line served two purposes: it proved the block was not pre-mined before that date, and it bolted the project's mission statement into its earliest byte. On January 12, 2009, Hal Finney received the first Bitcoin transaction from Satoshi — 10 BTC.

## 3. Who is Satoshi Nakamoto?

Nobody knows. Satoshi communicated only in text, stayed purely technical, never cashed out the ~1 million BTC they mined, and stepped away from the project in December 2010 with a final message: *"I've moved on to other things."*

Candidates proposed over the years include Nick Szabo, Hal Finney, Dorian Nakamoto (a coincidence of names), Craig Wright (self-proclaimed, repeatedly debunked), and various teams. The honest answer in 2026 is that Satoshi's identity is still unknown — and arguably that's a feature, not a bug, because it keeps the network from having a single human figurehead.

## 4. The early Bitcoin years (2009–2012)

- **2009.** Bitcoin worth essentially zero. Mined on laptop CPUs. Mostly a cryptography-enthusiast toy.
- **2010.** Laszlo Hanyecz pays 10,000 BTC for two pizzas on May 22 — now celebrated as "Bitcoin Pizza Day" and worth billions in any later year.
- **2010.** The first Bitcoin exchange (Mt. Gox) launches.
- **2011.** Bitcoin reaches $1 in February. Hits $30 by June. First crash follows.
- **2012.** First halving (mining rewards cut from 50 to 25 BTC per block). Silk Road notoriety introduces Bitcoin to the mainstream press — for worse, not better.

## 5. Ethereum: from currency to computer (2013–2015)

In late 2013, a 19-year-old Russian-Canadian programmer named **Vitalik Buterin** wrote a whitepaper proposing something more ambitious than Bitcoin. His thesis: Bitcoin's scripting language was intentionally limited, and a richer execution environment on top of a blockchain would let people build arbitrary applications, not just payment systems.

He called it **Ethereum**.

A few co-founders joined: Gavin Wood (who wrote the Yellow Paper — the formal spec — and the Solidity language), Joseph Lubin, Charles Hoskinson, and others. A July 2014 crowd sale raised ~$18 million in Bitcoin, and Ethereum's mainnet went live **July 30, 2015**.

### What Ethereum added
| Concept | Bitcoin | Ethereum |
|---|---|---|
| Primary use | Digital cash | General computation on-chain |
| Programmability | Very limited scripts | Turing-complete smart contracts |
| Native currency | BTC | ETH (used to pay for computation — "gas") |
| Account model | UTXO | Account-based with balances |
| Block time | ~10 min | ~12 sec |
| Key innovation | Nakamoto consensus | The Ethereum Virtual Machine (EVM) |

The EVM is what makes Ethereum special. It is a deterministic virtual machine that every node runs in lockstep. If you deploy a program ("smart contract") to the EVM, every node executes every line of it the same way, with every state change recorded on-chain. Suddenly, you could put entire applications — not just payments — on a blockchain.

## 6. The DAO hack and the Ethereum fork (2016)

In April 2016, a decentralized investment fund called **The DAO** launched on Ethereum. It raised ~$150 million in ETH (about 14% of all ETH in existence at the time). In June, an attacker exploited a reentrancy bug in its smart contract and drained ~$60 million.

This forced a crisis-level question: *should the Ethereum community roll back the chain to undo the theft?* "Immutable" meant never rolling back. But losing 14% of the supply to one bug would kill the project.

The community fractured. Most chose to hard-fork, creating a new chain where the hack was reversed. A minority refused, insisting "the code is law," and continued running the original chain. That minority chain is **Ethereum Classic (ETC)**; the majority chain kept the **ETH** name.

It was the first real test of blockchain governance, and the lesson stuck: *immutability is a social agreement, not a law of physics*.

## 7. The ICO boom (2017)

Ethereum's ERC-20 token standard made it trivial to launch a new token — a few dozen lines of Solidity. Starting in 2017, projects raised billions of dollars selling tokens to the public in **Initial Coin Offerings (ICOs)**. Many were legitimate. Most were not. A large number raised enormous sums with little more than a whitepaper, then delivered nothing.

The SEC began treating many ICOs as unregistered securities offerings. By mid-2018 the bubble had popped, and the regulatory cleanup continues to this day.

Silver lining: ICO mania funded a lot of the infrastructure — wallets, dev tools, L2 research, early DeFi — that made the next cycle real.

## 8. DeFi Summer (2020)

By 2020, a cluster of Ethereum applications had matured enough to offer an entire parallel financial stack:

- **Uniswap** — automated decentralized exchange, no order books
- **Aave, Compound** — on-chain lending and borrowing
- **MakerDAO** — issues DAI, a decentralized stablecoin
- **Yearn** — automated yield aggregation
- **Curve** — stablecoin swaps with low slippage

Summer 2020 saw **yield farming** explode, with users hopping between protocols chasing token rewards. Ethereum TVL (total value locked) jumped from under $1 billion in early 2020 to over $15 billion by year-end. For the first time, serious dollars flowed through purely smart-contract-based finance.

DeFi's real legacy isn't yield farming mania — it's that these protocols are still running, composable, and collectively process billions of dollars per day in 2026.

## 9. NFTs (2021)

Non-Fungible Tokens (ERC-721) had existed since 2017 (CryptoKitties, anyone?), but 2021 was the year they went mainstream. CryptoPunks, Bored Apes, generative art, Beeple's $69 million Christie's auction, the NBA Top Shot boom.

Most of the hype was speculative, and the floor prices of most collections collapsed by 2022. But the technical primitive — **verifiable ownership of a unique digital item** — is durable and has real uses in ticketing, credentials, memberships, in-game assets, and identity.

## 10. The scalability crisis and the L2 era (2020–present)

As DeFi and NFTs exploded, Ethereum gas fees soared. Sending a simple transaction sometimes cost $50+. Clearly, a single L1 chain couldn't serve the world. Two scaling philosophies emerged:

### Alternative L1s
New "Ethereum killers" — **Solana, Avalanche, BNB Chain, Polygon PoS, Near, Aptos, Sui** — with higher throughput and lower fees. Some made architectural tradeoffs (less decentralization); some introduced genuinely new tech (Solana's Proof-of-History, Move language).

### Layer 2 rollups on Ethereum
Rather than abandon Ethereum's security, rollups batch thousands of transactions off-chain and post compressed proofs back to L1. Two flavors:

- **Optimistic rollups** — **Arbitrum, Optimism, Base** — assume batches are valid unless challenged within a window.
- **Zero-knowledge rollups** — **zkSync, StarkNet, Polygon zkEVM, Linea, Scroll** — prove correctness with cryptographic proofs.

By 2026, most Ethereum users never touch L1 directly. They transact on L2s where fees are cents and UX is snappy, while inheriting Ethereum's security for settlement.

## 11. The Merge: Ethereum moves to Proof of Stake (September 15, 2022)

Ethereum had planned since day one to move from Proof-of-Work to Proof-of-Stake. After years of research and a multi-year parallel "Beacon Chain," the main chain merged with the new consensus layer on **September 15, 2022**.

Effects:
- Energy use dropped ~99.95% overnight
- Issuance of new ETH fell sharply
- Validators (not miners) now secure the network
- The door opened for scalability upgrades like Danksharding

The Merge was one of the most ambitious live software migrations ever attempted. It went smoothly. If you had any doubt that blockchain engineering could handle transitions of massive consequence on mainnet, the Merge answered it.

## 12. 2022–2023: the reckoning

A bad stretch for the industry:
- **Terra/Luna collapse (May 2022)** — an algorithmic stablecoin design failed catastrophically, wiping out ~$40 billion.
- **Celsius, Voyager, BlockFi bankruptcies** — centralized lenders that borrowed short and lent long.
- **FTX implosion (November 2022)** — one of the largest exchanges committed massive fraud. Sam Bankman-Fried convicted.
- **Regulatory crackdown** — the SEC sued Binance, Coinbase, and others.

Crypto's reputation took a well-deserved hit. But importantly, the underlying blockchains kept running. Bitcoin made blocks. Ethereum made blocks. DeFi protocols processed transactions. The protocol layer survived the institutional layer's scandals.

## 13. 2024–2026: tokenization and real-world assets

After the cleanup, attention shifted to concrete, less speculative use cases:
- **Stablecoins** — now carrying trillions in annual volume. USDC, USDT, PYUSD. Real B2B payment rails.
- **Tokenized Treasuries** — BlackRock's BUIDL, Franklin Templeton's BENJI, others. Traditional finance discovering that on-chain Treasury funds settle faster and cheaper.
- **Real-World Asset (RWA)** tokenization — private credit, real estate, commodities.
- **Account abstraction (ERC-4337)** — making wallets work more like normal apps: no seed phrases, social recovery, gasless UX.
- **Zero-knowledge everything** — ZK proofs used for scaling, privacy, identity, and compute.

Crypto's center of gravity shifted from "will we change everything" to "where does this actually work, and at what scale."

## 14. Timeline of key milestones

| Year | Event |
|---|---|
| 1979 | Merkle trees published |
| 1982 | Byzantine Generals paper; Chaum's blind signatures |
| 1991 | Haber & Stornetta timestamp chains |
| 1997 | Hashcash (Adam Back) |
| 1998 | b-money (Wei Dai) |
| 2005 | Bit Gold (Nick Szabo) |
| Oct 2008 | Bitcoin whitepaper published |
| Jan 2009 | Bitcoin genesis block |
| 2010 | First BTC transaction for physical goods (the pizzas) |
| 2013 | Ethereum whitepaper by Vitalik Buterin |
| 2014 | Ethereum crowd sale |
| Jul 2015 | Ethereum mainnet launches |
| Jun 2016 | The DAO hack; Ethereum/Classic fork |
| 2017 | ICO boom; ERC-20 standardization |
| 2018 | ICO crash; "crypto winter" |
| 2020 | DeFi Summer; stablecoin adoption accelerates |
| 2021 | NFT mania; major L2s launch |
| May 2022 | Terra/Luna collapse |
| Sep 2022 | Ethereum Merge to PoS |
| Nov 2022 | FTX collapses |
| 2023 | BTC/ETH spot ETFs approved (US) |
| 2024 | BlackRock BUIDL; institutional RWA adoption |
| 2025–26 | Stablecoins become mainstream B2B rails; account abstraction goes live; ZK scales |

## 15. What this history teaches a newbie

1. **Blockchain is not magic.** Every "innovation" has a long prior-art lineage. Respect the cryptography that took 30 years to mature.
2. **Satoshi's insight was synthesis.** Combining PoW + Merkle trees + P2P gossip + the longest-chain rule produced something nobody had built before.
3. **Scalability is the eternal crisis.** Every boom overwhelmed the base layer; every response — alt L1s, rollups, sharding — is a scalability answer.
4. **Blockchains survive their scandals.** DAO, Mt. Gox, FTX, Terra — the ecosystem lost billions and kept running. That tells you something about the protocol layer's robustness, and something different about the application layer's.
5. **The cycles are real.** Hype, crash, build, repeat. The people who came out of each crash strongest were the ones who kept building during the winter.

## Further reading
- Satoshi Nakamoto, "Bitcoin: A Peer-to-Peer Electronic Cash System" (2008)
- Vitalik Buterin, "Ethereum Whitepaper" (2013)
- Nathaniel Popper, *Digital Gold* — the early-Bitcoin history as journalism
- Camila Russo, *The Infinite Machine* — Ethereum's origin story

## Next file to read
`05-what-makes-blockchain-unique.md` — the specific properties that make blockchains different from traditional databases, and when they genuinely matter.
