# 03 — How to Use Blockchain

## What you'll learn
- How to use blockchain as an end user (wallets, signing, gas, explorers)
- How to use blockchain as a developer (toolchain, hello-world contract deploy)
- The key concepts you meet at every step: accounts, keys, addresses, gas, nonces
- A complete walkthrough of deploying your first contract to Sepolia testnet
- How users actually interact with decentralized apps (dApps)

---

## 1. Two perspectives

Using blockchain means different things depending on who you are:

- **End user:** You want to hold some crypto, send it, interact with a dApp. Your tool is a wallet.
- **Developer:** You want to write code that runs on a blockchain — smart contracts, front-ends, indexers. Your tool is a development environment and a testnet.

This file walks both paths. You can do one, the other, or both in the same weekend.

---

# PART A — Using blockchain as an end user

## 2. Step 1: Get a wallet

A wallet is the app that holds your keys and signs transactions on your behalf. It is *not* where your money is stored — your money lives on the chain. The wallet just controls the key that lets you move it.

Mainstream options:

| Wallet | Chains | Form |
|---|---|---|
| MetaMask | Ethereum + all EVM L2s | Browser extension + mobile |
| Rabby | Ethereum + EVM chains | Browser extension (power-user friendly) |
| Phantom | Solana + EVM | Browser extension + mobile |
| Trust Wallet | Many chains | Mobile only |
| Coinbase Wallet | Many chains (self-custody, separate from the exchange) | Browser + mobile |
| Ledger / Trezor | Hardware wallets | Physical device |

For learning, install **MetaMask** (`metamask.io`). It is the most common one and almost every tutorial assumes it.

## 3. Step 2: Understand your seed phrase

When you create a wallet, it generates a 12-word (or 24-word) **seed phrase** (a.k.a. mnemonic, a.k.a. recovery phrase). Example:

```
rocket guitar lazy marble river hollow rigid ceramic
```

This phrase *is* your wallet. Anyone who has it can take everything in the wallet. Anyone who loses it loses everything forever.

Rules:
- Write it down on paper. Multiple copies. In multiple safe places.
- **Never** type it into any website, chat, or email.
- **Never** take a screenshot that might sync to the cloud.
- **Never** paste it into anything claiming to "restore," "verify," or "validate" your wallet.
- **Nobody legitimate will ever ask for it.**

Most first-time crypto users lose money in one of two ways: sending to the wrong address, or giving up their seed phrase to a scammer. Both are permanent. Respect the phrase.

## 4. Step 3: Your first address

Once the wallet is set up, it shows you an **address** — something like `0x742d35Cc6634C0532925a3b844Bc9e7595f1A8B4`. This is your public identifier. You can share it freely. People can send you crypto by sending to this address, and you can view its history on a block explorer.

You can have many addresses in one wallet (MetaMask lets you create accounts inside the same seed). Each address is independent as far as the chain is concerned.

## 5. Step 4: Get some testnet ETH

Before you touch real money, learn on a testnet. Testnets are full copies of the chain environment where the "money" has no value, and you can get it for free from a **faucet**.

The main Ethereum testnet for learning is **Sepolia**. In MetaMask:

1. Click the network selector at the top.
2. Switch to "Sepolia test network" (if hidden, enable "Show test networks" in settings).
3. Copy your address.
4. Visit a public Sepolia faucet (search "sepolia faucet" — there are a few; do not pay for faucet access).
5. Paste your address, prove you're human, wait a few minutes.

You should now see a small amount of Sepolia ETH in your wallet. Congratulations — you've just received your first blockchain transaction.

## 6. Step 5: Send your first transaction

