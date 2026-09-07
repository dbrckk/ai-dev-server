# AI Dev Server

Studio de création mobile autonome et environnement de développement pour GitHub Codespaces.

## Création d'une nouvelle application depuis ChatGPT

Le moteur `studio/` reçoit un brief dans `control/mobile-requests/`, enchaîne produit → design → développement → tests/compilation → revues → corrections et sauvegarde les sources dans une branche du dépôt cible. Il livre un APK Android debug et des captures quand les contrôles passent.

**[Configuration, utilisation et limites du studio mobile](docs/MOBILE_STUDIO.md)**. L'exemple est désactivé. Le moteur cible actuellement les nouvelles applications Flutter ; les cycles Jumpy historiques restent séparés.


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

## Sécurité

Les clés API, jetons et fichiers `.env` sont ignorés par Git. Ne jamais les committer dans le dépôt.

## Remarque

Free Claude Code et les fournisseurs IA évoluent rapidement. L'installation est volontairement séparée du build critique du Codespace afin qu'une modification de FCC ne rende pas la création du Codespace inutilisable.

