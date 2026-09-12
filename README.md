# AI Dev Server

Studio de création mobile autonome et environnement de développement pour GitHub Codespaces.

## Création d'une nouvelle application depuis ChatGPT

Le moteur `studio/` reçoit un brief dans `control/mobile-requests/`, enchaîne produit → design → développement → tests/compilation → revues → corrections et sauvegarde les sources dans une branche du dépôt cible. Il livre un APK Android debug et des captures quand les contrôles passent.

**[Configuration, utilisation et limites du studio mobile](docs/MOBILE_STUDIO.md)**. **[Repli CircleCI et activation](docs/CIRCLECI.md)**. L'exemple est désactivé. Le moteur cible actuellement les nouvelles applications Flutter ; les cycles Jumpy historiques restent séparés.


**[Prise en charge de Jumpy : référence Godot](docs/JUMPY_ONBOARDING.md)**

## Objectif

Depuis un smartphone, utiliser un Codespace comme machine Linux distante avec :

- Free Claude Code (FCC) comme passerelle multi-provider
- Claude Code
- OpenCode
- DeepSeek Harness Web
- cdesktop
- Git/GitHub
- génération de sprites via le plugin Pollinations pour OpenCode

## Démarrage

1. Créer/ouvrir un Codespace sur ce dépôt.
2. Attendre la fin du `postCreateCommand`.
3. Dans le terminal, exécuter `bash scripts/finish-fcc.sh` pour initialiser FCC si nécessaire.
4. Lancer l'interface voulue :
   - `bash scripts/start-fcc.sh`
   - `bash scripts/start-dsh.sh`
   - `bash scripts/start-cdesktop.sh`
5. Pour ajouter la génération d'images/sprites à OpenCode : `bash scripts/enable-sprites.sh`, puis `/poll login` dans OpenCode.

Les ports 8082, 3080 et 3000 sont prévus pour être forwardés par Codespaces.

## Generic autonomous engine

Les projets qui ne sont ni Flutter ni Godot passent maintenant par un moteur générique : analyse du repo, recherche de projets similaires dans le portefeuille GitHub du propriétaire, planification, modifications, vérifications réelles, revue, checkpoint Git puis nouvelle itération jusqu'à validation.

Stacks de vérification détectées actuellement : Node/npm, Python, Go, Rust, Maven, Gradle et .NET.

Documentation : **[Generic autonomous project engine](docs/GENERIC_ENGINE.md)**.

## Mode autonome jusqu'à la fin

AI Dev Server vise désormais à prendre en charge **un nouveau projet ou un projet existant supporté**, à travailler dessus sans intervention de routine et à continuer jusqu'à satisfaction de la définition de fini vérifiée.

Les échecs de tests, erreurs de modèle, quotas temporaires, défauts de code ou capacités internes manquantes doivent déclencher réparation, reroutage, reprise ou adaptation automatique — pas un transfert du travail à l'utilisateur.

Une intervention humaine n'est demandée que pour un prérequis externe réellement non automatisable (clé API/token à placer dans un secret manager, identité/KYC, paiement, accord légal, action propriétaire sur un store, etc.). Dans ce cas le pipeline produit `USER_INPUT_REQUIRED.txt` et `user-input-required.json`, sans jamais écrire le secret lui-même.

Documentation : **[Autonomous project ownership](docs/AUTONOMOUS_PROJECTS.md)**.

## Meta-router multi-agent

Le dépôt contient désormais une première couche de routage par capacités :

- registre d'agents interchangeable dans `studio/agents/` ;
- scoring selon capacités, disponibilité, gratuité et tâches longues ;
- sélection OpenCode / Codex / Claude Code / DeepSeek Harness / Hermes / OpenHands ;
- scanner automatique de `dbrckk/star-list` pour rechercher des dépôts utiles à chaque nouvelle phase de projet.

Commande rapide :

```bash
python studio/meta_router.py --capability code_editing --capability tests
```

Documentation : **[Meta-router et star-list](docs/META_ROUTER.md)**.

## Sécurité

Les clés API, jetons et fichiers `.env` sont ignorés par Git. Ne jamais les committer dans le dépôt.

## Remarque

Free Claude Code et les fournisseurs IA évoluent rapidement. L'installation est volontairement séparée du build critique du Codespace afin qu'une modification de FCC ne rende pas la création du Codespace inutilisable.

