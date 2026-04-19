# Cahier des charges

## Informations de l'étudiant

- Nom et prénom : **KOA ESSAMA PAULIN BRICE**
- Matricule : **25I2255**
- Niveau : **Licence 3 ICT**
- Établissement : **Université de Yaoundé I**
- Intitulé du devoir : **Conception d'une API JavaScript pour un système de transaction bancaire**

## 1. Contexte

Dans le domaine bancaire, les systèmes informatiques permettent d'automatiser la gestion des comptes et des opérations financières. Ce projet consiste à concevoir une API REST en JavaScript permettant de gérer des comptes bancaires, d'effectuer des dépôts, des retraits et de consulter l'historique des transactions.

## 2. Besoin

Le système doit permettre :

- de créer un compte bancaire
- de consulter la liste des comptes existants
- de consulter les informations d'un compte précis
- d'effectuer un dépôt sur un compte
- d'effectuer un retrait sur un compte
- de consulter l'historique des transactions d'un compte

## 3. Objectif général

Développer une API REST en JavaScript pour gérer les opérations bancaires de base d'un client à travers un système simple de comptes et de transactions.

## 4. Objectifs spécifiques

- créer un compte bancaire avec les informations du client
- générer un identifiant unique et un numéro de compte
- permettre le dépôt d'argent sur un compte
- permettre le retrait d'argent en vérifiant le solde disponible
- afficher la liste des comptes
- afficher les détails d'un compte
- afficher l'historique des transactions
- documenter l'API via une interface Swagger locale

## 5. Acteurs

### 5.1 Client

Le client est l'utilisateur principal du système. Il peut :

- ouvrir un compte
- consulter son compte
- effectuer un dépôt
- effectuer un retrait
- consulter l'historique de ses opérations

### 5.2 Administrateur système

L'administrateur assure le suivi du système. Il peut :

- consulter les comptes enregistrés
- suivre les transactions
- maintenir l'application

## 6. Cas d'utilisation

### Cas d'utilisation 1 : Créer un compte

- Acteur principal : Client
- Description : le client fournit ses informations personnelles pour créer un compte bancaire.
- Résultat attendu : un compte est créé avec un identifiant unique et un numéro de compte.

### Cas d'utilisation 2 : Lister les comptes

- Acteur principal : Administrateur système
- Description : le système retourne tous les comptes enregistrés.
- Résultat attendu : la liste des comptes est affichée.

### Cas d'utilisation 3 : Consulter un compte

- Acteur principal : Client
- Description : le client demande les informations détaillées de son compte.
- Résultat attendu : le système retourne les informations du compte et les transactions associées.

### Cas d'utilisation 4 : Effectuer un dépôt

- Acteur principal : Client
- Description : le client ajoute un montant sur son compte.
- Résultat attendu : le solde est mis à jour et une transaction de dépôt est enregistrée.

### Cas d'utilisation 5 : Effectuer un retrait

- Acteur principal : Client
- Description : le client retire un montant de son compte.
- Résultat attendu : si le solde est suffisant, le retrait est effectué et enregistré.

### Cas d'utilisation 6 : Consulter les transactions

- Acteur principal : Client
- Description : le client consulte l'historique de ses opérations.
- Résultat attendu : le système affiche toutes les transactions du compte.

## 7. Spécifications fonctionnelles

Le système doit :

- accepter la création d'un compte avec `full_name`, `phone_number`, `email` et `initial_balance`
- générer automatiquement `id` et `account_number`
- retourner la liste complète des comptes
- retourner les détails d'un compte par son identifiant
- accepter un dépôt si le montant est strictement positif
- accepter un retrait si le montant est strictement positif et le solde suffisant
- enregistrer chaque transaction avec son type, son montant, sa description, son solde après opération et sa date
- fournir une documentation Swagger accessible localement

## 8. Spécifications non fonctionnelles

Le système doit respecter les contraintes suivantes :

- **Simplicité** : le code doit rester lisible et adapté à un devoir académique
- **Performance** : les requêtes doivent répondre rapidement pour les opérations simples
- **Fiabilité** : les données doivent être manipulées correctement pendant l'exécution du serveur
- **Maintenabilité** : le code doit être structuré clairement
- **Portabilité** : l'application doit fonctionner avec Node.js sans dépendances externes
- **Disponibilité** : l'API doit être utilisable tant que le serveur est démarré

## 9. Choix techniques

- Langage : **JavaScript**
- Environnement : **Node.js**
- Architecture : **API REST**
- Serveur HTTP : **module natif `http`**
- Documentation : **Swagger UI local**
- Format d'échange : **JSON**
- Persistance : **mémoire vive pendant l'exécution**

## 10. Description des endpoints

### 10.1 Accueil

- Méthode : `GET`
- URL : `/`

### 10.2 Créer un compte

- Méthode : `POST`
- URL : `/accounts`

#### Exemple de requête

```json
{
  "full_name": "KOA ESSAMA PAULIN BRICE",
  "phone_number": "699001122",
  "email": "thierry@example.com",
  "initial_balance": 10000
}
```

### 10.3 Lister les comptes

- Méthode : `GET`
- URL : `/accounts`

### 10.4 Consulter un compte

- Méthode : `GET`
- URL : `/accounts/{account_id}`

### 10.5 Faire un dépôt

- Méthode : `POST`
- URL : `/accounts/{account_id}/deposit`

```json
{
  "amount": 5000,
  "description": "Depot agence"
}
```

### 10.6 Faire un retrait

- Méthode : `POST`
- URL : `/accounts/{account_id}/withdraw`

```json
{
  "amount": 2000,
  "description": "Retrait client"
}
```

### 10.7 Lister les transactions d'un compte

- Méthode : `GET`
- URL : `/accounts/{account_id}/transactions`

## 11. Règles de gestion

- chaque compte possède un identifiant unique
- chaque compte possède un numéro de compte unique
- le solde initial doit être supérieur ou égal à zéro
- un dépôt doit avoir un montant strictement positif
- un retrait doit avoir un montant strictement positif
- un retrait est refusé si le solde est insuffisant
- chaque transaction modifie immédiatement le solde
- chaque transaction est conservée dans l'historique du compte

## 12. Limites actuelles

Cette version JavaScript présente les limites suivantes :

- il n'y a pas d'authentification
- il n'y a pas de base de données
- les données sont perdues à l'arrêt du serveur
- il n'y a pas encore de virement entre comptes
- il n'y a pas de gestion avancée des rôles

## 13. Conclusion

Cette API bancaire en JavaScript répond aux besoins de base d'un système de transaction bancaire académique. Elle permet la création de comptes, la consultation des comptes, les dépôts, les retraits et l'affichage des transactions. Elle constitue une base simple pour une amélioration future vers une application bancaire plus complète.
