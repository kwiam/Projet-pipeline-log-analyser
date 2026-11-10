Projet Pipeline Log Analyzer
Dans le cadre de mon cours de Python, j'ai réalisé un projet intitulé Pipeline Log Analyzer.
L'objectif de ce projet est de lire et d'analyser des fichiers de logs provenant d'un serveur afin d'extraire des informations sur les tentatives de connexion des utilisateurs.

+J'ai créé quatre modules principaux :

Ingestion : j'ai utilisé ce module pour lire les fichiers de logs présents dans le dossier data. J'ai également ajouté la possibilité de lire les fichiers compressés au format .gz.

Processing : j'ai ajouté ce module pour analyser les lignes récupérées, extraire les informations importantes et classer les événements.

Serving : j'ai utilisé ce module pour calculer les statistiques demandées et préparer les résultats du dashboard.

Storage : j'ai ajouté ce module pour enregistrer les résultats dans des fichiers CSV et dans un fichier texte.
J'ai également créé un fichier main.py à la racine du projet pour lancer les différents modules dans le bon ordre.

+Gestion des logs et des erreurs

J'ai créé un fichier logs_config.py pour centraliser la configuration des logs.

J'ai ajouté une fonction get_logger afin que chaque module puisse disposer de son propre fichier de logs.

J'ai également prévu un fichier commun logs/errors.log pour enregistrer les erreurs provenant des différents modules.

+ Analyse des fichiers de logs

Dans le module processing, j'ai utilisé les expressions régulières avec le module re pour extraire les informations présentes dans chaque ligne.

Les informations récupérées sont :

Le mois.

Le jour.

L'heure.

Le service.

Le message.

L'adresse IP.

Lors du traitement, j'ai obtenu les résultats suivants :

65 565 lignes lues.

65 555 lignes analysées.

10 lignes ignorées et signalées dans les logs.

+Localisation des adresses IP

J'ai créé le fichier processing/geo_location.py pour associer les adresses IP à des pays.

J'ai utilisé un fichier data_geo/geo_ips.csv contenant des correspondances entre des débuts d'adresses IP et des pays.

J'ai également prévu deux cas particuliers :

Les adresses IP privées sont identifiées comme « Réseau local ».

Les adresses IP absentes de ma table sont identifiées comme « Inconnu ».

+ Création du dashboard

Dans le module serving/app.py, j'ai ajouté les trois statistiques demandées :

Le nombre de tentatives de connexion échouées par pays.

Le nombre de connexions réussies par utilisateur.

Le nombre de tentatives échouées avec un utilisateur invalide.

Les résultats obtenus lors de mon analyse sont :

3 249 tentatives échouées avec un utilisateur invalide.

1 connexion réussie pour l'utilisateur adminesisa.

4 720 tentatives échouées associées au pays « Inconnu ».

+ Enregistrement des résultats

J'ai créé le fichier storage/save.py pour enregistrer les résultats du traitement.

Les résultats sont sauvegardés dans le dossier storage/results/.

J'ai prévu trois fichiers CSV pour les statistiques ainsi qu'un fichier dashboard.txt pour présenter les résultats.

J'ai aussi ajouté une gestion des erreurs avec try/except afin de signaler les problèmes pouvant survenir pendant l'écriture des fichiers.


+ Utilisation de Git

J'ai effectué des commits progressivement, en séparant les différentes étapes du projet par module.

J'ai également effectué des push après les différentes étapes afin d'envoyer les modifications sur le dépôt distant.

Pour consulter l'historique des commits, j'ai utilisé :

git log --oneline

+ Exécution du projet

Pour lancer le programme :

python main.py

