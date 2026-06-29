# 13 - What is Cryptocurrency?

## What you'll learn

- A plain-English definition of cryptocurrency that does not rely on hype
- How crypto actually differs from the rupees in your bank account
- The major categories of crypto (payment coins, smart contract platforms, stablecoins, utility tokens, governance tokens, meme coins, CBDCs)
- Where crypto "value" comes from and why prices move the way they do
- How crypto is issued, stored, and transferred
- The real-world uses that actually work today and the ones that are still mostly marketing
- Common scams, and a safety checklist for someone just starting out

This file is educational only. Nothing here is financial or legal advice.

---

## 1. The Simplest Honest Definition

Cryptocurrency is **digital money that lives on a blockchain** and is not issued or controlled by any single company, bank, or government.

Break that sentence into three pieces:

1. **Digital money** - It exists only as numbers in a database. There are no coins or paper notes.
2. **Lives on a blockchain** - The database is distributed across thousands of computers around the world, and every one of them keeps a copy. Changes must be agreed on by the network, not by one administrator.
3. **No central issuer** - There is no CEO, no RBI, no Federal Reserve that can freeze your account, print more of it, or change the rules on a whim. The rules are written in software and enforced by math.

That is it. Everything else - Bitcoin, Ethereum, Solana, stablecoins, NFTs, DeFi - is built on top of this basic idea.

> Important nuance: "no central issuer" is the original vision. In practice, many cryptocurrencies today have foundations, core dev teams, and large token holders who exert significant influence. Pure decentralization is a spectrum, not a binary.

---

## 2. How Crypto Differs From Fiat Money (INR, USD, EUR)

Fiat money is the regular money you use every day - rupees, dollars, euros. It is issued by a central bank and declared legal tender by a government.

| Aspect | Fiat (INR, USD) | Cryptocurrency |
|---|---|---|
| Who issues it? | Central bank (RBI, Fed, ECB) | Software protocol (no single issuer) |
| Supply rules | Can be expanded or reduced by policy | Usually fixed or algorithmically controlled |
| Legal tender? | Yes, by law | Almost never (El Salvador is the exception for Bitcoin) |
| Can be frozen? | Yes, by banks or courts | Only if held on a custodial service; not if self-custodied |
| Settlement time | Minutes to days (depending on rails) | Seconds to minutes on-chain |
| Works without internet? | Yes (cash) | No |
| Reversible? | Often (chargebacks, court orders) | No - transactions are final |
| Backed by? | Trust in the issuing government | Cryptographic rules and network consensus |

The key difference is **who you have to trust**. With fiat, you trust the government and your bank. With crypto, you trust a protocol - a piece of open-source code running on thousands of computers. Neither is automatically better. They are different trust models with different failure modes.

---

## 3. How Crypto Differs From the Digital Money in Your Bank App

This is the confusion that trips up most newcomers. When you open your HDFC or SBI app and see "Rs. 50,000," that is already digital. So how is crypto different?

The answer: **who owns the database**.

When your bank app shows Rs. 50,000, that number is an entry in HDFC's private database. HDFC can:

- Freeze the account
- Reverse a transaction
- Decline to send money to someone
- Fail and take your balance with them (though deposit insurance partly covers this)
- Be forced by a court or government to do any of the above

When a crypto wallet shows 0.5 ETH, that number is an entry in a public database that thousands of independent computers agree on. No single party can change it. If you hold the private key, you - and only you - can spend it.

Rough analogy:

- **Bank digital money** = an IOU from the bank, recorded in their private ledger
- **Cryptocurrency** = a bearer asset, recorded in a shared ledger anyone can verify

Bearer assets are powerful and dangerous. Powerful, because nobody can take them from you. Dangerous, because if you lose the key, nobody can help you recover it.

---

## 4. The Main Categories of Cryptocurrency

"Cryptocurrency" is an umbrella term. Under it sit several very different kinds of assets. Mixing them up is a common beginner mistake.

### 4.1 Payment Coins

The original category. Designed to be digital cash - a way to send value from one person to another without a bank in the middle.

**Examples:** Bitcoin (BTC), Litecoin (LTC), Bitcoin Cash (BCH), Monero (XMR - privacy-focused)

**What they do:** Move value. That is it. They are not programmable in any deep sense. Bitcoin has a simple scripting language but is not designed for complex applications.

