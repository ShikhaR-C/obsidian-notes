# Build 5 Small Blockchain Apps Across Different Domains

A hands-on follow-up to the theory tutorial. You will build five mini-projects in five different domains: DeFi, supply chain, healthcare, identity, and governance. Each project is complete enough to deploy to a testnet and interact with from a frontend.

## What you'll learn

- How to structure, compile, and deploy Solidity contracts with Hardhat
- How to import and compose OpenZeppelin primitives instead of hand-rolling everything
- How to model real-world domains in contract storage
- How to protect contracts with access control, reentrancy guards, and role-based permissions
- How to integrate IPFS for off-chain storage
- How to issue soulbound NFTs and verify credentials
- How to build a minimal DAO with proposals, voting, and execution
- How to connect contracts to a React frontend with viem
- How to write a Hardhat deployment script and testing checklist

## Prerequisites

- You have read `08-theory-tutorial.md` (or have equivalent background)
- Node.js 18+ installed
- Basic familiarity with React (JSX, useState, useEffect)
- A code editor (VS Code recommended) and a terminal

### One-time setup for all five projects

Create a workspace and initialize a Hardhat project:

```bash
mkdir blockchain-five && cd blockchain-five
npm init -y
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
npm install @openzeppelin/contracts
npx hardhat init
```

Pick "Create a JavaScript project" when prompted. This gives you:

```
blockchain-five/
  contracts/
  scripts/
  test/
  hardhat.config.js
```

Edit `hardhat.config.js` for Solidity 0.8.20 and a local network:

```javascript
require("@nomicfoundation/hardhat-toolbox");

module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: { enabled: true, runs: 200 },
    },
  },
  networks: {
    hardhat: { chainId: 31337 },
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL || "",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
    },
  },
};
```

Start a local node in one terminal:

```bash
npx hardhat node
```

In another terminal you will run `npx hardhat run scripts/<script>.js --network localhost` for each project.

For the React frontend snippets, create a sibling directory:

```bash
cd ..
npm create vite@latest web -- --template react
cd web
npm install viem wagmi @tanstack/react-query
```

You can run each project's frontend snippet inside this `web/` app.

---

## Project 1 — Finance/DeFi: Simple Token Vault

### Problem statement

In DeFi, a **vault** lets users deposit a token and earn rewards passively. The classic use case: users deposit a "reward token", and over time their share grows proportionally to how long they stayed. This is the core mechanism behind staking, yield farming, and liquidity mining.

We will build:

1. An ERC-20 token (`RewardToken`).
2. A vault contract that lets users deposit and withdraw the token, and distributes newly minted reward tokens over time proportional to each user's time-weighted share.

### Domain context

DeFi (Decentralized Finance) recreates traditional financial services — lending, borrowing, trading, insurance — on-chain, without banks. Total value locked in DeFi has ranged from tens to hundreds of billions of dollars in recent years. Staking vaults, lending pools, and AMMs (automated market makers) are the three fundamental building blocks.

### Architecture

```
 ┌─────────┐  deposit(amount)  ┌─────────────┐
 │  User   │ ────────────────▶ │             │
 │         │ ◀──────────────── │   Vault     │
 │         │     rewards       │  (contract) │
 └─────────┘                   └─────────────┘
      ▲                               │
      │                               │ mints rewards
      │                               ▼
      │                       ┌─────────────┐
      └────── transfer ──────▶│ RewardToken │
                              │   (ERC-20)  │
                              └─────────────┘
```

Data model inside the vault:

```
totalDeposited      (uint256)
rewardRate          (tokens per second, global)
lastUpdate          (uint256 timestamp)
rewardPerTokenStored (accumulator)

per-user:
  balance[user]
  userRewardPerTokenPaid[user]
  rewards[user]
```

This is the canonical **Synthetix staking** math, used by nearly every yield farm since 2020.

### RewardToken contract

`contracts/RewardToken.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract RewardToken is ERC20, Ownable {
    constructor() ERC20("Reward Token", "RWD") Ownable(msg.sender) {
        _mint(msg.sender, 1_000_000 ether);
    }

    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
}
```

### Vault contract

`contracts/Vault.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

interface IMintableToken is IERC20 {
    function mint(address to, uint256 amount) external;
}

contract Vault is ReentrancyGuard, Ownable {
    IMintableToken public immutable token;

    uint256 public rewardRate;          // tokens per second, global
    uint256 public lastUpdate;
    uint256 public rewardPerTokenStored;
    uint256 public totalDeposited;

    mapping(address => uint256) public balanceOf;
    mapping(address => uint256) public userRewardPerTokenPaid;
    mapping(address => uint256) public rewards;

    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event RewardClaimed(address indexed user, uint256 amount);

    constructor(address _token, uint256 _rewardRate) Ownable(msg.sender) {
        token = IMintableToken(_token);
        rewardRate = _rewardRate;
        lastUpdate = block.timestamp;
    }

    modifier updateReward(address account) {
        rewardPerTokenStored = rewardPerToken();
        lastUpdate = block.timestamp;
        if (account != address(0)) {
            rewards[account] = earned(account);
            userRewardPerTokenPaid[account] = rewardPerTokenStored;
        }
        _;
    }

    function rewardPerToken() public view returns (uint256) {
        if (totalDeposited == 0) return rewardPerTokenStored;
        uint256 timeDelta = block.timestamp - lastUpdate;
        return rewardPerTokenStored + (timeDelta * rewardRate * 1e18) / totalDeposited;
    }

    function earned(address account) public view returns (uint256) {
        return
            (balanceOf[account] *
                (rewardPerToken() - userRewardPerTokenPaid[account])) /
            1e18 +
            rewards[account];
    }

    function deposit(uint256 amount) external nonReentrant updateReward(msg.sender) {
        require(amount > 0, "Zero deposit");
        balanceOf[msg.sender] += amount;
        totalDeposited += amount;
        require(token.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        emit Deposited(msg.sender, amount);
    }

    function withdraw(uint256 amount) external nonReentrant updateReward(msg.sender) {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");
        balanceOf[msg.sender] -= amount;
        totalDeposited -= amount;
        require(token.transfer(msg.sender, amount), "Transfer failed");
        emit Withdrawn(msg.sender, amount);
    }

    function claim() external nonReentrant updateReward(msg.sender) {
        uint256 reward = rewards[msg.sender];
        if (reward > 0) {
            rewards[msg.sender] = 0;
            token.mint(msg.sender, reward);
            emit RewardClaimed(msg.sender, reward);
        }
    }

    function setRewardRate(uint256 _rate) external onlyOwner updateReward(address(0)) {
        rewardRate = _rate;
    }
}
```

