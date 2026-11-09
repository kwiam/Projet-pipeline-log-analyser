import re

from logs_config import get_logger

logger = get_logger("processing")

"""
    in : list of rows
    out : dateTime, ip, Success, Failed , Invalid user fo sshd service

"""

pattern = re.compile(r'(?P<month>\w{3})\s+(?P<days>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<server>\w+)\s+(?P<service>\w+)\[.+:\s(?P<message>.+)')


IP_PATTERN = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')


def classify_event(message):
    """Donne une catégorie à un message de log."""
    lowered = message.lower()
    if "failed password" in lowered or "authentication failure" in lowered:
        return "Échec d'authentification"
    if "accepted password" in lowered or "accepted publickey" in lowered:
        return "Connexion réussie"
    if "invalid user" in lowered:
        return "Utilisateur invalide"
    if "session opened" in lowered:
        return "Session ouverte"
    if "session closed" in lowered:
        return "Session fermée"
    if "connection closed" in lowered or "disconnected from" in lowered:
        return "Déconnexion"
    return "Autre"


def extract_from_row(row):
    """Analyse une ligne : renvoie un dict, ou None si la ligne n'a pas le bon format."""
    match = re.search(pattern, row)
    if not match:
        return None
    message = match['message']
    ips = IP_PATTERN.findall(message)
    ip = ips[0] if ips else None
    return {
        'month': match['month'],
        'day': match['days'],
        'time': match['time'],
        'service': match['service'],
        'message': message,
        'ip': ip,
    }


def extract(rows):
    """Analyse toutes les lignes et ignore celles qui ne correspondent pas."""
    records = []
    ignored = 0
    for row in rows:
        parsed = extract_from_row(row)
        if parsed is None:
            ignored += 1
        else:
            records.append(parsed)
    logger.info(f"{len(records)} lignes analysées, {ignored} lignes ignorées (format non reconnu)")
    if ignored:
        logger.warning(f"{ignored} lignes ne correspondent pas à la regex et sont ignorées")
    return records


def _add_one(counter_dict, key):
    """Ajoute 1 au compteur de 'key' dans un dictionnaire (le crée à 0 si absent)."""
    counter_dict[key] = counter_dict.get(key, 0) + 1


def summarize(records):
    """Compte les événements, les jours et les IP."""
    events, days, ips = {}, {}, {}
    for r in records:
        _add_one(events, classify_event(r['message']))
        _add_one(days, f"{r['month']} {int(r['day'])}")
        if r['ip']:
            _add_one(ips, r['ip'])
    return {'events': events, 'days': days, 'ips': ips}


def count_by_ip(records):
    """Pour sshd : {ip: {'Success': n, 'Failed': n, 'Invalid': n}}.

    On regarde le DÉBUT du message, pour compter chaque tentative une seule fois
    (sinon "authentication failure" et "Failed password" compteraient 2 fois la même tentative).
    """
    counts = {}
    for r in records:
        if r['service'] != 'sshd' or not r['ip']:
            continue
        ip = r['ip']
        if ip not in counts:
            counts[ip] = {'Success': 0, 'Failed': 0, 'Invalid': 0}
        message = r['message']
        if message.startswith('Accepted'):
            counts[ip]['Success'] += 1
        elif message.startswith('Failed'):
            counts[ip]['Failed'] += 1
        elif message.startswith('Invalid user'):
            counts[ip]['Invalid'] += 1
    return counts


if __name__ == "__main__":
    from ingestion.raw import toRows
    records = extract(toRows("data"))
    print(summarize(records)['events'])