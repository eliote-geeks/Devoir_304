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
    description="""
## Systeme de transaction bancaire — Devoir 304

API REST permettant de gerer des comptes bancaires et d'executer des operations de depot et de retrait.

---

## Fonctions du systeme

| # | Fonction | Methode | URL |
|---|----------|---------|-----|
| 1 | Creer un compte | POST | `/accounts` |
| 2 | Lister les comptes | GET | `/accounts` |
| 3 | Consulter un compte | GET | `/accounts/{account_id}` |
| 4 | Effectuer un depot | POST | `/accounts/{account_id}/deposit` |
| 5 | Effectuer un retrait | POST | `/accounts/{account_id}/withdraw` |
| + | Historique des transactions | GET | `/accounts/{account_id}/transactions` |

---

## Cas de test par fonction

### Fonction 1 — Creer un compte (`POST /accounts`)

| # | Description | Donnees envoyees | Resultat attendu | Code HTTP |
|---|-------------|-----------------|-----------------|-----------|
| CT-01 | Creation valide avec solde initial | `full_name`, `phone_number`, `email`, `initial_balance: 10000` | Compte cree avec ID et numero de compte generes automatiquement | 201 |
| CT-02 | Creation valide sans email ni solde | `full_name`, `phone_number` seulement | Compte cree avec balance = 0 | 201 |
| CT-03 | Champ `full_name` absent | Corps sans `full_name` | Erreur de validation | 422 |
| CT-04 | Champ `phone_number` absent | Corps sans `phone_number` | Erreur de validation | 422 |
| CT-05 | Solde initial negatif | `initial_balance: -500` | Erreur de validation | 422 |

### Fonction 2 — Lister les comptes (`GET /accounts`)

| # | Description | Precondition | Resultat attendu | Code HTTP |
|---|-------------|-------------|-----------------|-----------|
| CT-06 | Liste vide au demarrage | Aucun compte cree | Tableau vide `[]` | 200 |
| CT-07 | Liste avec comptes existants | Au moins un compte cree | Tableau de comptes sans les transactions | 200 |

### Fonction 3 — Consulter un compte (`GET /accounts/{account_id}`)

| # | Description | Precondition | Resultat attendu | Code HTTP |
|---|-------------|-------------|-----------------|-----------|
| CT-08 | Compte existant | Compte cree au prealable | Details du compte avec ses transactions | 200 |
| CT-09 | Compte inexistant | ID invente | Message d'erreur `Compte introuvable.` | 404 |

### Fonction 4 — Effectuer un depot (`POST /accounts/{account_id}/deposit`)

| # | Description | Precondition | Donnees | Resultat attendu | Code HTTP |
|---|-------------|-------------|---------|-----------------|-----------|
| CT-10 | Depot valide | Compte existant | `amount: 5000` | Solde mis a jour, transaction enregistree | 200 |
| CT-11 | Depot avec description | Compte existant | `amount: 3000, description: "Depot agence"` | Solde mis a jour, libelle visible | 200 |
| CT-12 | Montant zero | Compte existant | `amount: 0` | Erreur de validation (montant > 0 requis) | 422 |
| CT-13 | Montant negatif | Compte existant | `amount: -1000` | Erreur de validation | 422 |
| CT-14 | Compte inexistant | ID invente | `amount: 5000` | Message d'erreur `Compte introuvable.` | 404 |

### Fonction 5 — Effectuer un retrait (`POST /accounts/{account_id}/withdraw`)

| # | Description | Precondition | Donnees | Resultat attendu | Code HTTP |
|---|-------------|-------------|---------|-----------------|-----------|
| CT-15 | Retrait valide | Compte avec solde >= montant | `amount: 2000` | Solde diminue, transaction enregistree | 200 |
| CT-16 | Retrait egal au solde | Compte avec solde = 5000 | `amount: 5000` | Solde = 0, transaction enregistree | 200 |
| CT-17 | Solde insuffisant | Compte avec solde = 1000 | `amount: 5000` | Erreur `Solde insuffisant` | 400 |
| CT-18 | Montant zero | Compte existant | `amount: 0` | Erreur de validation | 422 |
| CT-19 | Montant negatif | Compte existant | `amount: -500` | Erreur de validation | 422 |
| CT-20 | Compte inexistant | ID invente | `amount: 1000` | Message d'erreur `Compte introuvable.` | 404 |

---

## Specifications fonctionnelles

- Creation d'un compte avec nom complet, telephone, email (optionnel) et solde initial (optionnel)
- Generation automatique d'un identifiant unique (UUID) et d'un numero de compte (format `ACC-AAAAMMJJ-XXXXXXXX`)
- Persistance des donnees dans un fichier JSON local
- Validation : solde initial >= 0, montants de transaction > 0
- Refus du retrait si le solde est insuffisant
- Enregistrement de chaque transaction avec date, type, montant et solde apres operation

## Specifications non fonctionnelles

- **Performance** : reponses rapides pour toutes les operations simples
- **Fiabilite** : donnees persistees dans `data/accounts.json`, protegees par un verrou de fichier
- **Securite** : montants negatifs bloques, retraits non autorises rejetes
- **Maintenabilite** : code organise en modules (`main.py`, `models.py`, `storage.py`)
- **Evolutivite** : architecture preparee pour ajouter authentification et virements
""",
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
    summary="Point d'entree de l'API",
    description="Retourne un message de bienvenue et le lien vers la documentation Swagger.",
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
    description="""
Cree un nouveau compte bancaire.

Un identifiant unique (UUID) et un numero de compte (format `ACC-AAAAMMJJ-XXXXXXXX`) sont generes automatiquement.

**Cas de test couverts par cet endpoint :**

| # | Cas | Requete | Reponse attendue |
|---|-----|---------|-----------------|
| CT-01 | Creation valide avec solde | `full_name` + `phone_number` + `email` + `initial_balance: 10000` | 201 — compte cree |
| CT-02 | Creation valide sans email | `full_name` + `phone_number` uniquement | 201 — balance = 0 |
| CT-03 | `full_name` manquant | Corps sans `full_name` | 422 — erreur validation |
| CT-04 | `phone_number` manquant | Corps sans `phone_number` | 422 — erreur validation |
| CT-05 | Solde initial negatif | `initial_balance: -500` | 422 — erreur validation |

**Exemples de test manuel (Swagger) :**
- Utiliser l'exemple **"CT-01 Valide avec solde"** pour le cas nominal
- Modifier le corps pour tester les cas d'erreur
""",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "CT-01 — Creation valide avec solde initial": {
                            "summary": "CT-01 : Creation valide (cas nominal)",
                            "description": "Cas nominal : tous les champs fournis. Resultat attendu : HTTP 201, compte cree avec ID et numero generes.",
                            "value": {
                                "full_name": "KOA ESSAMA PAULIN BRICE",
                                "phone_number": "699001122",
                                "email": "paulin@example.com",
                                "initial_balance": 10000,
                            },
                        },
                        "CT-02 — Creation sans email ni solde": {
                            "summary": "CT-02 : Creation minimale (cas nominal)",
                            "description": "Cas nominal : seuls les champs obligatoires. Resultat attendu : HTTP 201, balance = 0.",
                            "value": {
                                "full_name": "NGUEMA ONDOA CAROLE",
                                "phone_number": "677445566",
                            },
                        },
                        "CT-03 — full_name manquant (erreur)": {
                            "summary": "CT-03 : full_name absent → 422",
                            "description": "Cas d'erreur : champ obligatoire absent. Resultat attendu : HTTP 422.",
                            "value": {
                                "phone_number": "699001122",
                                "initial_balance": 5000,
                            },
                        },
                        "CT-04 — phone_number manquant (erreur)": {
                            "summary": "CT-04 : phone_number absent → 422",
                            "description": "Cas d'erreur : champ obligatoire absent. Resultat attendu : HTTP 422.",
                            "value": {
                                "full_name": "KOA ESSAMA PAULIN BRICE",
                                "initial_balance": 5000,
                            },
                        },
                        "CT-05 — Solde initial negatif (erreur)": {
                            "summary": "CT-05 : Solde negatif → 422",
                            "description": "Cas d'erreur : solde initial negatif interdit. Resultat attendu : HTTP 422.",
                            "value": {
                                "full_name": "TEST NEGATIF",
                                "phone_number": "600000001",
                                "initial_balance": -500,
                            },
                        },
                    }
                }
            }
        }
    },
)
def create_bank_account(payload: AccountCreate) -> dict:
    account = create_account(payload.model_dump())
    return {key: value for key, value in account.items() if key != "transactions"}


