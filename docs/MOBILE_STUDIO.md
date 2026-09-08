# Studio mobile autonome

## Ce qui est implémenté

Un moteur générique pour **nouvelles applications Flutter**, avec livraison Android de démonstration. Le dépôt de contrôle reçoit un brief JSON ; GitHub Actions enchaîne produit, direction artistique, développement, tests, revue de code, inspection multimodale des captures et corrections. Les rôles sont des appels distincts au modèle configuré, pas une garantie d'indépendance entre plusieurs fournisseurs.

Les sources et l'état sont enregistrés dans `studio/<id>` du dépôt cible. Les échecs et budgets épuisés restent explicites. Le moteur ne fusionne pas automatiquement et ne publie pas sur les stores.

## Utilisation depuis une conversation ChatGPT

1. Créer un dépôt GitHub **vide**, ou avec seulement README, LICENSE et .gitignore.
2. Donner son URL et les instructions générales à ChatGPT disposant d'un connecteur GitHub autorisé à écrire.
3. ChatGPT crée un fichier `control/mobile-requests/<id>.json` dans `ai-dev-server`, à partir de l'exemple, avec le bon `target_repo` et `enabled: true`.
4. Le push sur main déclenche le workflow. La planification toutes les 20 minutes reprend les demandes inachevées, dans les limites fixées. La planification est best effort ; ce n'est pas une horloge garantie. Désactiver une demande empêche les futurs cycles, sans interrompre un job déjà lancé (annulable dans Actions).
5. Lire `report.json`, les captures et `app-debug.apk` lorsqu'il existe dans les artifacts du workflow. Le code et les checkpoints sont dans le dépôt cible.

ChatGPT ne transmet pas automatiquement les conversations à GitHub : le connecteur doit réellement écrire le brief. Un simple message sans accès GitHub ne déclenche rien.

## Configuration initiale unique

Dans les secrets Actions de ce dépôt :

| Paramètre | Usage |
|---|---|
| `STUDIO_GITHUB_TOKEN` | Jeton avec Contents lecture/écriture sur les dépôts cibles. Repli sur `CODESPACES_PAT` existant ; son accès réel reste à vérifier. |
| `STUDIO_API_KEY` | Clé du fournisseur IA. Repli sur `NVIDIA_NIM_API_KEY` existant. |

Dans les variables Actions :

| Paramètre | Valeur par défaut |
|---|---|
| `STUDIO_API_BASE` | `https://integrate.api.nvidia.com/v1` ; API HTTPS compatible chat/completions |
| `STUDIO_MODEL` | `nvidia/nemotron-3-super-120b-a12b` ; doit être disponible pour la clé configurée |
| `STUDIO_VISION_MODEL` | Sur le endpoint NVIDIA par défaut : `nvidia/nemotron-nano-12b-v2-vl`. Sur un autre fournisseur : configuration explicite requise. La valeur `disabled` désactive la revue. |

Les noms de modèles/configurations fournisseurs ne prouvent pas leur disponibilité. Un fournisseur absent, un quota ou une réponse invalide bloque explicitement. Aucun abonnement ChatGPT n'est converti en clé API par ce moteur. Le fournisseur IA et GitHub Actions peuvent consommer des quotas ou être facturés selon votre compte ; le code ne garantit pas un fonctionnement gratuit illimité.

## Contrat et budgets

L'exemple est **désactivé** et ne crée aucune application sans brief activé. Champs obligatoires : `id`, `target_repo`, `app_name`, `brief`, `enabled`. Champs optionnels : `max_rounds` (3 par défaut, maximum 6), `max_calls` (12, maximum 30), `max_cycles` (5, maximum 10). Une tentative HTTP peut être réessayée deux fois sur une erreur transitoire ; le plafond concerne les appels logiques, pas le nombre exact de requêtes ni un plafond monétaire. Cinq projets actifs maximum, un brief actif par dépôt cible.

Le même identifiant désigne un brief immuable. Pour un autre brief, utiliser un nouvel identifiant et un nouveau dépôt vide. La mise à jour d'une application existante avec un nouveau brief est une évolution future, pas une fonctionnalité annoncée comme livrée.

## Contrôles exécutés

- Validation stricte du brief, chemins, types, taille et recherche de motifs de secrets.
- Produit et design persistés ; checkpoints après les phases et les essais échoués.
- Analyse Flutter, tests du projet, quatre rendus réels par parcours déclaré et pour l'écran initial : compact clair, compact sombre, grand texte, écran large.
- Assertions de rendu sans exception, taille des cibles Android, étiquettes d'accessibilité et contraste ; les règles Flutter ne remplacent pas un audit complet.
- Compilation d'un APK debug, existence et empreinte SHA-256 de l'artefact livré.
- Revue du code puis revue des captures par modèle vision, avec correction automatique si rejet.

L'image de compilation Flutter 3.44.0 Linux amd64 est épinglée au digest publié par Cirrus Labs : https://github.com/cirruslabs/docker-images-flutter/pkgs/container/flutter . Sources de l'image : https://github.com/cirruslabs/docker-images-flutter ; licence MIT. L'image est une dépendance de build isolée. Les SDK et dépendances d'applications gardent leurs licences respectives.

## Isolation

