# encoding: utf-8
# date : 2021/10/04
# BSC에서 원하는 토큰 가격 확인하기 
#
# pip install web3
#
# web3 doc
# https://web3py.readthedocs.io/en/stable/

from web3 import Web3, HTTPProvider, IPCProvider
import time
import os
from urllib.request import urlopen, Request
import json
import datetime

# todo : 현재는 수동으로 입력, 자동으로 처리하기 위해서는 값을 찾는 방법을 알아야
# 1. 적절한 gas 비 받는 함수 찾기
# 2. routing 정보를 구하는 방법 (예 sps -> bnb -> busd) 
# 3. swapTokensForExactTokens, swapExactTokensForTokens  구분하는 방법
#      token을 넣을 때, 뺄 때 각각 사용한다. 넣고/빼는 토큰이 어떤 것인지 확인 방법
#   3.1 설정에서 mid 값을 뺄 필요가 있아      


# 거래 변수들
GAS = 250001  # 개스 값이 필요한 값보다 커야한다. 적으면 오류   300,000이 넘는 경우도 있음
GAS_PRICE = '5.1'
SLIPPAGE = 0.01

# 수정할 부분
my_addr = '본인 bsc주소'
my_priv = "본인 bsc private key"
# 수정할 부분 끝

sc_tokens = {
    'bnb' : '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
    'wbnb1' : '0x24f7C33ae5f77e2A9ECeed7EA858B4ca2fa1B7eC',
    'busd' : '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56',
    'dec' : '0xE9D7023f2132D55cbd4Ee1f78273CB7a3e74F10A', # 
    'sps' : '0x1633b7157e7638C4d6593436111Bf125Ee74703F'
}

w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))

print(w3.isConnected())

def get_time_str(cont='T') :
    date=datetime.datetime.now()
    form = '%Y/%m/%d'+cont+'%H:%M:%S'
    return date.strftime(form)

# 토큰 주소가 valid한지 조사가 필요한 경우에는 아래 함수 사용
# addr1 = w3.toChecksumAddress(token_addr)
def get_pair_info(swap_info, reverse=0):
    pair = []
    from_token = swap_info['from']
    if reverse :
        from_token = swap_info['to']
    pair.append(sc_tokens[from_token])

    if 'mid' in swap_info :
        pair.append(sc_tokens[swap_info['mid']])

    to_token = swap_info['to']
    if reverse :
        to_token = swap_info['from']
    pair.append(sc_tokens[to_token])

    return pair

def get_swap_amount_out(exchange, swap_info, pair):

    in_decimal = 18
    if 'in_decimal' in swap_info :
        in_decimal = swap_info['in_decimal']
    amount = swap_info['amount'] *(10 ** in_decimal)

    ret = exchange.functions.getAmountsOut(amountIn=amount, path=pair).call()

    given_amount = ret[0]

    last = len(ret) - 1   # 두개 이상의 코인을 거쳐갈 수 있음. 마지막에 있는 것이 원하는 코인의 수량

    out_decimal = 18
    if 'out_decimal' in swap_info :
        out_decimal = swap_info['out_decimal']
    out_amount = ret[last]

    from_token = swap_info['from']
    to_token = swap_info['to']

    print('[%s] %s -> %s %10.3f %10.3f'%(get_time_str(), from_token, to_token, swap_info['amount'], out_amount / (10 ** out_decimal )))
    
    return {'from':from_token, 'to':to_token, 'from_amount':amount, 'to_amount':out_amount}
    
# amount in의 경우에는 get_pair_info 요구시 마지막에 1 추가
def get_swap_amount_in(exchange, swap_info, pair):
    
    in_decimal = 18
    if 'in_decimal' in swap_info :
        in_decimal = swap_info['in_decimal']
    amount = swap_info['amount'] *(10 ** in_decimal)
    ret = exchange.functions.getAmountsIn(amountOut=amount, path=pair).call()

    last = len(ret) - 1   # 두개 이상의 코인을 거쳐갈 수 있음. 마지막에 있는 것이 원하는 코인의 수량

    out_decimal = 18
    if 'out_decimal' in swap_info :
        out_decimal = swap_info['out_decimal']
    out_amount = ret[0]

    from_token = swap_info['from']
    to_token = swap_info['to']

    print('[%s] %s -> %s %10.3f %10.3f'%(get_time_str(), to_token, from_token, out_amount/ (10 ** out_decimal ), swap_info['amount']))
    
    return {'from':to_token, 'to':from_token, 'from_amount':out_amount, 'to_amount':amount}


if 1:
    # 본인이 거래할 토큰과 path, 거래할 수량을 입력 
    # in_decimal : token에 따라서 in_amount의 decimal이 틀린 경우 있음, default = 18
    trading_pair = [
        {'from':'sps', 'mid': 'bnb', 'to':'busd', 'amount':100},
    ]
    exch_addr = '0x10ED43C718714eb63d5aA57B78B54704E256024E'  # v2

    exch_abi = '[{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'
    addr = w3.toChecksumAddress(exch_addr)
    exchange = w3.eth.contract(address=addr, abi=exch_abi)

    while(1) :
        for each in trading_pair :
            # 매도 확인
            pair = get_pair_info(each)
            ret = get_swap_amount_out(exchange, each, pair)  # for 매도
                
            pair = get_pair_info(each, 1)
            ret = get_swap_amount_in(exchange, each, pair) # for 매수
        print('')
        time.sleep(10)

