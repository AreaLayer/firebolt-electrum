# Firebolt Electrum Plugin (Experimental) ⚡ 🕵️

>Firebolt electrum plugin

**CoinJoin Process:**

 1. Peer Discovery: Discover peers and establish connections.
 2. CoinJoin Request: Send CoinJoin requests to peers and await responses.
 3. Transaction Creation and Signing: If peers acknowledge the CoinJoin request, create and sign the CoinJoin transaction.
 4.  Broadcasting: Broadcast the final CoinJoin transaction to the Bitcoin network.

### Run software

**Pre Requisite**

- Phython installed
- Electrum developer mode
- Testnet/Signet compatible

### Run electrum

``
./run_electrum
``
### Observations

⚠️ It is not compatible with Lighting Network

⚠️ Not use for mainnet
