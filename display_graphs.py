# filename: render_graph_from_check.py
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import argparse
from collections import OrderedDict

API_KEY = "APIKEY" # Replace with your actual API key
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
BASE_URL = "https://yourtext.guru/api/v2"

def extract_ordered_keywords(areas: dict) -> list:
    """Retourne la liste des mots-clés dans l’ordre d’apparition par niveau d’optimisation."""
    zones_order = [
        "overOptimization",        # Suroptimisation
        "strongOptimization",      # Optimisation forte
        "normalOptimization",      # Optimisation normale
        "subOptimization"          # Sous-optimisation
    ]
    ordered = OrderedDict()
    for zone in zones_order:
        for word in areas.get(zone, {}):
            ordered[word] = True
    return list(ordered.keys())

def build_dataframe_from_areas(areas: dict):
    levels = {
        "subOptimization": "Sous-optimisation",
        "normalOptimization": "Optimisation normale",
        "strongOptimization": "Optimisation forte",
        "overOptimization": "Suroptimisation"
    }

    ordered_words = extract_ordered_keywords(areas)
    df = pd.DataFrame(index=ordered_words, columns=levels.values()).fillna(0.0)

    for zone, label in levels.items():
        for word, (min_val, max_val) in areas.get(zone, {}).items():
            df.loc[word, label] = max_val - min_val

    return df

def fetch_check_data(guide_id: str, text="."):
    url = f"{BASE_URL}/guides/{guide_id}/check"
    payload = {"text": text}
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

def plot_svg(df: pd.DataFrame, guide_id: str, content_keywords=None):
    colors = {
        "Sous-optimisation": "#4da6ff",
        "Optimisation normale": "#70db70",
        "Optimisation forte": "#ffc34d",
        "Suroptimisation": "#ff4d4d"
    }

    fig, ax = plt.subplots(figsize=(15, 6))
    df_plot = df.fillna(0)

    bottom = pd.Series([0] * len(df_plot), index=df_plot.index)
    for label in colors:
        ax.bar(df_plot.index, df_plot[label], bottom=bottom, label=label, color=colors[label])
        bottom += df_plot[label]

    if content_keywords:
        for kw in content_keywords:
            if kw in df_plot.index:
                score = content_scores[kw]
                ax.plot(kw, score, 'o', color='black', label="Votre contenu" if kw == content_keywords[0] else "")

    ax.set_ylabel("Optimisation")
    ax.set_title(f"Graphique d’optimisation – Guide {guide_id}")
    ax.legend(loc="upper right")
    plt.xticks(rotation=90)
    plt.tight_layout()
    filename = f"graph_{guide_id}.svg"
    plt.savefig(filename, format="svg")
    plt.close()
    print(f"✅ SVG exporté : {filename}")

def plot_html(df: pd.DataFrame, guide_id: str, content_keywords=None):
    colors = {
        "Sous-optimisation": "#4da6ff",
        "Optimisation normale": "#70db70",
        "Optimisation forte": "#ffc34d",
        "Suroptimisation": "#ff4d4d"
    }

    df_plot = df.fillna(0)
    x = df_plot.index.tolist()
    fig = go.Figure()

    cumulative = [0] * len(x)
    for label in colors:
        y = df_plot[label].tolist()
        fig.add_trace(go.Bar(
            name=label,
            x=x,
            y=y,
            marker_color=colors[label],
            offsetgroup=0,
            base=cumulative
        ))
        cumulative = [c + v for c, v in zip(cumulative, y)]

    if content_keywords:
        for kw in content_keywords:
            if kw in x:
                fig.add_vline(x=kw, line_dash="dot", line_color="black")
                fig.add_trace(go.Scatter(
                    x=[kw], y=[0],
                    mode="markers",
                    marker=dict(color="black", size=8),
                    name="Votre contenu"
                ))

    fig.update_layout(
        barmode='stack',
        title=f"Optimisation par mot – Guide {guide_id}",
        xaxis_title="Mots-clés",
        yaxis_title="Optimisation",
        legend_title="Niveau",
        template="simple_white"
    )
    html_filename = f"graph_{guide_id}.html"
    fig.write_html(html_filename)
    print(f"✅ HTML exporté : {html_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--guide", required=True, help="ID du guide YourText.Guru")
    parser.add_argument("--text", default=".", help="Texte à analyser")
    args = parser.parse_args()

    data = fetch_check_data(args.guide, args.text)
    areas = data["areas"]
    content_scores = data.get("scores", {})
    content_keywords = [k for k, v in content_scores.items() if v > 0]
    df = build_dataframe_from_areas(areas)

    plot_svg(df, args.guide, content_keywords)
    plot_html(df, args.guide, content_keywords)