### How the math works

The key insight: instead of updating every user on every block, we maintain one global accumulator `rewardPerTokenStored`. Every time state changes (deposit, withdraw, claim), we:

1. Update the accumulator based on elapsed time and current total deposits.
2. Credit the calling user with their share since the last update.
3. Snapshot their accumulator value.

This is O(1) per transaction instead of O(N users), which is essential on-chain.

### Deployment script

`scripts/deploy-vault.js`:

```javascript
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying from:", deployer.address);

  const Token = await hre.ethers.getContractFactory("RewardToken");
  const token = await Token.deploy();
  await token.waitForDeployment();
  console.log("Token:", await token.getAddress());

  const Vault = await hre.ethers.getContractFactory("Vault");
  const rewardRate = hre.ethers.parseEther("0.01"); // 0.01 RWD per second
  const vault = await Vault.deploy(await token.getAddress(), rewardRate);
  await vault.waitForDeployment();
  console.log("Vault:", await vault.getAddress());

  // Give vault permission to mint rewards
  const tx = await token.transferOwnership(await vault.getAddress());
  await tx.wait();
  console.log("Ownership transferred");
}

main().catch((e) => { console.error(e); process.exit(1); });
```

Run:

```bash
npx hardhat run scripts/deploy-vault.js --network localhost
```

### Frontend snippet (viem + React)

```jsx
import { useState } from "react";
import { createPublicClient, createWalletClient, custom, http, parseEther, formatEther } from "viem";
import { hardhat } from "viem/chains";

const VAULT_ADDRESS = "0x...";
const VAULT_ABI = [
  { name: "deposit", type: "function", stateMutability: "nonpayable", inputs: [{ name: "amount", type: "uint256" }], outputs: [] },
  { name: "withdraw", type: "function", stateMutability: "nonpayable", inputs: [{ name: "amount", type: "uint256" }], outputs: [] },
  { name: "claim", type: "function", stateMutability: "nonpayable", inputs: [], outputs: [] },
  { name: "earned", type: "function", stateMutability: "view", inputs: [{ name: "user", type: "address" }], outputs: [{ type: "uint256" }] },
];

export function VaultApp() {
  const [amount, setAmount] = useState("");
  const [earned, setEarned] = useState("0");

  const publicClient = createPublicClient({ chain: hardhat, transport: http() });

  async function refreshEarned(address) {
    const value = await publicClient.readContract({
      address: VAULT_ADDRESS,
      abi: VAULT_ABI,
      functionName: "earned",
      args: [address],
    });
    setEarned(formatEther(value));
  }

  async function deposit() {
    const [account] = await window.ethereum.request({ method: "eth_requestAccounts" });
    const wallet = createWalletClient({ chain: hardhat, transport: custom(window.ethereum) });
    await wallet.writeContract({
      address: VAULT_ADDRESS,
      abi: VAULT_ABI,
      functionName: "deposit",
      args: [parseEther(amount)],
      account,
    });
  }

  return (
    <div>
      <h2>Staking Vault</h2>
      <input value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="Amount (RWD)" />
      <button onClick={deposit}>Deposit</button>
      <p>Earned: {earned} RWD</p>
    </div>
  );
}
```

Note: before calling `deposit` the user must first call `approve(vault, amount)` on the token contract — this is a separate transaction. Add an approve button, or use `approveMax` on first deposit.

### Testing checklist

- Deposit increases `balanceOf[user]` and `totalDeposited` by the correct amount
- Withdraw decreases both and transfers tokens back
- After depositing, `earned(user)` grows linearly with time
- `claim` transfers the earned amount and resets `rewards[user]`
- Two users depositing at different times receive rewards proportional to deposit size × time
- `withdraw` more than balance reverts
- Reentrancy: a malicious token cannot reenter `deposit`

Example Hardhat test to get started:

```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Vault", function () {
  it("distributes rewards over time", async function () {
    const [owner, alice] = await ethers.getSigners();
    const Token = await ethers.getContractFactory("RewardToken");
    const token = await Token.deploy();
    const Vault = await ethers.getContractFactory("Vault");
    const vault = await Vault.deploy(await token.getAddress(), ethers.parseEther("1"));
    await token.transferOwnership(await vault.getAddress());

    await token.mint(alice.address, ethers.parseEther("100"));
    await token.connect(alice).approve(await vault.getAddress(), ethers.parseEther("100"));
    await vault.connect(alice).deposit(ethers.parseEther("100"));

    await ethers.provider.send("evm_increaseTime", [60]);
    await ethers.provider.send("evm_mine");

    const earned = await vault.earned(alice.address);
    expect(earned).to.be.gt(0);
  });
});
```

### How to extend this

- Add a deposit/withdrawal fee
- Add a lock-up period with early-exit penalties
- Cap the reward rate per user
- Add a second staking token
- Integrate a price oracle to compute rewards in USD
- Add emergency withdrawal that skips reward calculation

---

## Project 2 — Supply Chain: Product Provenance Tracker

### Problem statement