**Why they matter:** Bitcoin is the original, and it is still the largest by market cap. It is often called "digital gold" because its supply is capped at 21 million coins and it is treated more as a store of value than as a medium of exchange.

### 4.2 Smart Contract Platforms

These are blockchains that can run programs, not just track balances. A "smart contract" is code that lives on the blockchain and executes automatically under defined conditions.

**Examples:** Ethereum (ETH), Solana (SOL), Avalanche (AVAX), BNB Chain (BNB), Cardano (ADA), Near (NEAR)

**What they do:** Provide a general-purpose computing environment. On top of them you can build lending protocols, exchanges, games, identity systems, NFTs, and countless other applications.

**Why they matter:** Almost all of the interesting activity in crypto - DeFi, NFTs, tokenized assets - happens on smart contract platforms, not on Bitcoin.

The native coin of the platform (ETH, SOL, AVAX) is used to pay transaction fees ("gas"). Without the native coin, you cannot use the blockchain.

### 4.3 Stablecoins

A stablecoin is a cryptocurrency designed to hold a stable value - almost always pegged 1:1 to a fiat currency (most often the US dollar).

Stablecoins are the category most relevant to actual business use, so they deserve extra attention.

**Why stable?** Because a currency that swings 10% in a day is useless for invoicing, payroll, or trade settlement.

**Three main types:**

| Type | How it works | Example | Main risk |
|---|---|---|---|
| Fiat-backed | Company holds $1 in a bank for every $1 of token issued | USDC, USDT | Trust in the issuer and its banking |
| Crypto-backed | Token is over-collateralized by other crypto held in a smart contract | DAI | Collateral can crash in value |
| Algorithmic | Supply expands and contracts automatically to maintain the peg | Previously UST (Terra) | Can "depeg" and collapse - UST wiped out ~$40B in 2022 |

**USDC** (issued by Circle) is generally considered the most transparent and compliance-friendly fiat-backed stablecoin, audited monthly. **USDT** (Tether) is the most widely used by volume but has had historical questions about its reserves. **DAI** (MakerDAO) is the leading crypto-backed stablecoin.

For B2B use - invoicing, cross-border payments, settlement - stablecoins are by far the most practical part of crypto today. Bitcoin is not. Ethereum is not. Stablecoins are.

### 4.4 Utility Tokens

Tokens that give you access to a service. Think of them like arcade tokens - they have a specific use inside a specific app.

**Examples:** Filecoin (FIL, used to pay for decentralized storage), Basic Attention Token (BAT, used in the Brave browser ad ecosystem), Chainlink (LINK, used to pay oracle node operators).

A utility token is only as valuable as the service it unlocks. If nobody uses the service, the token has no reason to have value.

### 4.5 Governance Tokens

Tokens that give you voting rights in a decentralized protocol. Holders vote on protocol upgrades, parameters, treasury spending, and so on. Similar in spirit to shareholder voting, but without the legal protections of being a shareholder.

**Examples:** Uniswap (UNI), Aave (AAVE), Compound (COMP), Maker (MKR)

In practice, most holders never vote, and governance often concentrates in a few large wallets.

### 4.6 Meme Coins

Tokens whose value is driven almost entirely by social hype and community energy rather than utility.

**Examples:** Dogecoin (DOGE), Shiba Inu (SHIB), Pepe (PEPE), plus thousands of short-lived tokens launched daily on Solana and Base.

Meme coins are closer to collectibles or gambling chips than to currencies. Some have produced life-changing returns; most go to zero. If you are new to crypto, treat these as entertainment money at best. Treat them as a loss from the start.

### 4.7 CBDCs - Central Bank Digital Currencies

A CBDC is digital money issued directly by a central bank. India has the Digital Rupee (e-rupee). China has the e-CNY. The EU is working on a digital euro.

CBDCs use some blockchain-adjacent technology but are philosophically the opposite of cryptocurrency:

| Cryptocurrency | CBDC |
|---|---|
| No central issuer | Issued by the central bank |
| Permissionless | Permissioned (the central bank controls access) |
| Pseudonymous | Fully identified to the issuer |
| Cannot be frozen by one party | Can be frozen by the central bank |
| Monetary policy by code | Monetary policy by central bank decree |

CBDCs are digital fiat, not crypto. They solve very different problems (faster payments, lower cost infrastructure, programmable policy) and introduce different tradeoffs (more surveillance, more control).

---

## 5. Where Does Crypto's Value Come From?

This is the most honest question you can ask, and it deserves an honest answer. Cryptocurrency value comes from a mix of:

