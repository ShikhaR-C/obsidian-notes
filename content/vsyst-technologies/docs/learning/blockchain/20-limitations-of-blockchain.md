# 20 - Limitations of Blockchain

## What You'll Learn

By the end of this file, you will understand:

- The scalability trilemma (decentralization vs security vs scalability) and why it's fundamental
- Real throughput numbers for major chains, and how they compare to Visa and traditional systems
- Why Proof of Work blockchains use so much energy and how Proof of Stake addressed it
- Storage bloat, full node requirements, and why running your own node is getting harder
- The user experience disasters that still plague crypto: keys, gas, wallets
- Why "pseudonymous" is not the same as "anonymous" and what chain analysis can reveal
- The oracle problem and why it matters for every smart contract that touches the real world
- The current state of global blockchain regulation and why it's so uncertain
- Famous smart contract bugs (DAO, Parity, Ronin) and what they teach us
- How 51% attacks work and which chains have been successfully attacked
- What blockchain is categorically NOT suitable for
- Why most "blockchain for X" projects of the last decade didn't need blockchain
- An honest checklist for when you should absolutely not use blockchain

---

## 1. Why You Need This File

The other files in this series make blockchain sound amazing. Censorship-resistant! Global! Trustless! Programmable money! But if you only read those files, you'd think blockchain is always the right tool. It's not. It's usually the wrong tool, honestly, and understanding why is essential to being a competent engineer, investor, or user in this space.

This file is the honest counterweight. Blockchain has real, serious, not-going-away limitations. Some of them will be reduced over time. Some are fundamental trade-offs that can't be eliminated. Learning where these walls are is more valuable than learning the hype.

---

## 2. The Scalability Trilemma

Vitalik Buterin popularized the idea of the **scalability trilemma**: a blockchain can have at most two of these three properties:

- **Decentralization**: many independent, low-resource participants can validate the chain.
- **Security**: the chain resists attacks even from well-funded adversaries.
- **Scalability**: the chain processes many transactions per second.

```
              Decentralization
                    /\
                   /  \
                  /    \
                 / Pick \
                / any  2 \
               /__________\
       Security            Scalability
```

Why is this a trilemma? Because the three properties pull against each other:

- If you want high scalability, you need fewer validators (faster agreement) or more powerful hardware (higher resource requirements), which reduces decentralization.
- If you want strong decentralization, you need to keep node requirements low so anyone can run one, which limits throughput.
- If you want strong security, you need to make attacks expensive, which typically means high resource requirements or large validator sets, which again tension with the other two.

Every blockchain picks its own point on this triangle. Bitcoin picks decentralization and security over scalability. Solana picks scalability and security over decentralization (node requirements are high, validator set is smaller). Permissioned chains pick scalability and security over decentralization by trusting a known set of validators.

### 2.1 The trilemma isn't absolute

Newer designs (rollups, sharding, zero-knowledge proofs) are trying to get better on all three axes. Layer 2 rollups, in particular, inherit the base layer's security and decentralization while adding scalability. But the fundamental trade-off is still there; L2s just move it to a different layer of the stack.

---

## 3. Throughput: The Numbers Are Brutal

Let's put real numbers on the table.

| System                  | Transactions per second (TPS) |
|-------------------------|-------------------------------|
| Bitcoin (L1)            | ~7                            |
| Ethereum (L1)           | ~15                           |
| Litecoin                | ~56                           |
| Cardano                 | ~250                          |
| Avalanche C-chain       | ~4,500                        |
| Solana (theoretical)    | ~65,000                       |
| Solana (sustained)      | ~3,000-5,000                  |
| Ethereum L2 (optimistic)| ~2,000-5,000                  |
| Ethereum L2 (zk)        | ~2,000-9,000                  |
| Visa (average)          | ~1,700                        |
| Visa (peak capacity)    | ~24,000                       |
| Mastercard              | ~5,000                        |
| Alipay (peak)           | ~120,000+                     |

Two things stand out:

1. **Bitcoin and Ethereum L1 are slow**. Seven transactions per second is roughly what a village post office does. Fifteen is not much better. Neither can possibly serve as a global payments system at the base layer.
2. **Even "fast" chains are slow compared to mature centralized systems**. Solana's best-case 3,000-5,000 TPS is impressive but still far below Alipay's daily handling capacity.

