import gradio as gr
import requests


API_URL = "http://127.0.0.1:8000/analyze"


def analyze_cv(cv_file, job_description):
    """
    Envoie le CV et l'offre d'emploi à l'API SmartCV AI.
    """

    if cv_file is None:
        return (
            "⚠️ Veuillez sélectionner un CV PDF.",
            "",
            "",
            "",
            "",
            ""
        )

    if not job_description or not job_description.strip():
        return (
            "⚠️ Veuillez saisir une description du poste.",
            "",
            "",
            "",
            "",
            ""
        )

    try:
        with open(cv_file, "rb") as file:
            files = {
                "cv": (
                    "cv.pdf",
                    file,
                    "application/pdf"
                )
            }

            data = {
                "job_description": job_description
            }

            response = requests.post(
                API_URL,
                files=files,
                data=data,
                timeout=120
            )

        if response.status_code != 200:
            try:
                error = response.json().get(
                    "detail",
                    "Erreur inconnue."
                )
            except Exception:
                error = response.text

            return (
                f"❌ Erreur API : {error}",
                "",
                "",
                "",
                "",
                ""
            )

        result = response.json()

        candidate = result.get("candidate", {})

        name = candidate.get("name") or "Non détecté"
        email = candidate.get("email") or "Non détecté"
        phone = candidate.get("phone") or "Non détecté"

        candidate_info = f"""
<div class="info-row">
  <div class="info-icon">👤</div>
  <div class="info-content">
    <span class="info-label">Nom complet</span>
    <span class="info-value">{name}</span>
  </div>
</div>
<div class="info-row">
  <div class="info-icon">✉️</div>
  <div class="info-content">
    <span class="info-label">Email</span>
    <span class="info-value">{email}</span>
  </div>
</div>
<div class="info-row">
  <div class="info-icon">📞</div>
  <div class="info-content">
    <span class="info-label">Téléphone</span>
    <span class="info-value">{phone}</span>
  </div>
</div>
"""

        matched = result.get("matched_skills", [])
        missing = result.get("missing_skills", [])

        matched_text = "\n".join(
            f"- ✅ {skill}"
            for skill in matched
        )

        missing_text = "\n".join(
            f"- ⚠️ {skill}"
            for skill in missing
        )

        if not matched:
            matched_text = "Aucune compétence correspondante détectée."

        if not missing:
            missing_text = "Aucune compétence manquante détectée."

        matched_output = f"""
### ✅ Compétences correspondantes

{matched_text}
"""

        missing_output = f"""
### ⚠️ Compétences à renforcer

{missing_text}
"""

        recommendations = result.get(
            "recommendations",
            []
        )

        recommendations_text = "\n".join(
            f"- 💡 {recommendation}"
            for recommendation in recommendations
        )

        if not recommendations_text:
            recommendations_text = "Aucune recommandation."

        recommendations_output = f"""
### 💡 Recommandations

{recommendations_text}
"""

        score = result.get("match_score", 0)

        if score >= 75:
            score_status = "🟢 Très bonne correspondance"
            score_color = "#10b981"
        elif score >= 50:
            score_status = "🟡 Correspondance moyenne"
            score_color = "#f59e0b"
        else:
            score_status = "🔴 Correspondance faible"
            score_color = "#ef4444"

        score_output = f"""
<div class="score-ring-wrap">
  <div class="score-ring" style="background: conic-gradient({score_color} {score * 3.6}deg, #e5e7eb 0deg);">
    <div class="score-ring-inner">
      <span class="score-number">{score}%</span>
    </div>
  </div>
  <p class="score-status">{score_status}</p>
  <p class="score-caption">Compatibilité entre votre CV et l'offre d'emploi</p>
</div>
"""

        return (
            candidate_info,
            score_output,
            matched_output,
            missing_output,
            recommendations_output,
            ""
        )

    except requests.exceptions.ConnectionError:
        return (
            "❌ Impossible de contacter l'API SmartCV AI. "
            "Vérifiez que FastAPI est lancé.",
            "",
            "",
            "",
            "",
            ""
        )

    except requests.exceptions.Timeout:
        return (
            "⏱️ L'analyse a pris trop de temps. "
            "Veuillez réessayer.",
            "",
            "",
            "",
            "",
            ""
        )

    except Exception as error:
        return (
            f"❌ Erreur : {str(error)}",
            "",
            "",
            "",
            "",
            ""
        )


