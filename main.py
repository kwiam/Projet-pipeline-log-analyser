"""Lance tout le pipeline : ingestion -> processing -> dashboard -> storage.

À lancer depuis la racine du projet :  python main.py
"""
from logs_config import get_logger
from ingestion.raw import toRows
from processing.extract_transforme import extract, summarize
from serving.app import generate_dashboard_metrics, build_dashboard
from storage.save import save_all

logger = get_logger("main")


def main():
    logger.info("Démarrage du pipeline")

    # 1. Ingestion : lire les fichiers de logs
    rows = toRows("data")
    if not rows:
        logger.error("Aucune ligne lue : vérifier le dossier data")
        print("Aucune ligne lue dans le dossier data.")
        return

    # 2. Processing : découper les lignes
    records = extract(rows)
    if not records:
        logger.error("Aucune ligne reconnue par la regex")
        print("Aucune ligne de log reconnue.")
        return

    summary = summarize(records)
    print(f"Lignes lues : {len(rows)}")
    print(f"Lignes analysées : {len(records)}")
    print("Événements :", summary["events"])
    print()

    # 3. Dashboard : calculer et afficher les 3 statistiques
    metrics = generate_dashboard_metrics(records)
    dashboard_text = build_dashboard(metrics)
    print(dashboard_text)

    # 4. Storage : enregistrer les résultats
    save_all(metrics, dashboard_text)
    logger.info("Pipeline terminé")


if __name__ == "__main__":
    main()