@app.get(
    "/accounts",
    response_model=list[AccountResponse],
    tags=["Accounts"],
    summary="Lister tous les comptes",
    description="""
Retourne la liste de tous les comptes bancaires enregistres dans le systeme.

**Cas de test couverts par cet endpoint :**

| # | Cas | Precondition | Reponse attendue |
|---|-----|-------------|-----------------|
| CT-06 | Liste vide | Aucun compte cree | HTTP 200 — tableau vide `[]` |
| CT-07 | Liste avec comptes | Au moins un compte cree | HTTP 200 — tableau de comptes (sans transactions) |

**Test manuel :**
1. Appeler cet endpoint avant de creer des comptes → verifier que la reponse est `[]`
2. Creer un ou plusieurs comptes via `POST /accounts`
3. Rappeler cet endpoint → verifier que les comptes crees apparaissent dans la liste
""",
)
def get_accounts() -> list[dict]:
    accounts = list_accounts()
    return [
        {key: value for key, value in account.items() if key != "transactions"}
        for account in accounts
    ]


@app.get(
    "/accounts/{account_id}",
    response_model=AccountDetails,
    tags=["Accounts"],
    summary="Consulter un compte",
    description="""
Retourne les informations detaillees d'un compte, y compris l'historique complet de ses transactions.

**Cas de test couverts par cet endpoint :**

| # | Cas | Precondition | Reponse attendue |
|---|-----|-------------|-----------------|
| CT-08 | Compte existant | ID valide recupere apres creation | HTTP 200 — details du compte avec transactions |
| CT-09 | Compte inexistant | ID invente ou invalide | HTTP 404 — `Compte introuvable.` |

**Test manuel :**
1. Creer un compte via `POST /accounts` et copier l'`id` retourne
2. Coller cet `id` dans le champ `account_id` de cet endpoint → verifier HTTP 200
3. Tester avec un ID invente ex: `00000000-0000-0000-0000-000000000000` → verifier HTTP 404
""",
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
    description="""
Ajoute un montant au solde du compte et enregistre la transaction dans l'historique.

Le montant doit etre **strictement positif**.

**Cas de test couverts par cet endpoint :**

| # | Cas | Donnees | Reponse attendue |
|---|-----|---------|-----------------|
| CT-10 | Depot valide | `amount: 5000` | HTTP 200 — solde augmente de 5000 |
| CT-11 | Depot avec description | `amount: 3000, description: "Depot agence"` | HTTP 200 — libelle visible dans la transaction |
| CT-12 | Montant nul (erreur) | `amount: 0` | HTTP 422 — montant doit etre > 0 |
| CT-13 | Montant negatif (erreur) | `amount: -1000` | HTTP 422 — montant doit etre > 0 |
| CT-14 | Compte inexistant (erreur) | ID invalide | HTTP 404 — `Compte introuvable.` |

**Test manuel :**
1. Creer un compte et copier son `id`
2. Executer un depot valide avec `amount: 5000` → verifier que `balance` augmente
3. Tester `amount: 0` → verifier le rejet
4. Tester avec un ID invente → verifier HTTP 404
""",
    responses={
        400: {"model": ErrorResponse, "description": "Requete invalide."},
        404: {"model": ErrorResponse, "description": "Compte introuvable."},
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "CT-10 — Depot valide": {
                            "summary": "CT-10 : Depot valide (cas nominal)",
                            "description": "Resultat attendu : HTTP 200, solde augmente de 5000.",
                            "value": {"amount": 5000},
                        },
                        "CT-11 — Depot avec description": {
                            "summary": "CT-11 : Depot avec libelle (cas nominal)",
                            "description": "Resultat attendu : HTTP 200, description visible dans la transaction.",
                            "value": {"amount": 3000, "description": "Depot agence"},
                        },
                        "CT-12 — Montant nul (erreur)": {
                            "summary": "CT-12 : Montant = 0 → 422",
                            "description": "Resultat attendu : HTTP 422, montant doit etre strictement positif.",
                            "value": {"amount": 0},
                        },
                        "CT-13 — Montant negatif (erreur)": {
                            "summary": "CT-13 : Montant negatif → 422",
                            "description": "Resultat attendu : HTTP 422, montant doit etre strictement positif.",
                            "value": {"amount": -1000},
                        },
                    }
                }
            }
        }
    },
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
    description="""
Retire un montant du solde du compte si le solde est suffisant, et enregistre la transaction.

Le montant doit etre **strictement positif** et ne peut pas depasser le solde disponible.

**Cas de test couverts par cet endpoint :**

| # | Cas | Precondition | Donnees | Reponse attendue |
|---|-----|-------------|---------|-----------------|
| CT-15 | Retrait valide | Solde >= montant | `amount: 2000` (solde = 10000) | HTTP 200 — solde diminue de 2000 |
| CT-16 | Retrait egal au solde | Solde = montant | `amount: 10000` (solde = 10000) | HTTP 200 — solde = 0 |
| CT-17 | Solde insuffisant (erreur) | Solde < montant | `amount: 50000` (solde = 1000) | HTTP 400 — `Solde insuffisant` |
| CT-18 | Montant nul (erreur) | Compte existant | `amount: 0` | HTTP 422 — montant doit etre > 0 |
| CT-19 | Montant negatif (erreur) | Compte existant | `amount: -500` | HTTP 422 — montant doit etre > 0 |
| CT-20 | Compte inexistant (erreur) | ID invalide | `amount: 1000` | HTTP 404 — `Compte introuvable.` |

**Test manuel :**
1. Creer un compte avec `initial_balance: 10000`
2. Effectuer un retrait de 2000 → verifier solde = 8000
3. Tenter un retrait de 50000 → verifier HTTP 400
4. Tenter un retrait de 0 → verifier HTTP 422
5. Tester avec un ID invente → verifier HTTP 404
""",
    responses={
        400: {"model": ErrorResponse, "description": "Solde insuffisant."},
        404: {"model": ErrorResponse, "description": "Compte introuvable."},
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "CT-15 — Retrait valide": {
                            "summary": "CT-15 : Retrait valide (cas nominal)",
                            "description": "Precondition : solde >= 2000. Resultat attendu : HTTP 200, solde diminue.",
                            "value": {"amount": 2000, "description": "Retrait DAB"},
                        },
                        "CT-16 — Retrait egal au solde": {
                            "summary": "CT-16 : Vider le compte (cas nominal)",
                            "description": "Precondition : compte avec solde initial 10000. Resultat attendu : HTTP 200, solde = 0.",
                            "value": {"amount": 10000, "description": "Retrait total"},
                        },
                        "CT-17 — Solde insuffisant (erreur)": {
                            "summary": "CT-17 : Solde insuffisant → 400",
                            "description": "Precondition : solde < 50000. Resultat attendu : HTTP 400, Solde insuffisant.",
                            "value": {"amount": 50000, "description": "Test solde insuffisant"},
                        },
                        "CT-18 — Montant nul (erreur)": {
                            "summary": "CT-18 : Montant = 0 → 422",
                            "description": "Resultat attendu : HTTP 422.",
                            "value": {"amount": 0},
                        },
                        "CT-19 — Montant negatif (erreur)": {
                            "summary": "CT-19 : Montant negatif → 422",
                            "description": "Resultat attendu : HTTP 422.",
                            "value": {"amount": -500},
                        },
                    }
                }
            }
        }
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
    summary="Historique des transactions",
    description="""
Retourne toutes les transactions (depots et retraits) associees a un compte bancaire.

**Cas de test couverts par cet endpoint :**

| # | Cas | Precondition | Reponse attendue |
|---|-----|-------------|-----------------|
| CT-21 | Compte sans transaction | Compte cree avec solde = 0 | HTTP 200 — tableau vide `[]` |
| CT-22 | Compte avec transactions | Depots et/ou retraits effectues | HTTP 200 — liste des transactions avec dates et soldes |
| CT-23 | Compte inexistant | ID invalide | HTTP 404 — `Compte introuvable.` |

**Test manuel :**
1. Creer un compte avec solde = 0 → consulter les transactions → verifier tableau vide
2. Creer un compte avec `initial_balance: 5000`, effectuer un depot et un retrait
3. Consulter les transactions → verifier que les 3 operations apparaissent dans l'ordre chronologique
""",
    responses={404: {"model": ErrorResponse, "description": "Compte introuvable."}},
)
def get_transactions(account_id: str) -> list[dict]:
    account = get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Compte introuvable.")
    return account["transactions"]
