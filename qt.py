import asyncio
import random
import json
from electrum.transaction import Transaction, TxOutput
from electrum.bitcoin import TYPE_ADDRESS, is_address
from electrum.wallet import Wallet
from electrum.network import Network
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class CoinJoinManager:

    def __init__(self):
        self.peers = []
        self.session_id = None
        self.outputs = []
        self.network = None
        self.wallet = None
        self.known_peers = None

    async def Network(self, network, wallet: Wallet, known_peers):
        self.network = network
        self.wallet = wallet
        self.known_peers = known_peers
        self.network = (Testnet, Signet, Regtest)
    
        if not self.network: 
            self.network = Network()

    async def initiate_coinjoin(self, wallet: Wallet, known_peers):
        self.session_id = self._generate_session_id()
        await self._discover_peers(known_peers)

        success = await self._send_coinjoin_requests(wallet)

        if success:
            success = await self._create_and_sign_coinjoin_transaction(wallet)

        return success

    def _generate_session_id(self):
        return str(random.randint(100000, 999999))

    async def _discover_peers(self, known_peers):
        self.peers = known_peers
        print(f"Discovered peers: {self.peers}")

    async def _send_coinjoin_requests(self, wallet: Wallet):
        tasks = [self._send_request_to_peer(peer, wallet) for peer in self.peers]
        results = await asyncio.gather(*tasks)
        return all(results)

    async def _send_request_to_peer(self, peer, wallet: Wallet):
        try:
            host, port = peer.split(':')
            reader, writer = await asyncio.open_connection(host, int(port))
            
            # Generate AES key and encrypt the request
            key = get_random_bytes(16)  # AES-128, for AES-256 use 32 bytes
            request = self._create_coinjoin_request(wallet)
            cipher = AES.new(key, AES.MODE_EAX)
            nonce = cipher.nonce
            ciphertext, tag = cipher.encrypt_and_digest(pad(request.encode(), AES.block_size))
            
            # Send the key and encrypted message
            writer.write(json.dumps({
                "key": key.hex(),
                "nonce": nonce.hex(),
                "ciphertext": ciphertext.hex(),
                "tag": tag.hex()
            }).encode())
            await writer.drain()

            response = await reader.read(1000)
            writer.close()
            await writer.wait_closed()

            response_data = json.loads(response.decode())
            if response_data.get("status") == "ACK":
                if is_address(response_data["address"]):
                    self.outputs.append(TxOutput(TYPE_ADDRESS, response_data["address"], response_data["amount"]))
                    return True
            return False
        except Exception as e:
            print(f"Failed to communicate with {peer}: {e}")
            return False

    def _create_coinjoin_request(self, wallet: Wallet):
        return json.dumps({
            "session_id": self.session_id,
            "wallet_info": "example",
            "address": wallet.get_receiving_address(),
            "amount": 100000
        })

    async def _create_and_sign_coinjoin_transaction(self, wallet: Wallet):
        if not self.outputs:
            print("No outputs collected for CoinJoin")
            return False

        tx = wallet.make_unsigned_transaction([], self.outputs, fee=1000)
        wallet.sign_transaction(tx, password=None)
        result = await wallet.network.broadcast_transaction(tx)
        print(f"Broadcast result: {result}")

        return result is not None

async def handle_client(reader, writer):
    data = await reader.read(1000)
    message = data.decode()
    request = json.loads(message)

    response = {
        "status": "ACK",
        "address": "tb1qexampleaddress",
        "amount": 100000
    }

    writer.write(json.dumps(response).encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def run_server():
    server = await asyncio.start_server(handle_client, '0.0.0.0', 12345)

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    known_peers = ["127.0.0.1:12345", "127.0.0.1:12346", "127.0.0.1:12347"]

    # Run the server for testing (normally, peers would run this)
    asyncio.run(run_server())

    # Run the CoinJoin process
    # wallet = ...  # Get the wallet instance
    # coinjoin_manager = CoinJoinManager()
    # asyncio.run(coinjoin_manager.initiate_coinjoin(wallet, known_peers))