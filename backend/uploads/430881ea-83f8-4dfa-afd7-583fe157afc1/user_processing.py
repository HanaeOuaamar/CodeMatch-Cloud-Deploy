# src/user_processing.py
import csv

def load_users(path):
    """Charge les utilisateurs à partir d'un fichier CSV (colonnes 'name', 'age')."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Assurez-vous d'avoir 'age' converti en int, comme le demande le TP
        return [{"name": r["name"], "age": int(r["age"])} for r in reader]

def filter_adults(users):
    """Retourne uniquement les utilisateurs majeurs (age >= 18)."""
    return [u for u in users if u["age"] >= 18]