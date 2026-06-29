# 04 — Who Already Uses Blockchain

## What you'll learn
- The major industries where blockchain is in real production today
- Specific companies, what they built, and (where it's failed) why
- A reality check on "enterprise blockchain" vs. public-chain adoption
- A reference table of notable deployments you can cite

---

## 1. The honest framing

"Who uses blockchain?" has two answers, and they point in different directions:

1. **At the protocol level:** billions of dollars of real value flow daily through Bitcoin, Ethereum, and a handful of other public chains. Stablecoins alone move trillions per year. This is not toy volume.
2. **At the enterprise level:** many famous "blockchain transformation" projects of 2018–2022 were quietly shelved. Hype cleared out a generation of bad projects; the ones still standing are more specific.

Both answers are true at the same time. This file lists who's actually using blockchain, in which category, and how seriously.

## 2. Finance and payments

This is the biggest and most mature category. It's also where public-chain adoption is clearly winning.

### Stablecoins — the quiet giant
- **Circle (USDC)** — fiat-backed USD stablecoin, the most regulated major issuer. Billions outstanding.
- **Tether (USDT)** — by volume the largest stablecoin. Hundreds of billions in daily transfer volume.
- **PayPal (PYUSD)** — PayPal launched its own stablecoin in 2023, issued by Paxos.
- **DAI / MakerDAO** — decentralized stablecoin backed by crypto collateral and RWAs.

Annual stablecoin transfer volume now rivals or exceeds major payment networks. This is not speculation — this is B2B settlement, cross-border payments, and on-chain treasury management.

### Tokenized funds and RWAs
- **BlackRock BUIDL** — BlackRock's tokenized Treasury fund on Ethereum, launched 2024. Institutional-grade, real money.
- **Franklin Templeton BENJI** — tokenized money-market fund.
- **Fidelity** — tokenization experiments and institutional custody.
- **Ondo Finance** — tokenizes US Treasuries for on-chain access.

### Bank-operated infrastructure
- **JPMorgan Onyx / JPM Coin** — wholesale payment rail between JPMorgan accounts, processed billions in volume. Permissioned blockchain.
- **Partior** — Singapore-based interbank settlement platform backed by DBS, Standard Chartered, Temasek, JPMorgan.
- **Visa USDC settlement** — Visa settles merchant payments in USDC on Ethereum and Solana for some issuers.
- **Mastercard** — crypto-to-fiat settlement experiments.

### Exchanges and brokers (centralized)
- **Coinbase** — publicly traded US exchange, regulated, tens of millions of users.
- **Binance** — largest global exchange by volume.
- **Kraken, Bitstamp, Gemini** — regulated US/EU exchanges.
- **Robinhood, Cash App, Revolut, PayPal** — mainstream apps with crypto buy/sell.

## 3. Supply chain and provenance

This is the category that promised the most in 2018 and delivered the least. Some things did work; many didn't.

### What worked
- **IBM Food Trust** — Walmart famously used it to track leafy greens after E. coli outbreaks, reducing traceback time from days to seconds. Nestlé, Dole, and others joined.
- **De Beers Tracr** — tracks rough diamonds from mine to cutter to polisher, reducing conflict-diamond risk. Fully in production.
- **VeChain** — public chain used by luxury goods and wine authentication at scale.
- **Everledger** — provenance for diamonds, wine, art.

### What didn't
- **Maersk TradeLens** (joint venture with IBM) — shipping logistics blockchain. Shut down in 2022 after failing to attract enough carriers. Other shipping lines refused to join a platform partially controlled by a competitor.
- **Many IBM Hyperledger pilots** in consumer goods, pharma, and retail were discreetly wound down.

### The lesson
Supply-chain blockchain works when the participants share strong incentives and no single party dominates. It fails when one company tries to own the network and expects its competitors to cheerfully join. The network effect cuts both ways.

## 4. Healthcare

Progress is slow but real in narrow slices.

- **MediLedger** — pharmaceutical supply-chain verification, live in production, used by US drug distributors to satisfy DSCSA regulations (track-and-trace for controlled pharmaceuticals).
- **Chronicled** — similar pharma compliance network.
- **Akiri** — healthcare data-sharing network using DLT patterns.
- **Electronic health records** on blockchain: lots of pilots, few successes. HIPAA, PII, and the right to delete make public chains a bad fit; permissioned chains are usable but often not better than federated databases.

Healthcare's strongest on-chain use cases are **compliance** (pharma tracking), **consent management** (who can access what), and **provenance** (verifying drug authenticity) — not full health records.

## 5. Gaming and digital assets

The 2021 NFT boom's biggest legacy is that game studios now take on-chain assets seriously, with mixed results.

- **Axie Infinity** — the original "play-to-earn" breakout. Collapsed after its Ronin bridge was hacked ($620M stolen, 2022). Still operating, much reduced.
- **Immutable / Immutable zkEVM** — dedicated L2 for games. Hosts Gods Unchained, Guild of Guardians.
- **Sorare** — blockchain-based fantasy football, serious licensing deals with FIFA, MLB, NBA.
- **Ronin Network** — Sky Mavis's L2, focus on gaming.
- **Sky Mavis / The Sandbox / Decentraland** — virtual worlds with token economies, much reduced from 2021 highs.

Honest take: after four years and many billions of dollars, no blockchain game has achieved mainstream hit status. The primitive (verifiable item ownership) is real and useful in niche ways. The "entire game is on-chain" thesis has mostly failed.

## 6. Identity and credentials

A growing category with meaningful wins.

- **ENS (Ethereum Name Service)** — human-readable names like `alice.eth` mapping to Ethereum addresses. Millions of names registered. Effectively DNS for crypto identities.
- **Polygon ID** — zero-knowledge identity framework.
- **Worldcoin** — controversial. Uses iris scans to establish one-person-one-account at global scale.
- **Civic** — KYC/identity verification tied to blockchain.
- **Gitcoin Passport** — anti-sybil identity for grant-giving and governance.
- **Disco / Verifiable Credentials** frameworks — academic credentials, professional licenses.

Adjacent: **decentralized ID (DID)** standards — not tied to one chain, but often implemented with blockchains as anchor points.

## 7. Real estate

A small but concrete category.

- **Propy** — tokenized property transactions, closed real deals in the US.
- **RealT** — tokenized rental property ownership, mostly Detroit and other US markets.
- **Swiss cantons** — Zug, Zurich have tokenized property registries as pilots.

Real estate tokenization is one of the clearest "right fit for blockchain" use cases — illiquid assets, many parties, lots of paperwork, lots of trust issues — but legal integration lags the technology by a decade.

## 8. Governance and public sector

- **Estonia** — not on a public blockchain, but Estonia's KSI timestamp infrastructure for government records is a distant cousin.
- **Dubai Blockchain Strategy** — government services on-chain; a mix of genuine deployments and marketing.
- **Georgia (country)** — land registry on a Bitcoin-anchored system.
- **Colorado (US state)** — accepts some cryptocurrency tax payments via intermediaries.
- **El Salvador** — adopted Bitcoin as legal tender in 2021. Experiment with mixed results.

## 9. Art, media, and creators

- **OpenSea** — largest NFT marketplace, massive volume drops from 2021 peak but still active.
- **Blur** — professional NFT trader's marketplace.
- **Sotheby's, Christie's** — both auctioned NFTs during 2021 peak (Beeple's $69M Christie's sale was a landmark). Both still run occasional NFT auctions.
- **Magic Eden** — Solana-first NFT marketplace.
- **Audius** — decentralized music streaming.
- **Royal** — music royalty tokenization.
- **Mirror.xyz** — blockchain-anchored publishing platform.

## 10. Decentralized social and publishing

- **Lens Protocol** — Aave-built social graph on Polygon. Developer-focused.
- **Farcaster** — crypto-native social, has had meaningful user growth in 2024–26.
- **Nostr** — not strictly a blockchain, but crypto-adjacent censorship-resistant protocol.

## 11. Insurance

- **Etherisc** — parametric crop and flight-delay insurance.
- **Nexus Mutual** — decentralized smart-contract insurance.
- **Lemonade's Crypto Climate Coalition** — parametric insurance for smallholder farmers.

## 12. Central Bank Digital Currencies (CBDCs)

Separate from crypto — but built on DLT in most cases.

- **China — e-CNY / DCEP** — the most advanced CBDC, used by hundreds of millions in pilot cities.
- **India — Digital Rupee (e₹)** — wholesale and retail pilots running in major cities.
- **Brazil — Drex** — CBDC in pilot phase.
- **EU — Digital Euro** — in preparation, not yet launched.
- **UK, Japan, Canada** — research phase.
- **Nigeria — eNaira** — launched 2021, low adoption.
- **Bahamas — Sand Dollar** — live since 2020.

CBDCs are politically controversial but technically largely uncontroversial. They're databases with central-bank signatures and whatever privacy policy the regulator chooses. Whether they count as "blockchain" depends on how purist you are about the word.

## 13. Enterprise blockchain platforms

A short list of what got used, versus pitched:

- **Hyperledger Fabric** — IBM's permissioned chain framework. Many deployments including Food Trust, MediLedger, various trade-finance networks.
- **R3 Corda** — used by banks and insurers for trade settlement and syndicated loans. Marco Polo Network (trade finance) shut down 2022.
- **Quorum / Hyperledger Besu** — permissioned Ethereum derivatives, used by banks.
- **Baseline Protocol** — uses public Ethereum as an anchor for private enterprise workflows.

## 14. Table of notable deployments

| Year | Entity | Use Case | Chain |
|---|---|---|---|
| 2017 | Walmart / IBM | Food traceability | Hyperledger Fabric |
| 2018 | De Beers | Diamond provenance (Tracr) | Ethereum-based, custom |
| 2019 | JPMorgan | Inter-bank settlement (JPM Coin) | Quorum / Onyx |
| 2020 | MakerDAO | Decentralized stablecoin (DAI) | Ethereum |
| 2020 | Visa | USDC settlement pilot | Ethereum |
| 2021 | El Salvador | Bitcoin as legal tender | Bitcoin |
| 2021 | Christie's | Beeple NFT auction | Ethereum |
| 2021 | Sky Mavis | Axie Infinity (before exploit) | Ronin |
| 2021 | PayPal | Crypto buy/sell in-app | Various |
| 2022 | Ethereum Foundation | The Merge (PoS transition) | Ethereum |
| 2023 | PayPal | PYUSD stablecoin issuance | Ethereum / Solana |
| 2023 | MediLedger | DSCSA pharma compliance | Ethereum-based |
| 2023 | SEC | Approves Bitcoin spot ETFs | — |
| 2024 | BlackRock | BUIDL tokenized Treasury fund | Ethereum |
| 2024 | Franklin Templeton | BENJI money-market fund | Multiple chains |
| 2024 | SEC | Approves Ethereum spot ETFs | — |
| 2025+ | Partior | Live wholesale settlement | Permissioned |

## 15. Who is NOT using blockchain (usefully)

Equally important for a newbie: avoid being fooled by press releases. Categories where "blockchain adoption" is mostly theater or has failed:

- **Retail payments** — card networks still dominate 100x.
- **Most of enterprise supply chain** — lots of pilots, few successes.
- **Voting** — occasional municipal experiments, no serious democracy runs on blockchain.
- **Social media** — Lens and Farcaster are niches, not replacements for Twitter.
- **Consumer file storage** — IPFS exists but isn't mainstream.
- **Distributed compute** — Golem, Akash — research and niche.

## 16. What this tells you

- Blockchain adoption is **concentrated in finance and settlement**, because that's where the properties (finality, composability, trust minimization) have clear monetary value.
- **Enterprise blockchain** survives in narrow slices where the alternative was worse: pharma compliance, diamond provenance, specific regulated markets.
- **Consumer adoption** via stablecoins and CEX apps is real but unglamorous — people use crypto for cross-border payments and savings, not NFTs.
- **Government adoption** is small but serious, mostly via CBDCs.

If you want to work in blockchain professionally, follow the money and the pain points. Stablecoin infrastructure, RWA tokenization, and institutional settlement are where the serious jobs are in 2026. Everything else is a smaller market.

## Further reading
- Messari's annual "Crypto Theses" report — an institutional-style overview of real adoption
- a16z "State of Crypto" — venture capitalist's view, bullish but data-backed
- `messari.io/research` for current state of the industry
- Chainalysis annual crypto crime report — sobering, useful

## Next file to read
`06-can-anyone-use-it.md` — a practical answer to whether you, personally, can use blockchain today.
