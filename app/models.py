from typing import Literal

from pydantic import BaseModel, Field


class AccountCreate(BaseModel):
    full_name: str = Field(
        ...,
        min_length=3,
        max_length=120,
        description="Nom complet du titulaire du compte.",
        examples=["KOA ESSAMA PAULIN BRICE"],
    )
    phone_number: str = Field(
        ...,
        min_length=6,
        max_length=20,
        description="Numero de telephone du client.",
        examples=["699001122"],
    )
    email: str | None = Field(
        default=None,
        max_length=120,
        description="Adresse email du client.",
        examples=["paulin@example.com"],
    )
    initial_balance: float = Field(
        default=0,
        ge=0,
        description="Solde initial du compte. Il doit etre superieur ou egal a zero.",
        examples=[10000],
    )


class AccountResponse(BaseModel):
    id: str = Field(description="Identifiant unique du compte.")
    account_number: str = Field(description="Numero unique du compte bancaire.")
    full_name: str = Field(description="Nom complet du titulaire.")
    phone_number: str = Field(description="Numero de telephone du titulaire.")
    email: str | None = Field(default=None, description="Adresse email du titulaire.")
    balance: float = Field(description="Solde courant du compte.")
    created_at: str = Field(description="Date de creation du compte au format ISO 8601.")


class TransactionRequest(BaseModel):
    amount: float = Field(
        ...,
        gt=0,
        description="Montant de l'operation. Il doit etre strictement positif.",
        examples=[5000],
    )
    description: str | None = Field(
        default=None,
        max_length=150,
        description="Libelle ou motif de la transaction.",
        examples=["Depot agence"],
    )


class TransferRequest(BaseModel):
    to_account_id: str = Field(
        ...,
        description="Identifiant UUID du compte destinataire.",
        examples=["b5c6d7e8-f9a0-1234-bcde-567890abcdef"],
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Montant a virer. Il doit etre strictement positif.",
        examples=[3000],
    )
    description: str | None = Field(
        default=None,
        max_length=150,
        description="Motif du virement.",
        examples=["Remboursement loyer"],
    )


class TransferResponse(BaseModel):
    from_account: "AccountDetails" = Field(description="Compte source apres le virement.")
    to_account: "AccountDetails" = Field(description="Compte destinataire apres le virement.")


class TransactionResponse(BaseModel):
    transaction_id: str = Field(description="Identifiant unique de la transaction.")
    transaction_type: Literal["deposit", "withdraw", "transfer_out", "transfer_in"] = Field(description="Type de transaction.")
    amount: float = Field(description="Montant de la transaction.")
    description: str | None = Field(default=None, description="Description de la transaction.")
    balance_after: float = Field(description="Solde du compte apres l'operation.")
    created_at: str = Field(description="Date de creation de la transaction au format ISO 8601.")


class AccountDetails(AccountResponse):
    transactions: list[TransactionResponse] = Field(default_factory=list)


TransferResponse.model_rebuild()


class HomeResponse(BaseModel):
    message: str = Field(description="Message de bienvenue de l'API.")
    documentation: str = Field(description="Lien vers l'interface Swagger locale.")


class ErrorResponse(BaseModel):
    detail: str = Field(description="Message d'erreur retourne par l'API.")
