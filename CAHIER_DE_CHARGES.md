# Cahier des charges

## Informations de l'étudiant

- Nom et prénom : **KOA ESSAMA PAULIN BRICE**
- Matricule : **25I2255**
- Niveau : **Licence 3 ICT**
- Établissement : **Université de Yaoundé I**
- Intitulé du devoir : **Conception d'une API pour un système de transaction bancaire**

## 1. Contexte

Les établissements financiers ont besoin de solutions numériques pour gérer les opérations de base des clients. Dans ce devoir, il s'agit de concevoir une API REST permettant de gérer des comptes bancaires et d'exécuter des opérations simples de transaction, notamment les dépôts et les retraits.

Cette API constitue une base logicielle pouvant être intégrée plus tard à une application web, mobile ou desktop.

## 2. Besoin

Le système doit permettre :

- d'enregistrer un nouveau client sous forme de compte bancaire
- de consulter la liste des comptes créés
- de consulter les informations d'un compte précis
- d'effectuer un dépôt sur un compte
- d'effectuer un retrait sur un compte
- de conserver l'historique des transactions réalisées

## 3. Objectif général

Mettre en place une API REST sécurisée et simple à utiliser pour gérer des comptes bancaires et les opérations de transaction de base.

## 4. Objectifs spécifiques

- créer un compte bancaire
- attribuer automatiquement un numéro de compte
- afficher la liste de tous les comptes
- afficher les détails d'un compte
- enregistrer les dépôts
- enregistrer les retraits
- vérifier qu'un retrait ne dépasse pas le solde disponible
- conserver les transactions dans une structure persistante

## 5. Acteurs

### 5.1 Client

Le client représente l'utilisateur final du système bancaire. Il peut :

- ouvrir un compte
- consulter son compte
- effectuer un dépôt
- effectuer un retrait
- consulter ses transactions

### 5.2 Administrateur système

L'administrateur supervise le bon fonctionnement de l'application. Il peut :

- consulter la liste des comptes
- suivre les transactions
- maintenir le système

## 6. Cas d'utilisation

### Cas d'utilisation 1 : Créer un compte

- Acteur principal : Client
- Description : le client fournit ses informations personnelles pour ouvrir un compte.
- Résultat attendu : un compte est créé avec un identifiant unique et un numéro de compte.

### Cas d'utilisation 2 : Consulter la liste des comptes

- Acteur principal : Administrateur système
- Description : le système affiche tous les comptes enregistrés.
- Résultat attendu : la liste complète des comptes est retournée.

### Cas d'utilisation 3 : Consulter un compte

- Acteur principal : Client
- Description : le client consulte les informations d'un compte donné.
- Résultat attendu : les informations du compte sont affichées.

### Cas d'utilisation 4 : Effectuer un dépôt

- Acteur principal : Client
- Description : le client ajoute de l'argent sur son compte.
- Résultat attendu : le solde du compte est mis à jour et la transaction est enregistrée.

### Cas d'utilisation 5 : Effectuer un retrait

- Acteur principal : Client
- Description : le client retire de l'argent de son compte.
- Résultat attendu : si le solde est suffisant, le montant est retiré et la transaction est enregistrée.

### Cas d'utilisation 6 : Consulter les transactions

- Acteur principal : Client
- Description : le client visualise l'historique de ses opérations.
- Résultat attendu : toutes les transactions associées au compte sont affichées.

## 7. Spécifications fonctionnelles

Le système doit :

- permettre la création d'un compte avec nom complet, numéro de téléphone, email et solde initial
- générer automatiquement un identifiant unique et un numéro de compte
- stocker les informations des comptes
- retourner la liste de tous les comptes créés
- retourner les détails d'un compte par son identifiant
- accepter un montant positif pour un dépôt
- accepter un montant positif pour un retrait
- refuser un retrait si le solde est insuffisant
- enregistrer chaque transaction avec sa date, son type, son montant et le solde après opération

## 8. Spécifications non fonctionnelles

Le système doit respecter les contraintes suivantes :

- **Performance** : la réponse de l'API doit être rapide pour les opérations simples
- **Fiabilité** : les données doivent être conservées dans un fichier JSON local
- **Maintenabilité** : le code doit être structuré de manière claire et modulaire
- **Évolutivité** : l'architecture doit permettre d'ajouter plus tard l'authentification, le virement et la suppression d'un compte
- **Sécurité** : les montants négatifs et les retraits non autorisés doivent être bloqués
- **Disponibilité** : l'API doit rester accessible tant que le serveur FastAPI est en cours d'exécution

## 9. Choix techniques

- Architecture : API REST
- Langage : Python
- Framework : FastAPI
- Serveur d'exécution : Uvicorn
- Persistance : fichier JSON local
- Format d'échange : JSON

## 10. Description des ressources de l'API

### 10.1 Créer un compte

- Méthode : `POST`
- URL : `/accounts`

#### Corps de la requête

```json
{
  "full_name": "KOA ESSAMA PAULIN BRICE",
  "phone_number": "699001122",
  "email": "paulin@example.com",
  "initial_balance": 10000
}
```

#### Réponse attendue

```json
{
  "id": "uuid-du-compte",
  "account_number": "ACC-20260415-AB12CD34",
  "full_name": "KOA ESSAMA PAULIN BRICE",
  "phone_number": "699001122",
  "email": "paulin@example.com",
  "balance": 10000,
  "created_at": "2026-04-15T15:00:00Z"
}
```

### 10.2 Lister les comptes

- Méthode : `GET`
- URL : `/accounts`

#### Réponse attendue

```json
[
  {
    "id": "uuid-du-compte",
    "account_number": "ACC-20260415-AB12CD34",
    "full_name": "KOA ESSAMA PAULIN BRICE",
    "phone_number": "699001122",
    "email": "paulin@example.com",
    "balance": 10000,
    "created_at": "2026-04-15T15:00:00Z"
  }
]
```

### 10.3 Consulter un compte

- Méthode : `GET`
- URL : `/accounts/{account_id}`

### 10.4 Faire un dépôt

- Méthode : `POST`
- URL : `/accounts/{account_id}/deposit`

#### Corps de la requête

```json
{
  "amount": 5000,
  "description": "Depot agence"
}
```

### 10.5 Faire un retrait

- Méthode : `POST`
- URL : `/accounts/{account_id}/withdraw`

#### Corps de la requête

```json
{
  "amount": 2000,
  "description": "Retrait DAB"
}
```

### 10.6 Lister les transactions d'un compte

- Méthode : `GET`
- URL : `/accounts/{account_id}/transactions`

## 11. Règles de gestion

- un compte possède un identifiant unique
- un compte possède un numéro de compte unique
- le solde initial doit être supérieur ou égal à zéro
- un dépôt doit obligatoirement avoir un montant strictement positif
- un retrait doit obligatoirement avoir un montant strictement positif
- un retrait est refusé si le solde du compte est insuffisant
- chaque opération modifie immédiatement le solde du compte
- chaque opération est enregistrée dans l'historique du compte

## 12. Limites actuelles du projet

Cette première version est volontairement simple :

- il n'y a pas encore d'authentification
- il n'y a pas encore de base de données relationnelle
- il n'y a pas encore de virement entre comptes
- les rôles client et administrateur ne sont pas encore séparés par un mécanisme d'accès

## 13. Conclusion

Ce projet répond au besoin de base d'un système de transaction bancaire académique. Il permet de créer des comptes, de les consulter, de gérer les dépôts et les retraits, et de garder une trace des opérations. Il constitue une bonne fondation pour une évolution vers un système bancaire plus complet.
