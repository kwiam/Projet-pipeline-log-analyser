import re

from logs_config import get_logger
from processing.geo_location import get_country


logger = get_logger("serving")


USER_PATTERN = re.compile(r'(?:for (?:invalid user )?|[Ii]nvalid user )(\S*) from')


def extract_user_from_message(message):
    """Renvoie le nom d'utilisateur du message, ou 'inconnu' s'il est vide."""
    match = USER_PATTERN.search(message)
    if match and match.group(1):
        return match.group(1)
    return "inconnu"


def add_one(counter, key):

    if key in counter:
        counter[key] = counter[key] + 1
    else:
        counter[key] = 1


def sort_desc(counter):
    """Trie un dictionnaire du plus grand nombre au plus petit."""
    pairs = []
    for key in counter:
        pairs.append((counter[key], key))
    pairs.sort(reverse=True)

    result = {}
    for value, key in pairs:
        result[key] = value
    return result


def generate_dashboard_metrics(records):
    """Calcule les 3 statistiques du dashboard.

    - échec = message sshd qui commence par "Failed password"
    - échec avec utilisateur invalide = "Failed password for invalid user"
    - réussite = message sshd qui commence par "Accepted"
    """
    failed_by_country = {}
    success_by_user = {}
    invalid_user_attempts = []

    for r in records:
        if r["service"] != "sshd":
            continue

        message = r["message"]
        try:
            if message.startswith("Accepted"):
                # Statistique 2 : réussites par utilisateur
                user = extract_user_from_message(message)
                add_one(success_by_user, user)

            elif message.startswith("Failed password"):
                # Statistique 1 : échecs par pays
                country = get_country(r["ip"])
                add_one(failed_by_country, country)

                # Statistique 3 : échecs avec un utilisateur invalide
                if message.startswith("Failed password for invalid user"):
                    user = extract_user_from_message(message)
                    invalid_user_attempts.append({"user": user, "ip": r["ip"]})
        except Exception as e:
            logger.error(f"Erreur sur la ligne {message!r} : {e}")

    logger.info(
        f"Métriques : {sum(failed_by_country.values())} échecs, "
        f"{sum(success_by_user.values())} réussites, "
        f"{len(invalid_user_attempts)} échecs avec utilisateur invalide"
    )
    return {
        "failed_by_country": sort_desc(failed_by_country),
        "success_by_user": sort_desc(success_by_user),
        "invalid_user_count": len(invalid_user_attempts),
        "invalid_user_details": invalid_user_attempts,
    }


def add_top_lines(lines, counter, limit=10):
    """Ajoute à la liste 'lines' les 'limit' premières lignes d'un dictionnaire."""
    count = 0
    for name in counter:
        lines.append(f"  {name} : {counter[name]}")
        count = count + 1
        if count == limit:
            break


def build_dashboard(metrics):
    """Construit le texte du dashboard à partir des statistiques."""
    lines = []
    lines.append("DASHBOARD - ANALYSE DES CONNEXIONS SSH")
    lines.append("")

    lines.append("1. Tentatives échouées par pays")
    add_top_lines(lines, metrics["failed_by_country"])
    lines.append("")

    lines.append("2. Connexions réussies par utilisateur")
    add_top_lines(lines, metrics["success_by_user"])
    lines.append("")

    lines.append("3. Tentatives échouées avec un utilisateur invalide")
    lines.append(f"  Total : {metrics['invalid_user_count']}")
    names = {}
    for attempt in metrics["invalid_user_details"]:
        add_one(names, attempt["user"])
    lines.append("  Noms invalides les plus essayés :")
    add_top_lines(lines, sort_desc(names))

    return "\n".join(lines)


if __name__ == "__main__":
    from ingestion.raw import toRows
    from processing.extract_transforme import extract

    records = extract(toRows("data"))
    metrics = generate_dashboard_metrics(records)
    print(build_dashboard(metrics))