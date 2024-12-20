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
from zksk import Secret, DLRep
from zksk import utils
from pqcrypto.kem.kyber import generate_keypair, encrypt, decrypt
from datetime import datetime, timedelta

class CoinJoinManager:

    def __init__(self):
        self.peers = []
        self.session_id = None
        self.outputs = []
        self.network = None
        self.wallet = None
        self.known_peers = None
        self.shared_secrets = {}  # Store shared secrets with peers

    async def setup_network(self, network, wallet: Wallet, known_peers):
        self.network = network
        self.wallet = wallet
        self.known_peers = known_peers
        if not self.network: 
            self.network = Network()

    async def initiate_coinjoin(self, wallet: Wallet, known_peers):
        self.session_id = self._generate_session_id()
        self.secret = Secret(utils.get_random_secret())
        self.zk_proof = DLRep(self.secret, self.session_id)
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

            # Generate PQC key pair (CRYSTALS-Kyber)
            public_key, private_key = generate_keypair()
            self.shared_secrets[peer] = private_key

            # Send public key to peer
            writer.write(json.dumps({"public_key": public_key.hex()}).encode())
            await writer.drain()

            # Receive encrypted session key from peer
            response = await reader.read(1000)
            response_data = json.loads(response.decode())
            encrypted_session_key = bytes.fromhex(response_data['encrypted_key'])

            # Decrypt session key
            session_key = decrypt(self.shared_secrets[peer], encrypted_session_key)

            # Create and encrypt CoinJoin request
            request = self._create_coinjoin_request(wallet)
            cipher = AES.new(session_key, AES.MODE_EAX)
            nonce = cipher.nonce
            ciphertext, tag = cipher.encrypt_and_digest(pad(request.encode(), AES.block_size))

            # Send encrypted request
            writer.write(json.dumps({
                "session_id": self.session_id,
                "zk_proof": self.zk_proof.value,
                "nonce": nonce.hex(),
                "ciphertext": ciphertext.hex(),
                "tag": tag.hex()
            }).encode())
            await writer.drain()

            # Handle response
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

# Dictionary to track request counts and time windows
request_counts = {}
time_window = timedelta(seconds=60)  # Time window for rate limiting
request_limit = 10  # Maximum requests allowed per IP within the time window
blacklisted_ips = set()  # Set to store blacklisted IP addresses

async def handle_client(reader, writer):
    peername = writer.get_extra_info('peername')
    ip = peername[0]

    # Check if IP is blacklisted
    if ip in blacklisted_ips:
        writer.close()
        await writer.wait_closed()
        return

    # Rate limiting
    now = datetime.now()
    if ip not in request_counts:
        request_counts[ip] = []
    request_counts[ip] = [timestamp for timestamp in request_counts[ip] if now - timestamp < time_window]

    if len(request_counts[ip]) >= request_limit:
        blacklisted_ips.add(ip)
        writer.close()
        await writer.wait_closed()
        return

    request_counts[ip].append(now)

    data = await reader.read(1000)
    message = data.decode()
    request = json.loads(message)

    # Encrypt session key using peer's public key
    peer_public_key = bytes.fromhex(request['public_key'])
    encrypted_session_key = encrypt(peer_public_key, get_random_bytes(16))

    response = {
        "encrypted_key": encrypted_session_key.hex()
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