The scaling path forward for most chains is **Layer 2**. Instead of making L1 fast, you let L1 be a secure settlement layer and push the actual activity to L2s that post compressed proofs back to L1. This works well in practice, but it introduces complexity, bridge risk, and UX challenges.

### 3.1 Why base layer TPS is hard to increase

To double Bitcoin's TPS, you'd need to double the block size or halve the block time. Doubling the block size means every node has to download and store twice as much data, which prices out smaller operators and centralizes the network. Halving the block time increases orphan rates (blocks that are mined but rejected because a competing block arrived first), which hurts security. There's a reason the Bitcoin community fought for years over a block size increase. It's not a simple dial.

---

## 4. Energy Consumption

### 4.1 The Proof of Work problem

Bitcoin uses around **120-150 TWh per year** of electricity. For context, that's roughly the annual consumption of a mid-sized country like Argentina or Norway. All of this energy goes toward repeatedly guessing hashes to find a valid nonce. From a pure computation standpoint, this work has no other purpose.

Defenders argue this energy "secures" the chain by making attacks expensive. Critics argue there's no reason to burn fossil fuels when equally secure alternatives exist. Both sides have a point.

The story is more nuanced than "Bitcoin boils the oceans":

- A lot of Bitcoin mining uses stranded or renewable energy that would otherwise go unused (hydropower, flared natural gas, excess solar).
- Mining is location-independent, so miners chase the cheapest electricity, which is often renewable.
- But a significant fraction still comes from coal, especially after China's mining ban pushed miners to less-regulated jurisdictions.

Either way, the energy use is real and it's a legitimate objection to PoW.

### 4.2 Proof of Stake response

Ethereum's transition to Proof of Stake (The Merge, September 2022) cut its energy consumption by **~99.95%** overnight. Ethereum now uses roughly the same energy as a medium-sized data center, not a country. This proved that secure, decentralized consensus doesn't require burning terawatts.

Every serious new chain launched since ~2018 uses PoS or something similar. Bitcoin is the major exception, and it's unlikely to ever switch because the cultural and political commitment to PoW is deeply entrenched.

### 4.3 Hardware waste

Beyond energy, PoW mining produces enormous **electronic waste**. ASICs (application-specific chips for mining) have a useful life of 2-4 years before newer, more efficient models render them obsolete. One estimate put Bitcoin's annual e-waste at tens of thousands of metric tons, comparable to the Netherlands' IT waste.

---

## 5. Storage Bloat and Full Node Requirements

Every time someone sends a transaction, it gets added to the chain forever. And every full node has to download and store the entire history. As chains grow, so do the storage requirements.

| Chain     | Approximate full node size (2024) |
|-----------|-----------------------------------|
| Bitcoin   | ~580 GB                           |
| Ethereum  | ~1.2 TB (archive: ~20 TB)         |
| Solana    | >400 TB (archival, impractical)   |
| BSC       | >2 TB                             |

Ethereum archive nodes (which store all historical state) require 20+ TB. Solana effectively requires enterprise-grade hardware to run. Most users don't run full nodes, which means they rely on hosted nodes (Infura, Alchemy, public RPCs) and this re-centralizes the network in practice.

### 5.1 State growth is the real problem

Raw data growth is manageable (disks are cheap). The harder problem is **state growth**: the set of currently-active account balances, smart contract data, etc. Every node has to keep this in memory for fast lookups. Ethereum's state is growing by gigabytes per year, and unlike archive data, there's no easy way to compress or prune it.

