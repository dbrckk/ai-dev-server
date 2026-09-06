# AI Dev Server

Environnement de développement mobile-first pour GitHub Codespaces.

## Objectif

Depuis un smartphone, utiliser un Codespace comme machine Linux distante avec :

- Free Claude Code (FCC) comme passerelle multi-provider
- Claude Code
- OpenCode
- DeepSeek Harness Web
- cdesktop
- Git/GitHub
- outils de préparation de sprites

## Démarrage

1. Créer/ouvrir un Codespace sur ce dépôt.
2. Attendre la fin du `postCreateCommand`.
3. Dans le terminal, exécuter `./scripts/finish-fcc.sh` pour initialiser FCC si nécessaire.
4. Lancer une interface :
   - `./scripts/start-fcc.sh`
   - `./scripts/start-dsh.sh`
   - `./scripts/start-cdesktop.sh`

Les ports 8082, 3080 et 3000 sont prévus pour être forwardés par Codespaces.

> Les clés/API et authentifications restent à renseigner par l'utilisateur dans les interfaces concernées. Ne jamais les committer dans le dépôt.
