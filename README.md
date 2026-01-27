# TransportPro - Système de gestion de transport & livraison

Projet universitaire USTHB L3 ISIL  
**Auteurs :** Malak Lakroun, Meziane Halla, Ouznani Mohamed, Larbi Oussama

---

## Présentation

TransportPro est une application web complète pour la gestion des opérations de transport et de livraison. Elle permet de gérer l’ensemble du cycle logistique : clients, expéditions, tournées, chauffeurs, véhicules, incidents, réclamations, facturation, et bien plus.  
Le projet est développé avec Django (Python) et propose une interface moderne et intuitive pour les agents et administrateurs.

---

## Fonctionnalités principales

- **Gestion des expéditions**  
  - Création, édition, suppression d’expéditions
  - Suivi du statut (en attente, en cours, livrée, annulée)
  - Affectation à une tournée
  - Export PDF/CSV des expéditions

- **Gestion des clients**  
  - Ajout, modification, suppression de clients
  - Recherche et filtrage
  - Export CSV

- **Gestion des chauffeurs et véhicules**  
  - Ajout, modification, suppression de chauffeurs et véhicules
  - Affectation à des tournées

- **Gestion des destinations, zones tarifaires et types de service**  
  - Paramétrage des zones et tarifs
  - Gestion des types de services proposés

- **Gestion des tournées**  
  - Planification des tournées de livraison
  - Affectation automatique ou manuelle des expéditions
  - Suivi du déroulement de la tournée (heures, incidents, retards, etc.)

- **Facturation**  
  - Génération automatique des factures clients
  - Suivi des paiements et relances

- **Gestion des incidents et réclamations**  
  - Déclaration d’incidents lors des tournées
  - Suivi et traitement des réclamations clients

- **Dashboard administrateur et agent**  
  - Statistiques globales (nombre d’expéditions, taux de livraison, incidents, etc.)
  - Visualisation graphique des performances

- **Authentification et gestion des utilisateurs**  
  - Gestion des rôles (admin, agent, chauffeur)
  - Sécurité et permissions

---

## Structure du projet

```
delivery_management/
├── apps/
│   ├── clients/         # Gestion des clients
│   ├── dashboard/       # Tableaux de bord et statistiques
│   ├── expedition/      # Gestion des expéditions
│   ├── facturation/     # Factures et paiements
│   ├── incidents/       # Incidents de transport
│   ├── logistics/       # Chauffeurs, véhicules, destinations
│   ├── reclamation/     # Réclamations clients
│   ├── tour/            # Tournées de livraison
│   └── users/           # Utilisateurs et rôles
├── db.sqlite3           # Base de données SQLite (par défaut)
├── manage.py            # Commandes Django
├── static/              # Fichiers statiques (CSS, JS, images)
├── templates/           # Templates HTML
├── Pipfile              # Dépendances Python
└── README.md            # Ce fichier
```

Chaque dossier d’application contient un fichier `README.md` décrivant ses fonctionnalités spécifiques.

---

## Installation et démarrage

### 1. Cloner le dépôt

```sh
git clone <repo-url>
cd delivery_management
```

### 2. Installer les dépendances

```sh
pip install pipenv
pipenv install
pipenv shell
```

### 3. Appliquer les migrations

```sh
python manage.py makemigrations
python manage.py migrate
```

### 4. Créer un superutilisateur

```sh
python manage.py createsuperuser
```

### 5. Lancer le serveur de développement

```sh
python manage.py runserver
```

### 6. Accéder à l’application

- Application : [http://localhost:8000/](http://localhost:8000/)
- Administration : [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## Scripts utiles

- **Lancer les tests unitaires**
  ```sh
  python manage.py test
  ```
- **Générer les fichiers de migration**
  ```sh
  python manage.py makemigrations
  python manage.py migrate
  ```
- **Créer des données de démonstration (optionnel)**
  ```sh
  python manage.py loaddata <fixture>
  ```

---

## Technologies utilisées

- **Backend** : Python 3, Django 4
- **Frontend** : HTML5, CSS3, JavaScript (Bootstrap)
- **Base de données** : SQLite (par défaut, compatible PostgreSQL/MySQL)
- **PDF** : [WeasyPrint](https://weasyprint.org/) pour la génération de documents PDF
- **Gestion des dépendances** : Pipenv

---

## Organisation des rôles

- **Administrateur** : Gestion complète du système, accès à toutes les fonctionnalités
- **Agent** : Gestion opérationnelle (expéditions, tournées, incidents, etc.)


---

## Contribution

Les contributions sont les bienvenues !  
Merci de créer une issue ou une pull request pour toute suggestion ou amélioration.

---

## Licence

MIT License. Voir [LICENSE](LICENSE).

---

> Projet réalisé par Malak Lakroun, Meziane Halla, Ouznani Mohamed, Larbi Oussama  
> USTHB L3 ISIL