Send any amount from your wallet to another address you control (or a friend's). Note what the wallet shows you:

- **From:** your address
- **To:** recipient address
- **Amount:** how much to send
- **Gas fee:** the fee paid to validators for including your transaction
- **Nonce:** a counter — each transaction from an address has one, and they must increment
- **Network:** which chain you're sending on (CRITICAL — sending on the wrong network sends your funds into the void)

When you click "confirm," the wallet signs the transaction with your private key and broadcasts it. Within seconds to a minute, it should appear on the chain.

## 7. Step 6: Read a block explorer

A block explorer is a search engine for the chain. The canonical Ethereum one is **Etherscan** (and for Sepolia, `sepolia.etherscan.io`).

Paste your address into the search bar. You'll see:
- Every transaction your address has ever made
- Your current balance
- Tokens you hold (if any)
- Contract interactions

Click into a transaction and you'll see its full details: sender, recipient, value, gas used, block number, timestamp, and the exact bytes of data it carried. Everything is verifiable. No permission needed.

Block explorers are the single best tool for learning what's really happening on-chain. Browse them the way you browse Wikipedia.

## 8. Step 7: Use a dApp

Decentralized applications are front-ends that talk to smart contracts instead of a traditional backend. To use one:

1. Visit the dApp's website.
2. Click "Connect Wallet."
3. Your wallet pops up and asks you to approve the connection. This only shares your address, not any keys.
4. Perform an action (swap, mint, stake, whatever).
5. Your wallet pops up again, this time asking you to approve a *transaction*. Read it, confirm, pay gas.
6. Wait for the transaction to be mined.
7. The dApp updates to show the result.

A good practice dApp on testnet: **Uniswap on Sepolia** (if available) — swap some Sepolia ETH for a test token. You've now used a decentralized exchange. Same mechanics apply on mainnet with real value.

## 9. Key concepts you've met

| Concept | What it is |
|---|---|
| **Account** | An identity on the chain. For Ethereum: `{address, nonce, balance, code, storage}` |
| **Private key** | A 256-bit secret. Signs transactions. Never leaves your device. |
| **Public key** | Derived from the private key. Shared with others. |
| **Address** | A hash of the public key, usually 20 bytes. What you share. |
| **Seed phrase** | A human-readable encoding of a master key from which all private keys derive. |
| **Gas** | A measure of computation. Each operation has a fixed gas cost. |
| **Gas price** | How much you pay per unit of gas, in ETH. You set it; the network takes it. |
| **Nonce** | A per-address counter to prevent replay and enforce ordering. |
| **Mempool** | The waiting room of pending transactions. |
| **Confirmation** | When your transaction lands in a block. Deeper = more certain. |

---

# PART B — Using blockchain as a developer

## 10. The developer toolchain

For Ethereum and EVM chains, the modern stack is roughly:

| Layer | Tool |
|---|---|
| Contract language | **Solidity** (also Vyper, less common) |
| Dev framework | **Hardhat** or **Foundry** |
| Contract standards | **OpenZeppelin** contract library |
| JS/TS client | **ethers.js** or **viem** |
| React hooks | **wagmi** + **RainbowKit** |
| Test chain | Hardhat local node, Anvil (Foundry), or Sepolia testnet |
| Browser IDE | **Remix** (`remix.ethereum.org`) — great for beginners, no install |
| Indexer | **The Graph** for GraphQL queries over chain data |
| RPC provider | **Alchemy**, **Infura**, **QuickNode** — your gateway to nodes |

For your first contract, Remix is the fastest path. For a real project, use Hardhat or Foundry.

## 11. Hello World: write, compile, deploy, interact

We'll deploy a tiny contract on Sepolia using Hardhat. This is the "I've shipped a smart contract to a public blockchain" milestone. It takes about 30 minutes the first time.

### 11.1 Install tooling
Assumes Node.js 20+ is installed.

```bash
mkdir my-first-contract && cd my-first-contract
npm init -y
npm install --save-dev hardhat
npx hardhat init      # pick "Create a JavaScript project"
```

You now have a folder with `contracts/`, `scripts/`, `test/`, and a `hardhat.config.js`.

### 11.2 Write the contract
Create `contracts/Greeter.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract Greeter {
    string public greeting;

    event GreetingChanged(address indexed by, string newGreeting);

    constructor(string memory initialGreeting) {
        greeting = initialGreeting;
    }

    function setGreeting(string memory newGreeting) external {
        greeting = newGreeting;
        emit GreetingChanged(msg.sender, newGreeting);
    }
}
```

This contract stores a string, exposes it, and lets anyone change it.

### 11.3 Compile it
```bash
npx hardhat compile
```

### 11.4 Add a network config
Edit `hardhat.config.js` to add Sepolia. You'll need a Sepolia RPC URL (get a free one from Alchemy or Infura) and a private key (the one from MetaMask you funded earlier — *use a throwaway test wallet, never your main wallet*).

```js
require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.24",
  networks: {
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL,
      accounts: [process.env.SEPOLIA_PRIVATE_KEY],
    },
  },
};
```

Create `.env` (and add it to `.gitignore`):
```
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY
SEPOLIA_PRIVATE_KEY=0xYOUR_TEST_WALLET_KEY
```

Install dotenv: `npm install --save-dev dotenv` and `require("dotenv").config();` at the top of the config.

### 11.5 Write a deploy script
`scripts/deploy.js`:

```js
const hre = require("hardhat");

async function main() {
  const Greeter = await hre.ethers.getContractFactory("Greeter");
  const greeter = await Greeter.deploy("hello, chain");
  await greeter.waitForDeployment();

  console.log("Greeter deployed to:", await greeter.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

### 11.6 Deploy
```bash
npx hardhat run scripts/deploy.js --network sepolia
```

You'll see an address printed to the console. Paste it into `sepolia.etherscan.io` and behold: **your contract, live on a public blockchain, readable by anyone, forever**.

### 11.7 Call it
Write a second script or use the Hardhat console:

```bash
npx hardhat console --network sepolia
```

```js
const Greeter = await ethers.getContractFactory("Greeter");
const greeter = Greeter.attach("0xYOUR_DEPLOYED_ADDRESS");
await greeter.greeting();                 // returns "hello, chain"
await greeter.setGreeting("hi again");    // sends a transaction
await greeter.greeting();                 // returns "hi again"
```

That's the full loop: read state (free), write state (costs gas), emit events, respond to them from a front-end.

## 12. Next developer steps

Once you've done Greeter:
1. Deploy an **ERC-20 token** using OpenZeppelin (five lines of Solidity).
2. Deploy an **ERC-721 NFT** with metadata.
3. Build a tiny React front-end with **wagmi + viem** that connects MetaMask and lets you call `setGreeting` from the browser.
4. Write Hardhat **tests** — this is the core skill and where you'll spend most of your professional blockchain time.
5. Move on to the 5 project tutorials in `09-practical-tutorial-5-domains.md`.

## 13. Security as a daily practice

As a developer, burn the following into your brain:

- **Always use OpenZeppelin contracts** for standard functionality. Don't reinvent ERC-20.
- **Never `tx.origin` for auth.** Use `msg.sender`.
- **Mind reentrancy.** Use `nonReentrant` modifier or follow checks-effects-interactions.
- **Write tests before deploying anywhere.** Test the happy path, the sad path, and the adversarial path.
- **Never deploy your first contract to mainnet.** Do Sepolia runs until you can recite the workflow in your sleep.
- **Don't put your real private key in a `.env`.** Use hardware wallets or key management tools in production.
- **Audit before you move real money.** Paid audits start in the low five figures. Worth every cent.

## 14. Getting stuck and unstuck

When something breaks — and it will:
- **Etherscan shows everything.** Look up the failed transaction; the revert reason is usually there.
- **Hardhat has verbose logs.** Run with `--verbose` and look at the stack trace.
- **Discord is where Web3 questions get answered** — each chain and tool has its own.
- **Stack Exchange for Ethereum** is excellent.
- **The documentation is actually good** for Ethereum, Hardhat, OpenZeppelin. Read it before guessing.

## Further reading
- Ethereum.org "Developers" portal — the canonical starting point
- OpenZeppelin docs — reference implementations for everything
- `docs/learning/blockchain/08-theory-tutorial.md` — the theory tutorial in this folder, for deeper concepts

## Next file to read
`04-who-uses-blockchain.md` — who's actually using this stuff in production today.
