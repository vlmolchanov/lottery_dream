from brownie import VRFv2Consumer
from scripts.helpfull_scripts import get_account
import time


def deploy_contract():
    account = get_account()
    subscriptionId = 3156
    consumer_contract = VRFv2Consumer.deploy(subscriptionId, {"from": account})
    print(f"Contract is {consumer_contract}")


def main():
    if len(VRFv2Consumer) <= 0:
        deploy_contract()
    account = get_account()
    consumer_contract = VRFv2Consumer[-1]
    tx = consumer_contract.requestRandomWords({"from": account})
    tx.wait(1)
    time.sleep(120)
    requestId = consumer_contract.s_requestId()
    print(requestId)
    random0 = consumer_contract.s_randomWords(0)
    random1 = consumer_contract.s_randomWords(1)
    print(random0)
    print(random1)
