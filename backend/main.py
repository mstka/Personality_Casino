from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
from enum import Enum

app = FastAPI(title="Roulette Service")  # FastAPI アプリケーションを作成

class BetType(str, Enum):
    """賭けの種類"""
    number = "number"
    color = "color"
    parity = "parity"

class Bet(BaseModel):
    """ベット情報を保持するデータモデル"""
    bet_type: BetType
    value: str
    amount: float

# ルーレットの色分け (ヨーロピアンスタイル 0 あり)
RED_NUMBERS = {
    1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36
}
BLACK_NUMBERS = {
    2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35
}

@app.post("/spin")
def spin(bet: Bet):
    """ルーレットを回してベット結果を返す"""
    # ベット額の簡易チェック
    if bet.amount <= 0:
        raise HTTPException(status_code=400, detail="Bet amount must be positive")

    number = random.randint(0, 36)
    if number == 0:
        color = "green"
    elif number in RED_NUMBERS:
        color = "red"
    else:
        color = "black"

    parity = "even" if number != 0 and number % 2 == 0 else "odd"  # 0 は奇数扱い
    result = {
        "number": number,
        "color": color,
        "parity": parity
    }

    win = False
    payout = 0.0  # 払い戻し金額

    if bet.bet_type == BetType.number:
        if bet.value.isdigit() and int(bet.value) == number:
            win = True
            payout = bet.amount * 35
    elif bet.bet_type == BetType.color:
        if bet.value.lower() == color:
            win = True
            payout = bet.amount
    elif bet.bet_type == BetType.parity:
        if bet.value.lower() == parity:
            win = True
            payout = bet.amount

    return {
        "result": result,
        "bet_outcome": "win" if win else "lose",
        "payout": payout
    }  # JSON レスポンスとして結果を返す

