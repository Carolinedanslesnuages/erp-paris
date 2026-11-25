# ERP Paris

**Objectif :** La Préfecture de police publie la liste des établissements parisiens recevant du public sous la forme d'un fichier CSV difficile à réutiliser.
**Type :** API (sans écran), documentée en OpenAPI (`/api/docs`)
**Stack :** Python 3.13, FastAPI + PostgreSQL (modèle ADA `api-fastapi`)
**Créé le :** 2026-11-25 par Carolinedanslesnuages

## Lancer le projet
| Action | Commande |
|---|---|
| Base de données | `docker compose up -d` |
| Lancer l'API | `uvicorn app.main:app --reload` |

## Stories réalisées
- Demande libre #1 : recherche des établissements parisiens recevant du public (code postal, type, enseigne) à partir du fichier de la Préfecture de police nettoyé.