# =========================================================
# CSS — DESIGN MODERNE SOMBRE
# =========================================================

CSS = """
/* =========================
   FONTS
========================= */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

/* =========================
   VARIABLES
========================= */
:root {
    --bg-0: #07090f;
    --bg-1: #0d1019;
    --bg-2: #131726;
    --bg-3: #1a1f33;
    --border-1: #1e2337;
    --border-2: #2a3048;
    --border-glow: #4f46e5;

    --ink-0: #ffffff;
    --ink-1: #e8ecf5;
    --ink-2: #b8c0d8;
    --ink-3: #7a8298;
    --ink-4: #525a70;

    --brand-1: #6366f1;
    --brand-2: #8b5cf6;
    --brand-3: #06b6d4;
    --brand-4: #ec4899;

    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;

    --shadow-sm: 0 2px 8px rgba(0,0,0,0.4);
    --shadow-md: 0 8px 24px rgba(0,0,0,0.45);
    --shadow-lg: 0 20px 50px rgba(0,0,0,0.55);
    --shadow-glow: 0 0 40px rgba(99,102,241,0.25);

    --radius-sm: 10px;
    --radius-md: 16px;
    --radius-lg: 22px;
    --radius-xl: 28px;
}

/* =========================
   RESET / GLOBAL
========================= */
*, *::before, *::after {
    box-sizing: border-box;
}

html, body,
gradio-app,
.gradio-container,
.dark {
    background: var(--bg-0) !important;
    color: var(--ink-1) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.gradio-container {
    max-width: 1320px !important;
    margin: 0 auto !important;
    padding: 32px 24px !important;
    position: relative;
    overflow-x: hidden;
}

/* Animated background orbs */
.gradio-container::before {
    content: "";
    position: fixed;
    top: -15%;
    left: -10%;
    width: 55vw;
    height: 55vw;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.14) 0%, transparent 65%);
    z-index: 0;
    pointer-events: none;
    animation: floatOrb1 18s ease-in-out infinite;
}

.gradio-container::after {
    content: "";
    position: fixed;
    bottom: -20%;
    right: -10%;
    width: 50vw;
    height: 50vw;
    background: radial-gradient(circle, rgba(236, 72, 153, 0.10) 0%, transparent 65%);
    z-index: 0;
    pointer-events: none;
    animation: floatOrb2 22s ease-in-out infinite;
}

@keyframes floatOrb1 {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(60px, 40px) scale(1.08); }
}

@keyframes floatOrb2 {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(-50px, -30px) scale(1.1); }
}

.gradio-container > * {
    position: relative;
    z-index: 1;
}

/* =========================
   TYPOGRAPHY
========================= */
h1, h2, h3, h4 {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
    color: var(--ink-0) !important;
    letter-spacing: -0.02em;
}

h2 { font-size: 22px !important; font-weight: 700 !important; }
h3 { font-size: 18px !important; font-weight: 700 !important; margin-bottom: 12px !important; }

p, span, label, li {
    color: var(--ink-1);
}

/* =========================
   HERO
========================= */
.hero {
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(ellipse at top left, rgba(99,102,241,0.18) 0%, transparent 50%),
        radial-gradient(ellipse at bottom right, rgba(236,72,153,0.15) 0%, transparent 50%),
        linear-gradient(135deg, #0a0d18 0%, #12162b 50%, #1a1235 100%);
    border: 1px solid var(--border-1);
    border-radius: var(--radius-xl);
    padding: 60px 52px;
    margin-bottom: 32px;
    box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255,255,255,0.05);
    animation: heroIn 0.7s cubic-bezier(0.16, 1, 0.3, 1);
}

.hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    mask-image: radial-gradient(ellipse at center, black 30%, transparent 75%);
}

.hero::after {
    content: "";
    position: absolute;
    top: -50%;
    right: -5%;
    width: 480px;
    height: 480px;
    background: radial-gradient(circle, rgba(139,92,246,0.35) 0%, transparent 65%);
    pointer-events: none;
    animation: pulseGlow 6s ease-in-out infinite;
}

@keyframes pulseGlow {
    0%, 100% { opacity: 0.8; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.08); }
}

@keyframes heroIn {
    from { opacity: 0; transform: translateY(-20px) scale(0.98); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.35);
    backdrop-filter: blur(10px);
    padding: 8px 18px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.3px;
    margin-bottom: 22px;
    color: #c7d2fe;
    position: relative;
    z-index: 2;
    box-shadow: 0 4px 20px rgba(99,102,241,0.25);
    animation: badgeIn 0.6s 0.2s backwards cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes badgeIn {
    from { opacity: 0; transform: translateY(-8px); }
    to { opacity: 1; transform: translateY(0); }
}

.hero h1 {
    font-size: 52px;
    font-weight: 800;
    margin: 0 0 16px 0;
    line-height: 1.1;
    background: linear-gradient(90deg, #ffffff 0%, #c7d2fe 50%, #a5b4fc 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    position: relative;
    z-index: 2;
    animation: titleIn 0.7s 0.3s backwards cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes titleIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

.hero p {
    font-size: 17px;
    line-height: 1.7;
    color: #a5aecb;
    max-width: 660px;
    margin: 0;
    position: relative;
    z-index: 2;
    animation: titleIn 0.7s 0.4s backwards cubic-bezier(0.16, 1, 0.3, 1);
}

/* =========================
   CARDS
========================= */
.card {
    background: linear-gradient(180deg, rgba(19,23,38,0.9) 0%, rgba(13,16,25,0.95) 100%);
    backdrop-filter: blur(12px);
    border-radius: var(--radius-lg);
    padding: 28px;
    border: 1px solid var(--border-1);
    box-shadow: var(--shadow-md);
    transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    overflow: hidden;
    animation: cardIn 0.6s backwards cubic-bezier(0.16, 1, 0.3, 1);
}

.card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.5), transparent);
    opacity: 0;
    transition: opacity 0.35s ease;
}

.card:hover {
    border-color: var(--border-2);
    transform: translateY(-3px);
    box-shadow: var(--shadow-lg), 0 0 0 1px rgba(99,102,241,0.1);
}

.card:hover::before {
    opacity: 1;
}

@keyframes cardIn {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}

.card h2, .card h3 {
    margin-top: 0 !important;
    color: var(--ink-0) !important;
}

/* =========================
   INPUTS / TEXTAREA / FILE
========================= */
label > span,
.block > label,
.gr-form label {
    font-weight: 600 !important;
    color: var(--ink-0) !important;
    font-size: 13.5px !important;
    letter-spacing: 0.2px;
    margin-bottom: 8px !important;
    display: inline-block;
}

textarea,
input[type="text"],
input[type="email"],
input[type="number"],
.gr-textbox,
.gr-file {
    border-radius: var(--radius-md) !important;
    border: 1.5px solid var(--border-1) !important;
    background: rgba(10, 13, 22, 0.7) !important;
    color: var(--ink-0) !important;
    font-size: 14.5px !important;
    transition: all 0.25s ease !important;
    font-family: 'Inter', sans-serif !important;
}

textarea {
    padding: 14px 16px !important;
    line-height: 1.6 !important;
}

textarea::placeholder,
input::placeholder {
    color: var(--ink-4) !important;
}

textarea:focus,
input:focus {
    border-color: var(--brand-1) !important;
    background: rgba(15, 19, 32, 0.9) !important;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15),
                0 0 20px rgba(99, 102, 241, 0.1) !important;
    outline: none !important;
}

/* File upload */
.gr-file,
[data-testid="file"] {
    border: 1.5px dashed var(--border-2) !important;
    background: rgba(10, 13, 22, 0.5) !important;
    border-radius: var(--radius-md) !important;
    transition: all 0.3s ease !important;
    padding: 20px !important;
}

.gr-file:hover,
[data-testid="file"]:hover {
    border-color: var(--brand-1) !important;
    background: rgba(99, 102, 241, 0.05) !important;
    transform: scale(1.005);
}

[data-testid="file"] * {
    color: var(--ink-2) !important;
}

/* =========================
   BUTTON ANALYZE
========================= */
.analyze-button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%) !important;
    background-size: 200% 200% !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    padding: 18px 28px !important;
    letter-spacing: 0.3px;
    cursor: pointer !important;
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.35),
                inset 0 1px 0 rgba(255,255,255,0.2) !important;
    transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
    position: relative;
    overflow: hidden;
    margin: 8px 0 20px 0 !important;
}

.analyze-button::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, transparent, rgba(255,255,255,0.15), transparent);
    transform: translateX(-100%);
    transition: transform 0.6s ease;
}

.analyze-button:hover {
    transform: translateY(-3px);
    background-position: 100% 50% !important;
    box-shadow: 0 16px 40px rgba(99, 102, 241, 0.5),
                inset 0 1px 0 rgba(255,255,255,0.3) !important;
}

.analyze-button:hover::before {
    transform: translateX(100%);
}

.analyze-button:active {
    transform: translateY(-1px) scale(0.99);
}

/* =========================
   SECTION TITLE
========================= */
.section-title {
    display: flex;
    align-items: center;
    gap: 14px;
    font-size: 24px;
    font-weight: 800;
    margin: 24px 0 20px 0 !important;
    color: var(--ink-0);
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.section-title .bar {
    width: 5px;
    height: 28px;
    border-radius: 4px;
    background: linear-gradient(180deg, var(--brand-1), var(--brand-2));
    display: inline-block;
    box-shadow: 0 0 16px rgba(99, 102, 241, 0.6);
    animation: barPulse 2s ease-in-out infinite;
}

@keyframes barPulse {
    0%, 100% { box-shadow: 0 0 16px rgba(99, 102, 241, 0.6); }
    50% { box-shadow: 0 0 28px rgba(139, 92, 246, 0.9); }
}

/* =========================
   SCORE RING
========================= */
.score-card {
    background: linear-gradient(160deg, rgba(19,23,38,0.95), rgba(15,18,32,0.98));
    border-radius: var(--radius-lg);
    padding: 32px;
    border: 1px solid var(--border-1);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-md);
    position: relative;
    overflow: hidden;
}

.score-card::before {
    content: "";
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: conic-gradient(from 0deg, transparent, rgba(99,102,241,0.08), transparent 30%);
    animation: rotateBg 8s linear infinite;
    pointer-events: none;
}

@keyframes rotateBg {
    to { transform: rotate(360deg); }
}

.score-ring-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    position: relative;
    z-index: 1;
    animation: popIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.score-ring {
    width: 180px;
    height: 180px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5),
                0 0 0 1px rgba(255,255,255,0.05),
                inset 0 0 20px rgba(0,0,0,0.3);
    transition: background 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
}

.score-ring::after {
    content: "";
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    background: inherit;
    filter: blur(12px);
    opacity: 0.4;
    z-index: -1;
}

.score-ring-inner {
    width: 140px;
    height: 140px;
    border-radius: 50%;
    background: linear-gradient(160deg, #0d1019, #131726);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: inset 0 4px 12px rgba(0, 0, 0, 0.6);
    border: 1px solid rgba(255,255,255,0.05);
}

.score-number {
    font-size: 38px;
    font-weight: 800;
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: var(--ink-0);
    letter-spacing: -0.02em;
    text-shadow: 0 2px 12px rgba(99,102,241,0.5);
}

.score-status {
    font-size: 17px;
    font-weight: 700;
    margin: 14px 0 0 0;
    color: var(--ink-0);
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.score-caption {
    font-size: 13px;
    color: var(--ink-3);
    margin: 0;
    text-align: center;
}

@keyframes popIn {
    from { opacity: 0; transform: scale(0.8); }
    to { opacity: 1; transform: scale(1); }
}

/* =========================
   INFO ROWS (CANDIDAT)
========================= */
.info-row {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 16px;
    background: rgba(10, 13, 22, 0.5);
    border: 1px solid var(--border-1);
    border-radius: var(--radius-md);
    margin-bottom: 10px;
    transition: all 0.3s ease;
}

.info-row:hover {
    background: rgba(99, 102, 241, 0.06);
    border-color: rgba(99, 102, 241, 0.3);
    transform: translateX(4px);
}

.info-icon {
    width: 40px;
    height: 40px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.15));
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 12px;
    font-size: 18px;
}

.info-content {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
    flex: 1;
}

.info-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--ink-3);
    font-weight: 600;
}

.info-value {
    font-size: 14.5px;
    color: var(--ink-0);
    font-weight: 500;
    word-break: break-word;
}

/* =========================
   RESULT LISTS (Markdown)
========================= */
.card ul, .card ol {
    padding-left: 0 !important;
    list-style: none !important;
    margin: 0 !important;
}

.card li {
    padding: 10px 14px;
    font-size: 14.5px;
    color: var(--ink-1);
    background: rgba(10, 13, 22, 0.4);
    border: 1px solid var(--border-1);
    border-radius: 10px;
    margin-bottom: 8px;
    transition: all 0.25s ease;
    line-height: 1.5;
}

.card li:hover {
    background: rgba(99, 102, 241, 0.06);
    border-color: rgba(99, 102, 241, 0.3);
    transform: translateX(4px);
}

.card li:last-child {
    margin-bottom: 0;
}

/* =========================
   STATUS BANNER
========================= */
#status-banner {
    font-weight: 600;
    text-align: center;
    color: var(--ink-0);
    padding: 12px 20px;
    border-radius: var(--radius-md);
    margin: 8px 0;
    min-height: 0;
    transition: all 0.3s ease;
}

#status-banner:not(:empty) {
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.25);
    color: #fca5a5;
}

/* =========================
   FOOTER
========================= */
.footer {
    text-align: center;
    color: var(--ink-3);
    font-size: 13px;
    margin-top: 44px;
    padding: 24px 0 10px 0;
    border-top: 1px solid var(--border-1);
    line-height: 1.8;
}

.footer b {
    color: var(--ink-1);
    font-weight: 700;
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* =========================
   SCROLLBAR
========================= */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: var(--bg-1);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--brand-1), var(--brand-2));
    border-radius: 10px;
    border: 2px solid var(--bg-1);
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, var(--brand-2), var(--brand-4));
}

/* =========================
   RESPONSIVE
========================= */
@media (max-width: 768px) {
    .gradio-container {
        padding: 16px 12px !important;
    }
    .hero {
        padding: 40px 24px;
        border-radius: var(--radius-lg);
    }
    .hero h1 {
        font-size: 34px;
    }
    .hero p {
        font-size: 15px;
    }
    .card {
        padding: 20px;
        border-radius: var(--radius-md);
    }
    .score-ring {
        width: 150px;
        height: 150px;
    }
    .score-ring-inner {
        width: 116px;
        height: 116px;
    }
    .score-number {
        font-size: 30px;
    }
    .section-title {
        font-size: 20px;
    }
}
"""


