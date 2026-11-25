# Relecture : API de recherche des établissements parisiens recevant du public

Réalisé hors story, en mode libre

**Branche :** libre/1-la-prefecture-de-police-pu
**Demande :** une API qui lit le fichier CSV de la Préfecture de police, le nettoie et permet de
rechercher par code postal, par type d'établissement et par enseigne. Précisions du PO : enseigne =
mot contenu dans le nom sans tenir compte des majuscules ni des accents ; lignes inutilisables
ignorées avec indication de leur nombre.

## Critères d'acceptation
- [x] Nettoyage (espaces, point-virgule final, ville unique « Paris », types secondaires séparés) — `tests/test_erp_nettoyage.py` « test_les_espaces_en_trop_et_le_point_virgule_final_sont_retires », « test_toutes_les_villes_sont_ecrites_paris », « test_les_types_secondaires_multiples_sont_separes »
- [x] Enseigne contenant une virgule réparée — « test_une_enseigne_contenant_une_virgule_est_reparee »
- [x] Ligne irréparable écartée et comptée — « test_une_ligne_irreparable_est_ecartee_et_comptee », « test_la_reponse_indique_les_lignes_ecartees »
- [x] Recherche par code postal exact — `tests/test_erp.py` « test_recherche_par_code_postal_exact »
- [x] Recherche par type (principal ou secondaire) — « test_recherche_par_type_principal_et_secondaire »
- [x] Recherche par enseigne sans accents ni majuscules — « test_recherche_par_enseigne_sans_accent_ni_majuscule »
- [x] Filtres combinables, résultats paginés — « test_les_filtres_se_combinent », « test_resultats_pagines »
- [x] Aucun résultat = liste vide — « test_recherche_sans_resultat_renvoie_une_liste_vide »
- [x] Erreurs claires en français (422) — « test_code_postal_invalide_renvoie_un_message_clair », « test_parametres_de_page_invalides »
- [x] Routes dans la documentation — « test_les_routes_figurent_dans_la_documentation »
- [x] Lecture du vrai fichier — « test_le_vrai_fichier_est_lisible »

## Accessibilité (RGAA)
API sans écran : aucun test axe-core, aucun critère d'interface concerné.
- [ ] **À vérifier par un humain** : la documentation en ligne (`/api/docs`) est lisible, en français, avec des exemples fictifs.

## Périmètre
5 fichiers de code ou de test ajoutés (`app/erp.py`, `app/erp_nettoyage.py`, 2 fichiers de tests), 2 modifiés (`app/main.py`, `tests/test_sante.py`, dont une assertion assouplie : la liste des routes n'est plus limitée à `/api`) ; retiré car hors sujet : rien ; dépendances ajoutées : aucune.
À traiter séparément : le fichier contient environ 5 000 lignes vides (séparateurs seuls) ; elles sont ignorées et **non comptées** parmi les lignes écartées. Sur le vrai fichier, aucune ligne n'est écartée : les 53 lignes à virgules dans le nom sont réparées.

## État partagé
Aucun : le fichier est lu une fois et gardé en mémoire (pas de base de données, pas de migration).

## À vérifier en priorité par le développeur
- Réparation des lignes : le code postal sert de repère ; l'enseigne est tout ce qui précède les deux numéros et la voie.
- Hypothèses : 20 résultats par page par défaut, 50 au maximum ; toute ville devient « Paris ».
- Les tests utilisent de petits extraits fictifs ; un seul test lit le vrai fichier public.

## Résultat du contrôle final
- Tests : 23 réussis (0 d'accessibilité, sans écran) — code de retour 0
- Lint : code de retour 0
- Types (mypy) : code de retour 0
- Anti-fuite (gitleaks) : non lancé ici, aucun secret ajouté
