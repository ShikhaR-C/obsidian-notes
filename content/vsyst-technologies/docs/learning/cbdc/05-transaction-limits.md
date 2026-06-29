# 5. Transaction Limits & Financial Aspects

## Retail CBDC (e₹-R) — Wallet & Transaction Limits

### Tiered KYC-Based Limits

| Tier | KYC Level | Wallet Holding Limit | Per-Transaction Limit |
|------|-----------|---------------------|-----------------------|
| Tier 1 | Minimum / No KYC | ₹10,000 | ₹5,000 |
| Tier 2 | Basic KYC | ₹1,00,000 (₹1 lakh) | ₹50,000 |
| Tier 3 | Full KYC | ₹2,00,000 (₹2 lakh) | ₹2,00,000 |

- **Daily limits**: Up to ₹2 lakh for fully KYC-compliant wallets (varies by issuing bank).
- **Monthly limits**: Not explicitly capped at protocol level — governed by the issuing bank's policies and wallet tier.
- The tiered structure mirrors the RBI's **Prepaid Payment Instrument (PPI) norms**.

### Can Huge Transactions Be Made?

**Retail CBDC — No.** The retail digital rupee is designed for day-to-day consumer payments, not large-value transfers. Maximum ₹2 lakh per transaction for fully KYC wallets.

**Wholesale CBDC — Yes.** That's the entire purpose. e₹-W handles large-value interbank and government securities transactions in the **crores of rupees** range.

### Comparison with Other Payment Systems

| System | Per-Transaction Limit |
|--------|----------------------|
| e₹-R (Full KYC) | ₹2,00,000 |
| UPI (general) | ₹1,00,000 |
| UPI (tax, IPO, insurance) | ₹2,00,000 – ₹5,00,000 |
| RTGS | ₹2,00,000 minimum, **no upper cap** |
| NEFT | **No upper cap** |
| e₹-W (Wholesale) | **No retail-style cap** |

> **Key takeaway:** For large-value transactions, RTGS/NEFT or the wholesale CBDC are the appropriate instruments. Retail CBDC is intentionally capped as the digital equivalent of physical cash.

---

## Interest & Returns

### e-₹ Does NOT Earn Interest

This is a **deliberate and fundamental design choice** by the RBI.

**Why no interest?**
- e-₹ is designed as the **digital equivalent of physical cash** — a ₹500 note in your pocket doesn't earn interest, and neither does e-₹.
- If CBDC paid interest, it would **directly compete with bank deposits**, causing disintermediation — people withdrawing savings from banks to hold interest-bearing CBDC.
- This could **destabilize the banking system** by reducing banks' deposit base and impairing their ability to lend.

### Comparison

| Instrument | Interest | Liquidity | Risk |
|-----------|----------|-----------|------|
| e-₹ (CBDC) | **0%** | Instant (like cash) | Zero (sovereign liability) |
| Savings Account | 2.7–4% | High (instant via UPI/ATM) | DICGC insured up to ₹5 lakh |
| Fixed Deposit | 6–7.5% | Low (premature withdrawal penalty) | DICGC insured up to ₹5 lakh |
| Physical Cash | 0% | Instant | Theft, counterfeit risk |

### Future Possibility
- The RBI has not ruled out interest-bearing CBDC in the long term.
- Academic papers discuss **tiered remuneration** models (e.g., 0% up to a threshold, negative interest above it to discourage hoarding).
- Not implemented currently.

---

## Offline Capability

### Status: Pilot Stage (Active Development)

- RBI has been conducting **offline CBDC pilots since 2023**.
- Designed for areas with poor or no internet connectivity — critical for India's rural population.

### Technology
- **NFC-based transactions** — tap-and-pay using NFC-enabled phones or smart cards.
- **NFC smart cards** (similar to metro cards) tested for tap-and-pay without internet.
- **Proximity-based** transfers between two NFC-enabled phones explored.
- Offline transactions have **lower value limits** than online ones (to mitigate double-spending risk).
- Wallet periodically **syncs with the central ledger** when connectivity is restored.

### Key Challenge
- Preventing **double-spending** in offline mode.
- RBI exploring cryptographic solutions and **hardware-based security** (secure enclaves in phones, dedicated chips in smart cards).

---

## Interoperability

### UPI Integration (Live)
- **CBDC-UPI interoperability has been implemented** as of 2024.
- Users can **scan UPI QR codes** to make payments using their e-₹ wallet balance.
- Merchants do **not need separate infrastructure** — any existing UPI QR code works.
- Leverages India's massive UPI ecosystem (300+ million users, 10+ billion monthly transactions).

### Integration with Existing Payment Systems
- e₹-R wallets issued through existing banking apps and dedicated CBDC wallet apps.
- P2P and P2M transactions supported.
- Load from bank account, redeem back to bank account.
- Wholesale CBDC interoperates with existing G-Sec settlement infrastructure.

### Unified Ledger Interface (ULI)
- RBI has discussed a **Unified Ledger** concept that would bring together CBDCs, tokenized deposits, and other digital assets on a common programmable platform.

---

*Sources: RBI Concept Note (Oct 2022), RBI Annual Reports, RBI Governor/Deputy Governor Speeches*