FORCE_DARK_JS = """
function forceDark() {
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.replace(url.href);
    }
}
"""


# =========================================================
# THEME GRADIO
# =========================================================

THEME = gr.themes.Soft(
    primary_hue=gr.themes.colors.indigo,
    secondary_hue=gr.themes.colors.violet,
    neutral_hue=gr.themes.colors.slate,
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "monospace"],
).set(
    body_background_fill="#07090f",
    body_background_fill_dark="#07090f",
    background_fill_primary="#0d1019",
    background_fill_primary_dark="#0d1019",
    background_fill_secondary="#131726",
    background_fill_secondary_dark="#131726",
    block_background_fill="#131726",
    block_background_fill_dark="#131726",
    block_border_color="#1e2337",
    block_border_color_dark="#1e2337",
    border_color_primary="#1e2337",
    border_color_primary_dark="#1e2337",
    body_text_color="#e8ecf5",
    body_text_color_dark="#e8ecf5",
    body_text_color_subdued="#7a8298",
    body_text_color_subdued_dark="#7a8298",
    input_background_fill="#0a0d16",
    input_background_fill_dark="#0a0d16",
    input_border_color="#1e2337",
    input_border_color_dark="#1e2337",
    button_primary_background_fill="#6366f1",
    button_primary_background_fill_dark="#6366f1",
    button_primary_text_color="#ffffff",
    button_primary_text_color_dark="#ffffff",
)


