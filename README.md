# AI Dev Server

Plateforme d'ingénierie autonome multi-engine et environnement de développement pour GitHub/Codespaces.

## Pipeline autonome

Le moteur `studio/` reçoit un brief, détecte le type de projet et prend en charge trois familles :

- **Flutter** : produit, design, développement, tests, rendu, revue visuelle, build release, device QA, store metadata, privacy/security, AAB/APK et signature Android trusted ;
- **Godot** : import de dépôt existant, tests headless, device/runtime journeys, visual QA, build AAB signé, metadata/privacy/security, final review et publication Play opt-in ;
- **Generic** : analyse de repo existant, planification, modifications, vérification réelle et revue sur Node/npm, Python, Go, Rust, Maven, Gradle, .NET et plusieurs autres toolchains détectées.

La génération continue jusqu'à une définition de fini vérifiée, un blocage technique réel, ou une action humaine externe explicitement requise.

La publication Google Play est **désactivée par défaut**. Lorsqu'elle est activée dans le brief, le chemin trusted utilise Android Publisher v3 en mode validate-first ; un commit Play requiert une approbation explicite côté runner. Les credentials de signing et de publication ne sont jamais transmis au modèle ou au workspace applicatif.

**[Configuration et limites du studio mobile](docs/MOBILE_STUDIO.md)** · **[Generic engine](docs/GENERIC_ENGINE.md)** · **[Jumpy/Godot](docs/JUMPY_ONBOARDING.md)** · **[Repli CircleCI](docs/CIRCLECI.md)**

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

Stacks de vérification détectées notamment : Node/npm, Python, Go, Rust, Maven, Gradle, .NET, Deno, Bun, PHP, Ruby, Elixir, Swift, CMake et Make.

Documentation : **[Generic autonomous project engine](docs/GENERIC_ENGINE.md)**.

## Mode autonome jusqu'à la fin

AI Dev Server vise désormais à prendre en charge **un nouveau projet ou un projet existant supporté**, à travailler dessus sans intervention de routine et à continuer jusqu'à satisfaction de la définition de fini vérifiée.

Les échecs de tests, erreurs de modèle, quotas temporaires, défauts de code ou capacités internes manquantes doivent déclencher réparation, reroutage, reprise ou adaptation automatique — pas un transfert du travail à l'utilisateur.

Une intervention humaine n'est demandée que pour un prérequis externe réellement non automatisable (clé API/token à placer dans un secret manager, identité/KYC, paiement, accord légal, action propriétaire sur un store, etc.). Dans ce cas le pipeline produit `USER_INPUT_REQUIRED.txt` et `user-input-required.json`, sans jamais écrire le secret lui-même.

Documentation : **[Autonomous project ownership](docs/AUTONOMOUS_PROJECTS.md)**.

## Meta-router multi-agent et apprentissage

Le routage ne se limite plus à un score statique :

- registre d'agents interchangeable dans `studio/agents/` ;
- sélection OpenCode / Codex / Claude Code / DeepSeek Harness / Hermes / OpenHands selon disponibilité/capacités ;
- apprentissage du succès vérifié par coût pour `model_only`, `agent_only`, `model→agent`, `agent→model` et `dual` ;
- exploration/exploitation bornée, recency, incertitude et détection de changement de régime ;
- mémoire contextuelle pondérée par type de tâche et stack ;
- scanner de `dbrckk/star-list` pour fournir des références de projets pertinentes ;
- budget prédictif, quotas de phase, timeout global, contrôle de dérive et réserve de vérification.

Commande rapide :

```bash
python studio/meta_router.py --capability code_editing --capability tests
```

Documentation : **[Meta-router et star-list](docs/META_ROUTER.md)**.

## Sécurité et gates CI

Les clés API, jetons et fichiers `.env` sont ignorés par Git. Ne jamais les committer dans le dépôt.

Le pipeline inclut notamment :

- sandbox applicatif sans credentials ;
- AAB signé uniquement après la build, hors workspace projet ;
- vérification de certificat/signature ;
- SBOM, hashes des dépendances, provenance registry et contrôle de licences ;
- classification privacy/Data Safety conservative ;
- checkpoints scellés et reprise inter-run ;
- vérification d'identité des PR de promotion de capabilities ;
- `Validate AI Dev Server`, `Mobile Studio Real Build`, `Multi-Engine E2E Benchmark` et `Fault Injection Gate`.

Le benchmark multi-engine couvre un vrai build Flutter, un smoke generic complet et les régressions Jumpy/Godot pinées.

### Exploitation V1.1

Commandes multi-projets :

```bash
python studio/fleet_dashboard.py --root studio-output
python studio/fleet_supervisor.py --root studio-output
python studio/fleet_maintenance.py --root studio-output
```

- `fleet_dashboard.py` agrège santé, état runtime, leases, checkpoints et télémétrie par projet ;
- `fleet_supervisor.py` produit des décisions déterministes `none/restart/quarantine/inspect` sans exécuter de redémarrage destructif ;
- `fleet_maintenance.py` compacte la télémétrie et supprime uniquement des fichiers temporaires reconnus dans `.autonomy`.

### Vérification opérationnelle V1

Le serveur expose maintenant deux contrôles machine-readable :

```bash
python studio/v1_gate.py
python studio/v1_gate.py --project-out studio-output/<project-id>
python studio/runtime_health.py studio-output/<project-id>
```

- `v1_gate.py` retourne `ready`, `operational` ou `blocked` et utilise un code de sortie non nul en cas de blocage ;
- `runtime_health.py` vérifie state durable, checkpoints, leases et télémétrie d'un projet autonome ;
- la disponibilité d'un hôte seul et la santé d'un projet actif restent volontairement séparées.

## Remarque

Free Claude Code et les fournisseurs IA évoluent rapidement. L'installation est volontairement séparée du build critique du Codespace afin qu'une modification de FCC ne rende pas la création du Codespace inutilisable.

