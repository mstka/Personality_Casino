from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
from enum import Enum
import uuid

import sqlite3
from pathlib import Path

app = FastAPI(title="Roulette Service")  # FastAPI アプリケーションを作成

# CORS を許可してフロントエンドからのアクセスを容易にする
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# メモリ上のセッション管理
sessions = {}

# SQLite データベース初期化
DB_PATH = str(Path(__file__).parent / "users.db")
with sqlite3.connect(DB_PATH) as conn:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, coins INTEGER)"
    )

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

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT username FROM users WHERE username = ?",
            (req.username,),
        )
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="既に存在するユーザー名です")
        conn.execute(
            "INSERT INTO users (username, password, coins) VALUES (?, ?, ?)",
            (req.username, req.password, 1000),
        )
        conn.commit()

    return {"message": "registered"}

@app.post("/login")
def login(req: LoginRequest):
    """ログイン処理: トークンを返す"""

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT username, password FROM users WHERE username = ?",
            (req.username,),
        )
        row = cur.fetchone()
        if not row or row["password"] != req.password:
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

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT coins FROM users WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="ユーザーが見つかりません")
        return {"coins": row["coins"]}

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

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT coins FROM users WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="ユーザーが見つかりません")
        coins = row["coins"]
        if coins < bet.amount:
            raise HTTPException(status_code=400, detail="コイン残高が不足しています")

        coins -= bet.amount

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
        coins += payout
        conn.execute(
            "UPDATE users SET coins = ? WHERE username = ?",
            (coins, username),
        )
        conn.commit()

    return {
        "result": result,
        "bet_outcome": "win" if win else "lose",
        "payout": payout,
        "coins": coins,
    }  # JSON レスポンスとして結果を返す
