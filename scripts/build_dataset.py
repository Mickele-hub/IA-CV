"""
Script interactif pour construire data/training/raw_pairs.json
sans avoir à écrire du JSON à la main.
 
Utilisation :
    python scripts/build_dataset.py
 
À placer dans le dossier scripts/ à la racine du projet
(au même niveau que app/, data/, etc.) pour que les imports
vers app.services fonctionnent tels quels. Si tu le mets
ailleurs, ajuste le sys.path.insert ci-dessous.
"""
 
import json
import sys
from pathlib import Path
 
# Permet d'importer app.services.* même si ce script est
# lancé depuis scripts/ plutôt que depuis la racine du projet
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
 
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.text_cleaner import clean_text
 
 
OUTPUT_PATH = Path("data/training/raw_pairs.json")
 
 
def load_existing_pairs() -> list[dict]:
    """
    Charge les paires déjà enregistrées, s'il y en a.
    """
 
    if not OUTPUT_PATH.exists():
        return []
 
    with open(OUTPUT_PATH, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            print(
                f"⚠️  {OUTPUT_PATH} existe mais n'est pas un JSON "
                "valide. Il sera écrasé au prochain enregistrement."
            )
            return []
 
 
def save_pairs(pairs: list[dict]) -> None:
    """
    Enregistre les paires sur disque, après chaque ajout,
    pour ne jamais perdre de travail en cas de fermeture
    accidentelle.
    """
 
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
 
    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(pairs, file, ensure_ascii=False, indent=2)
 
 
def read_multiline(prompt: str) -> str:
    """
    Permet de coller un texte sur plusieurs lignes (une offre
    d'emploi, un CV collé à la main, etc.). Termine la saisie
    quand l'utilisateur tape 'FIN' seul sur une ligne.
    """
 
    print(prompt)
    print("(termine par une ligne contenant seulement FIN)")
 
    lines = []
 
    while True:
        line = input()
 
        if line.strip() == "FIN":
            break
 
        lines.append(line)
 
    return "\n".join(lines)
 
 
def get_cv_text() -> str | None:
    """
    Demande à l'utilisateur comment fournir le texte du CV :
    soit un chemin vers un PDF (extrait automatiquement),
    soit du texte collé directement.
    """
 
    print("\n--- CV ---")
    print("1. Chemin vers un fichier PDF")
    print("2. Coller le texte du CV directement")
 
    choice = input("Choix (1/2) : ").strip()
 
    if choice == "1":
        path_str = input("Chemin du fichier PDF : ").strip()
        path = Path(path_str)
 
        if not path.exists():
            print(f"⚠️  Fichier introuvable : {path}")
            return None
 
        try:
            with open(path, "rb") as file:
                raw_text = extract_text_from_pdf(file)
        except Exception as error:
            print(f"⚠️  Erreur pendant l'extraction du PDF : {error}")
            return None
 
        return clean_text(raw_text)
 
    if choice == "2":
        raw_text = read_multiline("Colle le texte du CV :")
        return clean_text(raw_text)
 
    print("⚠️  Choix invalide.")
    return None
 
 
def get_job_text() -> str:
    """
    Demande le texte de l'offre d'emploi (toujours collé,
    pas de PDF pour une offre).
    """
 
    print("\n--- Offre d'emploi ---")
    raw_text = read_multiline(
        "Colle le texte de l'offre (idéalement plusieurs phrases, "
        "comme une vraie annonce) :"
    )
    return clean_text(raw_text)
 
 
def get_label() -> str | None:
    """
    Demande directement à l'utilisateur si cette paire est un
    bon match, un match partiel ou un mauvais match. Plus fiable
    ici qu'une labellisation automatique via skills.json, qui ne
    couvre que du vocabulaire tech et ne fonctionnerait pas pour
    des CV d'autres domaines.
    """
 
    print("\n--- Label ---")
    print("1. Good Fit (bon match)")
    print("2. Potential Fit (match partiel)")
    print("3. No Fit (mauvais match)")
 
    choice = input("Choix (1/2/3) : ").strip()
 
    label_map = {
        "1": "Good Fit",
        "2": "Potential Fit",
        "3": "No Fit",
    }
 
    label = label_map.get(choice)
 
    if label is None:
        print("⚠️  Choix invalide.")
 
    return label
 
 
def main() -> None:
    pairs = load_existing_pairs()
 
    print(f"{len(pairs)} paire(s) déjà enregistrée(s) dans {OUTPUT_PATH}.")
 
    while True:
        print("\n============================")
        print(f"Total actuel : {len(pairs)} paire(s)")
        print("============================")
 
        cv_text = get_cv_text()
 
        if not cv_text:
            print("Paire ignorée (pas de texte de CV valide).")
        else:
            job_text = get_job_text()
 
            if not job_text:
                print("Paire ignorée (pas de texte d'offre).")
            else:
                label = get_label()
 
                if not label:
                    print("Paire ignorée (label invalide).")
                else:
                    pairs.append({
                        "cv_text": cv_text,
                        "job_text": job_text,
                        "label": label
                    })
 
                    save_pairs(pairs)
 
                    print(
                        f"✅ Paire enregistrée. "
                        f"Total : {len(pairs)} paire(s) dans {OUTPUT_PATH}"
                    )
 
        again = input(
            "\nAjouter une autre paire ? (o/n) : "
        ).strip().lower()
 
        if again != "o":
            break
 
    print(
        f"\nTerminé. {len(pairs)} paire(s) au total dans {OUTPUT_PATH}."
    )
 
 
if __name__ == "__main__":
    main()
 