with gr.Blocks(
    title="SmartCV AI",
    theme=THEME,
    css=CSS,
    js=FORCE_DARK_JS
) as demo:

    # =========================
    # HEADER
    # =========================

    gr.HTML(
        """
        <div class="hero">
            <span class="hero-badge">✨ Analyse propulsée par l'IA</span>
            <h1>🤖 SmartCV AI</h1>
            <p>
                Analysez votre CV avec l'intelligence artificielle
                et découvrez instantanément sa compatibilité avec
                une offre d'emploi, avec des recommandations
                personnalisées pour maximiser vos chances.
            </p>
        </div>
        """
    )

    # =========================
    # INPUT SECTION
    # =========================

    with gr.Row(equal_height=True):

        with gr.Column(
            scale=1,
            elem_classes="card"
        ):

            gr.Markdown(
                """
                ## 📄 Votre CV

                Importez votre CV au format PDF.
                """
            )

            cv_input = gr.File(
                label="CV au format PDF",
                file_types=[".pdf"],
                type="filepath"
            )

        with gr.Column(
            scale=1,
            elem_classes="card"
        ):

            gr.Markdown(
                """
                ## 💼 Offre d'emploi

                Collez ici la description du poste.
                """
            )

            job_input = gr.Textbox(
                label="Description du poste",
                placeholder=(
                    "Exemple :\n\n"
                    "Nous recherchons un développeur Python "
                    "avec des compétences en FastAPI, Docker, "
                    "PostgreSQL et Git..."
                ),
                lines=10
            )

    analyze_button = gr.Button(
        "🚀 Analyser mon CV",
        variant="primary",
        elem_classes="analyze-button"
    )

    status = gr.Markdown(
        "",
        elem_id="status-banner"
    )

    # =========================
    # RESULTS
    # =========================

    gr.HTML(
        """
        <div class="section-title">
            <span class="bar"></span> Résultats de l'analyse
        </div>
        """
    )

    with gr.Row(equal_height=True):

        with gr.Column(
            scale=1,
            elem_classes="card"
        ):

            candidate_output = gr.HTML(
                "<p style='color:#7a8298;'>Les informations du candidat apparaîtront ici.</p>"
            )

        with gr.Column(
            scale=1,
            elem_classes="score-card"
        ):

            score_output = gr.HTML(
                "<p style='color:#7a8298;'>En attente d'analyse…</p>"
            )

    with gr.Row(equal_height=True):

        with gr.Column(
            elem_classes="card"
        ):

            matched_output = gr.Markdown(
                "Les compétences correspondantes apparaîtront ici."
            )

        with gr.Column(
            elem_classes="card"
        ):

            missing_output = gr.Markdown(
                "Les compétences manquantes apparaîtront ici."
            )

    with gr.Row():

        with gr.Column(
            elem_classes="card"
        ):

            recommendations_output = gr.Markdown(
                "Les recommandations apparaîtront ici."
            )

    # =========================
    # FOOTER
    # =========================

    gr.HTML(
        """
        <div class="footer">
            <b>SmartCV AI</b> · Analyse intelligente de CV
            <br>
            Powered by FastAPI · Sentence Transformers · Gradio
        </div>
        """
    )

    # =========================
    # EVENT
    # =========================

    analyze_button.click(
        fn=analyze_cv,
        inputs=[
            cv_input,
            job_input
        ],
        outputs=[
            candidate_output,
            score_output,
            matched_output,
            missing_output,
            recommendations_output,
            status
        ]
    )


if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860
    )