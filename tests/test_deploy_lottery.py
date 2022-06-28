from brownie import Lottery, exceptions, network
from scripts.helpfull_scripts import get_account
from scripts.deploy_lottery import deploy_lottery
import pytest

# def deploy_lottery():
#     print("Deploying new lottery")
#     account = get_account()
#     lottery_conract = Lottery.deploy({"from": account})
#     return lottery_conract


def test_deploy_lottery():
    # Arrange
    account = get_account()
    print(f"Account is {account}")
    # Act
    lottery = deploy_lottery()
    print(f"Lottery is {lottery}")
    # Assert
    assert lottery.owner() == account
    assert lottery.lottery_state() == 1


def test_start_lottery():
    # Arrange
    if len(Lottery) <= 0:
        deploy_lottery()
    account = get_account()
    lottery = Lottery[-1]
    # Act
    if lottery.lottery_state() == 1:
        lottery.startLottery({"from": account})
    # Assert
    assert lottery.lottery_state() == 0

    if (
        network.show_active() == "development"
    ):  # for some reason doesn't work with testnets
        with pytest.raises(exceptions.VirtualMachineError):
            lottery.startLottery({"from": account})


def test_enter():
    # Arrange
    # if len(Lottery) <= 0:
    #    deploy_lottery()
    deploy_lottery()

    account = get_account()
    lottery = Lottery[-1]
    if lottery.lottery_state() == 1:
        lottery.startLottery({"from": account})

    # Act
    prev_balance = lottery.balance()
    print(f"Prev balance = {prev_balance}")
    ethVal = 1 * 10**10
    lottery.enter({"from": account, "value": ethVal})
    print(f"After enter balance = {lottery.balance()}")
    assert lottery.balance() == prev_balance + ethVal
    assert lottery.players(lottery.getPlayersNumber() - 1) == account

    prev_balance = lottery.balance()
    if (
        network.show_active() == "development"
    ):  # for some reason doesn't work with testnets
        with pytest.raises(exceptions.VirtualMachineError):
            lottery.enter({"from": account, "value": 1 * 10**7})

    assert lottery.balance() == prev_balance


def test_end_lottery():
    # Arrange
    # if len(Lottery) <= 0:
    #     deploy_lottery()
    deploy_lottery()

    account = get_account()
    lottery = Lottery[-1]
    if lottery.lottery_state() == 1:
        lottery.startLottery({"from": account})
    ethVal = 1 * 10**10
    lottery.enter({"from": account, "value": ethVal})

    # Act
    assert lottery.balance() > 0
    lottery.endLottery({"from": account})

    # Assert
    assert lottery.lottery_state() == 1
    assert lottery.balance() == 0
    assert lottery.recentWinner() == account
    assert lottery.getPlayersNumber() == 0


def test_get_entrance_fee():
    # Arrange
    lottery = deploy_lottery()
    # Act
    ethVal = lottery.getEntranceFee(lottery.entranceFeeUSD())
    # Assert
    # Actual price = 3091, entrance fee = 50. Answer = 50 / 3091 * 10 ** 18 = 0.01617 * 10 ^ 18
    print(ethVal)
    assert ethVal < 0.0165 * 10**18
    assert ethVal > 0.0160 * 10**18
