import streamlit as st
from tavily import TavilyClient
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Configuration de l'apparence de l'application ---
st.set_page_config(page_title="AI Visibility Tracker", page_icon="🤖", layout="wide")

# --- Configuration de l'API ---


# Initialisation des clients
tavily = TavilyClient(api_key=TAVILY_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

st.markdown("""
<style>
 .main { background-color: #f8f9fa; }
    .stAlert { border-radius: 10px; }
    div[data-testid="stMetricValue"] { font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- En-tête ---
st.title("🚀 AI Visibility Tracker")
st.write("Outil d'analyse SEO à l'ère de l'intelligence artificielle (Optimisation GEO)")

# --- Entrées ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        target_brand = st.text_input("💎 Votre marque ou domaine :", placeholder="Ex : Tesla ou digikala.com")
    with col2:
        query = st.text_input("🔍 Question de l'utilisateur (Requête) :", placeholder="Ex : Quelle est la meilleure voiture électrique au monde ?")

if st.button("Lancer l'analyse intelligente et le suivi des concurrents"):
    if not target_brand or not query:
        st.warning("Veuillez saisir le nom de la marque et la question.")
    else:
        with st.spinner('Recherche en direct et analyse par Llama 3 en cours...'):
            try:
                # 1. Phase de recherche (Tavily)
                search_result = tavily.search(query=query, search_depth="advanced", max_results=5)
                
                # Extraction du contenu pour l'analyse IA
                context_text = "\n".join([f"Source: {r['url']}\nContent: {r['content']}" for r in search_result['results']])
                
                # 2. Phase d'analyse intelligente (Groq - Llama 3)
                prompt = f"""
You are an AI-powered search engine and AI visibility analyst,
similar to ChatGPT, Gemini, or Perplexity.

Context from live search (Tavily):
{context_text}

Your task is to BOTH:
1) Generate an AI search-style answer to a user query
2) Analyze brand visibility inside that AI-generated answer.

━━━━━━━━━━━━━━━━━━━━━━
STEP 1 — AI SEARCH RESPONSE
━━━━━━━━━━━━━━━━━━━━━━

Answer the following user query in a neutral, informative, and structured way.
Use the provided Context from live search to inform your answer.
When relevant, naturally mention brands, tools, or companies,
as an AI search engine would do in 2026.

User Query:
"{query}"

━━━━━━━━━━━━━━━━━━━━━━
STEP 2 — AI VISIBILITY ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━

Now analyze YOUR OWN answer above with respect to the target brand.

Target Brand:
"{target_brand}"

Perform the following:

1. Is the target brand mentioned?
2. If yes, what is its approximate position?
   (Early / Middle / Late)
3. List all competing brands mentioned BEFORE the target brand.
4. Describe the context of the mention:
   (Positive / Neutral / Negative)
5. Give an AI Visibility Score from 0 to 100
   based on position, prominence, and context.

━━━━━━━━━━━━━━━━━━━━━━
STEP 3 — COMPETITOR WHY ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━

Explain briefly WHY the competitors appearing before the target brand
are more visible in AI-generated answers.
Base your reasoning on:
- Brand authority
- Product specialization
- Content clarity
- Use-case alignment

━━━━━━━━━━━━━━━━━━━━━━
STEP 4 — ACTIONABLE RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━

Provide 3 to 5 concrete, actionable recommendations
to improve the target brand’s visibility in AI-generated answers (GEO).
Focus on:
- Content structure
- AI-oriented SEO (GEO)
- Brand positioning
- Comparative & educational content

━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (VERY IMPORTANT)
━━━━━━━━━━━━━━━━━━━━━━

Return the result in FRENCH, using clean Markdown,
with EXACTLY the following sections:

## 🤖 Réponse du moteur IA
## 📊 Analyse de visibilité IA
## 🧠 Analyse des concurrents (WHY)
## 🚀 Recommandations actionnables
"""
                
                chat_completion = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                )
                ai_analysis = chat_completion.choices[0].message.content

                # 3. Affichage des résultats
                st.divider()
                
                # Affichage des métriques rapides
                brand_found = target_brand.lower() in context_text.lower()
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Statut de présence dans la réponse IA", "✅ Positif" if brand_found else "❌ Négatif")
                with c2:
                    st.metric("Modèle d'analyse", "Llama 3.3 (Groq)")

                # Affichage de l'analyse complète de l'IA
                st.subheader("📝 Rapport d'analyse stratégique (AI Insights)")
                st.markdown("### 📋 Rapport Final")
                st.markdown(ai_analysis)
                
                # Affichage des sources trouvées
                with st.expander("🔗 Voir les sources extraites par Tavily"):
                    for res in search_result['results']:
                        st.write(f"- [{res['title']}]({res['url']})")

            except Exception as e:
                st.error(f"Erreur d'exécution : {str(e)}")
                if "401" in str(e) or "unauthorized" in str(e).lower():
                    st.warning("⚠️ Il semble que les clés API soient invalides ou expirées. Veuillez obtenir de nouvelles clés depuis le panneau Tavily et Groq et les remplacer.")
                if "connection" in str(e).lower() or "max retries" in str(e).lower():
                    st.warning("⚠️ Problème de connexion Internet. Veuillez vérifier votre connexion VPN (les services Groq/Tavily peuvent être bloqués).")

# --- Pied de page de présentation ---
st.sidebar.title("À propos du projet")
st.sidebar.info("""
Ce projet est conçu pour le défi **SEO AI Systems**.
- **Data Engine:** Tavily Search API
- **Inference Engine:** Groq (Llama 3)
- **Frontend:** Streamlit
""")