1. **Scarcity** - Bitcoin is capped at 21 million. Ether has no hard cap but has net deflationary mechanics. Scarcity alone does not create value (there are plenty of rare things nobody wants), but scarcity plus demand does.
2. **Utility** - Can the token actually do something? ETH pays for Ethereum gas. USDC is used for real-world settlement. A token with genuine recurring utility has a demand floor.
3. **Network effects** - The more people who use a chain, the more valuable it becomes. This is why Bitcoin and Ethereum dominate despite being technically older and slower than many newer chains.
4. **Speculation** - The honest part nobody likes to admit. A large share of crypto price movement is pure speculation: people buying because they think someone else will pay more later. This is not unique to crypto - gold, art, and startup equity have the same dynamic - but crypto is unusually exposed to it.
5. **Narrative** - Stories move markets. "Digital gold," "the world computer," "web3," "AI agents," and so on. Narratives are not fake - they shape what people build - but they are not the same as fundamentals.

A useful mental model: the long-run floor of a crypto asset's value comes from utility and network effects. Everything above that is speculation and narrative.

---

## 6. How Crypto Is Created

New coins enter circulation in several ways.

### 6.1 Mining (Proof of Work)

Computers compete to solve a cryptographic puzzle. The winner proposes the next block of transactions and is rewarded with newly minted coins plus fees. This is how Bitcoin works, and how Ethereum worked until 2022.

Mining is energy-intensive because the security comes from the cost of the computation.

### 6.2 Staking (Proof of Stake)

Holders lock up (stake) their coins as collateral. The protocol randomly selects stakers to propose blocks. Honest behavior is rewarded; cheating is punished by "slashing" (losing part of the stake). Ethereum switched to Proof of Stake in September 2022 (the Merge), reducing its energy use by ~99.9%.

Staking produces yield, typically 3-7% per year, paid in the native token.

### 6.3 Pre-mine

The founders mint a large portion of the supply before public launch and distribute it to team, investors, treasury, and community. Most newer chains do this. It is efficient but concentrates ownership.

### 6.4 ICO / IDO / IEO / Airdrop

- **ICO** (Initial Coin Offering): The project sells tokens directly to the public for fiat or other crypto. Extremely common in 2017. Now largely replaced due to regulation.
- **IDO** (Initial DEX Offering): Tokens launched via a decentralized exchange.
- **IEO** (Initial Exchange Offering): A centralized exchange hosts the sale.
- **Airdrop**: Tokens distributed free to early users, often as a reward for past activity on the protocol.

Each method has different legal implications, which we cover in file 15.

---

## 7. Wallets: Where Crypto Actually Lives

A "wallet" is not where your crypto is stored - the balances live on the blockchain. A wallet is a piece of software (or hardware) that holds the **private key** that proves ownership.

Two important axes:

### 7.1 Hot vs Cold

- **Hot wallet** - Connected to the internet. Convenient, quick to use, but exposed to hacks and malware. Examples: MetaMask, Phantom, Coinbase Wallet, Trust Wallet.
- **Cold wallet** - Offline. Private keys never touch an internet-connected device. Much safer for long-term holding. Examples: Ledger, Trezor (hardware devices), paper wallets.

### 7.2 Custodial vs Self-Custody

- **Custodial** - A company holds your keys for you. You log in with a username and password. Examples: Coinbase, Binance, most exchange accounts. If they get hacked, go bankrupt, or freeze your account, you have a problem. Mt. Gox (2014) and FTX (2022) are the cautionary tales.
- **Self-custody** (non-custodial) - You hold your own keys, typically as a 12- or 24-word "seed phrase." If you lose it, there is no recovery. If you leak it, your funds can be drained.

The crypto saying: **"Not your keys, not your coins."** It is a simplification, but it captures a real tradeoff. Custodial is convenient; self-custody is sovereign.

For beginners, a reasonable setup is:
- Small amounts on a reputable custodial exchange for learning
- Larger amounts on a hardware wallet you bought directly from the manufacturer (never from Amazon or a reseller - supply chain attacks are real)

---

## 8. Exchanges: Where You Buy and Sell

### 8.1 Centralized Exchanges (CEX)

Traditional companies that run order books. You deposit fiat, trade crypto, withdraw. They handle KYC (identity verification).

**Examples:** Coinbase (US, publicly listed), Kraken (US), Binance (global), WazirX and CoinDCX (India).

