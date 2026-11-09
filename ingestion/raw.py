import gzip
import logging
from pathlib import Path

# Configuration des logs pour enregistrer les erreurs du module d'ingestion
Path("storage").mkdir(exist_ok=True)
logging.basicConfig(
    filename="storage/app_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - [ingestion] - %(message)s",
)


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
    logging.error(error_msg)
    return []
  except Exception as e:
    error_msg = f"Erreur inattendue sur le répertoire {path} : {e}"
    print(error_msg)
    logging.error(error_msg)
    return []

  for file_path in files:
    if not file_path.is_file():
      continue

    try:
      opener = gzip.open if file_path.suffix == ".gz" else open
      with opener(file_path, mode="rt", errors="replace") as f:
        rows.extend(f.readlines())
    except Exception as e:
      error_msg = f"Erreur lors de la lecture du fichier {file_path.name} : {e}"
      print(error_msg)
      logging.error(error_msg)

  return rows


if __name__ == "__main__":
  data = toRows("./log_analysis/data")
  if data:
    print(data[:10])