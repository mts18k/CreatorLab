from __future__ import annotations

import html
import json
import os
import random
import re
import unicodedata
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
STATE_FILE = DATA_DIR / "creatorlab_state.json"
DATA_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="CreatorLab — Studio de création",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Design ----------
st.html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    :root { --cl-bg: #0b0c12; --cl-panel: #131520; --cl-panel2: #191c2a; --cl-border: #292d40; --cl-text: #f6f7fb; --cl-muted: #a7abc0; --cl-purple: #a78bfa; --cl-cyan: #67e8f9; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: radial-gradient(circle at 85% 0%, rgba(119,75,222,.16), transparent 28%), var(--cl-bg); color: var(--cl-text); }
    h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -.035em; }
    h1 { font-weight: 700 !important; }
    [data-testid="stSidebar"] { background: #0e1019; border-right: 1px solid var(--cl-border); }
    [data-testid="stSidebar"] * { font-family: 'Space Grotesk', sans-serif; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #d9dcef; }
    .cl-brand { padding: 10px 4px 22px 4px; }
    .cl-logo { display:inline-flex; width:42px; height:42px; border-radius:14px; align-items:center; justify-content:center; background:linear-gradient(135deg,#a78bfa,#67e8f9); color:#10111b; font-size:22px; font-weight:800; margin-right:10px; vertical-align:middle; }
    .cl-brand-name { display:inline-block; vertical-align:middle; font-family:'Space Grotesk',sans-serif; font-size:22px; font-weight:700; }
    .cl-brand-sub { margin:8px 0 0 2px; color:#8f94ad; font-size:12px; letter-spacing:.10em; text-transform:uppercase; }
    .cl-hero { padding: 27px 29px; border:1px solid #323650; border-radius:24px; background:linear-gradient(120deg,rgba(167,139,250,.17),rgba(103,232,249,.07) 55%,rgba(255,255,255,.025)); margin-bottom:20px; }
    .cl-kicker { color:#c4b5fd; text-transform:uppercase; letter-spacing:.15em; font-size:11px; font-weight:700; }
    .cl-hero-title { font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:clamp(30px,4vw,43px); line-height:1.08; margin:9px 0 10px; }
    .cl-gradient { background:linear-gradient(90deg,#c4b5fd,#67e8f9); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
    .cl-subtitle { color:#b7bbce; max-width:780px; font-size:15px; line-height:1.6; }
    .cl-card { background:linear-gradient(145deg,rgba(24,27,42,.96),rgba(17,19,29,.96)); border:1px solid var(--cl-border); border-radius:18px; padding:18px 19px; min-height:115px; }
    .cl-card-label { color:#a4a9bf; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:.09em; }
    .cl-card-value { font-family:'Space Grotesk',sans-serif; font-size:32px; font-weight:700; margin-top:6px; color:#f6f7fb; }
    .cl-card-note { color:#8e94ad; font-size:12px; margin-top:2px; }
    .cl-section-title { font-size:21px; font-weight:700; margin:19px 0 5px; }
    .cl-muted { color:#a4a9bf; font-size:13px; }
    .cl-pill { display:inline-block; border:1px solid #3b3d57; color:#d9d2ff; background:rgba(167,139,250,.09); padding:4px 9px; border-radius:100px; font-size:11px; margin-right:5px; }
    .cl-idea { border:1px solid #292d40; background:rgba(19,21,32,.9); border-radius:16px; padding:17px 18px; margin:9px 0; }
    .cl-idea h3 { font-size:17px; margin:5px 0 7px; }
    .cl-idea p { color:#b8bdd0; font-size:13px; line-height:1.5; margin:4px 0; }
    .cl-num { color:#a78bfa; font-size:12px; font-weight:700; letter-spacing:.08em; }
    .cl-empty { border:1px dashed #393d54; border-radius:17px; padding:24px; text-align:center; color:#a4a9bf; }
    div.stButton > button, div.stDownloadButton > button { border-radius:12px; font-weight:700; border:1px solid #4a426a; transition:all .15s ease; }
    div.stButton > button[kind="primary"] { background:linear-gradient(100deg,#9b87f5,#6bdfee); color:#11121b; border:0; }
    div.stButton > button:hover, div.stDownloadButton > button:hover { border-color:#a78bfa; transform:translateY(-1px); }
    [data-testid="stMetric"] { background:#151724; border:1px solid #292d40; padding:14px 16px; border-radius:16px; }
    [data-testid="stMetricLabel"] { color:#a4a9bf; }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stTimeInput input, .stNumberInput input { border-radius:11px !important; }
    .stTabs [data-baseweb="tab-list"] { gap:8px; }
    .stTabs [data-baseweb="tab"] { border-radius:10px; padding:8px 15px; }
    footer { visibility:hidden; }
    </style>
    """
)

# ---------- Data ----------
def default_state() -> dict[str, Any]:
    return {
        "creator_name": "Mon studio",
        "niche": "Gaming",
        "platforms": ["YouTube", "TikTok"],
        "drafts": [],
        "calendar": [],
        "idea_bank": [],
        "settings": {"default_tone": "Dynamique", "default_language": "Français"},
    }


def load_state() -> dict[str, Any]:
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            base = default_state()
            if isinstance(data, dict):
                base.update(data)
                for key in ("drafts", "calendar", "idea_bank"):
                    if not isinstance(base.get(key), list):
                        base[key] = []
                if not isinstance(base.get("settings"), dict):
                    base["settings"] = default_state()["settings"]
                return base
        except (json.JSONDecodeError, OSError):
            pass
    return default_state()


def save_state() -> None:
    temp = STATE_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(st.session_state.app_state, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(STATE_FILE)


if "app_state" not in st.session_state:
    st.session_state.app_state = load_state()
if "latest_content" not in st.session_state:
    st.session_state.latest_content = ""
if "ideas_ai_result" not in st.session_state:
    st.session_state.ideas_ai_result = ""
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

state: dict[str, Any] = st.session_state.app_state

# ---------- Content engine (offline-first, AI optional) ----------
PLATFORMS = ["YouTube", "YouTube Shorts", "TikTok", "Instagram Reels", "Twitch", "Instagram", "Facebook"]
NICHES = ["Gaming", "Lifestyle", "Humour", "Sport / fitness", "Cuisine", "Tech", "Mode / beauté", "Éducation", "Musique", "Voyage", "Autre"]
TONES = ["Dynamique", "Drôle", "Mystérieux", "Inspirant", "Pro", "Chill", "Storytelling", "Provocateur (sans insulte)"]

HOOKS = [
    "Personne ne m'avait prévenu de ça…",
    "J'ai testé ça pendant 7 jours : voilà le résultat.",
    "Tu fais sûrement cette erreur sans le savoir.",
    "Je pensais que c'était impossible, jusqu'à aujourd'hui.",
    "Le détail qui change tout, c'est celui-là.",
    "On va voir si cette astuce tient vraiment ses promesses.",
    "Voici ce que j'aurais aimé savoir avant de commencer.",
    "Reste jusqu'à la fin : le dernier point est le plus surprenant.",
]


def clean_words(value: str) -> list[str]:
    words = re.findall(r"[A-Za-zÀ-ÿ0-9]+", value.lower())
    stop = {"avec", "pour", "dans", "des", "les", "une", "sur", "qui", "que", "est", "mon", "mes", "the", "and", "from", "this", "that"}
    return [w for w in words if len(w) > 2 and w not in stop]


def local_ideas(niche: str, platform: str, tone: str, topic: str, count: int = 8) -> list[dict[str, str]]:
    topics = [t.strip() for t in re.split(r"[,;\n]", topic) if t.strip()]
    if not topics:
        topics = {
            "Gaming": ["un défi impossible", "un secret méconnu", "un test de jeu", "un moment drôle"],
            "Lifestyle": ["une routine réaliste", "un défi de 7 jours", "une habitude utile"],
            "Humour": ["une situation gênante", "un faux tuto", "un POV du quotidien"],
            "Sport / fitness": ["une progression", "une erreur de débutant", "un mini défi"],
            "Cuisine": ["une recette rapide", "un test de recette virale", "une astuce cuisine"],
            "Tech": ["un outil gratuit", "un comparatif", "une astuce méconnue"],
        }.get(niche, ["une astuce utile", "un test honnête", "une expérience personnelle"])
    formats = {
        "YouTube": ["Le guide complet", "J'ai testé", "Top 5", "Avant / après", "La vérité sur"],
        "YouTube Shorts": ["En 30 secondes", "Le savais-tu ?", "3 astuces rapides", "Le mini défi"],
        "TikTok": ["POV :", "J'ai testé", "Tu savais que…", "Le défi du jour"],
        "Instagram Reels": ["3 idées à garder", "Le résultat en 20 secondes", "Petit rappel :", "Avant / après"],
        "Twitch": ["Session défi", "Objectif communautaire", "Découverte en direct", "Le challenge du chat"],
    }
    chosen_formats = formats.get(platform, ["3 astuces", "J'ai testé", "Le guide rapide", "Le défi du jour"])
    templates = [
        ("Le défi que personne ne tente", "Lance un défi clair, montre les règles dès le départ puis révèle le résultat sans le faire durer inutilement."),
        ("3 choses que j'aurais aimé savoir", "Présente trois points concrets, un exemple pour chacun, puis termine avec le conseil le plus utile."),
        ("Mythe ou réalité ?", "Annonce une idée populaire, teste-la avec une méthode simple et donne ton verdict à la fin."),
        ("Du niveau débutant au résultat", "Montre le point de départ, les étapes clés et ce que tu as appris pendant l'expérience."),
        ("L'astuce qui fait gagner du temps", "Explique une seule astuce, montre-la à l'écran et compare rapidement avec la méthode habituelle."),
        ("Le classement honnête", "Compare trois options avec les mêmes critères et assume ton classement à la fin."),
        ("J'ai suivi un conseil pendant 24 h", "Présente le conseil, documente le test et partage ce qui a réellement changé."),
        ("La réaction que je n'attendais pas", "Construis une courte histoire autour d'un imprévu et garde la révélation pour le dernier tiers."),
        ("Erreur fréquente : fais plutôt ça", "Montre l'erreur, explique pourquoi elle arrive puis propose une alternative simple."),
        ("Une journée en mode…", "Raconte une mini aventure avec un objectif, un obstacle et une conclusion rapide."),
    ]
    results = []
    used: set[tuple[str, str]] = set()
    for i in range(count):
        topic_one = topics[i % len(topics)]
        fmt = chosen_formats[i % len(chosen_formats)]
        base_title, base_desc = templates[(i + len(niche)) % len(templates)]
        title = f"{fmt} : {topic_one.capitalize()}" if fmt.endswith(":") else f"{fmt} — {topic_one.capitalize()}"
        if (title, topic_one) in used:
            title = f"{title} #{i + 1}"
        used.add((title, topic_one))
        results.append({
            "title": title,
            "description": f"{base_desc} Thème : {topic_one}. Adapte le rythme au format {platform} et garde un ton {tone.lower()}.",
            "hook": random.choice(HOOKS),
            "format": fmt,
            "niche": niche,
            "platform": platform,
            "cta": random.choice(["Demande aux gens leur avis en commentaire.", "Invite à s'abonner pour la suite.", "Propose un défi à la communauté.", "Pose une question facile à répondre."]),
            "difficulty": random.choice(["Facile", "Moyen", "À préparer"]),
        })
    return results


def make_local_pack(topic: str, platform: str, duration: str, tone: str, audience: str, keywords: str) -> str:
    hook = random.choice(HOOKS)
    topic_clean = topic.strip() or "mon sujet du jour"
    keyword_list = [x.strip().lstrip("#") for x in re.split(r"[,;\n]", keywords) if x.strip()]
    if not keyword_list:
        keyword_list = clean_words(topic_clean)[:5] or ["createur", "conseils"]
    hashtags = " ".join("#" + re.sub(r"[^A-Za-zÀ-ÿ0-9_]", "", w.replace(" ", "")) for w in keyword_list[:8])
    length_note = {
        "15–30 secondes": "Garde une seule idée et coupe tout ce qui ne fait pas avancer la vidéo.",
        "30–60 secondes": "Prévois 3 à 5 plans rapides avec une conclusion nette.",
        "1–3 minutes": "Ajoute un exemple concret et une petite transition entre les parties.",
        "5–10 minutes": "Structure en chapitres et prévois un exemple ou une démonstration par partie.",
        "10+ minutes": "Pose une promesse claire, puis alterne démonstrations, explications et récapitulatifs.",
    }.get(duration, "Garde une structure claire et un rythme adapté au format.")
    return f"""# PACK CRÉATEUR — {topic_clean.upper()}\n\n## 1. Idée centrale\nCréer un contenu {tone.lower()} sur « {topic_clean} », destiné à {audience or 'une audience intéressée par ce sujet'}.\n\n## 2. Accroche (0–3 s)\n« {hook} »\nVisuel : commence directement par le résultat, une question ou le moment le plus intrigant.\n\n## 3. Script proposé\n**INTRO — 0 à 10 %**\n« Aujourd'hui, on teste/parle de {topic_clean}. Je vais te montrer l'essentiel, sans perdre de temps. »\n\n**PARTIE 1 — Le contexte**\nExplique en une ou deux phrases pourquoi le sujet mérite l'attention. Ajoute un exemple visuel ou une capture si c'est pertinent.\n\n**PARTIE 2 — La démonstration**\nMontre les étapes importantes. Utilise des plans courts, des sous-titres lisibles et un exemple concret.\n\n**PARTIE 3 — Le résultat**\nDonne ton avis honnête, ce qui fonctionne et ce qui pourrait être amélioré. Évite de promettre un résultat que tu n'as pas vérifié.\n\n**CONCLUSION / CTA**\n« Et toi, tu en penses quoi ? Dis-le en commentaire et abonne-toi si tu veux d'autres contenus comme celui-là. »\n\n## 4. Titres à tester\n1. {topic_clean.capitalize()} : ce qu'il faut vraiment savoir\n2. J'ai testé {topic_clean}… voici mon avis\n3. 3 choses à connaître sur {topic_clean}\n4. La méthode simple pour comprendre {topic_clean}\n5. Ce détail change tout dans {topic_clean}\n\n## 5. Description\nAujourd'hui, on s'intéresse à {topic_clean}. Dans cette vidéo, je partage les points importants, un exemple concret et mon avis.\n\n💬 Dis-moi en commentaire ce que tu en penses.\n🔔 Abonne-toi pour découvrir les prochaines vidéos.\n\n## 6. Hashtags\n{hashtags}\n\n## 7. Idée de miniature / couverture\nUn sujet visuel principal, un contraste fort, un visage ou un objet expressif si adapté, et 2 à 5 mots maximum. Évite de surcharger l'image.\n\n## 8. Conseils de montage\n- Retire les silences inutiles et démarre vite.\n- Ajoute des sous-titres pour les informations clés.\n- Varie les plans seulement quand cela aide à comprendre.\n- {length_note}\n\n**Plateforme :** {platform}  \n**Durée cible :** {duration}  \n**Ton :** {tone}  \n**Mots-clés :** {', '.join(keyword_list)}\n"""


def ask_ai(prompt: str, model: str = "gpt-4o-mini") -> str:
    api_key = st.session_state.get("api_key", "").strip()
    if not api_key:
        raise RuntimeError("Ajoute ta clé API OpenAI dans la section « Mode IA » de la barre latérale, ou utilise le mode local gratuit.")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Tu es CreatorLab, un assistant francophone pour créateurs de contenu. Tu proposes des idées originales, honnêtes et adaptées à la plateforme. N'invente pas de faits présentés comme réels. Réponds en français clair et structure le résultat avec des titres Markdown."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )
        return response.choices[0].message.content or "Aucune réponse reçue."
    except ImportError as exc:
        raise RuntimeError("Le paquet openai n'est pas installé. Lance le fichier lancer_creatorlab.bat ou installe les dépendances.") from exc
    except Exception as exc:
        raise RuntimeError(f"L'appel IA a échoué : {exc}") from exc


def save_draft(title: str, content: str, kind: str, platform: str) -> None:
    item = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "title": title[:120] or f"Brouillon {datetime.now().strftime('%d/%m %H:%M')}",
        "content": content,
        "kind": kind,
        "platform": platform,
        "created_at": datetime.now().isoformat(timespec="minutes"),
    }
    state["drafts"].insert(0, item)
    save_state()


def platform_badge(platform: str) -> str:
    return f'<span class="cl-pill">{platform}</span>'


def reset_publish_checklist_state() -> None:
    """Reset checklist values from a Streamlit callback, before widgets render."""
    for i in range(8):
        st.session_state[f"publish_check_{i}"] = False


def ascii_slug(value: str) -> str:
    """Turn user input into a simple username-safe token."""
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]", "", normalized).lower()


def local_pseudos(seed: str, niche: str, style: str, count: int = 12) -> list[str]:
    base = ascii_slug(seed)[:18] or ascii_slug(niche)[:14] or "createur"
    if style == "Gaming":
        endings = ["gg", "plays", "gaming", "clutch", "fps", "xp", "frag", "live", "tv", "clips", "quest", "respawn", "pixel", "zone", "exe"]
        starts = ["its", "hey", "real", "the", "yo", "just", "ultra", "neo", "mr"]
    elif style == "Minimaliste":
        endings = ["fr", "tv", "hq", "io", "lab", "co", "x", "z", "one", "live", "daily"]
        starts = ["its", "hey", "real", "im", "just"]
    elif style == "Créatif":
        endings = ["verse", "vibes", "studio", "flow", "lab", "world", "vision", "wave", "craft", "spark", "nova", "daily"]
        starts = ["hey", "madeby", "the", "its", "hello", "neo"]
    else:
        endings = ["official", "fr", "tv", "creator", "daily", "world", "zone", "live", "hub", "community", "clips", "plus"]
        starts = ["its", "the", "real", "hey", "just", "team"]
    candidates = [base, f"{base}_", f"{base}.", f"{base}fr"]
    candidates.extend(f"{base}{end}" for end in endings)
    candidates.extend(f"{start}{base}" for start in starts)
    candidates.extend(f"{base}_{end}" for end in endings)
    # Niche-specific options make the results more relevant without requiring an API.
    niche_token = ascii_slug(niche)[:10]
    if niche_token and niche_token != base:
        candidates.extend([f"{base}{niche_token}", f"{base}_{niche_token}", f"{niche_token}{base}"])
    cleaned = []
    seen = set()
    for item in candidates:
        item = re.sub(r"[^a-zA-Z0-9_.]", "", item)[:24].strip("._")
        if len(item) >= 3 and item.lower() not in seen:
            seen.add(item.lower())
            cleaned.append(item)
    random.shuffle(cleaned)
    # Put the simple base first, then keep results distinct.
    ordered = [base] + [x for x in cleaned if x.lower() != base.lower()]
    return ordered[:count]


def local_bios(pseudo: str, niche: str, platform: str, tone: str, length: str, include_cta: bool) -> list[str]:
    name = pseudo.strip() or "TonPseudo"
    niche_text = niche.lower()
    tone_line = {
        "Dynamique": "Du contenu qui bouge, des idées qui claquent ⚡",
        "Drôle": "Des moments improbables et un peu de chaos 😂",
        "Mystérieux": "Une vibe à part. Le reste se découvre ici 🌙",
        "Inspirant": "On progresse ensemble, une création à la fois ✨",
        "Pro": "Création, conseils et coulisses avec une approche claire.",
        "Chill": "On se pose, on crée, on partage 🌊",
        "Storytelling": "Des histoires, des découvertes et des moments à raconter 🎬",
        "Provocateur (sans insulte)": "Des avis assumés, des tests honnêtes et zéro blabla 🔥",
    }.get(tone, "Des idées et des moments à partager ✨")
    cta = "⬇️ Suis-moi pour la suite" if include_cta else ""
    platform_line = {
        "TikTok": "Vidéos courtes et moments forts",
        "Instagram": "Posts, Reels et coulisses",
        "YouTube": "Vidéos et projets en préparation",
        "Twitch": "Lives et moments avec la communauté",
        "Discord": "Rejoins la communauté",
    }.get(platform, "Nouveautés et coulisses")
    templates = [
        f"{name} ✦ {niche_text}\n{tone_line}\n{cta}",
        f"Bienvenue dans mon univers 🎬\n{platform_line}\n{cta}",
        f"Je partage mes découvertes autour de {niche_text}.\nDu contenu sincère, à ma façon ✨\n{cta}",
        f"{name} | créateur\n{tone_line}\nIci, on parle de {niche_text}. {cta}",
        f"Un pseudo, plein d'idées 💡\n{niche.capitalize()} et bonne énergie.\n{cta}",
        f"Créateur {niche_text} 🎮\n{platform_line}\n{cta}",
    ]
    if niche.lower() not in {"gaming", "jeux vidéo"}:
        templates[-1] = f"Créateur {niche_text} ✨\nConseils • découvertes • moments forts\n{cta}"
    limit = {"Mini": 85, "Standard": 150, "Détaillée": 240}.get(length, 150)
    out = []
    for text in templates:
        text = re.sub(r"\n{2,}", "\n", text).strip()
        if len(text) > limit:
            text = text[: max(0, limit - 1)].rsplit(" ", 1)[0].rstrip(" •|-") + "…"
        if text not in out:
            out.append(text)
    return out


def analyze_title(title: str) -> tuple[int, list[str], list[str]]:
    """A transparent editorial heuristic, not a prediction of views."""
    clean = title.strip()
    if not clean:
        return 0, ["Écris un titre pour lancer l'analyse."], []
    score = 40
    strengths: list[str] = []
    suggestions: list[str] = []
    length = len(clean)
    if 28 <= length <= 70:
        score += 20
        strengths.append("Longueur assez lisible pour de nombreux formats.")
    elif length < 28:
        score += 10
        suggestions.append("Ajoute un peu de contexte pour qu'on comprenne mieux la promesse.")
    else:
        suggestions.append("Raccourcis le titre et place l'idée principale au début.")
    if re.search(r"\b\d+\b", clean):
        score += 8
        strengths.append("Le chiffre rend la structure concrète.")
    if "?" in clean:
        score += 6
        strengths.append("La question peut donner envie de découvrir la réponse.")
    power_words = ["testé", "pourquoi", "comment", "erreurs", "astuces", "guide", "vrai", "impossible", "meilleur", "secret", "avant"]
    if any(w in clean.lower() for w in power_words):
        score += 10
        strengths.append("Le titre donne un angle ou une promesse claire.")
    if any(w in clean.lower() for w in ["100% garanti", "choquant", "tu ne croiras jamais"]):
        score -= 10
        suggestions.append("Évite les promesses exagérées si le contenu ne les prouve pas.")
    if clean.count("!") > 1 or clean.count("?") > 1:
        score -= 5
        suggestions.append("Réduis les signes de ponctuation répétés.")
    if len(re.findall(r"[A-ZÀ-Ý]", clean)) > max(8, len(clean) * 0.55):
        score -= 8
        suggestions.append("Évite d'écrire presque tout en majuscules.")
    words = clean_words(clean)
    if len(words) < 3:
        suggestions.append("Précise le sujet ou le bénéfice pour ton audience.")
    if not suggestions:
        suggestions.append("Teste une autre variante et choisis celle qui représente le mieux la vidéo.")
    return max(0, min(100, score)), strengths, suggestions


def local_thumbnail_brief(topic: str, style: str, emotion: str, text_overlay: str, platform: str) -> str:
    short_text = text_overlay.strip() or "2–4 mots maximum"
    return f"""# Concept de miniature — {topic.strip()}\n\n**Plateforme :** {platform}\n**Style :** {style}\n**Émotion principale :** {emotion}\n\n- **Sujet principal :** un seul personnage, objet ou élément lié à « {topic.strip()} », grand et facile à reconnaître.\n- **Composition :** sujet décalé sur un côté, espace libre de l'autre pour le texte.\n- **Arrière-plan :** simple, contrasté, sans détails qui détournent l'attention.\n- **Texte à afficher :** « {short_text} ». Utilise une police épaisse et vérifie la lisibilité sur mobile.\n- **Couleurs :** deux couleurs dominantes et un accent pour attirer le regard.\n- **À éviter :** trop de texte, éléments minuscules, fausses promesses et détails inutiles.\n\n**Prompt visuel de départ :** Miniature {platform}, sujet {topic.strip()}, style {style.lower()}, émotion {emotion.lower()}, composition claire, contraste fort, arrière-plan simple, espace réservé au texte « {short_text} », lisible sur écran de téléphone.\n"""


def repurpose_content(topic: str, original: str) -> str:
    basis = original.strip() or topic.strip()
    seed = topic.strip() or "ce sujet"
    return f"""# Déclinaisons de contenu — {seed}\n\n## TikTok / Reel (20–40 s)\n**Accroche :** « Tu savais ça sur {seed} ? »\n**Structure :** montre le résultat ou l'idée principale immédiatement, explique un point clé, termine par une question courte.\n**CTA :** « Tu connaissais déjà ? »\n\n## YouTube (format long)\n**Titre provisoire :** « {seed.capitalize()} : test, explications et verdict »\n**Structure :** contexte → démonstration → 3 points importants → limites ou erreurs → conclusion honnête.\n\n## Short (moins d'une minute)\n**0–3 s :** accroche visuelle.\n**3–35 s :** une seule idée de {seed}, illustrée avec un exemple.\n**35–50 s :** résultat et conseil pratique.\n\n## Publication communautaire\n« Je prépare du contenu sur {seed}. Qu'est-ce que tu aimerais voir : un guide, un test ou mes erreurs à éviter ? »\n\n## Pour améliorer la déclinaison\nGarde le même thème, mais adapte le rythme et l'accroche à chaque plateforme. Ne copie pas tout mot pour mot.\n\n---\n**Notes originales (à retravailler) :**\n{basis[:1200]}\n"""

# ---------- Sidebar ----------
PAGES = ["Accueil", "Idées de contenu", "Studio de création", "Titres & hashtags", "Pseudo & bio", "Boîte à outils", "Planning éditorial", "Mes brouillons", "Paramètres"]
if "page_override" in st.session_state:
    st.session_state["navigation"] = st.session_state.pop("page_override")

with st.sidebar:
    st.html(
        "<div class='cl-brand'><span class='cl-logo'>✦</span><span class='cl-brand-name'>CreatorLab</span><div class='cl-brand-sub'>Ton studio de contenu</div></div>"
    )
    page = st.radio(
        "NAVIGATION",
        PAGES,
        label_visibility="collapsed",
        key="navigation",
    )
    st.html("<div style='height:10px'></div>")
    st.html("<div class='cl-muted'>MODE IA</div>")
    ai_enabled = st.toggle("Activer l'IA OpenAI", value=False, help="L'API OpenAI peut être facturée séparément de ChatGPT.")
    if ai_enabled:
        st.session_state.api_key = st.text_input("Clé API OpenAI", value=st.session_state.api_key, type="password", placeholder="sk-…", help="Utilisée uniquement en mémoire pendant cette session. Ne la partage pas.")
        st.caption("La clé n'est pas enregistrée dans le fichier de données.")
    else:
        st.caption("Mode local : gratuit, sans clé API.")
    st.divider()
    name_sidebar = st.text_input("Nom du studio", value=state.get("creator_name", "Mon studio"), max_chars=40)
    if name_sidebar != state.get("creator_name"):
        state["creator_name"] = name_sidebar
        save_state()
    st.html("<div style='color:#777d98;font-size:11px;margin-top:12px'>CREATORLAB • VERSION 1.1</div>")

# ---------- Header utility ----------
def hero(kicker: str, title: str, subtitle: str) -> None:
    st.html(
        f"<div class='cl-hero'><div class='cl-kicker'>{kicker}</div><div class='cl-hero-title'>{title}</div><div class='cl-subtitle'>{subtitle}</div></div>"
    )


def save_button(label: str, title: str, content: str, kind: str, platform: str, key: str) -> None:
    if st.button(label, key=key, type="primary", use_container_width=True):
        save_draft(title, content, kind, platform)
        st.success("Ajouté à Mes brouillons !")

# ---------- Pages ----------
if page == "Accueil":
    hero("CRÉE • TESTE • PUBLIE", f"Bienvenue dans <span class='cl-gradient'>CreatorLab</span>.", "Ton atelier pour trouver des idées, écrire plus vite et publier avec une vraie méthode. Choisis un outil et passe de l'idée au contenu.")
    draft_count = len(state["drafts"])
    calendar_count = len(state["calendar"])
    ideas_count = len(state["idea_bank"])
    upcoming = sorted([x for x in state["calendar"] if x.get("status") != "Publié"], key=lambda x: x.get("date", ""))
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.html(f"<div class='cl-card'><div class='cl-card-label'>Brouillons</div><div class='cl-card-value'>{draft_count}</div><div class='cl-card-note'>Tes contenus sauvegardés</div></div>")
    with c2:
        st.html(f"<div class='cl-card'><div class='cl-card-label'>Idées sauvegardées</div><div class='cl-card-value'>{ideas_count}</div><div class='cl-card-note'>À développer quand tu veux</div></div>")
    with c3:
        st.html(f"<div class='cl-card'><div class='cl-card-label'>Publications planifiées</div><div class='cl-card-value'>{calendar_count}</div><div class='cl-card-note'>Dans ton calendrier</div></div>")
    with c4:
        st.html(f"<div class='cl-card'><div class='cl-card-label'>À publier</div><div class='cl-card-value'>{len(upcoming)}</div><div class='cl-card-note'>Hors contenus déjà publiés</div></div>")
    st.html("<div class='cl-section-title'>Ton espace de création</div><div class='cl-muted'>Des outils rapides pour débloquer ta prochaine publication.</div>")
    a, b, c = st.columns(3)
    with a:
        st.html("<div class='cl-card'><div style='font-size:26px'>💡</div><h3>Brainstorm</h3><p class='cl-muted'>Trouve des idées adaptées à ta niche et à ta plateforme.</p></div>")
        if st.button("Trouver des idées →", key="home_ideas", use_container_width=True):
            st.session_state["page_override"] = "Idées de contenu"
            st.rerun()
    with b:
        st.html("<div class='cl-card'><div style='font-size:26px'>🎬</div><h3>Studio</h3><p class='cl-muted'>Crée un pack avec script, titres, description et hashtags.</p></div>")
        if st.button("Ouvrir le studio →", key="home_studio", use_container_width=True):
            st.session_state["page_override"] = "Studio de création"
            st.rerun()
    with c:
        st.html("<div class='cl-card'><div style='font-size:26px'>🗓️</div><h3>Planning</h3><p class='cl-muted'>Organise les prochains posts et garde le cap.</p></div>")
        if st.button("Préparer mon planning →", key="home_calendar", use_container_width=True):
            st.session_state["page_override"] = "Planning éditorial"
            st.rerun()
    d, e = st.columns(2)
    with d:
        st.html("<div class='cl-card'><div style='font-size:26px'>🎭</div><h3>Pseudo & bio</h3><p class='cl-muted'>Trouve un pseudo mémorisable et une description de profil.</p></div>")
        if st.button("Créer mon identité →", key="home_pseudobio", use_container_width=True):
            st.session_state["page_override"] = "Pseudo & bio"
            st.rerun()
    with e:
        st.html("<div class='cl-card'><div style='font-size:26px'>🧰</div><h3>Boîte à outils</h3><p class='cl-muted'>Analyse ton titre, estime la durée et prépare ta miniature.</p></div>")
        if st.button("Ouvrir les outils →", key="home_tools", use_container_width=True):
            st.session_state["page_override"] = "Boîte à outils"
            st.rerun()
    st.html("<div class='cl-section-title'>Conseil créateur du jour</div>")
    tips = [
        "Une vidéo = une idée principale. Si tu dois expliquer cinq choses, fais une série.",
        "Écris l'accroche avant le reste du script : elle doit donner une raison de rester.",
        "Teste deux titres différents, mais garde une promesse honnête par rapport au contenu.",
        "Note les questions de ta communauté : elles peuvent devenir tes prochaines vidéos.",
        "Un rythme de publication tenable vaut mieux qu'un calendrier parfait impossible à suivre.",
    ]
    tip_index = date.today().toordinal() % len(tips)
    st.info(tips[tip_index])
    if state["drafts"]:
        st.html("<div class='cl-section-title'>Derniers brouillons</div>")
        for draft in state["drafts"][:3]:
            st.html(f"<div class='cl-idea'><div class='cl-num'>{html.escape(str(draft.get('kind','CONTENU')).upper())} · {html.escape(str(draft.get('platform','')))}</div><h3>{html.escape(str(draft.get('title','Sans titre')))}</h3><p>{html.escape(str(draft.get('created_at','')))}</p></div>")

elif page == "Idées de contenu":
    hero("01 / BRAINSTORM", "Des idées à la chaîne.", "Génère des concepts selon ton sujet, ton réseau et ton style. Tu peux sauvegarder les idées que tu veux garder.")
    with st.form("ideas_form"):
        c1, c2 = st.columns(2)
        with c1:
            niche = st.selectbox("Ta niche", NICHES, index=NICHES.index(state.get("niche", "Gaming")) if state.get("niche") in NICHES else 0)
            platform = st.selectbox("Plateforme", PLATFORMS, index=PLATFORMS.index("TikTok"))
            tone = st.selectbox("Style", TONES, index=0)
        with c2:
            topics = st.text_input("Sujets ou mots-clés (facultatif)", placeholder="ex. Minecraft, défis, astuces")
            audience = st.selectbox("Audience", ["Débutants", "Fans déjà passionnés", "Grand public", "Communauté fidèle", "Autres créateurs"])
            count = st.slider("Nombre d'idées", 4, 12, 8)
        use_ai = ai_enabled and bool(st.session_state.api_key.strip())
        submitted = st.form_submit_button("✨ Générer mes idées", type="primary", use_container_width=True)
    if submitted:
        state["niche"] = niche
        save_state()
        if use_ai:
            prompt = f"Génère {count} idées de contenu très distinctes en français. Niche: {niche}; plateforme: {platform}; ton: {tone}; audience: {audience}; sujets/mots-clés: {topics or 'propose des thèmes adaptés'}. Pour chaque idée donne un titre court, une accroche, un concept en 2 phrases, un CTA et une difficulté. N'utilise pas de tableau."
            try:
                st.session_state.ideas_ai_result = ask_ai(prompt)
                st.session_state.ideas_origin = "ai"
            except RuntimeError as exc:
                st.error(str(exc))
                st.session_state.generated_ideas = local_ideas(niche, platform, tone, topics, count)
                st.session_state.ideas_origin = "local"
                st.session_state.ideas_ai_result = ""
        else:
            st.session_state.generated_ideas = local_ideas(niche, platform, tone, topics, count)
            st.session_state.ideas_origin = "local"
            st.session_state.ideas_ai_result = ""
    if st.session_state.get("ideas_origin") == "ai" and st.session_state.ideas_ai_result:
        st.markdown(st.session_state.ideas_ai_result)
        save_button("💾 Sauvegarder cette liste", "Idées IA", st.session_state.ideas_ai_result, "Idées", platform if "platform" in locals() else "Plusieurs", "save_ai_ideas")
    elif st.session_state.get("generated_ideas"):
        for i, item in enumerate(st.session_state.generated_ideas):
            st.html(f"<div class='cl-idea'><div class='cl-num'>IDÉE {i+1:02d} · {html.escape(str(item['difficulty']).upper())}</div><h3>{html.escape(str(item['title']))}</h3><p><b>Accroche :</b> {html.escape(str(item['hook']))}</p><p>{html.escape(str(item['description']))}</p><p><b>CTA :</b> {html.escape(str(item['cta']))}</p><div>{platform_badge(html.escape(str(item['platform'])))}{platform_badge(html.escape(str(item['niche'])))}</div></div>")
            if st.button("＋ Sauvegarder cette idée", key=f"saveidea_{i}"):
                state["idea_bank"].insert(0, {**item, "saved_at": datetime.now().isoformat(timespec="minutes")})
                save_state()
                st.success("Idée sauvegardée dans tes données locales.")
        if st.session_state.generated_ideas:
            all_ideas = "\n\n".join(f"{i+1}. {x['title']}\nAccroche: {x['hook']}\n{x['description']}\nCTA: {x['cta']}" for i, x in enumerate(st.session_state.generated_ideas))
            st.download_button("Télécharger toutes les idées (.txt)", data=all_ideas, file_name="creatorlab_idees.txt", use_container_width=True)
    else:
        st.html("<div class='cl-empty'>💡 Choisis tes paramètres puis clique sur Générer mes idées.</div>")

elif page == "Studio de création":
    hero("02 / STUDIO", "De l'idée au contenu.", "Décris ce que tu veux publier et CreatorLab prépare une première version que tu peux modifier, sauvegarder et télécharger.")
    with st.form("studio_form"):
        topic = st.text_input("Sujet de la vidéo *", placeholder="Ex. J'ai essayé de gagner une partie sans utiliser telle option")
        c1, c2, c3 = st.columns(3)
        with c1:
            platform = st.selectbox("Plateforme", PLATFORMS, key="studio_platform")
            duration = st.selectbox("Durée", ["15–30 secondes", "30–60 secondes", "1–3 minutes", "5–10 minutes", "10+ minutes"])
        with c2:
            tone = st.selectbox("Ton", TONES)
            audience = st.text_input("Audience", value="des personnes qui aiment ce sujet")
        with c3:
            keywords = st.text_input("Mots-clés séparés par des virgules", placeholder="astuces, débutant, test")
            pack_type = st.selectbox("Type de contenu", ["Pack complet", "Script uniquement", "Short / Reel", "Vidéo YouTube longue", "Story / post"])
        generated = st.form_submit_button("🚀 Créer mon contenu", type="primary", use_container_width=True)
    if generated:
        if not topic.strip():
            st.warning("Ajoute un sujet pour pouvoir générer ton contenu.")
        else:
            prompt = f"Crée un {pack_type} en français pour {platform}. Sujet: {topic}. Durée: {duration}. Ton: {tone}. Audience: {audience}. Mots-clés: {keywords or 'à proposer'}. Donne: idée centrale, accroche, script avec sections ou indications de plans, 5 titres, description, hashtags adaptés, idée de miniature/couverture, CTA et conseils de montage. Reste honnête et évite les promesses trompeuses. Formate en Markdown."
            if ai_enabled and st.session_state.api_key.strip():
                with st.spinner("CreatorLab prépare ton contenu…"):
                    try:
                        content = ask_ai(prompt)
                    except RuntimeError as exc:
                        st.error(str(exc))
                        content = make_local_pack(topic, platform, duration, tone, audience, keywords)
            else:
                content = make_local_pack(topic, platform, duration, tone, audience, keywords)
            st.session_state.latest_content = content
            st.session_state["studio_edit"] = content
            st.session_state.latest_title = topic
            st.session_state.latest_platform = platform
            st.session_state.latest_kind = pack_type
    if st.session_state.get("latest_content") and page == "Studio de création":
        st.html("<div class='cl-section-title'>Ton contenu prêt à retravailler</div>")
        edited = st.text_area("Tu peux modifier le contenu ici", value=st.session_state.latest_content, height=430, key="studio_edit")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 Sauvegarder dans Mes brouillons", type="primary", use_container_width=True):
                save_draft(st.session_state.get("latest_title", "Nouveau contenu"), edited, st.session_state.get("latest_kind", "Pack complet"), st.session_state.get("latest_platform", "YouTube"))
                st.success("Brouillon sauvegardé sur ce PC.")
        with c2:
            st.download_button("⬇ Télécharger en Markdown", data=edited, file_name="creatorlab_contenu.md", mime="text/markdown", use_container_width=True)

elif page == "Titres & hashtags":
    hero("03 / OPTIMISATION", "Fais ressortir ton post.", "Prépare des variantes de titres, des descriptions et des hashtags sans tomber dans le clickbait mensonger.")
    tab1, tab2, tab3 = st.tabs(["Titres", "Hashtags", "Description"])
    with tab1:
        topic = st.text_input("Sujet du contenu", placeholder="Ex. les meilleurs réglages pour débuter", key="title_topic")
        platform = st.selectbox("Plateforme cible", PLATFORMS, key="title_platform")
        goal = st.selectbox("Objectif du titre", ["Intriguer", "Être clair", "Promettre un apprentissage", "Raconter une expérience", "Faire rire"])
        if st.button("Générer 10 titres", type="primary", key="make_titles"):
            if not topic.strip():
                st.warning("Ajoute un sujet d'abord.")
            elif ai_enabled and st.session_state.api_key.strip():
                try:
                    st.session_state.title_result = ask_ai(f"Propose 10 titres variés en français pour {platform}, sujet: {topic}, objectif: {goal}. Ils doivent être accrocheurs mais honnêtes. Numérote-les, évite les titres presque identiques.")
                except RuntimeError as exc:
                    st.error(str(exc))
                    st.session_state.title_result = "\n".join([f"{i+1}. {t}" for i, t in enumerate([f"{topic.capitalize()} : ce qu'il faut savoir", f"J'ai testé {topic} : mon avis", f"3 erreurs à éviter avec {topic}", f"La méthode simple pour {topic}", f"Ce détail change tout dans {topic}", f"Avant de te lancer dans {topic}, regarde ça", f"Le guide rapide de {topic}", f"Ce que je referais différemment avec {topic}", f"{topic.capitalize()} : mythe ou réalité ?", f"Tout ce que j'aurais voulu savoir sur {topic}"])])
                    st.session_state["title_result_view"] = st.session_state.title_result
            else:
                base = [f"{topic.capitalize()} : ce qu'il faut vraiment savoir", f"J'ai testé {topic} : voici mon avis", f"3 erreurs à éviter avec {topic}", f"La méthode simple pour {topic}", f"Ce détail change tout dans {topic}", f"Avant de te lancer dans {topic}, regarde ça", f"Le guide rapide de {topic}", f"Ce que je referais différemment avec {topic}", f"{topic.capitalize()} : mythe ou réalité ?", f"Tout ce que j'aurais voulu savoir sur {topic}"]
                st.session_state.title_result = "\n".join(f"{i+1}. {t}" for i, t in enumerate(base))
                st.session_state["title_result_view"] = st.session_state.title_result
            if "title_result" in st.session_state:
                st.session_state["title_result_view"] = st.session_state.title_result
        if st.session_state.get("title_result"):
            st.text_area("Résultat", value=st.session_state.title_result, height=300, key="title_result_view")
            st.download_button("Télécharger les titres", st.session_state.title_result, file_name="creatorlab_titres.txt", use_container_width=True)
    with tab2:
        hash_topic = st.text_input("Sujet / niche", placeholder="Ex. gaming, minecraft, tutoriel", key="hash_topic")
        hash_platform = st.selectbox("Plateforme", ["TikTok", "Instagram Reels", "YouTube Shorts", "Instagram"], key="hash_platform")
        if st.button("Créer mes hashtags", type="primary"):
            words = clean_words(hash_topic)
            if not words:
                st.warning("Écris quelques mots-clés pour créer des hashtags.")
            else:
                taglist = list(dict.fromkeys(["#" + re.sub(r"[^a-zA-ZÀ-ÿ0-9_]", "", x) for x in words] + ["#createur", "#francophone", "#" + hash_platform.lower().replace(" ", "").replace("/", "")]))
                st.session_state.hashtag_result = " ".join(taglist[:15])
        if st.session_state.get("hashtag_result"):
            st.code(st.session_state.hashtag_result, language=None)
            st.download_button("Télécharger les hashtags", st.session_state.hashtag_result, file_name="creatorlab_hashtags.txt")
            st.caption("Les hashtags générés sont des suggestions. Vérifie leur pertinence et leur popularité sur la plateforme avant de publier.")
    with tab3:
        desc_topic = st.text_input("Sujet du post", placeholder="Ex. ma nouvelle vidéo sur…", key="desc_topic")
        desc_platform = st.selectbox("Plateforme", PLATFORMS, key="desc_platform")
        desc_tone = st.selectbox("Style de description", TONES, key="desc_tone")
        if st.button("Générer une description", type="primary"):
            if not desc_topic.strip():
                st.warning("Ajoute un sujet.")
            elif ai_enabled and st.session_state.api_key.strip():
                try:
                    st.session_state.description_result = ask_ai(f"Rédige une description en français pour un contenu {desc_platform} à propos de {desc_topic}. Ton {desc_tone}. Ajoute un appel à l'action naturel et évite les hashtags excessifs.")
                except RuntimeError as exc:
                    st.error(str(exc))
                    st.session_state.description_result = f"Aujourd'hui, je te partage du contenu sur {desc_topic}. Dis-moi ce que tu en penses en commentaire et suis le compte pour la suite !"
            else:
                st.session_state.description_result = f"Aujourd'hui, on parle de {desc_topic} 🎬\n\nJ'espère que ce contenu te sera utile ! Dis-moi ce que tu en penses en commentaire et suis le compte pour découvrir la suite.\n\n#création #communauté"
            st.session_state["description_view"] = st.session_state.description_result
        if st.session_state.get("description_result"):
            st.text_area("Description générée", value=st.session_state.description_result, height=180, key="description_view")
            st.download_button("Télécharger la description", st.session_state.description_result, file_name="creatorlab_description.txt")

elif page == "Pseudo & bio":
    hero("04 / IDENTITÉ CRÉATEUR", "Trouve ton pseudo. Crée ta bio.", "Génère des idées de noms de créateur et des descriptions de profil pour YouTube, TikTok, Instagram ou Twitch.")
    tab1, tab2 = st.tabs(["🎭 Générateur de pseudos", "✍️ Bio / description de profil"])
    with tab1:
        st.html("<div class='cl-section-title'>Un pseudo qui te ressemble</div>")
        c1, c2 = st.columns(2)
        with c1:
            seed = st.text_input("Ton prénom, mot-clé ou pseudo actuel", placeholder="Ex. Mathys, Nova, Pixel", key="pseudo_seed")
            pseudo_niche = st.selectbox("Univers / niche", NICHES, index=NICHES.index(state.get("niche", "Gaming")) if state.get("niche") in NICHES else 0, key="pseudo_niche")
        with c2:
            pseudo_style = st.selectbox("Style du pseudo", ["Gaming", "Minimaliste", "Créatif", "Général"], key="pseudo_style")
            pseudo_count = st.slider("Nombre de suggestions", 6, 24, 12, key="pseudo_count")
        if st.button("✨ Générer des pseudos", type="primary", key="generate_pseudos", use_container_width=True):
            if not seed.strip():
                st.warning("Écris un prénom, un mot-clé ou ton pseudo actuel.")
            elif ai_enabled and st.session_state.api_key.strip():
                try:
                    result = ask_ai(f"Propose {pseudo_count} pseudos de créateur courts, mémorisables et faciles à prononcer. Mot de départ: {seed}. Niche: {pseudo_niche}. Style: {pseudo_style}. Réponds uniquement avec une liste numérotée, sans affirmer que les noms sont disponibles.")
                    st.session_state.pseudo_result = result
                    st.session_state.pseudo_result_list = []
                except RuntimeError as exc:
                    st.error(str(exc))
                    st.session_state.pseudo_result_list = local_pseudos(seed, pseudo_niche, pseudo_style, pseudo_count)
                    st.session_state.pseudo_result = ""
            else:
                st.session_state.pseudo_result_list = local_pseudos(seed, pseudo_niche, pseudo_style, pseudo_count)
                st.session_state.pseudo_result = ""
        if st.session_state.get("pseudo_result_list"):
            result_text = "\n".join(f"{i+1}. @{name}" for i, name in enumerate(st.session_state.pseudo_result_list))
            st.code(result_text, language=None)
            st.caption("La disponibilité n'est pas vérifiée : cherche le pseudo sur chaque plateforme avant de l'adopter.")
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("⬇ Télécharger les pseudos", result_text, file_name="creatorlab_pseudos.txt", use_container_width=True)
            with c2:
                if st.button("💾 Sauvegarder dans mes brouillons", key="save_pseudos", use_container_width=True):
                    save_draft(f"Idées de pseudos — {seed}", result_text, "Pseudos", "Plusieurs")
                    st.success("Pseudos sauvegardés dans Mes brouillons.")
        elif st.session_state.get("pseudo_result"):
            st.markdown(st.session_state.pseudo_result)
            st.download_button("⬇ Télécharger les suggestions", st.session_state.pseudo_result, file_name="creatorlab_pseudos.txt")
    with tab2:
        st.html("<div class='cl-section-title'>Une bio courte et claire</div>")
        c1, c2 = st.columns(2)
        with c1:
            bio_pseudo = st.text_input("Pseudo à afficher", placeholder="Ex. NovaPlay", key="bio_pseudo")
            bio_niche = st.selectbox("Sujet principal", NICHES, index=NICHES.index(state.get("niche", "Gaming")) if state.get("niche") in NICHES else 0, key="bio_niche")
            bio_platform = st.selectbox("Plateforme", ["TikTok", "Instagram", "YouTube", "Twitch", "Discord", "Autre"], key="bio_platform")
        with c2:
            bio_tone = st.selectbox("Ambiance de la bio", TONES, key="bio_tone")
            bio_length = st.selectbox("Longueur", ["Mini", "Standard", "Détaillée"], index=1, key="bio_length")
            bio_cta = st.checkbox("Ajouter un appel à l'action", value=True, key="bio_cta")
        if st.button("✍️ Générer des descriptions", type="primary", key="generate_bios", use_container_width=True):
            if ai_enabled and st.session_state.api_key.strip():
                try:
                    st.session_state.bio_result = ask_ai(f"Écris 6 bios de profil différentes en français. Pseudo: {bio_pseudo or 'à définir'}. Thème: {bio_niche}. Plateforme: {bio_platform}. Ton: {bio_tone}. Longueur: {bio_length}. Appel à l'action: {'oui' if bio_cta else 'non'}. Chaque proposition doit avoir une personnalité distincte, être naturelle, sans hashtags excessifs ni fausses promesses. Numérote les propositions et ne dépasse pas environ 250 caractères chacune.")
                except RuntimeError as exc:
                    st.error(str(exc))
                    bios = local_bios(bio_pseudo, bio_niche, bio_platform, bio_tone, bio_length, bio_cta)
                    st.session_state.bio_result = "\n\n---\n\n".join(f"{i+1}. {bio}" for i, bio in enumerate(bios))
            else:
                bios = local_bios(bio_pseudo, bio_niche, bio_platform, bio_tone, bio_length, bio_cta)
                st.session_state.bio_result = "\n\n---\n\n".join(f"{i+1}. {bio}" for i, bio in enumerate(bios))
        if st.session_state.get("bio_result"):
            bio_edited = st.text_area("Descriptions générées (tu peux les modifier)", value=st.session_state.bio_result, height=300, key=f"bio_result_editor_{abs(hash(st.session_state.bio_result))}")
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("⬇ Télécharger les descriptions", bio_edited, file_name="creatorlab_bios.txt", use_container_width=True)
            with c2:
                if st.button("💾 Sauvegarder les bios", key="save_bios", use_container_width=True):
                    save_draft(f"Bios de profil — {bio_pseudo or 'mon profil'}", bio_edited, "Bio / description", bio_platform)
                    st.success("Descriptions sauvegardées dans Mes brouillons.")

elif page == "Boîte à outils":
    hero("05 / OUTILS RAPIDES", "Peaufine chaque détail.", "Un analyseur de titres, un générateur de concepts de miniatures, une estimation de durée de script, du recyclage de contenu et une checklist avant publication.")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Analyseur de titre", "🖼️ Miniature", "⏱️ Durée du script", "♻️ Recycler", "✅ Checklist"])
    with tab1:
        title_to_check = st.text_input("Colle ton titre", placeholder="Ex. J'ai testé 5 astuces sur Minecraft", key="analyzer_title")
        if st.button("Analyser le titre", type="primary", key="run_title_analysis"):
            score, strengths, suggestions = analyze_title(title_to_check)
            st.session_state.title_analysis = {"score": score, "strengths": strengths, "suggestions": suggestions, "title": title_to_check}
        analysis = st.session_state.get("title_analysis")
        if analysis:
            st.metric("Score éditorial indicatif", f"{analysis['score']}/100")
            st.progress(analysis["score"] / 100)
            st.caption("Ce score repose sur des règles simples de lisibilité, pas sur l'algorithme d'une plateforme et ne prédit pas les vues.")
            if analysis["strengths"]:
                st.markdown("**Ce qui fonctionne**")
                for note in analysis["strengths"]:
                    st.write("✅ " + note)
            st.markdown("**Pistes d'amélioration**")
            for note in analysis["suggestions"]:
                st.write("💡 " + note)
            st.download_button("Télécharger l'analyse", "Titre: " + analysis["title"] + f"\nScore indicatif: {analysis['score']}/100\n\n" + "\n".join(analysis["strengths"] + analysis["suggestions"]), file_name="creatorlab_analyse_titre.txt")
    with tab2:
        thumb_topic = st.text_input("Sujet de la miniature", placeholder="Ex. Mon premier tournoi sur Fortnite", key="thumb_topic")
        c1, c2 = st.columns(2)
        with c1:
            thumb_style = st.selectbox("Style visuel", ["Gaming énergique", "Minimaliste", "Cinématique", "Humour / réaction", "Tutoriel clair", "Mystérieux"], key="thumb_style")
            thumb_platform = st.selectbox("Destination", ["YouTube", "YouTube Shorts", "TikTok", "Instagram Reels"], key="thumb_platform")
        with c2:
            thumb_emotion = st.selectbox("Émotion à transmettre", ["Surprise", "Curiosité", "Excitation", "Humour", "Confiance", "Suspense"], key="thumb_emotion")
            thumb_overlay = st.text_input("Texte sur l'image (facultatif)", placeholder="Ex. C'EST POSSIBLE ?", key="thumb_overlay")
        if st.button("Créer le concept de miniature", type="primary", key="make_thumbnail"):
            if not thumb_topic.strip():
                st.warning("Entre le sujet de la vidéo.")
            elif ai_enabled and st.session_state.api_key.strip():
                try:
                    st.session_state.thumbnail_result = ask_ai(f"Crée un brief de miniature en français pour une vidéo sur {thumb_topic}, style {thumb_style}, émotion {thumb_emotion}, plateforme {thumb_platform}, texte éventuel {thumb_overlay or 'propose 2 à 4 mots'}. Donne composition, couleurs, éléments, texte et prompt visuel. Pas de promesse trompeuse.")
                except RuntimeError as exc:
                    st.error(str(exc))
                    st.session_state.thumbnail_result = local_thumbnail_brief(thumb_topic, thumb_style, thumb_emotion, thumb_overlay, thumb_platform)
            else:
                st.session_state.thumbnail_result = local_thumbnail_brief(thumb_topic, thumb_style, thumb_emotion, thumb_overlay, thumb_platform)
        if st.session_state.get("thumbnail_result"):
            thumb_edited = st.text_area("Concept de miniature", value=st.session_state.thumbnail_result, height=260, key=f"thumbnail_editor_{abs(hash(st.session_state.thumbnail_result))}")
            st.download_button("Télécharger le concept", thumb_edited, file_name="creatorlab_miniature.md")
            save_button("💾 Sauvegarder dans mes brouillons", thumb_topic or "Concept de miniature", thumb_edited, "Miniature", thumb_platform, "save_thumbnail_brief")
    with tab3:
        script_text = st.text_area("Colle ton script", placeholder="Écris ou colle ton texte ici…", height=200, key="script_duration_text")
        c1, c2 = st.columns(2)
        with c1:
            speaking_speed = st.select_slider("Vitesse de parole estimée", options=[100, 120, 140, 160, 180, 200], value=140, format_func=lambda x: f"{x} mots/min")
        with c2:
            pause_ratio = st.selectbox("Rythme du contenu", ["Rapide (peu de pauses)", "Naturel", "Posé (plus de pauses)"], index=1, key="script_pause_ratio")
        if script_text.strip():
            word_count = len(re.findall(r"\b[\wÀ-ÿ'-]+\b", script_text))
            pause_factor = {"Rapide (peu de pauses)": 1.03, "Naturel": 1.12, "Posé (plus de pauses)": 1.22}[pause_ratio]
            seconds = int((word_count / speaking_speed) * 60 * pause_factor)
            st.metric("Durée parlée estimée", f"{seconds // 60} min {seconds % 60:02d} s")
            st.caption(f"{word_count} mots · estimation indicative, sans compter les pauses de montage, les scènes ou la musique.")
            if seconds < 30:
                st.info("Pour un format plus long, développe avec un exemple ou une démonstration.")
            elif seconds > 600:
                st.info("Pense à structurer le script en chapitres et à prévoir des transitions.")
        else:
            st.caption("La durée s'affichera dès que tu colles ton script.")
    with tab4:
        repurpose_topic = st.text_input("Thème à décliner", placeholder="Ex. Mes 3 astuces Roblox", key="repurpose_topic")
        repurpose_original = st.text_area("Contenu existant (facultatif)", placeholder="Colle une description, un script ou tes notes…", height=140, key="repurpose_original")
        if st.button("Décliner ce contenu", type="primary", key="make_repurpose"):
            if not repurpose_topic.strip() and not repurpose_original.strip():
                st.warning("Entre un thème ou colle un contenu existant.")
            elif ai_enabled and st.session_state.api_key.strip():
                try:
                    st.session_state.repurpose_result = ask_ai(f"Décline ce contenu en français pour TikTok/Reel 30 secondes, YouTube format long, Short de moins d'une minute et post communautaire. Thème: {repurpose_topic}. Contenu: {repurpose_original[:4000]}. Donne un angle différent pour chaque format sans inventer de faits.")
                except RuntimeError as exc:
                    st.error(str(exc))
                    st.session_state.repurpose_result = repurpose_content(repurpose_topic, repurpose_original)
            else:
                st.session_state.repurpose_result = repurpose_content(repurpose_topic, repurpose_original)
        if st.session_state.get("repurpose_result"):
            repurpose_edited = st.text_area("Déclinaisons", value=st.session_state.repurpose_result, height=280, key=f"repurpose_editor_{abs(hash(st.session_state.repurpose_result))}")
            st.download_button("Télécharger les déclinaisons", repurpose_edited, file_name="creatorlab_declinaisons.md")
            save_button("💾 Sauvegarder les déclinaisons", repurpose_topic or "Déclinaisons de contenu", repurpose_edited, "Déclinaisons", "Plusieurs", "save_repurpose")
    with tab5:
        st.write("Coche les éléments avant de publier. La barre montre ta progression pour cette session.")
        checklist_items = ["L'accroche arrive rapidement", "Le titre représente vraiment le contenu", "Le son est clair", "Les sous-titres sont relus", "La miniature est lisible sur mobile", "La description et les liens sont vérifiés", "Les droits sur la musique et les visuels sont vérifiés", "J'ai regardé une dernière fois le rendu complet"]
        checked = [st.checkbox(item, key=f"publish_check_{i}") for i, item in enumerate(checklist_items)]
        ratio = sum(checked) / len(checklist_items)
        st.progress(ratio)
        st.metric("Prêt à publier", f"{sum(checked)}/{len(checklist_items)} étapes")
        if ratio == 1:
            st.success("Tout est coché. Fais un dernier contrôle puis publie !")
        st.button("Réinitialiser la checklist", key="reset_publish_checklist", on_click=reset_publish_checklist_state)

elif page == "Planning éditorial":
    hero("06 / ORGANISATION", "Ton calendrier de contenu.", "Planifie tes publications, garde une vue sur leur statut et exporte ton calendrier pour le conserver.")
    with st.expander("＋ Ajouter une publication", expanded=not state["calendar"]):
        with st.form("calendar_form"):
            c1, c2 = st.columns(2)
            with c1:
                cal_title = st.text_input("Titre / idée *", placeholder="Ex. 3 astuces pour débuter")
                cal_platform = st.selectbox("Plateforme", PLATFORMS)
                cal_date = st.date_input("Date prévue", value=date.today() + timedelta(days=1))
            with c2:
                cal_time = st.time_input("Heure prévue", value=time(18, 0))
                cal_status = st.selectbox("Statut", ["Idée", "À préparer", "Prêt", "Publié"])
                cal_notes = st.text_area("Notes (facultatif)", placeholder="Accroche, matériel, éléments à préparer…", height=90)
            add_cal = st.form_submit_button("Ajouter au planning", type="primary", use_container_width=True)
        if add_cal:
            if not cal_title.strip():
                st.warning("Donne un titre à ta publication.")
            else:
                state["calendar"].append({"id": datetime.now().strftime("%Y%m%d%H%M%S%f"), "title": cal_title.strip(), "platform": cal_platform, "date": cal_date.isoformat(), "time": cal_time.strftime("%H:%M"), "status": cal_status, "notes": cal_notes.strip()})
                state["calendar"].sort(key=lambda x: (x.get("date", ""), x.get("time", "")))
                save_state()
                st.success("Publication ajoutée au planning.")
                st.rerun()
    if state["calendar"]:
        sort_calendar = sorted(state["calendar"], key=lambda x: (x.get("date", ""), x.get("time", "")))
        total = len(sort_calendar)
        done = sum(1 for x in sort_calendar if x.get("status") == "Publié")
        c1, c2, c3 = st.columns(3)
        c1.metric("Publications prévues", total)
        c2.metric("Publiées", done)
        c3.metric("Restantes", total - done)
        st.html("<div class='cl-section-title'>Publications</div>")
        filter_status = st.selectbox("Filtrer par statut", ["Toutes", "Idée", "À préparer", "Prêt", "Publié"])
        for item in sort_calendar:
            if filter_status != "Toutes" and item.get("status") != filter_status:
                continue
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1.2, 1])
                with c1:
                    st.markdown(f"**{item.get('title','Sans titre')}**")
                    st.caption(f"{item.get('date','')} à {item.get('time','')} · {item.get('platform','')}")
                    if item.get("notes"):
                        st.write(item["notes"])
                with c2:
                    statuses = ["Idée", "À préparer", "Prêt", "Publié"]
                    new_status = st.selectbox("Statut", statuses, index=statuses.index(item.get("status", "Idée")) if item.get("status") in statuses else 0, key=f"cal_status_{item['id']}", label_visibility="collapsed")
                    if new_status != item.get("status"):
                        item["status"] = new_status
                        save_state()
                        st.rerun()
                with c3:
                    if st.button("Supprimer", key=f"cal_delete_{item['id']}"):
                        state["calendar"] = [x for x in state["calendar"] if x.get("id") != item["id"]]
                        save_state()
                        st.rerun()
        csv_text = "Date,Heure,Titre,Plateforme,Statut,Notes\n" + "\n".join(
            ",".join('"' + str(x.get(k, "")).replace('"', '""') + '"' for k in ["date", "time", "title", "platform", "status", "notes"])
            for x in sort_calendar
        )
        st.download_button("⬇ Exporter le planning CSV", csv_text, file_name="creatorlab_planning.csv", mime="text/csv")
    else:
        st.html("<div class='cl-empty'>Ton calendrier est vide pour l'instant. Ajoute ta première publication ci-dessus.</div>")

elif page == "Mes brouillons":
    hero("07 / BIBLIOTHÈQUE", "Tous tes brouillons au même endroit.", "Les contenus sauvegardés restent sur l'appareil où tu exécutes CreatorLab. Pense à exporter régulièrement une copie.")
    if state["drafts"]:
        for draft in state["drafts"]:
            with st.expander(f"{draft.get('title','Sans titre')} · {draft.get('platform','')} · {draft.get('created_at','')}"):
                st.caption(f"Type : {draft.get('kind','Contenu')} | Plateforme : {draft.get('platform','')}")
                edited_draft = st.text_area("Contenu", value=draft.get("content", ""), height=240, key=f"draft_text_{draft['id']}")
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button("Télécharger ce brouillon", data=edited_draft, file_name=f"{re.sub(r'[^a-zA-Z0-9_-]+','_',draft.get('title','brouillon'))[:40]}.md", key=f"download_draft_{draft['id']}", use_container_width=True)
                with c2:
                    if st.button("Enregistrer les modifications", key=f"update_draft_{draft['id']}", use_container_width=True):
                        draft["content"] = edited_draft
                        draft["updated_at"] = datetime.now().isoformat(timespec="minutes")
                        save_state()
                        st.success("Modifications enregistrées.")
                if st.button("Supprimer ce brouillon", key=f"delete_draft_{draft['id']}"):
                    state["drafts"] = [x for x in state["drafts"] if x.get("id") != draft["id"]]
                    save_state()
                    st.rerun()
        if st.button("Exporter tous mes brouillons (.json)"):
            st.download_button("Télécharger l'export JSON", json.dumps(state["drafts"], ensure_ascii=False, indent=2), file_name="creatorlab_brouillons.json", mime="application/json")
    else:
        st.html("<div class='cl-empty'>Tu n'as pas encore de brouillon. Crée un pack dans le Studio pour commencer.</div>")
    if state["idea_bank"]:
        st.html("<div class='cl-section-title'>Idées sauvegardées</div>")
        for idx, idea in enumerate(state["idea_bank"]):
            with st.expander(idea.get("title", "Idée sans titre")):
                st.write(idea.get("description", ""))
                st.caption(idea.get("hook", ""))
                if st.button("Supprimer l'idée", key=f"delete_idea_{idx}"):
                    state["idea_bank"].pop(idx)
                    save_state()
                    st.rerun()

elif page == "Paramètres":
    hero("08 / PERSONNALISATION", "Configure ton studio.", "Personnalise ton profil et télécharge une sauvegarde des données stockées localement.")
    with st.form("settings_form"):
        creator_name = st.text_input("Nom du studio", value=state.get("creator_name", "Mon studio"))
        niche = st.selectbox("Niche principale", NICHES, index=NICHES.index(state.get("niche", "Gaming")) if state.get("niche") in NICHES else 0)
        platforms = st.multiselect("Plateformes habituelles", PLATFORMS, default=[p for p in state.get("platforms", ["YouTube", "TikTok"]) if p in PLATFORMS])
        default_tone = st.selectbox("Ton préféré", TONES, index=TONES.index(state.get("settings", {}).get("default_tone", "Dynamique")) if state.get("settings", {}).get("default_tone") in TONES else 0)
        if st.form_submit_button("Enregistrer les paramètres", type="primary"):
            state["creator_name"] = creator_name.strip() or "Mon studio"
            state["niche"] = niche
            state["platforms"] = platforms
            state.setdefault("settings", {})["default_tone"] = default_tone
            save_state()
            st.success("Paramètres enregistrés.")
    st.html("<div class='cl-section-title'>Sauvegarde & confidentialité</div>")
    st.write("CreatorLab sauvegarde ses données dans `data/creatorlab_state.json` sur l'appareil où il tourne. Les brouillons ne sont pas envoyés à un compte en ligne automatiquement.")
    backup = json.dumps(state, ensure_ascii=False, indent=2)
    st.download_button("⬇ Télécharger une sauvegarde complète (.json)", backup, file_name="creatorlab_backup.json", mime="application/json", use_container_width=True)
    st.warning("Si tu héberges CreatorLab en ligne, les données locales de ce prototype ne deviennent pas automatiquement un compte multi-utilisateur. Avant une mise en ligne publique, il faudra ajouter des comptes et une base de données partagée.")
    st.html("<div class='cl-section-title'>Mode IA</div>")
    st.write("Le mode local n'utilise pas d'API et reste gratuit. Le mode OpenAI nécessite une clé API et peut entraîner une facturation selon ton utilisation. La clé saisie dans la barre latérale reste en mémoire durant la session et n'est pas écrite dans le fichier de données.")

# Footer
st.html("<div style='margin-top:34px;padding:15px 0;border-top:1px solid #292d40;color:#777d98;font-size:11px'>CREATORLAB · FAIT POUR PASSER DE L'IDÉE À LA PUBLICATION · Les suggestions sont des brouillons à personnaliser.</div>")
