# Per-Chain Wallet Tracker

A command-line tool for tracking wallet activity across multiple EVM-compatible blockchains using Etherscan-compatible APIs.  
It provides a detailed asset-level summary including native token and ERC-20 transfers, with optional JSON export.

---

## Features

- ✅ Multi-chain support (Ethereum, Polygon, BNB, Arbitrum, etc.)
- ✅ ERC-20 `transfer(address,uint256)` decoding
- ✅ Native token transfer parsing
- ✅ Internal transaction inclusion (optional)
- ✅ Asset-level aggregation (total sent/received, per-counterparty addresses)
- ✅ JSON export for integration or auditing

---

## Arguments

**Required**
| Argument       | Description                             |
| -------------- | --------------------------------------- |
| `--address`    | Wallet address to analyze               |
| `--api-key`    | Etherscan-compatible API key            |
| `--chain-name` | Target chain (see supported list below) |

**Optional**
| Argument        | Description                                  | Default    |
| --------------- | -------------------------------------------- | ---------- |
| `--start-block` | Start block number                           | `0`        |
| `--end-block`   | End block number                             | `99999999` |
| `--page`        | Page number for API pagination               | `1`        |
| `--offset`      | Number of transactions per page (max 10000)  | `100`      |
| `--sort`        | Sort order of transactions (`asc` or `desc`) | `asc`      |
| `--internal`    | Include internal transactions                | `False`    |
| `--json`        | Save full transaction data as `output.json`  | `False`    |

---

## Usage

```
python wallet_tracker.py \
  --address <WALLET_ADDRESS> \
  --api-key <ETHERSCAN_API_KEY> \
  --chain-name <CHAIN_NAME> \
  [--start-block <START_BLOCK>] \
  [--end-block <END_BLOCK>] \
  [--page <PAGE_NUMBER>] \
  [--offset <OFFSET>] \
  [--sort asc|desc] \
  [--internal] \
  [--json]
```
---

## Supported Chains

abstract, ape, arbitrum_nova, arbitrum_one, avalanche, base, bera, bittorrent, blast,
bnb, celo, cronos, ethereum, fantom, fraxtal, gnosis, kroma, mantle, moonbeam,
moonriver, op, opbnb, polygon, polygon_zk, scroll, sonic, sophon, swell, taiko,
uni, wemix, world, xai, xdc, zksync


