import io
from datetime import timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

st.set_page_config(page_title="NURTURA | Intelligence", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
BG="#0B1220"; PANEL="#121D30"; ACCENT="#56E0C1"; TEXT="#F4F7FC"; MUTED="#A9B7CC"
BLUE="#7C9CFF"; CORAL="#FF8D8D"; GOLD="#FFC46B"; VIOLET="#C5A4FF"; CYAN="#66D9EF"
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--bg:#0B1220;--panel:#121D30;--line:rgba(175,194,222,.16);--mint:#56E0C1;--blue:#7C9CFF;--coral:#FF8D8D;--gold:#FFC46B;--violet:#C5A4FF;--text:#F4F7FC;--muted:#A9B7CC}
html,body,[class*="css"]{font-family:Manrope,Inter,system-ui,sans-serif}
.stApp{background:radial-gradient(ellipse at 75% -8%,rgba(92,112,255,.18),transparent 33%),radial-gradient(ellipse at 8% 20%,rgba(52,224,193,.09),transparent 30%),var(--bg);color:var(--text)}
[data-testid="stHeader"]{background:rgba(11,18,32,.88)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#111B2D,#0B1220);border-right:1px solid var(--line)}
.block-container{padding-top:1.5rem;max-width:1580px;padding-bottom:3rem}
h1,h2,h3,h4{letter-spacing:-.035em!important;color:var(--text)!important}
p,li,label{color:#D4DEEC}
[data-testid="stMetric"]{background:linear-gradient(145deg,rgba(25,39,62,.96),rgba(16,27,44,.96));border:1px solid var(--line);padding:17px 18px;border-radius:17px;box-shadow:0 8px 28px rgba(0,0,0,.10)}
[data-testid="stMetricLabel"]{color:var(--muted)!important;font-size:.76rem!important;font-weight:750!important;letter-spacing:.035em}
[data-testid="stMetricValue"]{color:#F7FAFF!important;font-weight:850!important;letter-spacing:-.045em}
[data-testid="stMetricDelta"]{font-weight:700}
.stButton>button,.stDownloadButton>button{border-radius:11px;border:1px solid rgba(86,224,193,.38);background:linear-gradient(135deg,#8AF3DB,#56D7C0);color:#071C1A;font-weight:850;min-height:2.65rem;box-shadow:0 5px 18px rgba(86,224,193,.08);transition:all .18s ease}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:#D0FFF2;filter:brightness(1.04);transform:translateY(-1px)}
div[data-baseweb="select"]>div,div[data-baseweb="input"]>div,textarea{background:#121D30!important;border-color:var(--line)!important;border-radius:10px!important}
[data-testid="stFileUploader"]{background:rgba(18,29,48,.7);border:1px dashed rgba(86,224,193,.48);border-radius:15px;padding:12px}
[data-testid="stDataFrame"],[data-testid="stTable"]{border:1px solid var(--line);border-radius:13px;overflow:hidden}
[data-testid="stDataFrame"] [role="grid"]{font-variant-numeric:tabular-nums}
hr{border-color:var(--line)!important}
.brand{display:flex;align-items:center;gap:11px;margin-bottom:20px}
.mark{width:44px;height:44px;border-radius:14px;display:flex;align-items:center;justify-content:center;background:linear-gradient(145deg,#8AF3DB,#7C9CFF);color:#081521;font-size:24px;font-weight:900;box-shadow:0 6px 22px rgba(86,224,193,.15)}
.word{font-size:1.08rem;font-weight:900;letter-spacing:.13em;color:#F7FAFF}
.sub{font-size:.65rem;letter-spacing:.13em;text-transform:uppercase;color:#9FB0C8;margin-top:4px}
.eyebrow{color:var(--mint);text-transform:uppercase;font-size:.67rem;letter-spacing:.18em;font-weight:900;margin-bottom:9px}
.hero{border:1px solid var(--line);border-radius:22px;padding:26px 28px;background:linear-gradient(112deg,rgba(24,39,63,.98),rgba(16,27,45,.83));margin-bottom:21px;box-shadow:0 12px 36px rgba(0,0,0,.08)}
.hero-title{font-size:clamp(1.55rem,2.6vw,2.15rem);font-weight:900;letter-spacing:-.055em;line-height:1.18;margin-bottom:10px}
.hero-copy{color:#B7C5D9;max-width:900px;font-size:.91rem;line-height:1.7}
.tag{display:inline-block;padding:6px 10px;border:1px solid rgba(175,194,222,.2);border-radius:999px;color:#D2DDED;font-size:.7rem;margin:12px 5px 0 0;background:rgba(255,255,255,.025)}
.kicker{color:#A9B7CC;text-transform:uppercase;letter-spacing:.15em;font-size:.67rem;font-weight:900;margin:2px 0 12px}
.insight{padding:15px 16px;border:1px solid var(--line);border-left:3px solid var(--mint);background:linear-gradient(100deg,rgba(24,39,63,.8),rgba(18,29,48,.72));border-radius:12px;margin:8px 0;line-height:1.6}
.small{color:#A9B7CC;font-size:.77rem;line-height:1.6}
.footer{color:#8192AA;font-size:.7rem;border-top:1px solid var(--line);padding-top:15px;margin-top:28px}
.section-label{font-size:.68rem;text-transform:uppercase;letter-spacing:.14em;font-weight:900;color:#8EA2BF;margin-bottom:8px}
div[data-testid="stTabs"] button{font-weight:800}
[data-testid="stAlert"]{border-radius:12px}
@media(max-width:800px){.hero{padding:20px}.block-container{padding-left:1rem;padding-right:1rem}}
</style>
""", unsafe_allow_html=True)

REQUIRED=["date","product","units_sold","selling_price","unit_cost","stock_on_hand"]
ALIASES={"day":"date","order_date":"date","sales_date":"date","item":"product","product_name":"product","quantity":"units_sold","units":"units_sold","qty":"units_sold","price":"selling_price","unit_price":"selling_price","cost":"unit_cost","cost_per_unit":"unit_cost","stock":"stock_on_hand","inventory":"stock_on_hand"}

def demo_data():
    rng=np.random.default_rng(41); days=pd.date_range(end=pd.Timestamp.today().normalize(),periods=112,freq="D")
    items=[("Everyday Tote",620,280,85),("Desk Bottle",390,155,110),("Canvas Journal",260,92,145),("Travel Pouch",480,205,68),("Desk Organiser",850,410,32),("Cotton Cap",320,125,90),("Ceramic Mug",540,245,54),("Cable Kit",290,118,120)]
    rows=[]
    for d in days:
        for name,price,cost,stock in items:
            units=max(0,int(rng.poisson(5.5*(1.2 if d.dayofweek>4 else 1))+rng.normal(0,1.3)))
            rows.append({"date":d,"product":name,"units_sold":units,"selling_price":price,"unit_cost":cost,"stock_on_hand":max(0,stock-int((d-days[0]).days*.15)+int(rng.normal(0,6)))})
    return pd.DataFrame(rows)

def prep(raw):
    df=raw.copy()
    df.columns=[str(c).strip().lower().replace(" ","_").replace("-","_") for c in df.columns]
    df=df.rename(columns={c:ALIASES[c] for c in df.columns if c in ALIASES})
    missing=[c for c in REQUIRED if c not in df.columns]
    if missing: return None, f"Missing required columns: {', '.join(missing)}"
    df=df[REQUIRED].copy(); df["date"]=pd.to_datetime(df["date"],errors="coerce")
    df["product"]=df["product"].astype("string").str.strip()
    for c in REQUIRED[2:]: df[c]=pd.to_numeric(df[c],errors="coerce")
    before=len(df); df=df.dropna(subset=REQUIRED)
    if df.empty: return None,"No valid rows remain after checking required values."
    if (df[REQUIRED[2:]]<0).any().any(): return None,"Negative units, prices, costs or stock found. Correct these before analysing."
    df["revenue"]=df.units_sold*df.selling_price
    df["cogs"]=df.units_sold*df.unit_cost
    df["gross_profit"]=df.revenue-df.cogs
    df["margin_pct"]=np.where(df.revenue!=0,df.gross_profit/df.revenue*100,np.nan)
    return df.sort_values("date"), (f"Removed {before-len(df):,} invalid rows." if before>len(df) else None)

def money(x):
    if pd.isna(x): return "—"
    if abs(x)>=10_000_000:return f"₹{x/10_000_000:.2f}Cr"
    if abs(x)>=100_000:return f"₹{x/100_000:.2f}L"
    if abs(x)>=1000:return f"₹{x/1000:.1f}K"
    return f"₹{x:,.0f}"

def layout(fig,height=340):
    """Apply NURTURA's consistent chart typography, contrast, hover and grid styling."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Manrope, Inter, sans-serif", color="#B8C6DA", size=11),
        margin=dict(l=10,r=16,t=34,b=12),
        hoverlabel=dict(bgcolor="#17243A",bordercolor="rgba(86,224,193,.55)",font=dict(color="#F7FAFF",size=12)),
        legend=dict(bgcolor="rgba(0,0,0,0)",orientation="h",y=1.10,x=0,font=dict(size=10)),
        title_font=dict(size=15,color="#F4F7FC"),
        uniformtext_minsize=9,
        uniformtext_mode="hide",
    )
    fig.update_xaxes(showgrid=False,zeroline=False,linecolor="rgba(175,194,222,.16)",tickfont=dict(color="#A9B7CC"))
    fig.update_yaxes(showgrid=True,gridcolor="rgba(175,194,222,.10)",zeroline=False,tickfont=dict(color="#A9B7CC"))
    return fig

def pdf_bytes(df,period):
    buf=io.BytesIO(); doc=SimpleDocTemplate(buf,pagesize=landscape(A4),rightMargin=15*mm,leftMargin=15*mm,topMargin=14*mm,bottomMargin=14*mm)
    styles=getSampleStyleSheet(); styles.add(ParagraphStyle(name="NT",parent=styles["Title"],fontSize=22,textColor=colors.HexColor("#122233"),spaceAfter=5))
    styles.add(ParagraphStyle(name="NH",parent=styles["Heading2"],fontSize=12,textColor=colors.HexColor("#176B5D"),spaceBefore=10,spaceAfter=7))
    rev=df.revenue.sum(); gp=df.gross_profit.sum(); mar=gp/rev*100 if rev else 0
    prod=df.groupby("product",as_index=False).agg(Units=("units_sold","sum"),Revenue=("revenue","sum"),Profit=("gross_profit","sum")).sort_values("Revenue",ascending=False).head(12)
    story=[Paragraph("NURTURA",styles["NT"]),Paragraph("BUSINESS INTELLIGENCE · EXECUTIVE SNAPSHOT",styles["Normal"]),Paragraph(f"Period: {period}",styles["Normal"]),Spacer(1,8),Paragraph("Performance summary",styles["NH"])]
    data=[["Revenue","Gross profit","Gross margin","Units sold","Products"],[money(rev),money(gp),f"{mar:.1f}%",f"{df.units_sold.sum():,.0f}",str(df.product.nunique())]]
    t=Table(data,colWidths=[53*mm]*5); t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#F0F6F5")),("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#607080")),("TEXTCOLOR",(0,1),(-1,1),colors.HexColor("#122233")),("FONTNAME",(0,1),(-1,1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),8),("FONTSIZE",(0,1),(-1,1),13),("GRID",(0,0),(-1,-1),.4,colors.HexColor("#D5E1E5")),("PADDING",(0,0),(-1,-1),8)]))
    story += [t,Paragraph("Product performance",styles["NH"])]
    rows=[["Product","Units","Revenue","Gross profit"]]+[[str(r["product"]),f'{r["Units"]:,.0f}',money(r["Revenue"]),money(r["Profit"])] for _,r in prod.iterrows()]
    t2=Table(rows,repeatRows=1,colWidths=[80*mm,30*mm,45*mm,45*mm]); t2.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#132A36")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F4F7F8")]),("TEXTCOLOR",(0,1),(-1,-1),colors.HexColor("#1A2A36")),("GRID",(0,0),(-1,-1),.3,colors.HexColor("#D8E0E5")),("ALIGN",(1,1),(-1,-1),"RIGHT"),("PADDING",(0,0),(-1,-1),6)]))
    story += [t2,Spacer(1,10),Paragraph("Method note",styles["NH"]),Paragraph("Gross profit = units sold × (selling price − unit cost). Results depend on data completeness and the definitions used in the uploaded file. Forecasts are simple historical baselines, not guarantees.",styles["Normal"])]
    doc.build(story); return buf.getvalue()

with st.sidebar:
    st.markdown('<div class="brand"><div class="mark">◈</div><div><div class="word">NURTURA</div><div class="sub">Intelligence workspace</div></div></div>',unsafe_allow_html=True)
    st.markdown('<div class="small">◉ Session analytics environment<br/>One consistent dataset across each module.</div>',unsafe_allow_html=True)
    st.divider()
    page=st.radio("WORKSPACE",["◈ Executive overview","↗ Sales performance","▦ Product economics","⬡ Inventory control","◴ Forecast studio","✳ Decision center","⇩ Reports & exports","⊙ Data quality","⚙ Workspace settings"])
    st.divider()
    mode=st.radio("DATA SOURCE",["Explore demo data","Upload CSV"])
    upload=st.file_uploader("Business data CSV",type=["csv"]) if mode=="Upload CSV" else None
    st.caption("Required columns")
    st.code("date · product · units_sold\nselling_price · unit_cost\nstock_on_hand")
    st.markdown('<div class="small">BUILD 02.6 · DESIGNED FOR CLARITY</div>',unsafe_allow_html=True)

if mode=="Explore demo data": raw=demo_data()
elif upload is None:
    st.markdown('<div class="eyebrow">NURTURA / BUSINESS INTELLIGENCE</div><div class="hero"><div class="hero-title">A sharper view of your business.</div><div class="hero-copy">Upload operational records to turn sales and inventory data into a focused, decision-ready workspace. Start with demo data to explore the interface.</div></div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    a.markdown("### ◈ Performance"); a.write("Track revenue, gross profit, margin and product contribution.")
    b.markdown("### ⬡ Operations"); b.write("Surface stock pressure and estimated inventory cover.")
    c.markdown("### ✳ Decisions"); c.write("Test scenarios and export concise business reports.")
    st.info("Choose **Explore demo data** or upload a CSV from the sidebar.")
    st.stop()
else:
    try: raw=pd.read_csv(upload)
    except Exception as e: st.error(f"Could not read the CSV: {e}"); st.stop()

df,msg=prep(raw)
if df is None: st.error(msg); st.stop()
if msg: st.warning(msg)

with st.expander("⌘ Refine analysis · date range and product scope"):
    c1,c2,c3=st.columns([1,1,1.4])
    mind,maxd=df.date.min().date(),df.date.max().date()
    start=c1.date_input("From",value=mind,min_value=mind,max_value=maxd)
    end=c2.date_input("To",value=maxd,min_value=mind,max_value=maxd)
    products=sorted(df.product.unique().tolist())
    chosen=c3.multiselect("Products",products,default=products)
if start>end: st.error("Start date must be on or before end date."); st.stop()
d=df[(df.date.dt.date>=start)&(df.date.dt.date<=end)&(df.product.isin(chosen))].copy()
if d.empty: st.warning("No records match these filters."); st.stop()
rev=float(d.revenue.sum()); gp=float(d.gross_profit.sum()); margin=gp/rev*100 if rev else 0; units=float(d.units_sold.sum())
period=f"{start:%d %b %Y} — {end:%d %b %Y}"
pp=d.groupby("product",as_index=False).agg(units_sold=("units_sold","sum"),revenue=("revenue","sum"),cogs=("cogs","sum"),gross_profit=("gross_profit","sum"),latest_stock=("stock_on_hand","last"))
pp["margin_pct"]=np.where(pp.revenue!=0,pp.gross_profit/pp.revenue*100,np.nan)
st.markdown(f'<div class="eyebrow">NURTURA / OPERATING INTELLIGENCE</div><div class="hero"><div class="hero-title">{page.split(" ",1)[-1]}</div><div class="hero-copy">A focused operating view of commercial performance. All modules use the same filtered dataset, with transparent calculations and exportable outputs.</div><span class="tag">◉ {len(d):,} records</span><span class="tag">◷ {period}</span><span class="tag">▦ {d.product.nunique()} products</span></div>',unsafe_allow_html=True)

if page.startswith("◈"):
    st.markdown('<div class="kicker">01 / EXECUTIVE SIGNALS</div>',unsafe_allow_html=True)
    k=st.columns(5)
    for col,label,val in zip(k,["Net sales","Gross profit","Gross margin","Units sold","Products"],[money(rev),money(gp),f"{margin:.1f}%",f"{units:,.0f}",str(d.product.nunique())]): col.metric(label,val)
    daily=d.groupby(d.date.dt.date,as_index=False).agg(revenue=("revenue","sum"),gross_profit=("gross_profit","sum")); daily["date"]=pd.to_datetime(daily.date)
    left,right=st.columns([1.65,1])
    with left:
        st.markdown("### Revenue trajectory")
        fig=px.area(daily,x="date",y="revenue"); fig.update_traces(line=dict(color="#56E0C1",width=2.5),fillcolor="rgba(156,231,211,.10)",hovertemplate="%{x|%d %b}<br>₹%{y:,.0f}<extra></extra>"); fig.update_yaxes(tickprefix="₹",separatethousands=True)
        st.plotly_chart(layout(fig,350),use_container_width=True,config={"displayModeBar":False})
    with right:
        st.markdown("### Revenue mix")
        mix=pp.sort_values("revenue",ascending=False).head(7); fig=px.pie(mix,values="revenue",names="product",hole=.70,color_discrete_sequence=["#56E0C1","#7C9CFF","#FFC46B","#C5A4FF","#FF8D8D","#66D9EF","#A9B7CC"]); fig.update_traces(textinfo="percent",textfont=dict(size=11,color="#F7FAFF"),marker=dict(line=dict(color=BG,width=3),pull=[.035]+[0]*(len(mix)-1))); fig.update_layout(margin=dict(l=0,r=0,t=10,b=0),showlegend=True)
        st.plotly_chart(layout(fig,350),use_container_width=True,config={"displayModeBar":False})
    # A date-by-weekday heatmap reveals recurring trading patterns without inventing values.
    st.markdown("### Trading rhythm")
    heat = d.copy()
    heat["weekday"] = heat["date"].dt.day_name()
    heat["week"] = heat["date"].dt.to_period("W").apply(lambda p: p.start_time)
    heatmap_data = heat.pivot_table(index="weekday", columns="week", values="revenue", aggfunc="sum", fill_value=0)
    weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    heatmap_data = heatmap_data.reindex([w for w in weekday_order if w in heatmap_data.index])
    if not heatmap_data.empty:
        hm = go.Figure(data=go.Heatmap(
            z=heatmap_data.values, x=[x.strftime("%d %b") for x in heatmap_data.columns],
            y=heatmap_data.index, colorscale=[[0,"#17243A"],[.35,"#285B70"],[.7,"#2AAE9A"],[1,"#B6FFE9"]],
            colorbar=dict(title="Revenue",tickprefix="₹",tickfont=dict(color="#A9B7CC"),titlefont=dict(color="#A9B7CC")),
            hovertemplate="Week of %{x}<br>%{y}<br>Revenue: ₹%{z:,.0f}<extra></extra>"
        ))
        hm.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(layout(hm,280),use_container_width=True,config={"displayModeBar":False})
    # Revenue-to-profit bridge makes the gross-profit calculation visually explicit.
    st.markdown("### Revenue-to-profit bridge")
    bridge = go.Figure(go.Waterfall(
        name="Financial bridge",orientation="v",
        x=["Revenue","Cost of goods sold","Gross profit"],
        measure=["absolute","relative","total"],
        y=[rev,-float(d.cogs.sum()),0],
        text=[money(rev),money(-float(d.cogs.sum())),money(gp)],
        textposition="outside",
        connector={"line":{"color":"rgba(175,194,222,.32)"}},
        increasing={"marker":{"color":"#56E0C1"}},
        decreasing={"marker":{"color":"#FF8D8D"}},
        totals={"marker":{"color":"#7C9CFF"}},
        hovertemplate="%{x}<br>₹%{y:,.0f}<extra></extra>"
    ))
    bridge.update_yaxes(tickprefix="₹")
    st.plotly_chart(layout(bridge,300),use_container_width=True,config={"displayModeBar":False})

    best=pp.loc[pp.gross_profit.idxmax()]; low=pp.loc[pp.margin_pct.idxmin()]
    x,y=st.columns(2)
    x.markdown(f'<div class="insight"><b>✦ Profit contribution leader</b><br/><span class="small">{best["product"]} generated {money(best["gross_profit"])} in gross profit. Check availability and repeat-purchase drivers.</span></div>',unsafe_allow_html=True)
    y.markdown(f'<div class="insight"><b>◌ Margin review</b><br/><span class="small">{low["product"]} has the lowest calculated margin ({low["margin_pct"]:.1f}%). Validate pricing, discounts and cost inputs.</span></div>',unsafe_allow_html=True)

elif page.startswith("↗"):
    freq=st.segmented_control("Trend granularity",["Daily","Weekly","Monthly"],default="Weekly") or "Weekly"
    rule={"Daily":"D","Weekly":"W-MON","Monthly":"MS"}[freq]
    trend=d.set_index("date").resample(rule).agg(revenue=("revenue","sum"),gross_profit=("gross_profit","sum"),units_sold=("units_sold","sum")).reset_index()
    fig=go.Figure(); fig.add_trace(go.Scatter(x=trend.date,y=trend.revenue,name="Revenue",mode="lines",line=dict(color="#56E0C1",width=2.5),fill="tozeroy",fillcolor="rgba(156,231,211,.06)")); fig.add_trace(go.Scatter(x=trend.date,y=trend.gross_profit,name="Gross profit",mode="lines",line=dict(color="#7C9CFF",width=2.2))); fig.update_yaxes(tickprefix="₹")
    st.markdown("### Sales and profit trend"); st.plotly_chart(layout(fig,360),use_container_width=True,config={"displayModeBar":False})
    st.dataframe(trend,use_container_width=True,hide_index=True)
    st.markdown("### Product contribution by month")
    monthly = d.assign(month=d.date.dt.to_period("M").dt.to_timestamp()).groupby(["month","product"],as_index=False).agg(revenue=("revenue","sum"))
    if not monthly.empty:
        stacked = px.bar(monthly,x="month",y="revenue",color="product",barmode="stack",
                         color_discrete_sequence=["#56E0C1","#7C9CFF","#FFC46B","#C5A4FF","#FF8D8D","#66D9EF","#A9B7CC","#F4F7FC"])
        stacked.update_traces(marker_line_width=0,hovertemplate="%{fullData.name}<br>%{x|%b %Y}<br>Revenue: ₹%{y:,.0f}<extra></extra>")
        stacked.update_yaxes(tickprefix="₹")
        st.plotly_chart(layout(stacked,370),use_container_width=True,config={"displayModeBar":False})

elif page.startswith("▦"):
    a,b,c=st.columns(3); a.metric("Average product margin",f"{pp.margin_pct.mean():.1f}%"); b.metric("Top profit product",str(pp.loc[pp.gross_profit.idxmax(),"product"])); c.metric("Loss-making rows",f"{int((d.gross_profit<0).sum()):,}")
    left,right=st.columns([1.5,1])
    with left:
        fig=px.bar(pp.sort_values("margin_pct"),x="margin_pct",y="product",orientation="h",color="margin_pct",color_continuous_scale=["#FF8D8D","#FFC46B","#56E0C1"],text_auto=".1f"); fig.update_traces(marker_line_width=0,texttemplate="%{x:.1f}%",textposition="outside",cliponaxis=False,hovertemplate="<b>%{y}</b><br>Margin: %{x:.1f}%<extra></extra>"); fig.update_layout(coloraxis_showscale=False); fig.update_xaxes(ticksuffix="%",range=[min(0,float(pp.margin_pct.min())-5),max(100,float(pp.margin_pct.max())+10)])
        st.markdown("### Margin by product"); st.plotly_chart(layout(fig,390),use_container_width=True,config={"displayModeBar":False})
    with right:
        fig=px.scatter(pp,x="units_sold",y="gross_profit",size="revenue",color="margin_pct",hover_name="product",color_continuous_scale=["#FF8D8D","#FFC46B","#56E0C1"],size_max=46,custom_data=["revenue","margin_pct"]); fig.update_traces(marker=dict(line=dict(width=1,color="rgba(255,255,255,.45)"),opacity=.88),hovertemplate="<b>%{hovertext}</b><br>Units: %{x:,.0f}<br>Gross profit: ₹%{y:,.0f}<br>Revenue: ₹%{customdata[0]:,.0f}<br>Margin: %{customdata[1]:.1f}%<extra></extra>"); fig.update_yaxes(tickprefix="₹")
        st.markdown("### Volume vs. profit"); st.plotly_chart(layout(fig,390),use_container_width=True,config={"displayModeBar":False})
    st.dataframe(pp.sort_values("revenue",ascending=False),use_container_width=True,hide_index=True,column_config={"units_sold":st.column_config.NumberColumn("Units sold",format="localized"),"revenue":st.column_config.NumberColumn("Revenue (₹)",format="₹ %.2f"),"cogs":st.column_config.NumberColumn("Cost of goods (₹)",format="₹ %.2f"),"gross_profit":st.column_config.NumberColumn("Gross profit (₹)",format="₹ %.2f"),"margin_pct":st.column_config.NumberColumn("Margin",format="%.1f%%"),"latest_stock":st.column_config.NumberColumn("Latest stock",format="localized")})

elif page.startswith("⬡"):
    threshold=st.slider("Low-stock review threshold (units)",5,200,35,5)
    inv=pp[["product","latest_stock","units_sold","revenue","gross_profit"]].copy(); days=max(1,(end-start).days+1); inv["units_per_day"]=inv.units_sold/days; inv["cover_days"]=np.where(inv.units_per_day>0,inv.latest_stock/inv.units_per_day,np.nan)
    inv["status"]=np.where(inv.latest_stock<=threshold,"Review stock",np.where(inv.cover_days<7,"Low cover","Monitor"))
    a,b,c=st.columns(3); a.metric("Items below threshold",str(int((inv.latest_stock<=threshold).sum()))); b.metric("Median estimated cover",f"{inv.cover_days.median():.1f} days" if inv.cover_days.notna().any() else "N/A"); c.metric("Latest stock units",f"{inv.latest_stock.sum():,.0f}")
    fig=px.bar(inv.sort_values("latest_stock"),x="latest_stock",y="product",orientation="h",color="status",color_discrete_map={"Review stock":"#FF8D8D","Low cover":"#FFC46B","Monitor":"#56E0C1"}); fig.add_vline(x=threshold,line_dash="dash",line_color="#FFC46B"); st.plotly_chart(layout(fig,370),use_container_width=True,config={"displayModeBar":False})
    st.dataframe(inv.sort_values("latest_stock"),use_container_width=True,hide_index=True,column_config={"latest_stock":st.column_config.NumberColumn("Latest stock",format="localized"),"units_sold":st.column_config.NumberColumn("Units sold",format="localized"),"revenue":st.column_config.NumberColumn("Revenue (₹)",format="₹ %.2f"),"gross_profit":st.column_config.NumberColumn("Gross profit (₹)",format="₹ %.2f"),"units_per_day":st.column_config.NumberColumn("Units/day",format="%.2f"),"cover_days":st.column_config.NumberColumn("Estimated cover (days)",format="%.1f")})
    st.caption("Estimated cover assumes selected-period sales are a reasonable proxy for demand; it is not a replenishment order.")

elif page.startswith("◴"):
    st.markdown("### A transparent baseline")
    st.caption("This repeats a recent average. It is a benchmark, not an advanced machine-learning forecast.")
    a,b=st.columns(2); horizon=a.slider("Forecast horizon (days)",7,42,14,7); window=b.slider("Moving-average window (days)",3,28,7,1)
    daily=d.groupby(d.date.dt.floor("D"),as_index=False).agg(revenue=("revenue","sum")).sort_values("date"); series=daily.set_index("date").revenue.asfreq("D").fillna(0)
    if len(series)<=window: st.warning("Select a longer date range for this moving-average window.")
    else:
        fitted=series.rolling(window).mean().shift(1); valid=fitted.notna(); mae=float(np.mean(np.abs(series[valid]-fitted[valid]))); rmse=float(np.sqrt(np.mean((series[valid]-fitted[valid])**2)))
        dates=pd.date_range(series.index.max()+pd.Timedelta(days=1),periods=horizon,freq="D"); fc=pd.DataFrame({"date":dates,"baseline_revenue":[float(series.tail(window).mean())]*horizon})
        fig=go.Figure(); fig.add_trace(go.Scatter(x=series.index,y=series.values,name="Observed revenue",mode="lines",line=dict(color="#56E0C1",width=2.5))); fig.add_trace(go.Scatter(x=fc.date,y=fc.baseline_revenue,name="Baseline",mode="lines",line=dict(color="#FFC46B",width=2.5,dash="dash"))); fig.update_yaxes(tickprefix="₹")
        st.plotly_chart(layout(fig,380),use_container_width=True,config={"displayModeBar":False})
        a,b,c=st.columns(3); a.metric("Baseline daily revenue",money(fc.baseline_revenue.mean())); b.metric("Backtest MAE",money(mae)); c.metric("Backtest RMSE",money(rmse))
        st.download_button("⇩ Export forecast baseline CSV",fc.to_csv(index=False).encode(),file_name="nurtura_forecast_baseline.csv",mime="text/csv")
        st.caption("Backtest errors describe this historical series only. Holidays, promotions, stockouts and price changes are not modelled.")

elif page.startswith("✳"):
    st.markdown("### Scenario planning"); st.caption("Sensitivity analysis, not a prediction.")
    a,b,c=st.columns(3); price=a.slider("Selling-price change (%)",-20,20,0,1); volume=b.slider("Units-sold change (%)",-30,50,0,5); cost=c.slider("Unit-cost change (%)",-15,25,0,1)
    scenario_rev=rev*(1+price/100)*(1+volume/100); scenario_cost=float(d.cogs.sum())*(1+cost/100)*(1+volume/100); scenario_gp=scenario_rev-scenario_cost; scenario_margin=scenario_gp/scenario_rev*100 if scenario_rev else 0
    k=st.columns(4)
    for col,label,val in zip(k,["Scenario revenue","Scenario gross profit","Scenario margin","Profit change"],[money(scenario_rev),money(scenario_gp),f"{scenario_margin:.1f}%",money(scenario_gp-gp)]): col.metric(label,val)
    compare=pd.DataFrame({"Scenario":["Current data","Adjusted scenario"],"Revenue":[rev,scenario_rev],"Gross profit":[gp,scenario_gp]})
    fig=go.Figure(); fig.add_trace(go.Bar(x=compare.Scenario,y=compare.Revenue,name="Revenue",marker_color="#56E0C1")); fig.add_trace(go.Bar(x=compare.Scenario,y=compare["Gross profit"],name="Gross profit",marker_color="#7C9CFF")); fig.update_layout(barmode="group"); fig.update_yaxes(tickprefix="₹")
    st.plotly_chart(layout(fig,340),use_container_width=True,config={"displayModeBar":False})
    st.warning("Assumptions apply uniformly to all selected rows. Customer elasticity, fixed costs, taxes, returns and competitor response are not modelled.")

elif page.startswith("⇩"):
    st.markdown("### Build a clean handoff")
    a,b=st.columns(2)
    a.download_button("⇩ Download filtered records CSV",d.to_csv(index=False).encode(),file_name="nurtura_filtered_data.csv",mime="text/csv",use_container_width=True)
    b.download_button("⇩ Download product scorecard CSV",pp.to_csv(index=False).encode(),file_name="nurtura_product_scorecard.csv",mime="text/csv",use_container_width=True)
    try:
        a,b=st.columns(2); a.download_button("⇩ Download executive PDF",pdf_bytes(d,period),file_name="nurtura_executive_snapshot.pdf",mime="application/pdf",use_container_width=True)
    except Exception as e: st.error(f"PDF generation failed: {e}")
    st.markdown("Includes headline metrics, product performance and a method note. Check files for confidential fields before sharing.")

elif page.startswith("⊙"):
    a,b,c=st.columns(3); a.metric("Rows loaded",f"{len(raw):,}"); b.metric("Rows analysed",f"{len(d):,}"); c.metric("Missing required values",f"{int(d[REQUIRED].isna().sum().sum()):,}")
    audit=pd.DataFrame({"Check":["Required columns","Duplicate rows","Negative numeric values","Unit cost above selling price","Zero-revenue rows"],"Result":["Passed",f"{int(d.duplicated().sum()):,}",f"{int((d[REQUIRED[2:]]<0).any(axis=1).sum()):,}",f"{int((d.unit_cost>d.selling_price).sum()):,}",f"{int((d.revenue==0).sum()):,}"]})
    st.markdown("### Data-quality audit"); st.dataframe(audit,use_container_width=True,hide_index=True); st.markdown("### Normalized record preview"); st.dataframe(d.head(30),use_container_width=True,hide_index=True)
    st.caption("Duplicate rows are flagged, not automatically deleted, because identical rows can be legitimate records.")

elif page.startswith("⚙"):
    st.markdown("### Workspace profile")
    st.text_input("Workspace name",value="NURTURA Business Intelligence",disabled=True); st.text_input("Currency",value="INR · ₹",disabled=True); st.text_input("Data mode",value="Temporary app session / current runtime",disabled=True)
    st.markdown("### Data handling and security")
    st.warning("Prototype status: this build does not implement user accounts, password login, role-based access, tenant isolation, managed encryption, or a guaranteed deletion workflow. Do not upload customer-identifiable or sensitive business records.")
    st.markdown("### Metric definitions")
    st.markdown("- **Revenue:** units sold × selling price.\n- **Cost of goods sold:** units sold × unit cost.\n- **Gross profit:** revenue − cost of goods sold.\n- **Gross margin:** gross profit ÷ revenue × 100.\n- **Inventory cover:** latest recorded stock ÷ average daily units sold in the selected period.")
    st.markdown("### Product principle"); st.write("NURTURA prioritizes transparent calculations, consistent design, exportable outputs and explicit assumptions over opaque claims.")
    st.info("Visual upgrades do not add authentication or prove tenant isolation. Keep using synthetic or anonymized data until the security checks are implemented and verified.")

st.markdown('<div class="footer">NURTURA INTELLIGENCE WORKSPACE · Validate the data, challenge the assumptions, then decide.</div>',unsafe_allow_html=True)
