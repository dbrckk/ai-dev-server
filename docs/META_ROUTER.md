# Meta-router

Le meta-router est la première couche de l'évolution d'AI Dev Server vers un orchestrateur multi-agent.

## Objectif

- sélectionner un agent selon les capacités requises ;
- favoriser les solutions gratuites ;
- détecter les agents réellement installés ;
- consulter automatiquement `dbrckk/star-list` pour repérer des dépôts réutilisables ;
- garder les agents interchangeables.

## Utilisation

```bash
python studio/meta_router.py \
  --capability code_editing \
  --capability tests
```

Tâche longue :

```bash
python studio/meta_router.py \
  --capability repo_analysis \
  --capability long_task \
  --long-task
```

Recherche dans la star-list uniquement :

```bash
python studio/star_scanner.py agent memory mcp browser
```

## Agents enregistrés

- OpenCode
- Codex
- Claude Code
- DeepSeek Harness
- Hermes
- OpenHands

Un agent absent du système reste dans le classement mais reçoit une pénalité forte et n'est jamais sélectionné par `choose_agent`.

## Étape suivante

Brancher le routeur à l'orchestrateur existant, puis ajouter des adaptateurs d'exécution dédiés et un routeur multi-provider avec fallback et scoring historique.
