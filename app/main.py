from fastapi import FastAPI, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from app.models import (
    AccountCreate,
    AccountDetails,
    AccountResponse,
    ErrorResponse,
    HomeResponse,
    TransactionRequest,
    TransactionResponse,
)
from app.storage import apply_transaction, create_account, get_account, initialize_storage, list_accounts


app = FastAPI(
    title="API de transaction bancaire",
    description=(
        "API REST simple pour la gestion des comptes bancaires, des depots, "
        "des retraits et de l'historique des transactions."
    ),
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_tags=[
        {"name": "General", "description": "Informations generales sur l'API."},
        {"name": "Accounts", "description": "Gestion des comptes bancaires."},
        {"name": "Transactions", "description": "Operations de depot et de retrait."},
    ],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def startup() -> None:
    initialize_storage()


@app.get(
    "/",
    response_model=HomeResponse,
    tags=["General"],
    summary="Afficher le point d'entree de l'API",
    description="Retourne un message simple et le lien vers la documentation Swagger locale.",
)
def home() -> dict:
    return {
        "message": "Bienvenue sur l'API de transaction bancaire",
        "documentation": "/docs",
    }


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui() -> object:
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui/swagger-ui.css",
        swagger_favicon_url="/static/swagger-ui/favicon.svg",
        swagger_ui_parameters={
            "docExpansion": "list",
            "defaultModelsExpandDepth": 1,
            "displayRequestDuration": True,
            "filter": True,
        },
    )


@app.post(
    "/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Accounts"],
    summary="Creer un compte bancaire",
    description="Cree un nouveau compte bancaire avec generation automatique d'un identifiant et d'un numero de compte.",
)
def create_bank_account(payload: AccountCreate) -> dict:
    account = create_account(payload.model_dump())
    return {
        key: value
        for key, value in account.items()
        if key != "transactions"
    }


@app.get(
    "/accounts",
    response_model=list[AccountResponse],
    tags=["Accounts"],
    summary="Lister les comptes",
    description="Retourne la liste de tous les comptes bancaires enregistres.",
)
def get_accounts() -> list[dict]:
    accounts = list_accounts()
    return [
        {
            key: value
            for key, value in account.items()
            if key != "transactions"
        }
        for account in accounts
    ]


@app.get(
    "/accounts/{account_id}",
    response_model=AccountDetails,
    tags=["Accounts"],
    summary="Consulter un compte",
    description="Retourne les informations detaillees d'un compte, y compris ses transactions.",
    responses={404: {"model": ErrorResponse, "description": "Compte introuvable."}},
)
def get_account_by_id(account_id: str) -> dict:
    account = get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Compte introuvable.")
    return account


@app.post(
    "/accounts/{account_id}/deposit",
    response_model=AccountDetails,
    tags=["Transactions"],
    summary="Effectuer un depot",
    description="Ajoute un montant au solde du compte et enregistre la transaction dans l'historique.",
    responses={404: {"model": ErrorResponse, "description": "Compte introuvable."}},
)
def deposit_money(account_id: str, payload: TransactionRequest) -> dict:
    updated_account = apply_transaction(
        account_id=account_id,
        transaction_type="deposit",
        amount=payload.amount,
        description=payload.description,
    )
    if not updated_account:
        raise HTTPException(status_code=404, detail="Compte introuvable.")
    return updated_account


@app.post(
    "/accounts/{account_id}/withdraw",
    response_model=AccountDetails,
    tags=["Transactions"],
    summary="Effectuer un retrait",
    description="Retire un montant du compte si le solde est suffisant et enregistre l'operation.",
    responses={
        400: {"model": ErrorResponse, "description": "Solde insuffisant ou requete invalide."},
        404: {"model": ErrorResponse, "description": "Compte introuvable."},
    },
)
def withdraw_money(account_id: str, payload: TransactionRequest) -> dict:
    try:
        updated_account = apply_transaction(
            account_id=account_id,
            transaction_type="withdraw",
            amount=payload.amount,
            description=payload.description,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    if not updated_account:
        raise HTTPException(status_code=404, detail="Compte introuvable.")
    return updated_account


@app.get(
    "/accounts/{account_id}/transactions",
    response_model=list[TransactionResponse],
    tags=["Transactions"],
    summary="Lister les transactions d'un compte",
    description="Retourne toutes les transactions associees a un compte bancaire.",
    responses={404: {"model": ErrorResponse, "description": "Compte introuvable."}},
)
def get_transactions(account_id: str) -> list[dict]:
    account = get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Compte introuvable.")
    return account["transactions"]