Le modèle produit du JSON avec des fichiers complets ; aucune commande shell générée n'est exécutée sur l'hôte. Le modèle ne peut pas éditer `.github/`, la configuration native Android/iOS, les tests réservés `__studio*`, ni le moteur de validation. Les fichiers natifs proviennent de `flutter create`.

Les processus applicatifs s'exécutent dans Docker sans clé fournisseur, jeton GitHub, socket Docker, dépôt `.git` ou répertoire personnel de l'hôte. Réseau désactivé pour analyse/tests ; activé pour résolution des dépendances et build Android. Limites CPU/mémoire/processus et délais. Les conteneurs sont supprimés sur dépassement de délai de commande. Le code applicatif peut toujours être erroné ou malveillant : Docker et la recherche de motifs ne constituent pas une preuve formelle de sécurité.

## Statuts et limites de livraison

| Statut | Signification |
|---|---|
| `disabled` | Demande inactive |
| `product_complete`, `design_complete` | Checkpoint intermédiaire |
| `repair_needed` | Contrôle ou revue échoué ; reprise au prochain cycle si budget disponible |
| `blocked` | Configuration, fournisseur, protocole ou autre erreur bloquante |
| `awaiting_visual_review` | APK et revue de code disponibles ; modèle vision non configuré |
| `validated_preview` | Contrôles de cette version passés ; aucune promesse de perfection ni certification store |

Tous les rapports portent `release_status: not_store_ready`. Les tests visuels intégrés couvrent **l’écran initial et l’écran final de chaque parcours déclaré**. Ils ne couvrent pas automatiquement tous les états possibles. Les parcours d’acceptation sont figés dans le livrable produit avant le développement et rejoués par un banc de test que le modèle ne peut pas éditer par ses patches. Les tests supplémentaires restent générés pour le brief. Les goldens sont créés pour inspection, pas comparés à une référence de design approuvée. La revue IA peut manquer des défauts.

L'APK est une version debug installable pour essai, pas un AAB signé de production. iOS dispose de sources de plateforme générées, mais aucun build iOS n'est exécuté. Authentification, backend, paiements, publicités, push, configuration native spécifique, publication Play/App Store et assets raster complexes nécessitent encore des intégrations dédiées. Le moteur doit signaler ces dépendances, pas les simuler.

## Vérification du moteur

`python -m unittest discover -s tests -v` teste l'orchestration avec doubles de test, y compris échecs et reprise. Ce n'est pas une preuve de génération réelle par un modèle.

`python studio/smoke.py` utilise Docker et le SDK réels pour compiler et rendre une application témoin déterministe. Le job `mobile-smoke` de la CI exécute ce test sans secrets. Il ne teste pas la connectivité fournisseur ni les permissions du jeton cible.


## Parcours d’acceptation exécutables

Le livrable produit doit définir `journeys` : 1 à 6 parcours identifiés, chacun contenant 2 à 12 étapes, avec au moins une interaction et une assertion. Actions autorisées : `tap`, `enter_text`, `scroll`, `expect_text`, `expect_absent`, `expect_key`. Les sélecteurs sont des `ValueKey<String>` stables. Chaque parcours repart d’une application fraîche. Les chaînes sont encodées comme données, jamais interpolées en code Dart.

Chaque parcours s’exécute dans les quatre configurations d’affichage. Les captures de sa destination font l’objet d’une revue visuelle séparée ; toutes les revues doivent passer. Le budget d’appels s’applique aussi aux revues, donc un budget insuffisant peut bloquer un projet complexe. Les captures précédentes sont effacées avant le prochain essai.

## Essai réel du fournisseur sans dépôt cible

Le workflow `Real Provider Mobile Preview` exécute une génération réelle et bornée d’un minuteur de concentration, via `studio/provider_probe.py`. Il livre `source.zip`, le rapport, les captures et l’APK si les contrôles réussissent. Ce mode ne crée ni ne modifie un dépôt cible ; le champ de cible `preview/focus` est un identifiant local. Il ne prouve donc pas les permissions d’écriture du jeton GitHub.

Le contrôle `control/provider-probe.json` active/désactive cet essai. Il n’a aucune planification récurrente. Le budget est de 12 appels logiques et deux essais d’implémentation maximum. Aucun jeton GitHub cible n’est transmis au job. Sans clé fournisseur, le moteur s’arrête avant de démarrer Docker.


La réponse d’un modèle qui enfreint le schéma produit, fichiers ou verdict reçoit une demande de correction unique, comptabilisée dans le budget global. Les anciennes validations sans parcours ne sont plus considérées comme validées par le contrat actuel ; une nouvelle validation est nécessaire, dans le budget de cycles restant.

Le modèle vision NVIDIA par défaut est documenté ici : https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-nano-12b-v2-vl . Sa disponibilité effective et les quotas restent ceux de la clé configurée. Aucun autre fournisseur n’est sélectionné silencieusement.


Les réponses JSON invalides ou tronquées disposent également d’une reprise de protocole. Pour Nemotron 3 sur le endpoint NVIDIA, le budget de raisonnement est borné à 2 048 tokens afin de réserver de la place au livrable ; la réponse totale est limitée à 8 192 tokens pour les rôles documentaires/revues et 16 000 pour le code. Le mécanisme documenté est https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-super-120b-a12b-infer . Ces paramètres ne sont pas envoyés à d’autres modèles ou fournisseurs.
