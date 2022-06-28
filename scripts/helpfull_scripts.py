from brownie import accounts, network, config, MockV3Aggregator, VRFCoordinatorV2Mock

LOCKAL_BLOCKCHAIN_NETWORKS = ["development", "ganache-local"]
MAINNET_FORKED_NETWORKS = ["mainnet-fork"]

DECIMALS = 8
ETHPRICE = 296677777777


def get_account(index=0):
    if (
        network.show_active() in LOCKAL_BLOCKCHAIN_NETWORKS
        or network.show_active()
        in MAINNET_FORKED_NETWORKS  # in mainnet we also need account with eth, so brownie provide it to us
    ):
        return accounts[index]  # use first account in account array
    else:
        return accounts.add(
            config["wallets"]["from_key"]
        )  # accounts.add(private_key) create account with specified pKey.


contractNameToType = {
    "ethUsdPriceFeed": MockV3Aggregator,
    "vrfCoordinator": VRFCoordinatorV2Mock,
}


def deployMocks():
    print(f"Deploy Mocks")
    MockV3Aggregator.deploy(DECIMALS, ETHPRICE, {"from": get_account()})
    contract = VRFCoordinatorV2Mock.deploy(1, 1, {"from": get_account()})
    transaction = contract.createSubscription({"from": get_account()})
    subId = transaction.events["SubscriptionCreated"]["subId"]
    contract.fundSubscription(subId, 100000000000000, {"from": get_account()})
    print("Mock is deployed")


def get_contract(contract_name):
    if network.show_active() in LOCKAL_BLOCKCHAIN_NETWORKS:
        contractType = contractNameToType[contract_name]
        if len(VRFCoordinatorV2Mock) <= 0:
            deployMocks()
        return contractType[-1]
    else:
        return config["networks"][network.show_active()][contract_name]