Counterfeiting costs the global economy over $500 billion per year. A supply-chain tracker on a blockchain lets a manufacturer produce a digital "passport" for each physical product. At every transition — manufacturer to distributor to retailer to consumer — the current holder signs an on-chain transition. Anyone scanning the product's QR code can verify its authentic history without trusting any single party.

### Domain context

This pattern is already in production use: IBM Food Trust tracks mangoes and seafood; LVMH's Aura tracks luxury goods; De Beers' Tracr tracks diamonds. The common pattern: roles for each party, events emitted at each transition, and a public `view` function to read history.

### Architecture

```
Manufacturer ──▶ Distributor ──▶ Retailer ──▶ Consumer
     │              │              │            │
     └──── signed transitions on-chain ─────────┘

QR code ──▶ scan ──▶ frontend ──▶ read contract ──▶ render history
```

Data model:

```
Stages:           Created, WithDistributor, WithRetailer, Sold
Product:          id, currentOwner, currentStage, history[]
HistoryEntry:     actor, stage, timestamp, note
Roles:            MANUFACTURER_ROLE, DISTRIBUTOR_ROLE, RETAILER_ROLE
```

### Contract

`contracts/Provenance.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";

contract Provenance is AccessControl {
    bytes32 public constant MANUFACTURER_ROLE = keccak256("MANUFACTURER_ROLE");
    bytes32 public constant DISTRIBUTOR_ROLE = keccak256("DISTRIBUTOR_ROLE");
    bytes32 public constant RETAILER_ROLE = keccak256("RETAILER_ROLE");

    enum Stage { Created, WithDistributor, WithRetailer, Sold }

    struct HistoryEntry {
        address actor;
        Stage stage;
        uint256 timestamp;
        string note;
    }

    struct Product {
        uint256 id;
        address currentOwner;
        Stage currentStage;
        bool exists;
    }

    uint256 public nextProductId;
    mapping(uint256 => Product) public products;
    mapping(uint256 => HistoryEntry[]) private histories;

    event ProductCreated(uint256 indexed id, address indexed manufacturer);
    event ProductTransferred(uint256 indexed id, address indexed from, address indexed to, Stage newStage);

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function createProduct(string calldata note) external onlyRole(MANUFACTURER_ROLE) returns (uint256) {
        uint256 id = nextProductId++;
        products[id] = Product({
            id: id,
            currentOwner: msg.sender,
            currentStage: Stage.Created,
            exists: true
        });
        histories[id].push(HistoryEntry({
            actor: msg.sender,
            stage: Stage.Created,
            timestamp: block.timestamp,
            note: note
        }));
        emit ProductCreated(id, msg.sender);
        return id;
    }

    function transferToDistributor(uint256 id, address distributor, string calldata note)
        external
        onlyRole(MANUFACTURER_ROLE)
    {
        require(products[id].exists, "Unknown product");
        require(products[id].currentOwner == msg.sender, "Not current owner");
        require(products[id].currentStage == Stage.Created, "Wrong stage");
        require(hasRole(DISTRIBUTOR_ROLE, distributor), "Not a distributor");
        _transfer(id, distributor, Stage.WithDistributor, note);
    }

    function transferToRetailer(uint256 id, address retailer, string calldata note)
        external
        onlyRole(DISTRIBUTOR_ROLE)
    {
        require(products[id].currentOwner == msg.sender, "Not current owner");
        require(products[id].currentStage == Stage.WithDistributor, "Wrong stage");
        require(hasRole(RETAILER_ROLE, retailer), "Not a retailer");
        _transfer(id, retailer, Stage.WithRetailer, note);
    }

    function sellToConsumer(uint256 id, address consumer, string calldata note)
        external
        onlyRole(RETAILER_ROLE)
    {
        require(products[id].currentOwner == msg.sender, "Not current owner");
        require(products[id].currentStage == Stage.WithRetailer, "Wrong stage");
        _transfer(id, consumer, Stage.Sold, note);
    }

    function _transfer(uint256 id, address to, Stage newStage, string calldata note) private {
        address from = products[id].currentOwner;
        products[id].currentOwner = to;
        products[id].currentStage = newStage;
        histories[id].push(HistoryEntry({
            actor: to,
            stage: newStage,
            timestamp: block.timestamp,
            note: note
        }));
        emit ProductTransferred(id, from, to, newStage);
    }

    function getHistory(uint256 id) external view returns (HistoryEntry[] memory) {
        require(products[id].exists, "Unknown product");
        return histories[id];
    }
}
```

### Deployment script

`scripts/deploy-provenance.js`:

```javascript
const hre = require("hardhat");

async function main() {
  const [admin, manufacturer, distributor, retailer] = await hre.ethers.getSigners();
  const Provenance = await hre.ethers.getContractFactory("Provenance");
  const provenance = await Provenance.deploy();
  await provenance.waitForDeployment();
  console.log("Provenance:", await provenance.getAddress());

  const MFG = await provenance.MANUFACTURER_ROLE();
  const DIST = await provenance.DISTRIBUTOR_ROLE();
  const RET = await provenance.RETAILER_ROLE();

  await (await provenance.grantRole(MFG, manufacturer.address)).wait();
  await (await provenance.grantRole(DIST, distributor.address)).wait();
  await (await provenance.grantRole(RET, retailer.address)).wait();

  console.log("Roles granted");
}

main().catch((e) => { console.error(e); process.exit(1); });
```

### Frontend: QR scan and verify

