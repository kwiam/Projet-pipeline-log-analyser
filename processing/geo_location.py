import re
from pathlib import Path

from logs_config import get_logger


logger = get_logger("geolocation")


GEO_FILE = Path(__file__).resolve().parents[1] / "data_geo" / "geo_ips.csv"


IP_FORMAT = re.compile(r'^(?:\d{1,3}\.){3}\d{1,3}$')


def load_table():
    """Lit data_geo/geo_ips.csv et renvoie une liste de (début d'IP, pays)."""
    table = []
    try:
        with open(GEO_FILE, mode="r", encoding="utf-8") as f:
            for line in f:
                line = line.split("#")[0].strip()   
                if not line:
                    continue
                parts = line.split(";")
                if len(parts) == 2 and parts[1].strip():
                    table.append((parts[0].strip(), parts[1].strip()))
        logger.info(f"{len(table)} blocs d'IP chargés depuis {GEO_FILE.name}")
    except FileNotFoundError:
        logger.error(f"Fichier de géolocalisation introuvable : {GEO_FILE}")
    except Exception as e:
        logger.error(f"Erreur de lecture de {GEO_FILE.name} : {e}")
    return table



TABLE = load_table()


def get_country(ip):
    """Renvoie le pays d'une IP, ou 'Inconnu' si on ne le connaît pas.

    in : ip (texte, ex: '45.148.10.121') out : le pays (texte)
    """
    if not ip or not IP_FORMAT.match(ip):
        logger.warning(f"IP invalide ignorée : {ip!r}")
        return "Inconnu"

    
    if ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("127."):
        return "Réseau local"

    
    best_prefix = ""
    best_country = "Inconnu"
    for prefix, country in TABLE:
        if ip.startswith(prefix) and len(prefix) > len(best_prefix):
            best_prefix = prefix
            best_country = country
    return best_country


if __name__ == '__main__':
    print(get_country('10.10.33.81'))
    print(get_country('45.148.10.121'))