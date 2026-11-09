import re
from collections import Counter, defaultdict

"""
    in : list of rows
    out : dateTime, ip, Success, Failed , Invalid user fo sshd service

""" 

pattern = re.compile(r'(?P<month>\w{3})\s+(?P<days>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<server>\w+)\s+(?P<service>\w+)\[.+:\s(?P<message>.+)')

# Pour trouver l'adresse IP dans le message 
IP_PATTERN = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')


def classify_event(message):
    """Donne une catégorie à un message de log (idée du prof)."""
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
    ip = next(iter(IP_PATTERN.findall(message)), None)
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
    return [parsed for row in rows if (parsed := extract_from_row(row)) is not None]


def summarize(records):
    """Compte les événements, les jours et les IP (pour les graphiques)."""
    events = Counter(classify_event(r['message']) for r in records)
    days = Counter(f"{r['month']} {int(r['day'])}" for r in records)
    ips = Counter(r['ip'] for r in records if r['ip'])
    return {'events': events, 'days': days, 'ips': ips}


def count_by_ip(records):
    """Pour sshd : {ip: {'Success': n, 'Failed': n, 'Invalid': n}}.

    On compte chaque tentative une seule fois : on regarde le DÉBUT du message
    (sinon "authentication failure" et "Failed password" compteraient 2 fois la même tentative).
    """
    counts = defaultdict(lambda: {'Success': 0, 'Failed': 0, 'Invalid': 0})
    for r in records:
        if r['service'] != 'sshd' or not r['ip']:
            continue
        message = r['message']
        if message.startswith('Accepted'):
            counts[r['ip']]['Success'] += 1
        elif message.startswith('Failed'):
            counts[r['ip']]['Failed'] += 1
        elif message.startswith('Invalid user'):
            counts[r['ip']]['Invalid'] += 1
    return dict(counts)