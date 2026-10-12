# Recherche comparative Android et reverse engineering REA

Ce document connecte le démarrage du **Studio mobile** à la procédure de références d'applications Android de `repo-standards`. Il s'applique **aux nouvelles applications et refontes majeures** avant la spécification détaillée.

## Étapes de préparation (exigées avant de prétendre disposer d'un benchmark)

1. **Rechercher des alternatives** : de préférence 3 à 5 applications proches du besoin, avec éditeur, site/fiches officielles, version observée, publics cibles, capture autorisée et limites.
2. **Identifier les binaires réellement accessibles** : privilégier l'APK distribué directement par l'éditeur, une release officiellement publiée, ou un dépôt libre reconnu. Une URL de fiche Play Store **n'est pas** un lien de téléchargement APK. Les exports d'un appareil personnel doivent être distingués des téléchargements éditeur.
3. **Importer dans le catalogue de référence** : utiliser [`dbrckk/zombie-apk`](https://github.com/dbrckk/zombie-apk/blob/ad335eab2d65def1e63fbde0374fe2cba785b400/references/catalog.json) et son `scripts/reference_intake.py` pour conserver SHA-256, identité de package, preuves de certificat, URL, version et droits. Conserver les APK en stockage local/privé ; ne publier aucun binaire propriétaire dans le dépôt public sans autorisation.
4. **Inspecter avec REA** : [procédure REA immuable](https://github.com/dbrckk/repo-standards/blob/50662421a37d91cda086261d9b20b42288f66cc0/skills/app-reference-rea/SKILL.md), JDK 17+, JADX headless, commande `rea inspect-android-package ... --json`. Enregistrer ce qui a été **réellement exécuté** et l'empreinte du binaire inspecté. Conserver les JSON bruts dans `private-evidence/` (hors Git).
5. **Capitaliser et différencier** : constituer la matrice `référence → preuve → principe fonctionnel → implémentation originale → amélioration → validation`. Ne pas copier code, marques, interfaces pixel pour pixel, assets, clés, API privées ou méthodes de contournement.
6. **Brancher au brief** : fournir à la phase produit les liens officiels et les résumés d'inspection non propriétaires ; si REA ou APK indisponible, mentionner la cause exacte et travailler à partir des fonctionnalités publiquement documentées.

## Contrat d'état de la préparation

Produire ou mettre à jour un fichier de projet `docs/app-reference-research.md` avec :

| Champ | Valeur attendue |
| --- | --- |
| `benchmark_status` | `verified_sources` ou `insufficient_sources` |
| `comparables` | Éditeur, URL officielle, fonctionnalités démontrables (avec citations) |
| `apk_status` | `publisher_download_verified`, `private_export`, `store_only`, `unavailable` ou `unverified` |
| `apk_sha256`, `publisher_signer` | Valeurs **observées**, sinon `not_verified` |
| `rea_status` | `completed`, `blocked_missing_apk`, `blocked_missing_tool` ou `not_run` |
| `design_decisions` | Fonction observée, originalité, gain, critères de vérification |
| `legal_status` | Droits des binaires, ressources et licences établis ou `not_verified` |

Un brief dépourvu de cette recherche **ne prouve aucune analyse**. Le prompt `product` a été durci pour l'indiquer ; le runner existant ne possède **pas encore** un connecteur de recherche Google Play ou un moteur REA installé automatiquement. Un éditeur qui ne distribue pas d'APK directement ne doit pas être contourné, et le manque d'APK ne justifie pas une analyse inventée.

## Références

- [Skill REA / développement indépendant](https://github.com/dbrckk/repo-standards/blob/50662421a37d91cda086261d9b20b42288f66cc0/skills/app-reference-rea/SKILL.md)
- [Catalogue et outil d'ingestion APK](https://github.com/dbrckk/zombie-apk/blob/ad335eab2d65def1e63fbde0374fe2cba785b400/references/catalog.json)
- [REA amont](https://github.com/morluto/rea), [guide Android](https://github.com/morluto/rea/blob/main/docs/android-analysis.md)
- [Politique de confiance des sources externes](EXTERNAL_SOURCE_POLICY.md)

**Validation :** build et tests existants des composants affectés, après revue du PR. Aucun service hébergé, GPU, Play Console, publication ou licence ne sont déclenchés par cette procédure.
