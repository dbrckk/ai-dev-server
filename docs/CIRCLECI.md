# Repli CircleCI du studio mobile

## État livré

Le dépôt contient une configuration CircleCI 2.1 et un adaptateur qui réutilise le moteur Flutter existant. Le fournisseur sélectionné dans `control/ci.json` est `circleci`, car les derniers jobs GitHub Actions n'ont pas démarré. Cette sélection ne connecte pas le compte CircleCI et ne prouve pas une exécution sur ce service.

Les contrôles sans secrets passent sur les branches. La génération est limitée à `main`, utilise le contexte `mobile-studio` et un groupe série propre au projet. Chaque demande reçoit un dossier d'artefacts distinct ; un échec ne masque pas les résultats des autres demandes. Le budget de la file est de 70 minutes par job, en plus des budgets du moteur. Une demande interrompue reprend depuis son dernier checkpoint distant lors d'une prochaine exécution.

## Activation unique dans CircleCI

1. Connecter le dépôt GitHub `dbrckk/ai-dev-server` à un projet CircleCI, avec sa configuration `.circleci/config.yml` sur `main` et un déclencheur de push.
2. Créer le contexte `mobile-studio`. Le restreindre à ce projet et à la branche `main` dans CircleCI. Ne pas mettre les secrets de génération dans les variables globales du projet, qui pourraient être accessibles aux jobs de validation.
3. Ajouter au contexte `STUDIO_API_KEY` et `STUDIO_GITHUB_TOKEN` (Contents lecture/écriture sur les dépôts cibles). Les noms de repli `NVIDIA_NIM_API_KEY` et `CODESPACES_PAT` sont acceptés. Les secrets Actions ne sont pas transférés automatiquement. Ne pas coller les clés dans une conversation ni dans Git.
4. Ajouter si nécessaire `STUDIO_API_BASE`, `STUDIO_MODEL`, `STUDIO_CODE_MODEL` et `STUDIO_VISION_MODEL`. Les valeurs par défaut restent celles du moteur.
5. Exécuter une pipeline avec le paramètre `mode=smoke` pour vérifier Docker, Flutter, les captures et l'APK sans contexte secret.
6. Exécuter `mode=queue` (valeur par défaut) pour traiter les briefs activés. Une file vide produit un rapport vide et ne sollicite pas le fournisseur IA.
7. Configurer dans l'interface CircleCI un déclencheur planifié sur `main`, avec `mode=queue`, pour reprendre les checkpoints. Choisir la fréquence selon les crédits disponibles. Aucun cron YAML n'est imposé : les anciens scheduled workflows ne fonctionnent pas avec toutes les intégrations GitHub App.

Le mode `preview` utilise le témoin fournisseur sans dépôt cible. Il nécessite aussi `enabled: true` dans `control/provider-probe.json` ; ce contrôle est désactivé par défaut.

Les artefacts sont dans l'onglet Artifacts du job : `mobile-studio/<id>/` pour les demandes et `flutter-smoke/` pour le témoin. Leur rétention dépend du compte CircleCI. CircleCI a ses propres quotas/crédits ; ce repli n'est pas une garantie de gratuité ou de disponibilité.

## Changer de moteur

`control/ci.json` accepte exactement :

- `{"provider":"circleci"}` : CircleCI traite les générations.
- `{"provider":"github"}` : GitHub Actions traite les générations.
- `{"provider":"disabled"}` : les deux adaptateurs de génération sont inactifs.

Le choix est partagé par la file et le lanceur. Les contrôles sans secrets peuvent continuer sur les deux services. Avant un changement, terminer ou annuler les anciennes générations en cours : un job déjà démarré conserve son checkout. La sérialisation CircleCI ne constitue pas un verrou distribué avec GitHub Actions.

Ce repli est piloté par le fichier versionné, pas par une détection autonome des pannes. Il ne dépend pas d'un job GitHub pour démarrer CircleCI. Un retour de GitHub Actions ne réactive donc pas la génération automatiquement. Les relances manuelles d'anciens commits doivent être évitées.

## Vérification disponible

57 tests Python passent localement, dont sélection exclusive du fournisseur, rejet de configuration inconnue, refus des branches non-main, validation complète avant traitement et conservation des résultats de plusieurs demandes. Le YAML est lisible et ses restrictions de branche/contexte ont été contrôlées localement. La validation officielle CircleCI et l'exécution distante restent à effectuer après connexion du projet et du contexte.

Références officielles :
- https://circleci.com/docs/reference/configuration-reference/
- https://circleci.com/docs/guides/security/contexts/
- https://circleci.com/docs/guides/orchestrate/schedule-triggers/
- https://circleci.com/docs/guides/orchestrate/controlling-serial-execution-across-your-organization/

## Incidents et rapports progressifs

Le rapport `queue.json` est remplacé atomiquement avant et après chaque demande. Il distingue `pending`, `running`, `finished`, `failed`, `timed_out`, `worker_error` et `deferred`. `finished` signifie que le lanceur a terminé sans erreur ; le statut précis de validation de l'application est dans son propre `report.json`.

À l'expiration du budget, le lanceur arrête le groupe de processus de la demande et supprime uniquement les conteneurs portant l'identifiant de cette exécution. Un échec de nettoyage reste explicite. Les demandes suivantes sont différées. Cela ne remplace pas la reprise depuis les checkpoints distants : les changements non encore sauvegardés peuvent être perdus. Une interruption brutale de la machine peut empêcher l'envoi des artefacts, même si le rapport local avait été écrit.

61 tests Python passent après ces renforcements, incluant erreurs de lancement, rapport progressif, délai dépassé, arrêt ciblé et enveloppes de réponse IA mal formées. Le nettoyage Docker est testé avec des doubles ; sa vérification distante CircleCI reste à effectuer.
