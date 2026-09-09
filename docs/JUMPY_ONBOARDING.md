# Prise en charge de Jumpy

## Audit et périmètre

Jumpy est un jeu Godot, pas une application Flutter. Le moteur de création Flutter ne peut pas être appliqué à ce dépôt existant. Le profil `control/existing-projects/jumpy.json` fixe la référence auditée au commit `b9a8df120dc5da807f68b610e7bfcd0422f8cff5`, avec Godot 4.7.2 et l'empreinte SHA-256 de son archive officielle.

La scène principale est `scenes/Main.tscn`. `scripts/main.gd` contient le gameplay, le rendu procédural et l'interface. `profile.gd` gère la sauvegarde ; `integrations.gd` isole les intégrations externes. L'export Android est déclaré, mais sa présence ne prouve pas qu'un APK a été construit.

Les documents historiques annoncent une évolution autonome active. Ce sont des déclarations historiques, pas une preuve de disponibilité actuelle. L'ancien workflow `jumpy-autocycle.yml` du serveur ignorait le sélecteur CI : il le consulte désormais avant de lancer ses scripts. Son transfert vers le nouveau moteur Godot n'est pas encore réalisé.

## Référence exécutable

Le mode CircleCI `jumpy-baseline`, désormais par défaut, fonctionne sans contexte secret. Il :
1. récupère uniquement la révision Git fixée dans le profil ;
2. vérifie l'archive officielle Godot par SHA-256 ;
3. importe le projet dans un environnement temporaire sans identifiants hérités ;
4. exécute huit assertions : état initial, répétabilité du niveau quotidien, saut de départ, consommation unique du pulse, refus d'un second pulse, enregistrement unique de la mort, affichage du retry et remise à zéro du score au redémarrage ;
5. conserve les journaux et un rapport explicite dans les artefacts CircleCI.

Le projet est copié dans un répertoire temporaire ; aucune modification n'est publiée dans Jumpy. Les sauvegardes utilisateur des tests sont isolées. Ce lanceur exécute un instantané revu, sans fournisseur IA : ce n'est pas encore un bac à sable pour du code produit automatiquement.

Commande : `python3 studio/godot_baseline.py`. Elle nécessite Linux x86_64, Python, Git et l'accès aux téléchargements GitHub. Un import réussi ne suffit pas : les erreurs Godot, l'échec d'une assertion ou l'absence du marqueur de fin font échouer le contrôle.

## État de validation et suite

66 tests Python du serveur passent localement. Les huit assertions GDScript sont ajoutées mais leur exécution réelle reste à confirmer sur un environnement disposant de Godot et de l'accès réseau nécessaire. Aucun résultat de test de gameplay, capture, APK ou qualité graphique n'est inventé.

Les observations statiques à vérifier ensuite incluent la validation des valeurs chargées depuis la sauvegarde, le refus des dépenses négatives dans `spend_coins`, et le comportement d'un tap hors bouton lorsque les réglages sont ouverts. Elles ne sont pas présentées comme des défauts reproduits sur appareil.

La suite nécessaire est de faire passer cette référence, reproduire un défaut ciblé par un test, préparer un correctif sur une branche Jumpy, puis vérifier tests, captures réelles et build Android avant livraison. La mutation autonome de projets Godot existants, les comparaisons visuelles et le build Android Godot restent à développer.
