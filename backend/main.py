from fastapi import FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
from enum import Enum
import uuid

app = FastAPI(title="Roulette Service")  # FastAPI アプリケーションを作成

# CORS を許可してフロントエンドからのアクセスを容易にする
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# メモリ上のユーザー・セッション管理
users = {}
sessions = {}


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

class RegisterRequest(BaseModel):
    """ユーザー登録用リクエスト"""
    username: str
    password: str


class LoginRequest(BaseModel):
    """ログイン用リクエスト"""
    username: str
    password: str


class Token(BaseModel):
    """セッション確認用トークン"""
    token: str


class SpinRequest(Bet):
    """トークン付きのベット"""
    token: str


@app.post("/register")
def register(req: RegisterRequest):
    """ユーザー登録処理"""
    if req.username in users:
        raise HTTPException(status_code=400, detail="既に存在するユーザー名です")
    users[req.username] = {"password": req.password, "coins": 1000}
    return {"message": "registered"}


@app.post("/login")
def login(req: LoginRequest):
    """ログイン処理: トークンを返す"""
    user = users.get(req.username)
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="ログイン失敗")
    token = uuid.uuid4().hex
    sessions[token] = req.username
    return {"token": token}


@app.post("/balance")
def balance(token: Token):
    """現在のコイン残高を返す"""
    username = sessions.get(token.token)
    if not username:
        raise HTTPException(status_code=401, detail="認証エラー")
    return {"coins": users[username]["coins"]}

# ルーレットの色分け (ヨーロピアンスタイル 0 あり)
RED_NUMBERS = {
    1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36
}
BLACK_NUMBERS = {
    2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35
}

@app.post("/spin")
def spin(bet: SpinRequest):
    """ルーレットを回してベット結果を返す"""
    # 認証確認
    username = sessions.get(bet.token)
    if not username:
        raise HTTPException(status_code=401, detail="認証エラー")

    # ベット額の簡易チェックと残高確認
    if bet.amount <= 0:
        raise HTTPException(status_code=400, detail="Bet amount must be positive")
    user = users[username]
    if user["coins"] < bet.amount:
        raise HTTPException(status_code=400, detail="コイン残高が不足しています")

    user["coins"] -= bet.amount


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


    # 払い戻し
    user["coins"] += payout

    return {
        "result": result,
        "bet_outcome": "win" if win else "lose",
        "payout": payout,
        "coins": user["coins"],

    }  # JSON レスポンスとして結果を返す