Solutions in development include **state expiry** (old state gets archived and must be proved when accessed), **stateless clients** (nodes that don't store state at all, using proofs instead), and **sharding**. These are promising but not yet fully deployed.

### 5.2 Why this matters for decentralization

If running a full node requires $5,000 of hardware and a 1 Gbps internet connection, most people won't. They'll use hosted services. Those services become chokepoints. The network technically has thousands of nodes but effectively relies on a handful of providers. This is a subtle but serious erosion of decentralization.

---

## 6. User Experience Disasters

### 6.1 Key management

If you lose your private key, your funds are gone. Forever. No recovery. No password reset. No customer support. No "I forgot my password" email link.

Estimates suggest **millions of bitcoins** (hundreds of billions of dollars' worth) are permanently lost because people lost their keys or forgot their wallet passwords. There's the famous case of James Howells, a Welsh IT worker who threw out a hard drive containing keys to ~7,500 BTC and has spent years trying to get permission to excavate a landfill.

Key management in current wallets means memorizing or storing a 12-24 word "seed phrase." Anyone who gets this phrase controls your funds. If it's written on paper, it can burn. If it's digital, it can be hacked. If it's in your head, you can forget it or die without telling anyone.

This is not a solved problem. It's slowly improving with **social recovery wallets** (where trusted friends can help you recover), **hardware wallets** (dedicated devices), and **account abstraction** (smart contract wallets with recovery logic), but "easy and safe" is still elusive.

### 6.2 Gas fees

Every Ethereum transaction requires paying **gas**, a fee denominated in ETH. When the network is busy, gas prices spike. During the 2021 peak, a simple token swap could cost $200+ in gas. This pricing model is bizarre to normal users:

- Your fee varies wildly based on congestion at the moment of your transaction.
- A failed transaction still costs gas (you pay even if nothing happens).
- You need ETH to pay gas, even if you're only transacting in other tokens.
- Estimating the right gas limit is error-prone.

L2s have mostly solved the cost issue (fees are often pennies), but the conceptual complexity remains. Explaining gas to a non-technical user is one of the biggest onboarding hurdles in crypto.

### 6.3 Wallet complexity

To use Ethereum, a normal user must:

1. Install a browser extension (MetaMask) or a mobile app.
2. Generate a wallet and safely store the 12-word seed phrase.
3. Understand the difference between accounts, networks, and tokens.
4. Buy ETH from a centralized exchange (requiring KYC).
5. Transfer ETH to their wallet, paying withdrawal fees.
6. Add custom tokens if they want to see them.
7. Connect the wallet to a dapp, reviewing permission requests they don't understand.
8. Approve spending limits (a common phishing vector).
9. Sign transactions, reviewing hex data they can't verify.

Every step has pitfalls. Sign the wrong thing and lose everything. Connect to the wrong site and get drained. Fall for a phishing email and have your seed phrase stolen. There's no recourse.

Compare this to Apple Pay: tap your phone, done. That's the gap that crypto UX has to close, and it hasn't.

---

## 7. Privacy: Pseudonymous, Not Anonymous

A common misconception is that blockchains are anonymous. They are not. They are **pseudonymous**, which is a very different thing.

Your address is not your name, but every transaction to or from it is public forever. Link your address to your real identity (by, say, buying crypto on a KYC'd exchange), and your entire on-chain history is now tied to you. Chain analysis firms like **Chainalysis** and **TRM Labs** make a business out of tracking funds across the blockchain, linking addresses to individuals, and helping law enforcement.

### 7.1 Examples of real deanonymization

- **Silk Road investigators** used blockchain analysis to link Ross Ulbricht to Bitcoin transactions, helping secure his conviction.
- **Bitfinex hackers (2016)**: the stolen BTC sat dormant for years. In 2022, when the couple who held them tried to launder and cash out, chain analysis tracked their movements and led to their arrest.
- **Axie Infinity hack (2022)**: within weeks, investigators linked the stolen funds to North Korea's Lazarus Group.
- **Ordinary users**: many people have had their wallet balances, NFT purchases, and DeFi activity doxxed on Twitter after enemies linked addresses to them.

### 7.2 Privacy tools exist but are limited

- **Monero, Zcash**: cryptocurrencies with built-in privacy features. They work but have smaller ecosystems and are increasingly delisted from exchanges under regulatory pressure.
- **Mixers (Tornado Cash)**: services that break the link between source and destination addresses. Tornado Cash was sanctioned by the US Treasury in 2022 and its developer arrested.
- **Zero-knowledge proofs**: a promising technology for selective privacy. Still maturing.

For most users on most chains, **assume nothing you do on-chain is private**. If you need privacy, you need specialized tools and you need to use them very carefully.

---

## 8. The Oracle Problem

A blockchain knows what's happened on the blockchain. It knows nothing about the outside world. If you want a smart contract to depend on real-world data (stock prices, weather, sports results, election outcomes), someone has to **feed** that data to the contract. This is the job of an **oracle**.

The oracle problem is: **how can you trust the oracle?** If the oracle lies, the smart contract happily executes on the lie. "Garbage in, garbage out" has catastrophic consequences when the smart contract can't be undone.

### 8.1 Real oracle attacks

- **bZx (2020)**: attackers manipulated a price oracle (using flash loans to temporarily distort the price on an exchange) and drained ~$1 million from the bZx lending protocol. This was repeated several times.
- **Mango Markets (2022)**: Avraham Eisenberg manipulated the price of the MNGO token via self-trading, then used the inflated token as collateral to drain $114 million from the protocol. He was later charged.
- **PancakeBunny (2021)**: a price oracle manipulation attack caused $45 million in losses.

These weren't bugs in the smart contracts themselves. They were bugs in the oracle design: the smart contracts trusted a data source that could be manipulated.

### 8.2 Oracle solutions

- **Chainlink**: aggregates prices from many sources via many independent nodes, making manipulation expensive.
- **Time-weighted average prices (TWAP)**: use the average price over many blocks to resist short-term manipulation.
- **Optimistic oracles**: anyone can propose an answer; anyone can dispute it; disputes are resolved by a slower, more trusted mechanism.

None of these fully solve the problem. Oracles are still a significant source of risk in DeFi, and every smart contract that depends on off-chain data is, in some sense, only as secure as its oracle.

---

## 9. Regulatory Uncertainty

Blockchain regulation is a patchwork quilt. Different countries have radically different approaches, and the rules keep changing. A brief world tour:

- **United States**: the SEC and CFTC have been fighting over jurisdiction for years. The SEC has taken an aggressive enforcement stance, suing major exchanges (Coinbase, Binance, Kraken) and ruling that many tokens are unregistered securities. 2024 saw approval of spot Bitcoin and Ethereum ETFs, which was a big step toward institutional legitimacy.
- **European Union**: the **MiCA** (Markets in Crypto-Assets) regulation passed in 2023 and provides a comprehensive framework. It's considered more crypto-friendly than the US but still strict.
- **China**: banned cryptocurrency trading and mining in 2021. Hong Kong, however, has been more open.
- **El Salvador**: made Bitcoin legal tender in 2021. The experiment has had mixed results.
- **United Kingdom, Switzerland, Singapore, UAE, Japan**: generally have more favorable regimes with clearer rules.
- **India**: has flip-flopped multiple times; currently heavily taxed but not banned.
- **Russia**: has complicated rules; legal to own but not legal to use for payments.

### 9.1 Why regulatory uncertainty is a problem

If you run a blockchain business, you don't know what's allowed tomorrow. Protocols that looked safe in 2020 may be targets in 2024. Tokens that were "utility tokens" may be reclassified as securities. Developers of privacy tools (Tornado Cash) have been arrested for writing open-source code. Exchanges have been shut down or pushed out of jurisdictions with days of notice.

This chilling effect is real. It slows innovation, pushes developers to pseudonymity, and concentrates activity in the friendlier jurisdictions. It also means many "legitimate use cases" are legally unclear.

### 9.2 The tax complexity

In the US, every crypto-to-crypto trade is a taxable event. Swap ETH for USDC and you owe capital gains on the ETH. If you do 500 trades a year, you have 500 events to track. Most people don't and are technically in violation. Software helps but it's ugly, and the IRS has been increasing enforcement.

---

## 10. Smart Contract Bugs: Immutability Cuts Both Ways

Smart contracts are software. Software has bugs. When the bug is in a web app, you push a fix. When the bug is in a smart contract holding hundreds of millions of dollars, you... might not be able to fix it, and an attacker might drain everything before you notice.

### 10.1 Famous hacks

**The DAO (2016)**: The Decentralized Autonomous Organization was a crowd-funded investment vehicle on Ethereum. It had a reentrancy bug. Attackers exploited it and drained ~$60 million. To recover the funds, Ethereum hard-forked, splitting the community. Ethereum Classic is the remnant of those who refused to fork. This was blockchain's first big "code is law... unless it's really bad" moment.

**Parity Multi-sig (2017, twice)**: First, a bug let an attacker drain ~$30 million from wallets using a popular multi-sig library. A few months later, a user accidentally triggered a `suicide` function on the library contract itself, **permanently freezing ~$300 million** in ETH belonging to other wallets that depended on it. No attacker, just a single accidental command that turned half a billion dollars into a statue.

**Ronin Bridge (2022)**: The bridge used by the Axie Infinity game had only 9 validators, 5 of which were required to sign. Attackers (North Korea's Lazarus Group) compromised 5 of the validators and drained **$625 million**. Nobody noticed for six days. This is the largest single crypto hack to date.

**Poly Network (2021)**: an attacker exploited a flaw in a cross-chain bridge and drained **$610 million**. Strangely, the attacker later returned most of the funds, claiming they'd "done it for the lulz."

**Wormhole (2022)**: another bridge hack, **$325 million** stolen. The backers (Jump Crypto) bailed out the protocol.

**Euler Finance (2023)**: a flash loan attack exploited a donation function, draining **$197 million**. Unusually, the attacker eventually returned the funds after extended negotiation.

**Total DeFi losses to date**: several tens of billions of dollars across hundreds of incidents.

### 10.2 Why smart contracts are so hard to get right

- **Immutability**: you can't easily patch a deployed contract. Many projects use "upgradable proxy" patterns, but those introduce their own vulnerabilities and central points of control.
- **Adversarial environment**: every contract is a bounty. If a $100M bug exists, somebody will find it.
- **Composability makes reasoning hard**: your contract might be called by another contract you didn't anticipate, in a state you didn't expect. Flash loans let attackers temporarily control enormous amounts of capital to manipulate your contract.
- **Tooling is immature**: formal verification exists but is hard to apply; testing can't cover all edge cases; even audited contracts get hacked.

The lesson: **write simple contracts, audit them thoroughly, minimize their scope, and assume they'll be attacked**. Most developers don't do this, which is why losses keep mounting.

---

## 11. 51% Attacks

If a single entity controls more than half the hashpower (on PoW) or more than half the stake (on PoS), they can rewrite recent history. They can double-spend, censor, and reorganize blocks. This is the **51% attack**.

### 11.1 Chains that have been successfully attacked

- **Ethereum Classic (2019, 2020)**: multiple 51% attacks, resulting in double-spends worth millions of dollars. ETC survives but is considered much less secure.
- **Bitcoin Gold (2018, 2020)**: 51% attacks causing double-spends on exchanges.
- **Vertcoin (2018)**: 51% attacks.
- **Grin, Feathercoin, Verge**: various smaller chains have been hit.

Bitcoin itself has never suffered a successful 51% attack. The cost to mount one is estimated at billions of dollars of hardware plus ongoing electricity, and you'd probably destroy the value of your own holdings in the process. But for smaller PoW chains, attacks are cheap and common. You can literally rent hashpower from services like NiceHash and attack small chains for a few thousand dollars.

### 11.2 PoS attack model

In Proof of Stake, a 51% attack would require acquiring 51% of all staked tokens, then slashing them intentionally. This is extremely expensive at scale (for Ethereum, it would cost tens of billions of dollars and destroy most of what you just bought). PoS is also generally considered more resistant to attacks than PoW because the attacker cannot "sell the hardware" afterward; their attack capital is tied to the chain they're attacking.

### 11.3 The security-by-market-cap problem

A chain's security scales roughly with its market cap. Small chains are cheap to attack. This creates a barrier for new chains: until they become valuable, they're insecure, but until they're secure, they shouldn't be trusted with value. One mitigation is to merge-mine or share security with a larger chain, or (for new PoS chains) to bootstrap with a restricted validator set and gradually decentralize.

---

## 12. What Blockchain is NOT Suitable For

Let's be blunt. Blockchains are a bad fit for:

- **High-throughput data**: logging, analytics, telemetry. Use a time-series database.
- **Large files**: images, videos, documents. Use object storage (S3) or IPFS.
- **Private data**: health records, personal information, trade secrets. Use encrypted databases.
- **Data that legitimately needs to change**: records that must comply with the "right to be forgotten" (GDPR). Blockchain's immutability directly conflicts with deletion rights.
- **Low-latency applications**: real-time games, live trading. Blockchain confirmation times are too slow.
- **Applications where one party is the obvious trusted operator**: internal company systems, customer CRMs. A regular database is simpler.
- **Situations where the users won't tolerate seed phrases and gas fees**: most consumer apps.
- **Decisions that require human judgment**: dispute resolution, content moderation. Smart contracts can't reason.
- **Anything requiring universal consensus on a rapidly changing state**: real-time bids, chat messages, sensor data.

If your idea is on this list, do not use blockchain. You'll waste time, money, and user patience for no benefit.

---

## 13. Why Many "Blockchain for X" Projects Didn't Need Blockchain

The 2017-2021 era saw an explosion of "blockchain for [industry]" projects: blockchain for supply chain, blockchain for voting, blockchain for healthcare, blockchain for land registry, blockchain for identity, blockchain for charity, blockchain for music royalties. Most of these failed. Some reasons:

- **They had a trusted central party anyway**: a blockchain-based supply chain run by Walmart is just Walmart's database with extra steps. If you trust Walmart, use Walmart's database.
- **The bottleneck was not trust, it was data entry**: a blockchain-based food traceability system can't stop a farmer from lying about whether the tomatoes are organic. The problem isn't the database; it's the real-world input.
- **The cost-benefit didn't add up**: saving $0.50 on a form by using a blockchain that costs $2 per transaction is not a business.
- **Users didn't want it**: decentralized alternatives to Twitter, Facebook, and YouTube have never gained traction at scale because users prefer the centralized versions for performance and UX.
- **Regulators killed it**: projects that tried to "disrupt" regulated industries (banking, securities, real estate) ran into enforcement.
- **The founders didn't understand the technology**: they saw a buzzword and wanted to attach it to their product.

A useful heuristic: if removing the word "blockchain" from the pitch doesn't change the value proposition, the project doesn't need a blockchain.

---

## 14. An Honest Checklist: When NOT to Use Blockchain

Answer "yes" to any of these, and you probably shouldn't use blockchain:

- [ ] Is there a single trusted operator who can run a database?
- [ ] Do you need to store large files or high-throughput data?
- [ ] Do you need the data to be private by default?
- [ ] Do you need to modify or delete records after the fact?
- [ ] Do you need sub-second latency?
- [ ] Are your users non-technical and allergic to seed phrases?
- [ ] Is regulatory clarity essential for your business?
- [ ] Does your use case require human judgment or discretion?
- [ ] Is the only value-add "decentralization" with no concrete benefit from it?
- [ ] Would a regular database be 10x cheaper and faster?

If you answered "yes" to three or more, the right move is usually to build with a traditional stack. You can still use blockchain rails for a specific piece (e.g., a settlement or verification step) without forcing the entire application onto it.

---

## 15. A Fair Summary

Blockchain is a narrow tool that happens to be uniquely good at a narrow set of problems: trust-minimized settlement, censorship resistance, and verifiable digital scarcity. In that narrow niche, nothing else competes. Outside that niche, it's a bad database.

The honest posture is:

- **Respect the capability**: when blockchain's unique properties matter, they really matter.
- **Respect the limits**: most problems don't need those properties.
- **Don't reach for blockchain as a default**: reach for it when you've confirmed the alternatives don't work.
- **Accept the trade-offs**: slower, more expensive, harder to use, more exposed to bugs. You take those in exchange for censorship resistance and trust minimization.
- **Assume bugs**: if you build a smart contract, assume someone will try to break it, and design accordingly.
- **Assume nothing is private**: unless you're using privacy-preserving tech explicitly.
- **Assume regulation will change**: build for adaptability.

The people who do best in crypto, whether as builders, investors, or users, are the ones who hold both the strengths and the limitations in mind at the same time. The boosters and the skeptics are both wrong in different ways. The truth is in the middle: blockchain is a real, useful technology for specific problems, and a bad fit for everything else.

---

## Further Reading

- **"The Scalability Trilemma"** by Vitalik Buterin: the canonical explanation.
- **"Crypto theses"** by Messari (annual report): sober analysis of the industry's state.
- **Chainalysis annual crime report**: real data on how crypto is used and misused.
- **Rekt.news**: ongoing catalog of DeFi hacks and post-mortems. Essential reading for any builder.
- **"The Tyranny of Structurelessness"** by Jo Freeman: a 1970s essay about leaderless movements. Uncannily relevant to DAO governance failures.
- **"Blockchain, the Amazing Solution for Almost Nothing"** by Jesse Frederik: the strongest skeptical case, written accessibly.
- **"Bullish Case for Bitcoin"** by Vijay Boyapati: a counterweight from the other side.
- **Formal audits of major DeFi protocols**: publicly available, educational for understanding what goes wrong.

---

## Next File to Read

You've finished the foundational series (01, 02, 05, 20). From here, good directions include: a deeper file on smart contracts and the EVM, a file on stablecoins and DeFi primitives, a file on wallets and self-custody in practice, a file on zero-knowledge proofs and privacy, or a file on the regulatory landscape. Pick whichever aligns with what you want to build or understand next. Whatever you pick, keep this file's lessons in mind: blockchain is powerful in its niche and unhelpful outside it, and the best practitioners know the difference.
