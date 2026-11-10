from pathlib import Path

from logs_config import get_logger

# Logger du module storage : écrit dans logs/storage.log et logs/errors.log
logger = get_logger("storage")

# Dossier où on range les résultats : storage/results/
RESULTS_DIR = Path(__file__).resolve().parent / "results"


def save_counter(counter, filename, header):
    """Écrit un dictionnaire {nom: nombre} dans un fichier CSV (séparateur ;)."""
    try:
        RESULTS_DIR.mkdir(exist_ok=True)
        with open(RESULTS_DIR / filename, mode="w", encoding="utf-8") as f:
            f.write(header + "\n")
            for key in counter:
                f.write(f"{key};{counter[key]}\n")
        logger.info(f"{filename} : {len(counter)} lignes enregistrées")
    except Exception as e:
        logger.error(f"Impossible d'écrire {filename} : {e}")


def save_invalid_users(attempts, filename="invalid_users.csv"):
    """Écrit la liste des échecs avec utilisateur invalide (utilisateur;ip)."""
    try:
        RESULTS_DIR.mkdir(exist_ok=True)
        with open(RESULTS_DIR / filename, mode="w", encoding="utf-8") as f:
            f.write("utilisateur;ip\n")
            for a in attempts:
                f.write(f"{a['user']};{a['ip']}\n")
        logger.info(f"{filename} : {len(attempts)} lignes enregistrées")
    except Exception as e:
        logger.error(f"Impossible d'écrire {filename} : {e}")


def save_text(text, filename="dashboard.txt"):
    """Enregistre le texte du dashboard dans un fichier."""
    try:
        RESULTS_DIR.mkdir(exist_ok=True)
        with open(RESULTS_DIR / filename, mode="w", encoding="utf-8") as f:
            f.write(text)
        logger.info(f"{filename} enregistré")
    except Exception as e:
        logger.error(f"Impossible d'écrire {filename} : {e}")


def save_all(metrics, dashboard_text):
    """Enregistre toutes les statistiques dans storage/results/."""
    save_counter(metrics["failed_by_country"], "failed_by_country.csv", "pays;echecs")
    save_counter(metrics["success_by_user"], "success_by_user.csv", "utilisateur;reussites")
    save_invalid_users(metrics["invalid_user_details"])
    save_text(dashboard_text)