```jsx
import { useEffect, useState } from "react";
import { createPublicClient, http } from "viem";
import { hardhat } from "viem/chains";

const ADDRESS = "0x...";
const ABI = [
  {
    name: "getHistory",
    type: "function",
    stateMutability: "view",
    inputs: [{ name: "id", type: "uint256" }],
    outputs: [{
      type: "tuple[]",
      components: [
        { name: "actor", type: "address" },
        { name: "stage", type: "uint8" },
        { name: "timestamp", type: "uint256" },
        { name: "note", type: "string" },
      ],
    }],
  },
];
const STAGES = ["Created", "With Distributor", "With Retailer", "Sold"];

export function Verify({ productId }) {
  const [history, setHistory] = useState([]);
  const client = createPublicClient({ chain: hardhat, transport: http() });

  useEffect(() => {
    (async () => {
      const h = await client.readContract({
        address: ADDRESS,
        abi: ABI,
        functionName: "getHistory",
        args: [BigInt(productId)],
      });
      setHistory(h);
    })();
  }, [productId]);

  return (
    <div>
      <h3>Product #{productId}</h3>
      <ol>
        {history.map((entry, i) => (
          <li key={i}>
            <strong>{STAGES[entry.stage]}</strong> — {entry.actor}
            <br />
            <small>{new Date(Number(entry.timestamp) * 1000).toLocaleString()}</small>
            <br />
            <em>{entry.note}</em>
          </li>
        ))}
      </ol>
    </div>
  );
}
```

In production, the QR code would encode a URL like `https://myapp.com/verify/<productId>` and the frontend reads the history from the chain.

### Testing checklist

- Only MANUFACTURER can create products
- Only DISTRIBUTOR can transfer to retailer
- Only RETAILER can sell to consumer
- Wrong stage transitions revert
- History grows correctly at each step
- `getHistory` returns in chronological order
- Non-role addresses cannot transfer

### How to extend this

- Batch creation: `createProducts(uint256 count)` for factory lines
- Attach IPFS hash of product certification PDF
- Allow consumers to transfer ownership after sale (for resale markets)
- Add geo coordinates to each history entry
- Integrate Chainlink for authenticated temperature sensor data (cold chain)

---

## Project 3 — Healthcare: Medical Record Consent Registry

### Problem statement

Medical records are sensitive; you cannot and should not put them on-chain. But **consent** to access them can be. A patient should own the right to grant or revoke access to specific providers, on their own terms, with a public audit trail that regulators and the patient herself can inspect.

We will build a consent registry where:

- Patients upload encrypted medical records to IPFS
- They store only the IPFS hash on-chain, associated with their address
- They grant access to specific provider addresses
- They can revoke access at any time
- All grants and revocations emit events

### Domain context

HIPAA in the US and GDPR in the EU both emphasize patient ownership of data and auditability. Projects like MedRec (MIT), Medicalchain, and Patientory have explored this space. The design pattern used here — "on-chain metadata + off-chain storage + explicit consent" — is the industry standard.

### Architecture

```
┌─────────┐                            ┌──────────┐
│ Patient │ ──── encrypt + upload ──▶ │   IPFS   │
│         │                            └──────────┘
│         │    store CID + grant                │
│         │ ─────────────────────┐              │
│         │                      ▼              │
│         │                ┌──────────────┐     │
│         │                │   Registry   │     │
│         │                │  (contract)  │     │
│         │                └──────────────┘     │
│         │                      ▲              │
└─────────┘                      │              │
                                 │ grant check  │
                           ┌──────────┐         │
                           │ Provider │         │
                           │          │ ◀───────┘
                           └──────────┘    fetch CID
                                           decrypt
```

Data model:

```
per patient:
  recordCid (string)  – IPFS CID of the patient's records bundle
  grants[provider] -> GrantInfo{ granted, until, note }

Events: RecordUpdated, AccessGranted, AccessRevoked
```

### Contract

`contracts/ConsentRegistry.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ConsentRegistry {
    struct Grant {
        bool granted;
        uint256 expiresAt;
        string note;
    }

    // patient => current encrypted record pointer (IPFS CID)
    mapping(address => string) public recordCid;

    // patient => provider => grant
    mapping(address => mapping(address => Grant)) private _grants;

    event RecordUpdated(address indexed patient, string newCid);
    event AccessGranted(address indexed patient, address indexed provider, uint256 expiresAt, string note);
    event AccessRevoked(address indexed patient, address indexed provider);

    function setRecordCid(string calldata cid) external {
        recordCid[msg.sender] = cid;
        emit RecordUpdated(msg.sender, cid);
    }

    function grantAccess(address provider, uint256 durationSeconds, string calldata note) external {
        require(provider != address(0), "Zero provider");
        require(durationSeconds > 0 && durationSeconds <= 365 days, "Bad duration");
        uint256 expiresAt = block.timestamp + durationSeconds;
        _grants[msg.sender][provider] = Grant({
            granted: true,
            expiresAt: expiresAt,
            note: note
        });
        emit AccessGranted(msg.sender, provider, expiresAt, note);
    }

    function revokeAccess(address provider) external {
        delete _grants[msg.sender][provider];
        emit AccessRevoked(msg.sender, provider);
    }

    function hasAccess(address patient, address provider) external view returns (bool) {
        Grant memory g = _grants[patient][provider];
        return g.granted && block.timestamp < g.expiresAt;
    }

    function getGrant(address patient, address provider) external view returns (Grant memory) {
        return _grants[patient][provider];
    }
}
```

### Privacy pattern

Critical: the chain only stores:

1. The IPFS CID of an **encrypted** bundle.
2. The boolean grant + expiry.

