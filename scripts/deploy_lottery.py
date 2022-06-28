from brownie import Lottery, config, network, VRFCoordinatorV2Mock
from scripts.helpfull_scripts import (
    get_account,
    get_contract,
    LOCKAL_BLOCKCHAIN_NETWORKS,
)
import time


def deploy_lottery():
    print("Deploying new lottery")
    account = get_account()
    if network.show_active() in LOCKAL_BLOCKCHAIN_NETWORKS:
        subscriptionId = 1
    else:
        subscriptionId = 3156

    lottery_conract = Lottery.deploy(
        get_contract("ethUsdPriceFeed"),
        get_contract("vrfCoordinator"),
        config["networks"][network.show_active()].get("aavePoolAddress"),
        config["networks"][network.show_active()].get("aaveWethAddress"),
        subscriptionId,
        config["networks"][network.show_active()].get("keyHash"),
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    return lottery_conract


def main():
    flag_to_deploy_new_lottery = False
    if len(Lottery) <= 0 or flag_to_deploy_new_lottery:
        deploy_lottery()
        # To have ability to Fund RNG subscription
        if network.show_active() not in LOCKAL_BLOCKCHAIN_NETWORKS or False:
            print(f"Don't forget to fund subscription for {Lottery[-1]}")
            quit()

    account = get_account()
    lottery = Lottery[-1]
    if lottery.lottery_state() == 2:
        print("Lottery is calculating winner. Come later")
        quit()
    if lottery.lottery_state() == 3:
        print("Lottery is finished")
        print(f"Winner is {lottery.recentWinner()}")
        print("Sending money to winner")
        lottery.transferFundsToWinner({"from": account})
        quit()
    if lottery.lottery_state() == 1:
        lottery.startLottery({"from": account})
    print("Lottery is started")
    print(f"Money can be sent to {lottery} contract")
    print(
        f"Entrance fee is {lottery.entranceFeeUSD()} USD / {lottery.getEntranceFee()} wei"
    )
    # Enter lottery
    ethVal = lottery.getEntranceFee() + 1000
    tx = lottery.enter({"from": account, "value": ethVal})
    tx.wait(1)
    time.sleep(20)
    tx = lottery.enter({"from": account, "value": ethVal})
    tx.wait(1)
    time.sleep(20)
    tx = lottery.enter({"from": account, "value": ethVal})
    tx.wait(1)
    time.sleep(20)
    # tx = lottery.enter({"from": account, "value": ethVal})
    # tx.wait(1)
    # time.sleep(20)
    # tx = lottery.enter({"from": account, "value": ethVal})
    # tx.wait(1)
    # time.sleep(20)

    # calcWinner()
    transaction = lottery.endLottery({"from": account})
    transaction.wait(1)
    print(f"Number of participants is {lottery.getPlayersNumber()}")
    print("Selecting winner ......")

    if network.show_active() in LOCKAL_BLOCKCHAIN_NETWORKS:
        contract = VRFCoordinatorV2Mock[-1]
        requestId = transaction.events["RandomRequestSent"]["requestId"]
        tx = contract.fulfillRandomWords(requestId, lottery, {"from": account})
        tx.wait(1)
    else:
        time.sleep(180)

    if lottery.lottery_state() == 3:
        print("Lottery is finished")
        print(f"Winner is {lottery.recentWinner()}")
        print("Sending money to winner")
        lottery.transferFundsToWinner({"from": account})
    else:
        print("Winner is not specified yet. Wait a bit")
