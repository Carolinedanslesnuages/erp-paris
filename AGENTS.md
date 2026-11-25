# ERP Paris — instructions pour les agents de code

Lu par Codex, OpenCode, Cursor, Copilot, Gemini CLI… ; `CLAUDE.md` l'importe pour Claude Code.

Objectif : La Préfecture de police publie la liste des établissements parisiens recevant du public sous la forme d'un fichier CSV difficile à réutiliser.

**C'est une API, sans écran** : d'autres services l'appellent. Sa **documentation OpenAPI**
(`/api/docs`, générée à partir du code) est ce que montre l'aperçu : elle doit rester juste et lisible.

## Conventions
- **Noms explicites** : chaque variable, fonction, paramètre ou classe dit ce qu'il contient ou
  fait, en toutes lettres et en français (`reservations_du_jour`, `salle_libre`), jamais `x`, `s`,
  `tmp`, `data2`. Seuls les noms imposés par les bibliothèques restent tels quels.
- Python 3.13, FastAPI. **Un module par domaine** (`app/<domaine>.py`, un `APIRouter` nommé
  `routes`), branché dans `app/main.py`. Routes sous `/api/<domaine>` ; la racine mène à la
  documentation.
- **Entrées et sorties typées** par des modèles Pydantic (`BaseModel`) : la validation est
  automatique et un champ inconnu est refusé (`model_config = ConfigDict(extra="forbid")`).
  Types partout : mypy en mode strict, la CI échoue sinon.
- **Documentation** : chaque route a ses `tags`, son `summary`, ses réponses d'erreur
  (`responses={404: …}`) ; chaque champ ses `Field(description=…, examples=[…])` **fictifs**, en français.
- **Erreurs** : codes HTTP justes, message clair en français
  (`raise HTTPException(status_code=404, detail="Réservation introuvable")`).
- **Base** : SQLAlchemy 2 (`app/base.py`, une session par requête via `Depends(session_base)`).
  **Toute évolution de la base = une migration Alembic**
  (`alembic revision --autogenerate -m "<sujet>"`, relue avant fusion), signalée pour relecture.
- **Changement incompatible** pour les services qui appellent l'API (champ renommé ou supprimé,
  route déplacée) : à éviter ; sinon le signaler, et le commit le dit (`feat!:`).
- Tout critère d'acceptation se traduit par au moins un test pytest (`tests/test_<domaine>.py`,
  client `TestClient`), réponses d'erreur comprises.
- Dépendances : versions figées dans `requirements.txt` (application) et
  `requirements-dev.txt` (outils) ; une nouvelle dépendance est justifiée dans la fiche.

## Commandes
| Action | Commande |
|---|---|
| Environnement | `python3.13 -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt` |
| Base de données | `docker compose up -d` puis `alembic upgrade head` |
| Lancer l'API | `uvicorn app.main:app --reload` (documentation : http://localhost:8000/api/docs) |
| Tests | `pytest` |
| Lint et format | `ruff check . && ruff format --check .` |
| Types | `mypy app` |

## Messages de commit (release-please)
Conventional Commits, versions SemVer calculées par release-please (jamais à la main) :
`fix: …` → correctif (0.2.0 → 0.2.1), `feat: …` → fonctionnalité (0.2.0 → 0.3.0),
`feat!: …` ou `BREAKING CHANGE:` → changement incompatible (majeure ; mineure avant 1.0.0),
`test:`, `docs:`, `chore:`, `refactor:` → sans nouvelle version. Fusion en squash : le
**titre de la PR** devient le commit de `main` (contrôle « Titre de PR » en CI). Story issue
d'une issue GitHub : `Closes #<numéro>` dans le corps.

## Règles absolues
- **Un fichier, une responsabilité** : au plus 400 lignes non vides par fichier de code, 600 par fichier de test (contrôle « Taille des fichiers » en CI). Découper par responsabilité, jamais une fonction par fichier ; un fichier déjà trop long ne grossit plus.
- Aucune donnée réelle, aucun secret dans le dépôt (gitleaks bloque en CI, et en local une fois `pre-commit install` lancé ; `--no-verify` interdit).
- Une branche par story (`story/…`) ou par bug (`fix/…`) ; jamais de fusion par l'agent.
- Les décisions d'architecture sont tracées dans `docs/adr/`.
