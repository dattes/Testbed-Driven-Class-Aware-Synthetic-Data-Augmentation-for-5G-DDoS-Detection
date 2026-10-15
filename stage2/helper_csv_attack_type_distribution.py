# Jupyter Notebook: Verteilung der "attack type"-Spalte für mehrere Testdateien

# Voraussetzungen:
# pip install pandas

import os
import pandas as pd
from IPython.display import display, Markdown

# ============================================================
# 1. Runs definieren
# ============================================================
RUNS = [
    {
        "name": "tabDDPM_bal_aug",
        "dataset_key": "5gnidd_tabddpm_bal_aug_train",
        "files": ["5G-NIDD_Aug_tabDDPM/Balanced/test_input_with_label.csv"],
    },
    {
        "name": "tabDDPM_perclass_bal_aug",
        "dataset_key": "5gnidd_tabddpm_perclass_bal_aug_train",
        "files": ["Datasets/augmented_per_class_datasets/tabddpm/test_input_with_label_merged.csv"],
    },
    {
        "name": "not_aug_raw",
        "dataset_key": "5gnidd_not_aug_raw_train",
        "files": ["Datasets/prepped_raw/test_input_with_label.csv"],
    },
    {
        "name": "not_aug_dirty_raw",
        "dataset_key": "5gnidd_not_aug_dirty_raw_train",
        "files": ["Datasets/Encoded_test_raw_243177.csv"],
    },
    {
        "name": "not_aug_bal_raw",
        "dataset_key": "5gnidd_not_aug_bal_raw_train",
        "files": ["5G-NIDD_Aug_tabDDPM/Balanced/test_input_with_label.csv"],
    },
    {
        "name": "CTGAN_bal_aug",
        "dataset_key": "5gnidd_ctgan_bal_aug_train",
        "files": ["5G-NIDD_Aug_CTGAN/Balanced/test_input_with_label.csv"],
    },
    {
        "name": "CTGAN_perclass_bal_aug",
        "dataset_key": "5gnidd_ctgan_perclass_bal_aug_train",
        "files": ["Datasets/augmented_per_class_datasets/ctgan/test_input_with_label_merged.csv"],
    },
    {
        "name": "cedi_nidd",
        "dataset_key": "cedi_nidd_train",
        "files": ["cedi-nidd/pcap_ml_output/final/test_20_prepped_gbdt.csv"],
    }
]

# ============================================================
# 2. Konfiguration
# ============================================================
COLUMN_NAME = "Attack Type"   # Falls die Spalte anders heißt, hier anpassen
SAVE_OUTPUT = True             # True = Ergebnis-CSV pro Run speichern
OUTPUT_DIR = "attack_type_distributions"

if SAVE_OUTPUT:
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 3. Hilfsfunktion für Verteilungstabelle
# ============================================================
def make_distribution_table(df, column_name):
    if column_name not in df.columns:
        raise KeyError(f"Spalte '{column_name}' nicht gefunden. Vorhandene Spalten: {list(df.columns)}")

    counts = df[column_name].value_counts(dropna=False)
    percentages = df[column_name].value_counts(normalize=True, dropna=False) * 100

    result = pd.DataFrame({
        "attack_type": counts.index,
        "count": counts.values,
        "percentage (%)": percentages.round(2).values
    })

    result = result.sort_values(by="count", ascending=False).reset_index(drop=True)
    return result


# ============================================================
# 4. Alle Runs durchgehen und je Datei eine Tabelle erzeugen
# ============================================================
all_results = {}

for run in RUNS:
    run_name = run["name"]
    dataset_key = run.get("dataset_key", "")
    files = run.get("files", [])

    display(Markdown(f"## Run: `{run_name}`"))
    if dataset_key:
        display(Markdown(f"**dataset_key:** `{dataset_key}`"))

    if not files:
        print("Keine Dateien definiert.\n")
        continue

    for i, file_path in enumerate(files, start=1):
        display(Markdown(f"### Datei {i}: `{file_path}`"))

        if not os.path.exists(file_path):
            print(f"Datei nicht gefunden: {file_path}\n")
            continue

        try:
            df = pd.read_csv(file_path)
            result = make_distribution_table(df, COLUMN_NAME)

            # Im Speicher ablegen
            all_results[(run_name, file_path)] = result

            # Tabelle anzeigen
            display(result)

            # Optional speichern
            if SAVE_OUTPUT:
                safe_run_name = run_name.replace("/", "_").replace(" ", "_")
                safe_file_name = os.path.basename(file_path).replace(".csv", "")
                output_path = os.path.join(
                    OUTPUT_DIR,
                    f"{safe_run_name}__{safe_file_name}__attack_type_distribution.csv"
                )
                result.to_csv(output_path, index=False)
                print(f"Gespeichert unter: {output_path}\n")

        except Exception as e:
            print(f"Fehler beim Verarbeiten von {file_path}: {e}\n")


# ============================================================
# 5. Optional: Übersicht aller erfolgreich verarbeiteten Dateien
# ============================================================
display(Markdown("## Zusammenfassung"))
summary_rows = []

for (run_name, file_path), result in all_results.items():
    summary_rows.append({
        "run_name": run_name,
        "file": file_path,
        "rows_in_distribution": len(result),
        "total_samples": int(result["count"].sum())
    })

summary_df = pd.DataFrame(summary_rows)

if not summary_df.empty:
    display(summary_df)
else:
    print("Es konnten keine Dateien erfolgreich verarbeitet werden.")