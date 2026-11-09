import gzip
from pathlib import Path

from logs_config import get_logger

# Logger du module d'ingestion : écrit dans logs/ingestion.log et logs/errors.log
logger = get_logger("ingestion")


def toRows(path) -> list[str]:
  """Lit tous les fichiers d'un répertoire (.gz inclus).

  in : path (répertoire) out : liste de lignes
  """
  data_dir = Path(path)
  rows = []

  try:
    files = sorted(data_dir.iterdir())
  except FileNotFoundError as e:
    error_msg = f"{path} : répertoire introuvable ({e})"
    print(error_msg)
    logger.error(error_msg)
    return []
  except Exception as e:
    error_msg = f"Erreur inattendue sur le répertoire {path} : {e}"
    print(error_msg)
    logger.error(error_msg)
    return []

  for file_path in files:
    if not file_path.is_file():
      continue

    try:
      opener = gzip.open if file_path.suffix == ".gz" else open
      with opener(file_path, mode="rt", errors="replace") as f:
        lines = f.readlines()
      rows.extend(lines)
      logger.info(f"{file_path.name} : {len(lines)} lignes lues")
    except Exception as e:
      error_msg = f"Erreur lors de la lecture du fichier {file_path.name} : {e}"
      print(error_msg)
      logger.error(error_msg)

  logger.info(f"Total : {len(rows)} lignes lues dans {path}")
  return rows


if __name__ == "__main__":
  data = toRows("data")
  if data:
    print(data[:10])