# Système de transaction bancaire

API REST simple réalisée dans le cadre d'un devoir de Licence 3 ICT.

Étudiant : **KOA ESSAMA PAULIN BRICE**  
Matricule : **25I2255**  
Université : **Université de Yaoundé I**

## Fonctionnalités

- création d'un compte bancaire
- consultation de la liste des comptes
- consultation d'un compte précis
- dépôt d'argent sur un compte
- retrait d'argent sur un compte
- consultation de l'historique des transactions

## Technologies utilisées

- Python 3
- FastAPI
- Uvicorn
- stockage local dans un fichier JSON

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancement

```bash
uvicorn app.main:app --reload
```

L'API sera disponible sur :

- `http://127.0.0.1:8000`
- documentation Swagger : `http://127.0.0.1:8000/docs`

## Endpoints principaux

- `POST /accounts` : créer un compte
- `GET /accounts` : lister les comptes
- `GET /accounts/{account_id}` : afficher un compte
- `POST /accounts/{account_id}/deposit` : effectuer un dépôt
- `POST /accounts/{account_id}/withdraw` : effectuer un retrait
- `GET /accounts/{account_id}/transactions` : lister les transactions d'un compte

## Exemple de création de compte

```bash
curl -X POST http://127.0.0.1:8000/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Paulin Brice Koa Essama",
    "phone_number": "699001122",
    "email": "paulin@example.com",
    "initial_balance": 25000
  }'
```

## Structure du projet

```text
304_DEVOIR/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── storage.py
├── data/
│   └── accounts.json
├── CAHIER_DE_CHARGES.md
├── README.md
└── requirements.txt
```
