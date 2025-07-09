import argparse
import requests
import pandas as pd

API_KEY = "APIKEY" # Replace with your actual API key
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def fetch_serp_data(guide_id):
    url = f"https://yourtext.guru/api/v2/guides/{guide_id}/serp"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def generate_table(serps, output_file, format="csv"):
    df = pd.DataFrame([
        {
            "position": s["position"],
            "url": s["url"],
            "soseo": s["scores"].get("soseo", 0),
            "dseo": s["scores"].get("dseo", 0)
        }
        for s in serps
    ])
    if format == "csv":
        df.to_csv(output_file, index=False)
    elif format == "html":
        df.to_html(output_file, index=False)
    print(f"✅ Table exportée : {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Export SERP data (table or graph)")
    parser.add_argument("--guide", required=True, type=int, help="Guide ID")
    parser.add_argument("--score", choices=["soseo", "dseo"], default="soseo", help="Type de score à afficher")
    parser.add_argument("--output", default="serp_output.csv", help="Nom du fichier de sortie")
    parser.add_argument("--format", choices=["csv", "html", "svg", "png"], default="csv", help="Format de sortie (table ou image)")

    args = parser.parse_args()
    data = fetch_serp_data(args.guide)
    serps = data.get("serps", [])

    generate_table(serps, args.output, args.format)

if __name__ == "__main__":
    main()
