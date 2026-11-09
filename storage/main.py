"""Run the log ingestion, extraction, and plotting pipeline."""

from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parents[1]
project_path = str(PROJECT_DIR)
if project_path not in sys.path:
    sys.path.insert(0, project_path)

from ingestion import raw
from processing import extract_transforme
from processing import geo_location


def main() -> None:
    rows = raw.toRows(PROJECT_DIR / "data")
    records = extract_transforme.extract(rows)
    if not records:
        print("Aucune ligne de log reconnue dans le dossier data.")
        return

    summary = extract_transforme.summarize(records)
    print(f"Lignes lues : {len(rows)}")
    print(f"Lignes analysées : {len(records)}")
    print("\nAperçu des données nettoyées (5 premières lignes) :")
    for record in records[:5]:
        print(
            f"Mois={record['month']} | Jour={record['day']} | "
            f"Heure={record['time']} | IP={record['ip'] or '-'} | "
            f"Message={record['message']}"
        )
    print("Événements :")
    for event, count in summary["events"].most_common():
        print(f"  {event} : {count}")

    # --- Connexions SSH par IP (Success / Failed / Invalid) ---
    counts = extract_transforme.count_by_ip(records)
    total = {k: sum(c[k] for c in counts.values()) for k in ("Success", "Failed", "Invalid")}
    print(
        f"\nConnexions sshd -> réussies : {total['Success']} | "
        f"échouées : {total['Failed']} | utilisateur invalide : {total['Invalid']}"
    )

    top = sorted(counts.items(), key=lambda x: sum(x[1].values()), reverse=True)[:10]
    print(f"\n{'IP':<18}{'Success':>8}{'Failed':>8}{'Invalid':>9}  Localisation")
    for ip, c in top:
        loc = geo_location.get_location(ip) or {}
        place = f"{loc.get('city', '?')}, {loc.get('country', '?')}"
        print(f"{ip:<18}{c['Success']:>8}{c['Failed']:>8}{c['Invalid']:>9}  {place}")

    # --- Graphiques ---
    import matplotlib.pyplot as plt

    figure, axes = plt.subplots(3, 1, figsize=(12, 13), constrained_layout=True)

    event_items = summary["events"].most_common()
    axes[0].bar([item[0] for item in event_items], [item[1] for item in event_items], color="#27C482")
    axes[0].set_title("Événements détectés")
    axes[0].set_ylabel("Nombre de lignes")
    axes[0].tick_params(axis="x", rotation=25)

    day_items = sorted(
        summary["days"].items(),
        key=lambda item: (item[0].split()[0], int(item[0].split()[1])),
    )
    axes[1].plot([item[0] for item in day_items], [item[1] for item in day_items], marker="o", color="#AFDB10")
    axes[1].set_title("Volume des logs par jour")
    axes[1].set_ylabel("Nombre de lignes")
    axes[1].tick_params(axis="x", rotation=45)

    ip_items = summary["ips"].most_common(10)
    if ip_items:
        ip_items.reverse()
        axes[2].barh([item[0] for item in ip_items], [item[1] for item in ip_items], color="#DA482E")
        axes[2].set_title("10 adresses IP les plus fréquentes")
        axes[2].set_xlabel("Nombre d'occurrences")
    else:
        axes[2].text(0.5, 0.5, "Aucune adresse IP détectée", ha="center", va="center")
        axes[2].set_axis_off()

    plt.show()


if __name__ == "__main__":
    main()