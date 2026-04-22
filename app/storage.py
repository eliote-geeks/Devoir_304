import json
from pathlib import Path
from threading import Lock
from uuid import uuid4
from datetime import datetime, UTC


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "accounts.json"
FILE_LOCK = Lock()


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _generate_account_number() -> str:
    date_part = datetime.now(UTC).strftime("%Y%m%d")
    random_part = uuid4().hex[:8].upper()
    return f"ACC-{date_part}-{random_part}"


def initialize_storage() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps({"accounts": []}, indent=2), encoding="utf-8")


def _read_data() -> dict:
    initialize_storage()
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def _write_data(data: dict) -> None:
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def list_accounts() -> list[dict]:
    data = _read_data()
    return data["accounts"]


def get_account(account_id: str) -> dict | None:
    for account in list_accounts():
        if account["id"] == account_id:
            return account
    return None


def create_account(payload: dict) -> dict:
    with FILE_LOCK:
        data = _read_data()

        account = {
            "id": str(uuid4()),
            "account_number": _generate_account_number(),
            "full_name": payload["full_name"],
            "phone_number": payload["phone_number"],
            "email": payload.get("email"),
            "balance": round(float(payload.get("initial_balance", 0)), 2),
            "created_at": _now(),
            "transactions": [],
        }

        if account["balance"] > 0:
            account["transactions"].append(
                {
                    "transaction_id": str(uuid4()),
                    "transaction_type": "deposit",
                    "amount": account["balance"],
                    "description": "Solde initial",
                    "balance_after": account["balance"],
                    "created_at": _now(),
                }
            )

        data["accounts"].append(account)
        _write_data(data)
        return account


def transfer(from_id: str, to_id: str, amount: float, description: str | None) -> tuple[dict, dict] | None:
    with FILE_LOCK:
        data = _read_data()
        accounts = data["accounts"]

        from_account = next((a for a in accounts if a["id"] == from_id), None)
        to_account = next((a for a in accounts if a["id"] == to_id), None)

        if from_account is None or to_account is None:
            return None

        amount = round(float(amount), 2)

        if amount > round(float(from_account["balance"]), 2):
            raise ValueError("Solde insuffisant pour effectuer ce virement.")

        now = _now()
        transfer_id = str(uuid4())

        from_account["balance"] = round(float(from_account["balance"]) - amount, 2)
        from_account["transactions"].append({
            "transaction_id": str(uuid4()),
            "transaction_type": "transfer_out",
            "amount": amount,
            "description": description or f"Virement vers {to_account['account_number']}",
            "balance_after": from_account["balance"],
            "created_at": now,
            "transfer_id": transfer_id,
        })

        to_account["balance"] = round(float(to_account["balance"]) + amount, 2)
        to_account["transactions"].append({
            "transaction_id": str(uuid4()),
            "transaction_type": "transfer_in",
            "amount": amount,
            "description": description or f"Virement de {from_account['account_number']}",
            "balance_after": to_account["balance"],
            "created_at": now,
            "transfer_id": transfer_id,
        })

        _write_data(data)
        return from_account, to_account


def apply_transaction(account_id: str, transaction_type: str, amount: float, description: str | None) -> dict | None:
    with FILE_LOCK:
        data = _read_data()

        for account in data["accounts"]:
            if account["id"] != account_id:
                continue

            current_balance = float(account["balance"])
            amount = round(float(amount), 2)

            if transaction_type == "withdraw" and amount > current_balance:
                raise ValueError("Solde insuffisant pour effectuer ce retrait.")

            new_balance = current_balance + amount if transaction_type == "deposit" else current_balance - amount
            new_balance = round(new_balance, 2)

            transaction = {
                "transaction_id": str(uuid4()),
                "transaction_type": transaction_type,
                "amount": amount,
                "description": description,
                "balance_after": new_balance,
                "created_at": _now(),
            }

            account["balance"] = new_balance
            account["transactions"].append(transaction)
            _write_data(data)
            return account

        return None