The actual encryption keys are shared out-of-band with providers when access is granted (e.g., via ECIES using the provider's public key). A naive version can use a shared symmetric key exchanged over an off-chain channel; a production version uses per-grant key encapsulation.

### Deployment script

`scripts/deploy-consent.js`:

```javascript
const hre = require("hardhat");

async function main() {
  const Registry = await hre.ethers.getContractFactory("ConsentRegistry");
  const registry = await Registry.deploy();
  await registry.waitForDeployment();
  console.log("ConsentRegistry:", await registry.getAddress());
}

main().catch((e) => { console.error(e); process.exit(1); });
```

### Frontend: upload and grant

```jsx
import { useState } from "react";
import { createWalletClient, custom, parseAbi } from "viem";
import { hardhat } from "viem/chains";

const ABI = parseAbi([
  "function setRecordCid(string cid)",
  "function grantAccess(address provider, uint256 durationSeconds, string note)",
  "function revokeAccess(address provider)",
]);
const ADDRESS = "0x...";

async function uploadToIpfs(file) {
  // In production: pinata, web3.storage, or a self-hosted IPFS node.
  // Placeholder: assume the backend returns a CID.
  const form = new FormData();
  form.append("file", file);
  const res = await fetch("/api/pin", { method: "POST", body: form });
  const { cid } = await res.json();
  return cid;
}

export function PatientApp() {
  const [providerAddr, setProviderAddr] = useState("");

  async function upload(file) {
    const cid = await uploadToIpfs(file);
    const [account] = await window.ethereum.request({ method: "eth_requestAccounts" });
    const wallet = createWalletClient({ chain: hardhat, transport: custom(window.ethereum) });
    await wallet.writeContract({
      address: ADDRESS,
      abi: ABI,
      functionName: "setRecordCid",
      args: [cid],
      account,
    });
  }

  async function grant() {
    const [account] = await window.ethereum.request({ method: "eth_requestAccounts" });
    const wallet = createWalletClient({ chain: hardhat, transport: custom(window.ethereum) });
    await wallet.writeContract({
      address: ADDRESS,
      abi: ABI,
      functionName: "grantAccess",
      args: [providerAddr, 30n * 24n * 3600n, "One-month check-up"],
      account,
    });
  }

  return (
    <div>
      <h2>My Medical Records</h2>
      <input type="file" onChange={(e) => upload(e.target.files[0])} />
      <input value={providerAddr} onChange={(e) => setProviderAddr(e.target.value)} placeholder="Provider address" />
      <button onClick={grant}>Grant 30-day access</button>
    </div>
  );
}
```

### Testing checklist

- A patient can set and update their own CID
- `grantAccess` stores the grant and emits the event
- `hasAccess` returns true during the window and false after expiry
- `revokeAccess` sets `hasAccess` to false immediately
- Only the patient can grant or revoke their own records
- Grant duration above 365 days reverts
- No one can overwrite another patient's CID

### How to extend this

- Support multiple records per patient (array of CIDs by category)
- Integrate Ethereum Attestation Service for verifiable credentials
- Add emergency access that only triggers after an off-chain oracle confirms hospitalization
- Encrypt CIDs themselves so providers only see what they have access to
- Use ZK proofs to show "this patient consented" without revealing which patient

---

## Project 4 — Identity/Credentials: On-Chain Certificate Issuer

### Problem statement

Universities, bootcamps, and certification bodies issue credentials to millions of people a year. Paper credentials are easy to forge; digital PDFs even easier. A non-transferable NFT ("soulbound token") issued to the student's wallet is:

- Cryptographically verifiable as issued by a specific authority
- Permanently associated with the student's wallet
- Non-transferable (so cannot be sold or faked)
- Instantly verifiable by any employer with no middleman

### Domain context

The concept of "soulbound tokens" was proposed by Vitalik Buterin, Glen Weyl, and Puja Ohlhaver in 2022. Projects like Gitcoin Passport, ENS, POAP, and Binance Account Bound tokens all use variations of this pattern. ERC-5192 standardizes the soulbound property.

We will also add **Merkle proof** bulk issuance: instead of paying gas to mint 1,000 certificates, the issuer publishes a Merkle root, and each student mints their own by presenting a proof.

### Architecture

```
Issuer
  │
  │ 1. Compute Merkle root of all eligible (address, courseId) pairs
  │ 2. Call publishRoot(root)
  ▼
Contract (ERC-721 with _update override preventing transfer)
  │
  ▲
  │ 3. Student calls claim(proof, courseId) from their wallet
  │ 4. Contract verifies proof against root, mints token
  │
Student wallet
  │
  │ 5. Employer queries ownerOf/tokenURI to verify
```

### Contract

`contracts/Certificate.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

contract Certificate is ERC721, Ownable {
    uint256 public nextTokenId;

    // courseId => merkle root of eligible holders
    mapping(uint256 => bytes32) public courseRoots;
    mapping(uint256 => string) public courseURIs;

    // (address, courseId) => claimed
    mapping(address => mapping(uint256 => bool)) public claimed;

    // tokenId => courseId
    mapping(uint256 => uint256) public tokenCourse;

    event CourseAdded(uint256 indexed courseId, bytes32 root, string uri);
    event CertificateClaimed(address indexed student, uint256 indexed courseId, uint256 tokenId);

    error SoulboundTokenNonTransferable();

    constructor() ERC721("Certificate", "CERT") Ownable(msg.sender) {}

    function addCourse(uint256 courseId, bytes32 root, string calldata uri) external onlyOwner {
        courseRoots[courseId] = root;
        courseURIs[courseId] = uri;
        emit CourseAdded(courseId, root, uri);
    }

    function claim(uint256 courseId, bytes32[] calldata proof) external {
        require(!claimed[msg.sender][courseId], "Already claimed");
        bytes32 root = courseRoots[courseId];
        require(root != bytes32(0), "Unknown course");

        bytes32 leaf = keccak256(abi.encodePacked(msg.sender, courseId));
        require(MerkleProof.verify(proof, root, leaf), "Invalid proof");

        claimed[msg.sender][courseId] = true;
        uint256 tokenId = nextTokenId++;
        tokenCourse[tokenId] = courseId;
        _safeMint(msg.sender, tokenId);
        emit CertificateClaimed(msg.sender, courseId, tokenId);
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        _requireOwned(tokenId);
        return courseURIs[tokenCourse[tokenId]];
    }

    // Soulbound: block transfers
    function _update(address to, uint256 tokenId, address auth) internal override returns (address) {
        address from = _ownerOf(tokenId);
        if (from != address(0) && to != address(0)) {
            revert SoulboundTokenNonTransferable();
        }
        return super._update(to, tokenId, auth);
    }
}
```

The `_update` override is the soulbound trick: it allows mint (from == 0) and burn (to == 0), but blocks any transfer between two non-zero addresses.

### Building a Merkle tree off-chain

`scripts/build-tree.js`:

```javascript
const { StandardMerkleTree } = require("@openzeppelin/merkle-tree");
const fs = require("fs");

const students = [
  { address: "0x1111...1111", courseId: 1 },
  { address: "0x2222...2222", courseId: 1 },
  { address: "0x3333...3333", courseId: 1 },
];

const values = students.map((s) => [s.address, s.courseId]);
const tree = StandardMerkleTree.of(values, ["address", "uint256"]);

console.log("Root:", tree.root);
fs.writeFileSync("tree.json", JSON.stringify(tree.dump()));

// Proof for first student
for (const [i, v] of tree.entries()) {
  const proof = tree.getProof(i);
  console.log(`Proof for ${v[0]}:`, proof);
}
```

Install with:

```bash
npm install @openzeppelin/merkle-tree
```

### Deployment script

`scripts/deploy-certificate.js`:

```javascript
const hre = require("hardhat");

async function main() {
  const Cert = await hre.ethers.getContractFactory("Certificate");
  const cert = await Cert.deploy();
  await cert.waitForDeployment();
  console.log("Certificate:", await cert.getAddress());

  // After building the tree off-chain, call:
  const root = "0x..."; // from build-tree.js
  const uri = "ipfs://bafy.../solidity-101.json";
  await (await cert.addCourse(1, root, uri)).wait();
  console.log("Course 1 added");
}

main().catch((e) => { console.error(e); process.exit(1); });
```

### Frontend: student claim

```jsx
import { useState } from "react";
import { createWalletClient, custom, parseAbi } from "viem";
import { hardhat } from "viem/chains";

const ABI = parseAbi([
  "function claim(uint256 courseId, bytes32[] proof)",
]);
const ADDRESS = "0x...";

export function ClaimCertificate() {
  const [status, setStatus] = useState("");

  async function claim() {
    const [account] = await window.ethereum.request({ method: "eth_requestAccounts" });
    // Fetch the student's Merkle proof from the issuer's website or a JSON endpoint:
    const res = await fetch(`/api/proof?address=${account}&courseId=1`);
    const { proof } = await res.json();

    const wallet = createWalletClient({ chain: hardhat, transport: custom(window.ethereum) });
    const hash = await wallet.writeContract({
      address: ADDRESS,
      abi: ABI,
      functionName: "claim",
      args: [1n, proof],
      account,
    });
    setStatus(`Claimed: ${hash}`);
  }

  return (
    <div>
      <h2>Claim Your Certificate</h2>
      <button onClick={claim}>Claim</button>
      <p>{status}</p>
    </div>
  );
}
```

### Verifier (for employers)

```javascript
import { createPublicClient, http } from "viem";
import { hardhat } from "viem/chains";

const client = createPublicClient({ chain: hardhat, transport: http() });

export async function verifyHolder(address, courseId) {
  const claimed = await client.readContract({
    address: "0x...",
    abi: [{
      name: "claimed",
      type: "function",
      stateMutability: "view",
      inputs: [{ type: "address" }, { type: "uint256" }],
      outputs: [{ type: "bool" }],
    }],
    functionName: "claimed",
    args: [address, BigInt(courseId)],
  });
  return claimed;
}
```

### Testing checklist

- `addCourse` stores the root and is owner-gated
- `claim` with a valid proof mints a token
- `claim` with an invalid proof reverts
- Double-claim reverts
- `tokenURI` returns the course URI
- Transfer attempts revert with `SoulboundTokenNonTransferable`
- Burn (if allowed) succeeds

### How to extend this

- Add expiration dates per certificate (add `issuedAt` and `validUntil`)
- Allow the issuer to revoke individual certificates
- Support delegated verifiers (other contracts that can read holder status)
- Add multi-issuer support — a factory that deploys per-institution contracts
- Allow certificate holders to attach reviews/endorsements (with their own signature)

---

## Project 5 — Governance: Simple DAO with Proposals and Voting

### Problem statement

A DAO (Decentralized Autonomous Organization) coordinates a group of token holders to make collective decisions and execute them on-chain. The core loop is:

1. Someone proposes an action (e.g., "send 1,000 DAO tokens to this address")
2. Token holders vote during a fixed window
3. If the proposal passes quorum and majority, it can be executed after a timelock

### Domain context

Real DAOs today manage billions of dollars: Uniswap, Compound, Aave, MakerDAO, Optimism. The open-source reference is OpenZeppelin's Governor + Timelock contracts. Here we will build a simplified version from scratch so you understand every mechanic, then mention the production path.

### Architecture

```
            ┌──────────────┐
            │   Gov Token  │  balances determine voting power
            └──────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│               SimpleDAO               │
│ ┌─────────┐  ┌───────┐  ┌───────────┐ │
│ │ propose │─▶│ vote  │─▶│ execute   │ │
│ └─────────┘  └───────┘  └───────────┘ │
│                                       │
│  Proposal { target, data, value,      │
│             startTime, endTime,       │
│             yesVotes, noVotes,        │
│             executed, state }         │
└───────────────────────────────────────┘
                   │
                   ▼
           external contract call
```

State machine:

```
Pending ──(start)──▶ Active ──(end, pass)──▶ Succeeded ──(execute)──▶ Executed
                              │
                              └──(end, fail)──▶ Defeated
```

### Contracts

`contracts/GovToken.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract GovToken is ERC20 {
    constructor() ERC20("Governance Token", "GOV") {
        _mint(msg.sender, 1_000_000 ether);
    }
}
```

`contracts/SimpleDAO.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract SimpleDAO {
    enum ProposalState { Pending, Active, Defeated, Succeeded, Executed }

    struct Proposal {
        address proposer;
        address target;
        uint256 value;
        bytes data;
        string description;
        uint256 startTime;
        uint256 endTime;
        uint256 yesVotes;
        uint256 noVotes;
        bool executed;
        mapping(address => bool) hasVoted;
    }

    IERC20 public immutable govToken;
    uint256 public votingPeriod;   // seconds
    uint256 public timelock;       // seconds after end before execute
    uint256 public quorumVotes;    // minimum yes+no
    uint256 public proposalCount;

    mapping(uint256 => Proposal) private proposals;

    event ProposalCreated(uint256 indexed id, address indexed proposer, string description);
    event VoteCast(uint256 indexed id, address indexed voter, bool support, uint256 weight);
    event ProposalExecuted(uint256 indexed id);

    constructor(address _govToken, uint256 _votingPeriod, uint256 _timelock, uint256 _quorum) {
        govToken = IERC20(_govToken);
        votingPeriod = _votingPeriod;
        timelock = _timelock;
        quorumVotes = _quorum;
    }

    function propose(address target, uint256 value, bytes calldata data, string calldata description)
        external
        returns (uint256)
    {
        require(govToken.balanceOf(msg.sender) > 0, "No voting power");
        uint256 id = proposalCount++;
        Proposal storage p = proposals[id];
        p.proposer = msg.sender;
        p.target = target;
        p.value = value;
        p.data = data;
        p.description = description;
        p.startTime = block.timestamp;
        p.endTime = block.timestamp + votingPeriod;
        emit ProposalCreated(id, msg.sender, description);
        return id;
    }

    function vote(uint256 id, bool support) external {
        Proposal storage p = proposals[id];
        require(block.timestamp >= p.startTime, "Not started");
        require(block.timestamp < p.endTime, "Voting ended");
        require(!p.hasVoted[msg.sender], "Already voted");
        uint256 weight = govToken.balanceOf(msg.sender);
        require(weight > 0, "No voting power");
        p.hasVoted[msg.sender] = true;
        if (support) p.yesVotes += weight;
        else p.noVotes += weight;
        emit VoteCast(id, msg.sender, support, weight);
    }

    function state(uint256 id) public view returns (ProposalState) {
        Proposal storage p = proposals[id];
        if (p.executed) return ProposalState.Executed;
        if (block.timestamp < p.startTime) return ProposalState.Pending;
        if (block.timestamp < p.endTime) return ProposalState.Active;
        uint256 total = p.yesVotes + p.noVotes;
        if (total < quorumVotes) return ProposalState.Defeated;
        if (p.yesVotes > p.noVotes) return ProposalState.Succeeded;
        return ProposalState.Defeated;
    }

    function execute(uint256 id) external payable {
        Proposal storage p = proposals[id];
        require(state(id) == ProposalState.Succeeded, "Not succeeded");
        require(block.timestamp >= p.endTime + timelock, "Timelock not elapsed");
        p.executed = true;
        (bool ok, ) = p.target.call{value: p.value}(p.data);
        require(ok, "Execution failed");
        emit ProposalExecuted(id);
    }

    function getProposal(uint256 id) external view returns (
        address proposer,
        address target,
        uint256 value,
        bytes memory data,
        string memory description,
        uint256 startTime,
        uint256 endTime,
        uint256 yesVotes,
        uint256 noVotes,
        bool executed
    ) {
        Proposal storage p = proposals[id];
        return (
            p.proposer, p.target, p.value, p.data, p.description,
            p.startTime, p.endTime, p.yesVotes, p.noVotes, p.executed
        );
    }

    receive() external payable {}
}
```

### Note on voting power

This simple DAO uses `balanceOf` at execution time. A real DAO uses **snapshots** taken at proposal creation time (via ERC20Votes) to prevent users from buying tokens, voting, and immediately selling. To upgrade: import `ERC20Votes` from OpenZeppelin and use `getPastVotes(voter, blockNumber)` instead of `balanceOf`.

### Deployment script

`scripts/deploy-dao.js`:

```javascript
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const Token = await hre.ethers.getContractFactory("GovToken");
  const token = await Token.deploy();
  await token.waitForDeployment();
  console.log("GovToken:", await token.getAddress());

  const DAO = await hre.ethers.getContractFactory("SimpleDAO");
  const dao = await DAO.deploy(
    await token.getAddress(),
    3 * 24 * 3600,            // 3-day voting period
    1 * 24 * 3600,            // 1-day timelock
    hre.ethers.parseEther("100000") // quorum: 100k tokens
  );
  await dao.waitForDeployment();
  console.log("SimpleDAO:", await dao.getAddress());

  // Optional: fund the DAO with ETH for treasury actions
  await deployer.sendTransaction({
    to: await dao.getAddress(),
    value: hre.ethers.parseEther("10"),
  });
}

main().catch((e) => { console.error(e); process.exit(1); });
```

### Example: proposing a treasury transfer

```javascript
const { ethers } = require("hardhat");

async function main() {
  const dao = await ethers.getContractAt("SimpleDAO", "0x...");
  const recipient = "0xaaaa...aaaa";
  const amount = ethers.parseEther("1");

  // The DAO will call: recipient.call{value: 1 ether}("")
  const data = "0x"; // empty calldata — simple ETH transfer
  const tx = await dao.propose(recipient, amount, data, "Pay contributor for April");
  const receipt = await tx.wait();
  console.log("Proposal created in tx:", receipt.hash);
}

main();
```

For calling contract functions, encode the calldata:

```javascript
const iface = new ethers.Interface(["function transfer(address,uint256)"]);
const data = iface.encodeFunctionData("transfer", [recipient, amount]);
await dao.propose(tokenAddress, 0, data, "Send 1000 GOV to Alice");
```

### Frontend: list proposals and vote

```jsx
import { useEffect, useState } from "react";
import { createPublicClient, createWalletClient, custom, http, parseAbi } from "viem";
import { hardhat } from "viem/chains";

const ABI = parseAbi([
  "function proposalCount() view returns (uint256)",
  "function getProposal(uint256) view returns (address,address,uint256,bytes,string,uint256,uint256,uint256,uint256,bool)",
  "function state(uint256) view returns (uint8)",
  "function vote(uint256 id, bool support)",
  "function execute(uint256 id) payable",
]);
const ADDRESS = "0x...";
const STATES = ["Pending", "Active", "Defeated", "Succeeded", "Executed"];

export function DaoApp() {
  const [proposals, setProposals] = useState([]);
  const client = createPublicClient({ chain: hardhat, transport: http() });

  useEffect(() => {
    (async () => {
      const count = await client.readContract({
        address: ADDRESS, abi: ABI, functionName: "proposalCount",
      });
      const list = [];
      for (let i = 0n; i < count; i++) {
        const p = await client.readContract({
          address: ADDRESS, abi: ABI, functionName: "getProposal", args: [i],
        });
        const s = await client.readContract({
          address: ADDRESS, abi: ABI, functionName: "state", args: [i],
        });
        list.push({ id: i, description: p[4], yes: p[7], no: p[8], state: s });
      }
      setProposals(list);
    })();
  }, []);

  async function cast(id, support) {
    const [account] = await window.ethereum.request({ method: "eth_requestAccounts" });
    const wallet = createWalletClient({ chain: hardhat, transport: custom(window.ethereum) });
    await wallet.writeContract({
      address: ADDRESS, abi: ABI, functionName: "vote",
      args: [id, support], account,
    });
  }

  return (
    <div>
      <h2>DAO Proposals</h2>
      {proposals.map((p) => (
        <div key={p.id.toString()} style={{ border: "1px solid #ccc", padding: 12, margin: 8 }}>
          <h4>#{p.id.toString()} — {p.description}</h4>
          <p>State: {STATES[p.state]}</p>
          <p>Yes: {p.yes.toString()} / No: {p.no.toString()}</p>
          {p.state === 1 && (
            <>
              <button onClick={() => cast(p.id, true)}>Vote Yes</button>
              <button onClick={() => cast(p.id, false)}>Vote No</button>
            </>
          )}
        </div>
      ))}
    </div>
  );
}
```

### Testing checklist

- Propose with zero balance reverts
- Voting before start time reverts
- Voting after end time reverts
- Double vote reverts
- State progression: Pending → Active → Succeeded/Defeated → Executed
- Execute before timelock reverts
- Execute on a defeated proposal reverts
- Quorum enforcement (yes+no below quorum = Defeated)
- Voting weight equals balance at vote time
- Execution correctly calls the target and forwards value

Example test:

```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("SimpleDAO", function () {
  it("runs a full proposal lifecycle", async function () {
    const [deployer, voter] = await ethers.getSigners();
    const Token = await ethers.getContractFactory("GovToken");
    const token = await Token.deploy();
    await token.transfer(voter.address, ethers.parseEther("200000"));

    const DAO = await ethers.getContractFactory("SimpleDAO");
    const dao = await DAO.deploy(
      await token.getAddress(),
      3600, 600, ethers.parseEther("100000")
    );

    await dao.propose(voter.address, 0, "0x", "Test");
    await dao.connect(voter).vote(0, true);

    await ethers.provider.send("evm_increaseTime", [3601 + 601]);
    await ethers.provider.send("evm_mine");

    expect(await dao.state(0)).to.equal(3); // Succeeded
    await dao.execute(0);
    expect(await dao.state(0)).to.equal(4); // Executed
  });
});
```

### How to extend this

- Add **snapshot voting** with `ERC20Votes` so voters cannot game balances mid-vote
- Add **quadratic voting** (sqrt of token balance) to reduce whale influence
- Add **delegation** so small holders can delegate to representatives
- Split proposal types: parameter changes, treasury spends, contract upgrades
- Use a separate `TimelockController` (OpenZeppelin) as the executor so the DAO can hold funds via the timelock
- Add a "cancel" function for the proposer or emergency multisig
- Move on to the full OpenZeppelin Governor contract set — these are what production DAOs actually use

---

## Wrapping up

You have now built five production-shaped mini-apps across five very different domains. Each one touches a different pattern:

1. **Vault** — reward math with O(1) accumulators, reentrancy guards, ownership of token minting
2. **Provenance** — role-based access control, state machines, public audit trails
3. **Consent registry** — off-chain storage with on-chain authorization, time-bounded grants
4. **Certificate** — ERC-721 with soulbound extension, Merkle proofs for scalable issuance
5. **DAO** — proposal lifecycle, voting windows, timelocks, arbitrary execution

If you work through all five — actually deploy them, run the tests, wire the frontends, break them on purpose and fix them — you will have the working knowledge of a junior smart contract developer.

### Suggested order if you're new

1. Start with the Certificate project (Project 4) — it's the simplest to understand and deploy
2. Move to the Provenance tracker (Project 2) — role-based access is a pattern you will use everywhere
3. Then the Consent registry (Project 3) — simple but introduces off-chain integration
4. Tackle the Vault (Project 1) — the math is the hardest part of this file
5. Finish with the DAO (Project 5) — it pulls together nearly every concept

### Before deploying to mainnet

These tutorial contracts are **not audited** and are simplified for learning. Before deploying anything that will hold real value:

- Run `slither .` and fix all findings
- Write invariant and fuzz tests (use Foundry's `forge test --fuzz-runs 10000`)
- Get a professional audit from a reputable firm
- Deploy to testnet first and let it run for weeks
- Use a multisig (Safe) as the owner, not a single EOA
- Consider a bug bounty on Immunefi

### Next file to read

The previous file `08-theory-tutorial.md` is the companion theory document. If you built these projects first and want deeper explanations of *why* the EVM, gas, consensus, or cryptography work the way they do, go read that file next. Otherwise, the suggested real-world continuation is to pick one project from this file, deploy it to Sepolia testnet, and share the address with a friend who can interact with it from their own wallet.
