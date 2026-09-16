# Prise en charge de Jumpy

## Architecture active

Jumpy est un projet Godot existant. Il est pris en charge par le moteur multi-engine v1.3 via la requête `control/mobile-requests/jumpy.json` et le workflow générique `Autonomous Mobile Studio` (`.github/workflows/mobile-studio.yml`).

Le workflow spécialisé `jumpy-autocycle.yml` a été retiré afin qu'un seul ordonnanceur soit propriétaire du projet. Les anciens scripts `scripts/jumpy-studio-cycle-v*.sh` restent uniquement comme historique de migration ; ils ne constituent plus le chemin d'exécution planifié de Jumpy.

La requête Jumpy est activée avec la priorité maximale du contrat (`100`). La publication Google Play reste explicitement désactivée : le moteur peut mener le dépôt jusqu'à un candidat Android vérifié et doit signaler `human_action_required` lorsque la signature de release, un secret ou une action externe est réellement nécessaire.

## Projet cible

Dépôt : `dbrckk/Jumpy`.

Le moteur détecte Godot à partir de `project.godot` et importe le projet existant au lieu de le régénérer. La scène principale est `scenes/Main.tscn`. Le gameplay et le rendu sont principalement dans `scripts/main.gd`; le profil persistant est géré par `scripts/profile.gd` et les intégrations externes sont isolées dans `scripts/integrations.gd`.

L'objectif autonome est de terminer le jeu existant comme candidat de release Android, en conservant son coeur de gameplay : saut à une touche, correction aérienne, atterrissages parfaits/FLOW et progression déjà présente.

## Contrat de preuve v1.3

La réussite d'un cycle n'est pas équivalente à l'absence d'erreur d'un script. Le Goal Engine conserve l'objectif jusqu'à preuve machine de l'avancement ou jusqu'à un état terminal explicite.

Pour Godot, le chemin qualifié couvre notamment :

1. import et validation du projet existant ;
2. preview Godot vérifiée ;
3. export Android ;
4. QA sur appareil/runtime ;
5. parcours fonctionnels ;
6. QA visuelle ;
7. contrôles de release ;
8. artefact Android de release lorsque les éléments de signature sont disponibles ;
9. métadonnées/store assets ;
10. confidentialité et sécurité ;
11. revue finale liée aux preuves exactes.

Un échec technique reste un échec/réessai. Une capacité manquante déclenche l'adaptation prévue par le Goal Engine. Une action externe réellement nécessaire devient `human_action_required`. L'absence de patch ou d'agent ne doit jamais être transformée en faux succès.

## Publication et secrets

`play_publish.enabled` et `play_publish.commit` restent à `false` pour Jumpy. La création ou la fourniture d'une clé de signature, la configuration du Play Console et toute autorisation de publication restent hors du périmètre autonome tant qu'elles ne sont pas explicitement fournies par un canal sûr.

Les secrets GitHub/provider ne doivent pas être transmis au workspace produit ni aux validations Godot. Le moteur v1.3 conserve les frontières de confiance et les contrôles déjà qualifiés par la release stable.

## Baseline historique

Le profil `control/existing-projects/jumpy.json`, `studio/godot_baseline.py` et les anciens contrôles Jumpy restent utiles comme preuves historiques et tests de régression ciblés. Ils ne sont plus l'orchestrateur principal.

La première correction historique vérifiée concernait les dépenses invalides dans le profil. Cette preuve reste pertinente comme régression, mais la progression courante de Jumpy doit désormais passer par le Goal Engine multi-engine et ses checkpoints persistants.
