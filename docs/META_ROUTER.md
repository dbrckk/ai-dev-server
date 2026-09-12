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


## Routage multi-provider

Le studio accepte maintenant plusieurs endpoints compatibles `/chat/completions`.

Le fournisseur historique reste configuré avec :

- `STUDIO_API_BASE`
- `STUDIO_API_KEY`
- `STUDIO_MODEL`
- `STUDIO_CODE_MODEL`
- `STUDIO_VISION_MODEL`

Des fallbacks peuvent être ajoutés avec `STUDIO_PROVIDERS_JSON`. Les clés ne sont jamais placées dans le JSON : chaque entrée référence uniquement le nom d'une variable d'environnement contenant le secret.

Exemple :

```json
[
  {
    "name": "fallback-free",
    "base": "https://example-provider.invalid/v1",
    "key_env": "FALLBACK_API_KEY",
    "model": "general-model",
    "code_model": "coding-model",
    "vision_model": "vision-model",
    "priority": 80,
    "free_preferred": true
  }
]
```

Le routeur :

1. privilégie les fournisseurs marqués gratuits ;
2. sélectionne le modèle adapté au rôle ;
3. ignore un fallback dont la clé n'est pas disponible ;
4. bascule sur le fournisseur suivant si l'endpoint courant échoue ;
5. conserve `models_used` et `providers_used` pour la traçabilité.

Les fournisseurs vision sans `vision_model` ne sont pas utilisés pour les revues d'images.

### Suite

Le prochain palier est de faire passer aussi les chemins spécialisés (notamment l'auto-évolution) par ce routeur, puis d'ajouter un scoring historique de disponibilité/qualité/latence.
