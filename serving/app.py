from collections import Counter, defaultdict



from pathlib import Path
import sys

# Remonter à la racine du projet
PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
  sys.path.insert(0, str(PROJECT_DIR))

# Ensuite tu importes normalement
from ingestion.raw import toRows





def extract_user_from_message(message: str) -> str:
  """Extrait le nom d'utilisateur du message de log SSH

  (ex: 'Failed password for root from...' -> 'root')
  """
  parts = message.split()
  try:
    # Souvent, le nom d'utilisateur se trouve après 'for'
    if "for" in parts:
      for_index = parts.index("for")
      if for_index + 1 < len(parts):
        # Si c'est 'invalid user', le nom est après 'user'
        if parts[for_index + 1] == "user" and for_index + 2 < len(parts):
          return parts[for_index + 2]
        return parts[for_index + 1]
  except Exception:
    pass
  return "inconnu"


def get_country_from_ip(ip: str) -> str:
  """Associe une IP à un pays.

  Comme les packages externes (comme requests ou maxminddb) ne sont

  probablement pas autorisés s'ils n'ont pas été vus en cours,
  on peut utiliser un dictionnaire de test/mapping ou une règle simple.
  """
  if not ip:
    return "Inconnu"

  # Exemple de mapping statique pour les tests du projet
  # Tu pourras l'adapter ou le lier à une petite table de correspondance si besoin
  if ip.startswith("192.168.") or ip.startswith("10."):
    return "Local / Interne"
  elif ip.startswith("103."):
    return "Asie (Exemple)"
  elif ip.startswith("197."):
    return "Maroc"
  else:
    return "Autre"


def generate_dashboard_metrics(records: list[dict]) -> dict:
  """Génère toutes les métriques demandées pour le dashboard."""

  failed_by_country = Counter()
  success_by_user = Counter()
  invalid_user_attempts = []

  for r in records:
    if r["service"] != "sshd":
      continue

    message = r["message"]
    ip = r["ip"]
    user = extract_user_from_message(message)
    country = get_country_from_ip(ip)

    # 1. Nombre tentatives réussies par user
    if message.startswith("Accepted"):
      success_by_user[user] += 1

    # 2. Tentatives échouées (classiques ou invalid user)
    elif message.startswith("Failed") or message.startswith("Invalid"):
      failed_by_country[country] += 1

      # 3. Tentatives échouées avec invalid user
      if "invalid user" in message.lower():
        invalid_user_attempts.append({"user": user, "ip": ip, "message": message})

  return {
      "success_by_user": dict(success_by_user.most_common()),
      "failed_by_country": dict(failed_by_country.most_common()),
      "invalid_user_count": len(invalid_user_attempts),
      "invalid_user_details": invalid_user_attempts,
  }


if __name__ == "__main__":
  
  from processing.extract_transforme import extract, summarize
  from ingestion.raw import toRows

  # Chargement et traitement depuis l'ingestion et le processing
  raw_rows = toRows("./log_analysis/data")
  records = extract(raw_rows)
  metrics = generate_dashboard_metrics(records)

  print("=== RAPPORT DU DASHBOARD ===")
  print("Succès par utilisateur :", metrics["success_by_user"])
  print("Échecs par pays :", metrics["failed_by_country"])
  print(f"Nombre d'utilisateurs invalides : {metrics['invalid_user_count']}")