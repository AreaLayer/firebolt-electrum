from bitcoinlib.networks import Network

class BitcoinNetworkManager:
    def __init__(self, network_type='signet'):
        self.network_type = network_type
        self.network = self.set_network()

    def set_network(self):
        if self.network_type == 'mainnet':
            return Network('bitcoin')
        elif self.network_type == 'testnet':
            return Network('testnet')
        elif self.network_type == 'signet':
            return Network('signet')
        else:
            raise ValueError("Unsupported network type")

# Example usage
network_manager = BitcoinNetworkManager(network_type='signet')
print(f"Connected to {network_manager.network_type}")