**Pros:** Easy to use, fiat on/off ramps, liquidity, customer support.
**Cons:** Custodial risk, KYC friction, regulatory uncertainty, can be hacked or collapse.

### 8.2 Decentralized Exchanges (DEX)

Smart contracts that let users trade directly with a liquidity pool, no company in the middle. You connect your self-custody wallet and swap tokens.

**Examples:** Uniswap (Ethereum), PancakeSwap (BNB Chain), Raydium (Solana), Curve (stablecoin specialist).

**Pros:** Non-custodial, permissionless, no signup, access to thousands of tokens.
**Cons:** No fiat on-ramp, higher complexity, exposure to scam tokens, MEV (front-running), smart contract risk.

Most real users use both: a CEX to convert fiat to crypto, then move to a self-custody wallet, then interact with DEXs and DeFi from there.

---

## 9. Anatomy of a Crypto Transaction

When you send crypto, several things happen under the hood.

1. **Addresses** - Your wallet has a public address (something like `0x742d35Cc6634C0532925a3b844Bc9e7595f7E123`). It is derived from your public key. You can share it freely - it is like your bank account number.
2. **Signing** - Your wallet uses your private key to cryptographically sign a transaction. The signature proves you authorized it without revealing your key.
3. **Broadcasting** - The signed transaction is sent to the network's peer-to-peer layer.
4. **Gas** - On most chains, you pay a transaction fee ("gas") in the native coin. Gas prices rise when the network is congested. On Ethereum mainnet, a simple transfer can cost anywhere from $0.50 to $50 depending on congestion. On Polygon, Base, or Arbitrum, the same transfer is usually under a cent.
5. **Confirmation** - A validator or miner includes your transaction in the next block. That is your first confirmation.
6. **Finality** - After enough blocks on top of yours, the transaction is considered final and effectively irreversible. On Bitcoin, people often wait 6 blocks (~60 minutes). On Ethereum post-Merge, finality is ~12-15 minutes. On Solana, under a minute.

If you send to a wrong address, it is gone. There is no reversal. This is the single most important thing to internalize before you move any significant amount.

---

## 10. Why Crypto Is So Volatile

Crypto prices swing far more than stocks or fiat. Reasons:

- **Thin liquidity** - Even BTC, the largest, trades at a fraction of the daily volume of major equity or FX markets. Smaller tokens have even less. A modest order can move the price.
- **24/7 markets** - No circuit breakers, no market open or close. Panic and mania can feed on each other for days.
- **Narrative sensitivity** - Prices react strongly to tweets, regulatory rumors, hacks, and macro events.
- **Leverage** - A lot of crypto trading is on leverage. When prices move, forced liquidations cascade.
- **Young asset class** - Crypto is ~16 years old. There is no settled valuation framework the way there is for bonds or equities.

Volatility is not a bug to be fixed; it is a feature of any young, small, permissionless market. Over long time frames it tends to compress, but slowly.

---

## 11. Real-World Uses That Actually Work Today

There is a lot of hype in crypto. Here is what genuinely works in 2026, separated from what is still mostly marketing.

### Works well

- **Cross-border remittances** - Sending stablecoins is faster and cheaper than most wire transfers or remittance services. Real use case, real volume.
- **Inflation hedge for citizens of high-inflation economies** - In Argentina, Turkey, Lebanon, Nigeria, stablecoin demand is strongly driven by people protecting savings from local currency collapse. This is not speculation; it is survival.
- **On-chain lending and borrowing (DeFi)** - Aave, Compound, and similar protocols have been running for years with billions in deposits. They are technically sound, though not beginner friendly.
- **Settlement between crypto-native businesses** - Exchanges, market makers, and crypto companies routinely settle in stablecoins because it is faster than bank wires.
- **Programmable payments** - Streaming salaries, escrow, conditional payments, and micro-payments are genuinely easier on-chain than off.

### Works sometimes

- **Retail payments** - Technically possible, rarely used. Fees and UX are fine on L2s now, but merchant adoption is still thin.
- **Tokenized real-world assets** - Treasury bills, real estate, invoices. Growing fast but still small.
- **Identity and reputation** - Interesting work happening, not yet mainstream.

### Mostly hype

- **Bitcoin as a daily payment currency** - Too volatile, too slow for this. It is a store of value, not a payment rail.
- **"Web3 social media"** - Many attempts, none at scale.
- **NFTs as a new art market** - The 2021-22 bubble deflated. A smaller, healthier market remains, but it is not the revolution it was pitched as.
- **Play-to-earn gaming** - Mostly collapsed under its own economics.

