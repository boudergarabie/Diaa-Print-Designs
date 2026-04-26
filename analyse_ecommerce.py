import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Diaa Print & Designs · BI Dashboard",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
  html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    background-color: #F8F9FA !important;
  }
  [data-testid="collapsedControl"] { display: none; }
  section[data-testid="stSidebar"] { display: none; }
  .stApp { background-color: #F8F9FA; }
  .block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 1600px; }
  .card {
    background: #ffffff; border-radius: 16px; padding: 24px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.07), 0 1px 3px rgba(0,0,0,0.06);
    border: 1px solid #f0f0f0; margin-bottom: 0px;
  }
  .kpi-card {
    background: #ffffff; border-radius: 16px; padding: 22px 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 1px solid #f0f0f0;
    position: relative; overflow: hidden;
  }
  .kpi-icon  { font-size: 28px; margin-bottom: 12px; display: block; }
  .kpi-label { font-size: 12px; font-weight: 600; letter-spacing: 0.08em;
               text-transform: uppercase; color: #94a3b8; margin-bottom: 6px; }
  .kpi-value { font-size: 28px; font-weight: 800; color: #0f172a;
               line-height: 1; margin-bottom: 8px; }
  .kpi-badge { display: inline-flex; align-items: center; gap: 4px;
               padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
  .badge-green  { background: #dcfce7; color: #16a34a; }
  .badge-red    { background: #fee2e2; color: #dc2626; }
  .badge-blue   { background: #dbeafe; color: #2563eb; }
  .badge-orange { background: #ffedd5; color: #ea580c; }
  .kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 4px; border-radius: 16px 16px 0 0;
  }
  .kpi-ca::before      { background: linear-gradient(90deg, #6366f1, #8b5cf6); }
  .kpi-cmd::before     { background: linear-gradient(90deg, #06b6d4, #0284c7); }
  .kpi-panier::before  { background: linear-gradient(90deg, #10b981, #059669); }
  .kpi-livr::before    { background: linear-gradient(90deg, #f59e0b, #d97706); }
  .kpi-retour::before  { background: linear-gradient(90deg, #f43f5e, #dc2626); }
  .section-title { font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
  .section-sub   { font-size: 12px; color: #94a3b8; margin-bottom: 16px; }
  .dashboard-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
    border-radius: 20px; padding: 30px 36px; margin-bottom: 24px;
  }
  .header-title {
    font-size: 28px; font-weight: 800; margin: 0;
    background: linear-gradient(90deg, #ffffff, #a5b4fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .header-sub { font-size: 14px; color: #94a3b8; margin-top: 6px; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ───────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("diaaprintanddesigns(1).xlsx",
                       dtype={"Téléphone": str, "Téléphone 2": str})
    for col in ["Téléphone", "Téléphone 2"]:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: str(x).split(".")[0].zfill(9)
                if pd.notna(x) and str(x) not in ["nan","None",""] else ""
            )
    df["Date"]        = pd.to_datetime(df["Date d'expédition"], dayfirst=True, errors="coerce")
    df["Mois"]        = df["Date"].dt.to_period("M").astype(str)
    df["JourSemaine"] = df["Date"].dt.day_name()
    df["Montant"]     = pd.to_numeric(df["Montant"], errors="coerce").fillna(0)
    df["Livré"]       = df["Statut colis"].str.contains("Livr",   case=False, na=False).astype(int)
    df["Retour"]      = df["Statut colis"].str.contains("Retour", case=False, na=False).astype(int)
    df["categorie"]   = df["categorie"].str.strip().str.lower()
    return df

df = load_data()

# ─── KPIs ───────────────────────────────────────────────────────────────────────
total_ca    = df["Montant"].sum()
nb_cmd      = len(df)
panier      = df["Montant"].mean()
taux_livr   = df["Livré"].mean()  * 100
taux_retour = df["Retour"].mean() * 100

retour_by_cat = df.groupby("categorie")["Retour"].mean() * 100
cat_risque    = retour_by_cat.idxmax()
risk_val      = retour_by_cat.max()

wilaya_ca   = df.groupby("Wilaya")["Montant"].sum()
top_wil     = wilaya_ca.idxmax()
top_wil_pct = wilaya_ca.max() / total_ca * 100

# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dashboard-header">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;">
    <div>
      <h1 class="header-title">🖨️ Diaa Print & Designs</h1>
      <p class="header-sub">Tableau de bord commercial · Analyse des ventes et de la performance opérationnelle</p>
    </div>
    <div style="text-align:right;">
      <div style="font-size:12px;color:#64748b;">CA Total</div>
      <div style="font-size:32px;font-weight:800;color:#a5b4fc;">
        {total_ca:,.0f} <span style="font-size:16px;">DZD</span>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── KPI CARDS ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""<div class="kpi-card kpi-ca">
      <span class="kpi-icon">💰</span>
      <div class="kpi-label">Chiffre d'Affaires</div>
      <div class="kpi-value">{total_ca/1000:.1f}K</div>
      <span class="kpi-badge badge-blue">DZD Total</span>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card kpi-cmd">
      <span class="kpi-icon">📦</span>
      <div class="kpi-label">Commandes</div>
      <div class="kpi-value">{nb_cmd:,}</div>
      <span class="kpi-badge badge-blue">total</span>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card kpi-panier">
      <span class="kpi-icon">🛒</span>
      <div class="kpi-label">Panier Moyen</div>
      <div class="kpi-value">{panier:,.0f}</div>
      <span class="kpi-badge badge-green">DZD / cmd</span>
    </div>""", unsafe_allow_html=True)
with k4:
    bc_l = "badge-green" if taux_livr >= 70 else "badge-red"
    lb_l = "✅ Bon" if taux_livr >= 70 else "⚠️ Faible"
    st.markdown(f"""<div class="kpi-card kpi-livr">
      <span class="kpi-icon">🚚</span>
      <div class="kpi-label">Taux de Livraison</div>
      <div class="kpi-value">{taux_livr:.1f}%</div>
      <span class="kpi-badge {bc_l}">{lb_l}</span>
    </div>""", unsafe_allow_html=True)
with k5:
    bc_r = "badge-red" if taux_retour >= 20 else "badge-orange"
    lb_r = "⚠️ Élevé" if taux_retour >= 20 else "✅ Contrôlé"
    st.markdown(f"""<div class="kpi-card kpi-retour">
      <span class="kpi-icon">↩️</span>
      <div class="kpi-label">Taux de Retour</div>
      <div class="kpi-value">{taux_retour:.1f}%</div>
      <span class="kpi-badge {bc_r}">{lb_r}</span>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ─── BONUS KPI IA ───────────────────────────────────────────────────────────────
b1, b2 = st.columns(2)
with b1:
    st.markdown(f"""
    <div class="card" style="display:flex;align-items:center;gap:20px;padding:18px 24px;">
      <div style="font-size:36px;">🔍</div>
      <div>
        <div class="kpi-label">IA · Catégorie à Risque de Retour</div>
        <div style="font-size:20px;font-weight:700;color:#0f172a;">{cat_risque.title()}</div>
        <div style="font-size:12px;color:#94a3b8;margin-top:2px;">
          Taux de retour : <b style='color:#dc2626'>{risk_val:.1f}%</b>
          — Optimisez l'emballage de cette catégorie
        </div>
      </div>
    </div>""", unsafe_allow_html=True)
with b2:
    st.markdown(f"""
    <div class="card" style="display:flex;align-items:center;gap:20px;padding:18px 24px;">
      <div style="font-size:36px;">📍</div>
      <div>
        <div class="kpi-label">IA · Wilaya la Plus Rentable</div>
        <div style="font-size:20px;font-weight:700;color:#0f172a;">{top_wil}</div>
        <div style="font-size:12px;color:#94a3b8;margin-top:2px;">
          Représente <b style='color:#6366f1'>{top_wil_pct:.1f}%</b> du CA
          — Concentrez vos efforts marketing ici
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ─── AREA CHART + DONUT ─────────────────────────────────────────────────────────
lc, rc = st.columns([7, 3], gap="medium")

with lc:
    st.markdown("""<div class="card">
      <div class="section-title">📈 Comment nos ventes évoluent-elles dans le temps ?</div>
      <div class="section-sub">Tendance mensuelle du CA avec volume de commandes associé</div>
    """, unsafe_allow_html=True)

    monthly = (df.groupby("Mois")
               .agg(CA=("Montant","sum"), Commandes=("Montant","count"))
               .reset_index().sort_values("Mois"))

    # ── 12 mois complets, données manquantes = None (pas 0) pour ne pas casser la courbe
    all_months = [f"2025-{str(m).zfill(2)}" for m in range(1, 13)]
    monthly = monthly.set_index("Mois").reindex(all_months)
    monthly.index.name = "Mois"
    monthly = monthly.reset_index()

    mois_labels = {
        "2025-01":"Jan","2025-02":"Fév","2025-03":"Mar","2025-04":"Avr",
        "2025-05":"Mai","2025-06":"Jun","2025-07":"Jul","2025-08":"Aoû",
        "2025-09":"Sep","2025-10":"Oct","2025-11":"Nov","2025-12":"Déc"
    }
    monthly["MoisLabel"] = monthly["Mois"].map(mois_labels)

    ca_max  = monthly["CA"].max()
    cmd_max = monthly["Commandes"].max()

    fig_area = go.Figure()

    # Barres commandes — axe secondaire, plafond haut pour les tasser en bas
    fig_area.add_trace(go.Bar(
        x=monthly["MoisLabel"],
        y=monthly["Commandes"].fillna(0),
        name="Commandes",
        yaxis="y2",
        marker_color="rgba(16,185,129,0.28)",
        hovertemplate="<b>%{x}</b><br>Commandes: %{y:.0f}<extra></extra>"
    ))

    # Courbe CA — axe principal, connectGaps=False pour couper proprement après Juillet
    fig_area.add_trace(go.Scatter(
        x=monthly["MoisLabel"],
        y=monthly["CA"],          # NaN pour les mois sans données → ligne s'arrête
        mode="lines+markers",
        name="CA (DZD)",
        connectgaps=False,        # ← ne relie pas les points nuls
        line=dict(color="#6366f1", width=3),
        marker=dict(size=8, color="#6366f1", line=dict(color="white", width=2)),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.10)",
        hovertemplate="<b>%{x}</b><br>CA: %{y:,.0f} DZD<extra></extra>"
    ))

    fig_area.update_layout(
        height=320,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        hovermode="x unified",
        font=dict(family="Inter, sans-serif"),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=11, color="#94a3b8"),
            categoryorder="array",
            categoryarray=list(mois_labels.values())
        ),
        # Axe CA principal — courbe occupe les 3/4 supérieurs du graphique
        yaxis=dict(
            showgrid=True,
            gridcolor="#f1f5f9",
            tickfont=dict(size=10, color="#94a3b8"),
            tickformat=",.0f",
            range=[0, ca_max * 1.30],   # ← espace au-dessus de la courbe
        ),
        # Axe commandes secondaire — barres confinées au tiers inférieur
        yaxis2=dict(
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(size=10, color="#94a3b8"),
            range=[0, cmd_max * 6],     # ← barres très écrasées vers le bas
        ),
    )
    st.plotly_chart(fig_area, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with rc:
    st.markdown("""<div class="card">
      <div class="section-title">🏷️ Quelle catégorie domine notre marché ?</div>
      <div class="section-sub">Part de chaque type de produit dans le CA total</div>
    """, unsafe_allow_html=True)

    cat_data = (df.groupby("categorie")["Montant"].sum().reset_index()
                .rename(columns={"categorie":"Cat","Montant":"CA"}))
    cat_data["Cat"] = cat_data["Cat"].str.title()

    fig_donut = go.Figure(go.Pie(
        labels=cat_data["Cat"],
        values=cat_data["CA"],
        hole=0.58,
        marker=dict(
            colors=["#6366f1","#06b6d4","#10b981"],
            line=dict(color="white", width=3)
        ),
        textinfo="label+percent",              # ← texte sur les tranches
        textposition="inside",                 # ← texte à l'intérieur
        insidetextorientation="horizontal",    # ← texte horizontal, lisible
        textfont=dict(size=11, family="Inter", color="white"),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} DZD<br>%{percent}<extra></extra>",
    ))
    fig_donut.add_annotation(
        text=f"<b>{total_ca/1000:.1f}K</b><br>DZD",
        x=0.5, y=0.5, font_size=15, showarrow=False,
        font=dict(color="#0f172a", family="Inter")
    )
    fig_donut.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,                      # ← légende supprimée
        font=dict(family="Inter, sans-serif")
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ─── TOP PRODUITS + WILAYAS ─────────────────────────────────────────────────────
ins1, ins2 = st.columns([5, 5], gap="medium")

with ins1:
    st.markdown("""<div class="card">
      <div class="section-title">🏆 Quels sont les produits qui génèrent le plus de revenus ?</div>
      <div class="section-sub">Top 10 produits classés par chiffre d'affaires cumulé</div>
    """, unsafe_allow_html=True)
    prod_data = (df.groupby("Produit")["Montant"].sum()
                 .nlargest(10).reset_index().sort_values("Montant"))
    prod_data["Produit"] = prod_data["Produit"].str.upper()
    fig_bar = go.Figure(go.Bar(
        x=prod_data["Montant"], y=prod_data["Produit"], orientation="h",
        marker=dict(color=prod_data["Montant"], colorscale="Purp"),
        hovertemplate="<b>%{y}</b><br>CA: %{x:,.0f} DZD<extra></extra>",
        text=prod_data["Montant"].apply(lambda x: f"{x/1000:.1f}K"),
        textposition="outside",
        textfont=dict(size=11, color="#6366f1", family="Inter")
    ))
    fig_bar.update_layout(
        height=340, margin=dict(l=0,r=60,t=10,b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor="#f8f9fa",
                   tickfont=dict(size=10,color="#94a3b8"), tickformat=",.0f"),
        yaxis=dict(showgrid=False, tickfont=dict(size=11,color="#334155")),
        font=dict(family="Inter, sans-serif")
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with ins2:
    st.markdown("""<div class="card">
      <div class="section-title">🗺️ Où perdons-nous le plus d'argent à cause des retours ?</div>
      <div class="section-sub">Top 10 wilayas — CA généré vs pertes estimées sur retours</div>
    """, unsafe_allow_html=True)
    wilaya_agg = df.groupby("Wilaya").agg(
        CA=("Montant","sum"), Retours=("Retour","sum")
    ).reset_index()
    top10_wil  = wilaya_agg.nlargest(10,"CA").sort_values("CA")
    avg_ticket = df.groupby("Wilaya")["Montant"].mean().reindex(top10_wil["Wilaya"]).values
    fig_wil = go.Figure()
    fig_wil.add_trace(go.Bar(
        y=top10_wil["Wilaya"], x=top10_wil["CA"],
        name="CA (DZD)", orientation="h", marker_color="#06b6d4",
        hovertemplate="<b>%{y}</b><br>CA: %{x:,.0f} DZD<extra></extra>"
    ))
    fig_wil.add_trace(go.Bar(
        y=top10_wil["Wilaya"],
        x=top10_wil["Retours"] * avg_ticket,
        name="Pertes Retours", orientation="h",
        marker_color="rgba(244,63,94,0.7)",
        hovertemplate="<b>%{y}</b><br>Pertes: %{x:,.0f} DZD<extra></extra>"
    ))
    fig_wil.update_layout(
        barmode="overlay", height=340, margin=dict(l=0,r=0,t=10,b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor="#f8f9fa",
                   tickfont=dict(size=10,color="#94a3b8"), tickformat=",.0f"),
        yaxis=dict(showgrid=False, tickfont=dict(size=11,color="#334155")),
        font=dict(family="Inter, sans-serif")
    )
    st.plotly_chart(fig_wil, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ─── HEATMAP + LOGISTICS ────────────────────────────────────────────────────────
h1, h2 = st.columns([6, 4], gap="medium")

with h1:
    st.markdown("""<div class="card">
      <div class="section-title">📅 Activité par Jour × Catégorie</div>
      <div class="section-sub">Heatmap des ventes — identifier les pics de commande</div>
    """, unsafe_allow_html=True)
    order   = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    fr_days = {"Monday":"Lun","Tuesday":"Mar","Wednesday":"Mer","Thursday":"Jeu",
               "Friday":"Ven","Saturday":"Sam","Sunday":"Dim"}
    heat  = df.groupby(["JourSemaine","categorie"])["Montant"].sum().reset_index()
    pivot = heat.pivot(index="JourSemaine", columns="categorie", values="Montant").fillna(0)
    pivot = pivot.reindex([d for d in order if d in pivot.index])
    pivot.index = [fr_days.get(d,d) for d in pivot.index]
    fig_heat = px.imshow(pivot, color_continuous_scale="Purp",
                         aspect="auto", labels=dict(color="CA (DZD)"))
    fig_heat.update_layout(
        height=280, margin=dict(l=0,r=0,t=10,b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font=dict(family="Inter, sans-serif", size=12),
        xaxis=dict(title="", tickfont=dict(size=11,color="#334155")),
        yaxis=dict(title="", tickfont=dict(size=11,color="#334155"))
    )
    fig_heat.update_traces(
        hovertemplate="<b>%{y} · %{x}</b><br>CA: %{z:,.0f} DZD<extra></extra>"
    )
    st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with h2:
    st.markdown("""<div class="card">
      <div class="section-title">🚀 A domicile vs Stop Desk : Quel est le mode de livraison le plus fiable ?</div>
      <div class="section-sub">Taux de réussite (livraison effective) par mode logistique</div>
    """, unsafe_allow_html=True)

    col_presta = next((c for c in df.columns if "presta" in c.lower()), None)

    if col_presta:
        logist = df.groupby(col_presta).agg(
            Total=("Livré","count"), Livres=("Livré","sum")
        ).reset_index()
        logist["Taux"] = (logist["Livres"] / logist["Total"] * 100).round(1)
        logist = logist[
            logist[col_presta].str.strip().str.upper().isin(["A DOMICILE","STOP DESK"])
        ]
        logist[col_presta] = logist[col_presta].str.strip().str.title()

        fig_donut_log = go.Figure(go.Pie(
            labels=logist[col_presta],
            values=logist["Taux"],
            hole=0.60,
            marker=dict(colors=["#6366f1","#06b6d4"],
                        line=dict(color="white", width=3)),
            textinfo="label+percent",
            textposition="inside",
            insidetextorientation="horizontal",
            textfont=dict(size=12, family="Inter", color="white"),
            hovertemplate="<b>%{label}</b><br>Taux: %{value:.1f}%<extra></extra>",
            direction="clockwise",
            sort=False
        ))
        fig_donut_log.add_annotation(
            text="<b>Fiabilité</b><br>Livraison",
            x=0.5, y=0.5,
            font=dict(size=13, color="#0f172a", family="Inter"),
            showarrow=False
        )
        fig_donut_log.update_layout(
            height=280, margin=dict(l=10,r=10,t=10,b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            font=dict(family="Inter, sans-serif")
        )
        st.plotly_chart(fig_donut_log, use_container_width=True,
                        config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ─── CLUBS VS ANIME + PERFORMANCE ───────────────────────────────────────────────
univ_col1, univ_col2 = st.columns([4, 6], gap="medium")

with univ_col1:
    st.markdown("""<div class="card">
      <div class="section-title">⚽ Clubs vs Animé vs Autre</div>
      <div class="section-sub">Univers produits par CA généré</div>
    """, unsafe_allow_html=True)
    anime_kw = ["one piece","bleach","naruto","dragon","demon","manga","solo leveling"]
    club_kw  = ["mca","usma","jsk","crb","rck","usmb","nahd","csna","mab","mcb"]
    def classify(p):
        p = str(p).lower()
        if any(k in p for k in anime_kw): return "Animé 🎌"
        if any(k in p for k in club_kw):  return "Clubs 🏆"
        return "Autre 🎨"
    df2 = df.copy()
    df2["Univers"] = df2["Produit"].apply(classify)
    uni = df2.groupby("Univers")["Montant"].sum().reset_index()
    fig_uni = go.Figure(go.Pie(
        labels=uni["Univers"], values=uni["Montant"], hole=0.55,
        marker=dict(colors=["#f59e0b","#6366f1","#10b981"],
                    line=dict(color="white",width=3)),
        textinfo="label+percent",
        textposition="inside",
        insidetextorientation="horizontal",
        textfont=dict(size=11, family="Inter", color="white"),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} DZD<br>%{percent}<extra></extra>"
    ))
    fig_uni.update_layout(
        height=280, margin=dict(l=10,r=10,t=10,b=10),
        paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
        font=dict(family="Inter, sans-serif", size=12)
    )
    st.plotly_chart(fig_uni, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with univ_col2:
    st.markdown("""<div class="card">
      <div class="section-title">📊 Performance par Univers Produit</div>
      <div class="section-sub">Comparaison CA et taux de retour entre Clubs, Animé et Autre</div>
    """, unsafe_allow_html=True)
    df2_agg = df2.groupby("Univers").agg(
        CA=("Montant","sum"), Retours=("Retour","mean")
    ).reset_index()
    df2_agg["Retours"] = df2_agg["Retours"] * 100
    fig_perf = go.Figure()
    fig_perf.add_trace(go.Bar(
        x=df2_agg["Univers"], y=df2_agg["CA"],
        name="CA (DZD)",
        marker_color=["#6366f1","#f59e0b","#10b981"],
        hovertemplate="<b>%{x}</b><br>CA: %{y:,.0f} DZD<extra></extra>",
        text=df2_agg["CA"].apply(lambda x: f"{x/1000:.0f}K"),
        textposition="outside",
        textfont=dict(size=12, family="Inter")
    ))
    fig_perf.add_trace(go.Scatter(
        x=df2_agg["Univers"], y=df2_agg["Retours"],
        name="Taux Retour (%)", yaxis="y2",
        mode="markers+lines",
        marker=dict(size=12, color="#f43f5e", symbol="diamond",
                    line=dict(color="white", width=2)),
        line=dict(color="#f43f5e", width=2, dash="dot"),
        hovertemplate="<b>%{x}</b><br>Retour: %{y:.1f}%<extra></extra>"
    ))
    fig_perf.update_layout(
        height=280, margin=dict(l=0,r=0,t=20,b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(showgrid=False, tickfont=dict(size=12,color="#334155")),
        yaxis=dict(showgrid=True, gridcolor="#f8f9fa",
                   tickfont=dict(size=10,color="#94a3b8"), tickformat=",.0f"),
        yaxis2=dict(overlaying="y", side="right", showgrid=False,
                    tickfont=dict(size=10,color="#f43f5e"), ticksuffix="%",
                    range=[0, df2_agg["Retours"].max()*1.5]),
        font=dict(family="Inter, sans-serif")
    )
    st.plotly_chart(fig_perf, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)
