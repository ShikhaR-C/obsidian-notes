# 1. What is CBDC? — The Digital Rupee (e-₹)

## Definition

The **Digital Rupee (e-₹)** is India's Central Bank Digital Currency (CBDC) — a digital form of legal tender issued directly by the **Reserve Bank of India (RBI)**. It is a tokenized digital version of the Indian Rupee, representing a **direct liability of the central bank**, exactly like physical cash (banknotes and coins).

Unlike money in your bank account (which is a commercial bank's liability), e-₹ carries **zero counterparty risk** — it is sovereign-backed and guaranteed by the RBI.

---

## Legal Tender Status

- e-₹ is **legal tender** in India under law.
- The **Finance Act, 2022** amended **Section 22 of the RBI Act, 1934** to include "digital form" of banknotes.
- No merchant or entity can legally refuse e-₹ — just like physical rupees.

---

## Two Types of Digital Rupee

### e₹-W — Wholesale CBDC

| Aspect | Details |
|--------|---------|
| **Launched** | November 1, 2022 |
| **Purpose** | Interbank settlement of government securities (G-Sec) |
| **Users** | Banks and select financial institutions only |
| **Design** | Account/token-based on permissioned DLT |
| **Distribution** | RBI issues directly to participating banks |
| **Transaction size** | Large-value (crores of rupees) |
| **Key benefit** | Eliminates settlement risk, enables atomic (instant + final) settlement |

### e₹-R — Retail CBDC

| Aspect | Details |
|--------|---------|
| **Launched** | December 1, 2022 |
| **Purpose** | Day-to-day payments by the general public — digital equivalent of cash |
| **Users** | Individuals, merchants, businesses |
| **Design** | Token-based on permissioned DLT |
| **Denominations** | ₹0.50, ₹1, ₹2, ₹5, ₹10, ₹20, ₹50, ₹100, ₹200, ₹500 |
| **Distribution** | Two-tier: RBI → Banks → Public (via wallet apps) |
| **Transactions** | P2P (person-to-person), P2M (person-to-merchant) via QR codes |

---

## Underlying Technology

- Built on a **Distributed Ledger Technology (DLT)** platform — but it is **NOT a public blockchain** like Bitcoin or Ethereum.
- Uses a **permissioned/private DLT** where the RBI controls the network; only authorized entities (banks) operate nodes.
- The RBI's October 2022 Concept Note stated the technology choice is flexible — DLT is used, but the RBI reserved the right to use conventional centralized databases if needed.
- Retail e₹ is **token-based**: each unit is a distinct digital token with a unique serial identifier, analogous to a physical banknote.

---

## How e-₹ Differs from UPI, Crypto, and Bank Deposits

| Feature | Digital Rupee (e-₹) | UPI | Cryptocurrency | Bank Deposits |
|---------|---------------------|-----|----------------|---------------|
| **Issuer** | RBI (central bank) | Banks/NPCI (intermediary) | Decentralized / private | Commercial banks |
| **Nature** | Digital cash (token) | Payment rail over bank accounts | Private digital asset | Bank liability |
| **Legal tender** | Yes | No (payment method) | No (banned for payments in India) | No (claim on bank) |
| **Settlement** | Final & instant (like cash) | Near-instant, but settles via bank accounts | Varies by network | Subject to bank solvency |
| **Interest** | No (by design — it's cash) | N/A (account may earn interest) | Varies | Yes (savings/FD) |
| **Counterparty risk** | None (sovereign backing) | Bank/system risk | High | Deposit insurance up to ₹5 lakh |
| **Offline capability** | Planned (NFC-based) | Limited | No | No |
| **Privacy** | Managed anonymity for small txns | Banks see all transactions | Pseudonymous | Banks see all transactions |
| **Programmability** | Yes (planned) | No | Yes (smart contracts) | No |

### Key Distinction: e-₹ vs UPI
- **UPI** moves money *between bank accounts* — the money stays as a bank deposit.
- **e-₹** is the money itself — a digital token that transfers directly from one wallet to another, like handing over a physical note. No bank intermediation during the transfer.

---

## Key Design Principles (from RBI Concept Note)

1. **Two-tier distribution model** — RBI issues to banks, banks distribute to public (preserves the banking system's role)
2. **Non-interest bearing** — prevents competition with bank deposits and disintermediation risk
3. **Managed anonymity** — small-value transactions preserve cash-like privacy; larger transactions subject to KYC/AML
4. **Interoperable** — designed to work with existing payment infrastructure (UPI QR codes)
5. **Phased rollout** — cautious, pilot-based approach ("learning by doing")

---

*Source: RBI Concept Note on CBDC, October 7, 2022*
