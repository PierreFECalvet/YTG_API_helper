# create_guides.py
import argparse
import requests
import time

API_KEY = "APIKEY" # Replace with your actual API key
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
API_URL = "https://yourtext.guru/api/v2/guides"

def create_guide(keyword, lang, locale, search_engine="google"):
    API_URL_with_params = f"{API_URL}?query={keyword}&lang={lang}_{locale}&type={search_engine}"
    response = requests.post(API_URL_with_params, headers=HEADERS)
    if response.status_code == 201:
        print(f"✅ Guide créé pour : {keyword}")
    else:
        print(f"❌ Erreur pour {keyword} : {response.status_code}")

def bulk_create(filepath, lang, locale):
    with open(filepath, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]
    for kw in keywords:
        create_guide(kw, lang, locale)
        time.sleep(1.5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Créer des guides YourText.Guru")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--keyword", help="Mot-clé pour créer un guide unique")
    group.add_argument("--file", help="Fichier texte avec un mot-clé par ligne")
    parser.add_argument("--lang", default="fr", help="Langue du guide (ex: fr, en)")
    parser.add_argument("--locale", default="FR", help="Locale du guide (ex: FR, US)")
    parser.add_argument("-s_e", "--search_engine", default="google", choices=["google", "bing"], help="Moteur de recherche à utiliser pour le guide")
    
    args = parser.parse_args()

    if args.keyword:
        create_guide(args.keyword, args.lang, args.locale)
    elif args.file:
        bulk_create(args.file, args.lang, args.locale)