Being honest about this matters. Crypto has real uses. It also has a lot of speculation dressed up as innovation.

---

## 12. Common Scams

If you spend any time in crypto, you will encounter scams. Knowing the patterns is half the defense.

- **Rug pull** - A team launches a token, hypes it, collects money, then drains the liquidity pool and disappears. Especially common with meme coins.
- **Fake airdrop** - A message tells you you have won tokens. To claim them, you must connect your wallet and sign a transaction. The signature drains your wallet.
- **Phishing sites** - Fake Uniswap, fake MetaMask, fake Coinbase pages that steal your seed phrase or trick you into signing a malicious transaction.
- **Pig butchering** - A long-con romance or friendship scam where the scammer builds trust over weeks or months, then lures the victim into a fake "investment platform." Devastating and increasingly common.
- **Fake customer support** - You post a problem on Twitter or Discord; a "support agent" DMs you and asks for your seed phrase. Real support will never ask for your seed phrase. Ever.
- **Impersonation** - Fake Elon Musk, fake Vitalik, fake celebrity giveaways promising to double any crypto you send. They do not.
- **Pump and dump** - A group coordinates to buy a low-cap token, promote it heavily, and sell into retail buyers. The insiders profit; everyone else loses.
- **Approval drainers** - You approve a malicious contract to spend your tokens. Later, the contract drains them. Always review what you are signing, and use tools like Revoke.cash to clean up old approvals.

---

## 13. A Newbie Safety Checklist

Print this. Read it before every significant action.

1. **Start small.** Your first transactions should be with amounts you are comfortable losing entirely.
2. **Never share your seed phrase.** Not with support. Not with a friend. Not in any app other than the wallet you originally created. Nobody legitimate will ever ask.
3. **Write your seed phrase on paper or metal.** Not in a photo. Not in a cloud note. Not in an email to yourself.
4. **Use a hardware wallet for amounts that would hurt to lose.** Ledger or Trezor, bought directly from the manufacturer.
5. **Bookmark official sites.** Never reach MetaMask, Uniswap, Aave, or your exchange via a Google search. Google ads are a common phishing vector.
6. **Verify addresses character by character.** Malware can replace addresses in your clipboard. Always check the first and last 6 characters on the actual device screen.
7. **Be skeptical of unsolicited DMs.** If someone messages you first about crypto, assume it is a scam until proven otherwise.
8. **Assume anything promising "guaranteed returns" is a scam.** There are no guaranteed returns in crypto.
9. **Do not invest money you need for rent, food, or medical costs.** Crypto can lose 80% of its value in a year. It has before. It will again.
10. **Understand that you are your own bank.** That includes your own security team, your own backup strategy, and your own fraud department. There is no one to call if something goes wrong.

---

## 14. A Short Glossary

- **Blockchain** - A distributed append-only ledger secured by cryptography and consensus.
- **Wallet** - Software or hardware that holds private keys. Does not hold coins.
- **Private key** - The secret that proves ownership and signs transactions.
- **Seed phrase** - A 12- or 24-word human-readable backup of your private key.
- **Address** - A public identifier derived from your public key. Used to receive funds.
- **Gas** - The fee you pay to have a transaction processed.
- **Smart contract** - Code that runs on a blockchain under predefined conditions.
- **DeFi** - Decentralized Finance. Financial services built from smart contracts.
- **CEX / DEX** - Centralized and Decentralized Exchanges.
- **L1 / L2** - Layer 1 is a base blockchain (Ethereum). Layer 2 scales it (Arbitrum, Base, Optimism, Polygon zkEVM).

---

## Summary

Cryptocurrency is a new kind of money - digital, bearer, and based on shared software rather than a central issuer. It comes in several flavors, of which **stablecoins** are the most practical for real business use, smart contract platforms power the interesting applications, and payment coins (especially Bitcoin) serve mostly as a store of value. Its value is a mix of utility, network effects, scarcity, and speculation. It is powerful, unforgiving, and surrounded by scams. Start small, stay skeptical, and never share your seed phrase.

---

## Next file to read

**`14-crypto-in-our-app.md`** - Now that you understand what cryptocurrency is, the next question is practical: could we actually use any of this inside DZZLO OMS? That file walks through the real options for a B2B fuel distribution platform.
