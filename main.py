import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ──────────────────────────────────────────────
# 기본 설정
# ──────────────────────────────────────────────
st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", page_icon="📊", layout="wide")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data(ttl=3600)  # 1시간 동안 같은 데이터를 다시 안 불러오고 기억해 둡니다.
def load_data():
    """
    1년간 박스오피스 10위권에 든 영화 가운데, 이 기간에 개봉한 216편의 요약표를 불러옵니다.
    - openDt(개봉일, yyyymmdd 여덟 자리 숫자)를 진짜 날짜(datetime) 타입으로 바꿉니다.
    - genre 열은 '장르1|장르2' 처럼 세로막대(|)로 여러 개가 적혀 있을 수 있어서,
      첫 번째 장르만 뽑아 '대표장르'라는 새 열을 만듭니다.
    - nation 열도 같은 방식으로 첫 번째 나라만 뽑아 '대표국가'라는 새 열을 만듭니다.
    """
    df = pd.read_csv(DATA_URL)

    df["openDt"] = pd.to_datetime(df["openDt"], format="%Y%m%d")

    # genre가 "공포(호러)|미스터리" 처럼 되어 있으면 첫 번째 "공포(호러)"만 사용합니다.
    df["대표장르"] = df["genre"].astype(str).str.split("|").str[0]

    # nation도 "한국|베트남"처럼 여러 나라가 세로막대(|)로 이어져 있을 수 있어서,
    # 마찬가지로 첫 번째 나라만 뽑아 '대표국가'라는 새 열을 만듭니다.
    df["대표국가"] = df["nation"].astype(str).str.split("|").str[0]

    return df


df = load_data()

st.title("📊 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("이 기간에 개봉한 216편의 요약 데이터로 그리는 '분포와 관계' 그래프 모음집이에요.")

st.divider()

# ══════════════════════════════════════════════
# 섹션 1. 장르별 영화 편수 (도넛 그래프)
# ══════════════════════════════════════════════
st.header("1. 장르별 영화 편수")

genre_counts = df["대표장르"].value_counts().reset_index()
genre_counts.columns = ["대표장르", "편수"]

fig1 = go.Figure(data=go.Pie(
    labels=genre_counts["대표장르"],
    values=genre_counts["편수"],
    hole=0.5,  # 가운데를 뚫어서 도넛 모양으로 만듭니다.
    hovertemplate="장르: %{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
    textinfo="label+percent",
))

fig1.update_layout(title="장르별 영화 편수")

st.plotly_chart(fig1, use_container_width=True, key="fig1_genre_donut")

st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽을 수 있는 한 문장을 적어주세요)")

st.divider()

# ══════════════════════════════════════════════
# 섹션 2. 장르 안에 영화 - 트리맵 (칸 크기 = 총 관객)
# ══════════════════════════════════════════════
st.header("2. 장르별 영화 트리맵")

fig2 = px.treemap(
    df,
    path=["대표장르", "movieNm"],  # 큰 칸: 장르, 그 안의 작은 칸: 영화
    values="total_audi",  # 칸의 크기를 총 관객수로 정합니다.
    title="장르 안에 영화 - 칸 크기는 총 관객수",
)

# 마우스를 올리면 영화명과 총 관객이 보이도록 설정합니다.
# (장르 칸을 가리킬 때는 %{label}이 장르명이 되고, 영화 칸을 가리킬 때는 영화명이 됩니다.)
fig2.update_traces(
    hovertemplate="%{label}<br>총 관객: %{value:,}명<extra></extra>"
)

st.plotly_chart(fig2, use_container_width=True, key="fig2_genre_treemap")

st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽을 수 있는 한 문장을 적어주세요)")

st.divider()

# ══════════════════════════════════════════════
# 섹션 3. 총 관객수 분포 (히스토그램)
# ══════════════════════════════════════════════
st.header("3. 총 관객수 분포")

N_BINS = 30

fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=N_BINS,
    title="영화별 총 관객수 분포",
    labels={"total_audi": "총 관객수(명)"},
)
fig3.update_traces(
    hovertemplate="구간: %{x}<br>영화 수: %{y}편<extra></extra>"
)
fig3.update_layout(yaxis_title="영화 수(편)")

st.plotly_chart(fig3, use_container_width=True, key="fig3_total_audi_hist")

# 어느 구간에 영화가 가장 많이 몰려 있는지, 총 관객 1위 영화가 무엇인지 직접 계산해서 보여줍니다.
counts, bin_edges = np.histogram(df["total_audi"], bins=N_BINS)
busiest_idx = counts.argmax()
busiest_low, busiest_high = bin_edges[busiest_idx], bin_edges[busiest_idx + 1]

top_movie_row = df.loc[df["total_audi"].idxmax()]

st.info(
    f"💡 **이 그래프로 알 수 있는 것:** 영화 {int(counts[busiest_idx])}편이 "
    f"총 관객 {busiest_low:,.0f}명 ~ {busiest_high:,.0f}명 구간에 가장 많이 몰려 있고, "
    f"총 관객이 가장 많은 영화는 **'{top_movie_row['movieNm']}'**"
    f"(총 관객 {int(top_movie_row['total_audi']):,}명)이에요."
)

st.divider()

# ══════════════════════════════════════════════
# 섹션 4. 개봉일 스크린수 vs 총 관객 (산점도)
# ══════════════════════════════════════════════
st.header("4. 개봉일 스크린수와 총 관객의 관계")

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="대표장르",  # 장르마다 다른 색으로 구분합니다.
    hover_name="movieNm",  # 마우스를 올리면 영화명이 맨 위에 크게 보입니다.
    title="개봉일 스크린수 vs 총 관객",
    labels={"first_scrn": "개봉일 스크린수(개)", "total_audi": "총 관객수(명)", "대표장르": "장르"},
)

fig4.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}개<br>총 관객: %{y:,}명<extra></extra>"
)

st.plotly_chart(fig4, use_container_width=True, key="fig4_scrn_vs_audi_scatter")

st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽을 수 있는 한 문장을 적어주세요)")

st.divider()

# ══════════════════════════════════════════════
# 섹션 5. 장르별 총 관객 분포 (박스플롯, 10편 이상 장르만)
# ══════════════════════════════════════════════
st.header("5. 장르별 총 관객 분포")

# 영화가 10편 이상인 장르만 골라냅니다.
genre_movie_counts = df["대표장르"].value_counts()
qualified_genres = genre_movie_counts[genre_movie_counts >= 10].index

filtered_df = df[df["대표장르"].isin(qualified_genres)]

fig5 = px.box(
    filtered_df,
    x="대표장르",
    y="total_audi",
    points="outliers",  # 상자 밖으로 튀는 점(이상치)만 표시합니다.
    hover_name="movieNm",  # 이상치 점에 마우스를 올리면 영화명이 보입니다.
    category_orders={"대표장르": list(qualified_genres)},  # 편수가 많은 장르 순서로 나열합니다.
    title="장르별 총 관객 분포 (영화 10편 이상인 장르만)",
    labels={"대표장르": "장르", "total_audi": "총 관객수(명)"},
)

fig5.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>총 관객: %{y:,}명<extra></extra>"
)

st.plotly_chart(fig5, use_container_width=True, key="fig5_genre_boxplot")

st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽을 수 있는 한 문장을 적어주세요)")

st.divider()

# ══════════════════════════════════════════════
# 섹션 6. 개봉일 스크린수 vs 총 관객 (버블 그래프, 크기 = 첫 주 관객)
# ══════════════════════════════════════════════
st.header("6. 개봉일 스크린수와 총 관객의 관계 (버블 그래프)")

fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",  # 점 크기를 첫 주 관객수로 정합니다.
    color="대표장르",  # 장르마다 다른 색으로 구분합니다.
    hover_name="movieNm",  # 마우스를 올리면 영화명이 맨 위에 굵게 보입니다.
    size_max=40,
    title="개봉일 스크린수 vs 총 관객 (점 크기 = 첫 주 관객)",
    labels={
        "first_scrn": "개봉일 스크린수(개)",
        "total_audi": "총 관객수(명)",
        "대표장르": "장르",
        "first_week_audi": "첫 주 관객수",
    },
    # 점 크기(marker.size)는 화면에 그려지는 픽셀 크기라서 실제 관객수와 다릅니다.
    # 그래서 hover_data로 first_week_audi 원래 값을 콤마 형식으로 따로 넣어줍니다.
    hover_data={
        "first_scrn": ":,",
        "total_audi": ":,",
        "first_week_audi": ":,",
        "대표장르": False,  # 범례 색으로 이미 보이므로 툴팁에서는 생략합니다.
    },
)

st.plotly_chart(fig6, use_container_width=True, key="fig6_scrn_vs_audi_bubble")

st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽을 수 있는 한 문장을 적어주세요)")

st.divider()

# ══════════════════════════════════════════════
# 섹션 7. 제작 국가 → 장르 선버스트 (칸 크기 = 편수)
# ══════════════════════════════════════════════
st.header("7. 제작 국가별 장르 분포")

fig7 = px.sunburst(
    df,
    path=["대표국가", "대표장르"],  # 안쪽 칸: 제작 국가, 바깥쪽 칸: 장르
    title="제작 국가 → 장르 (칸 크기는 영화 편수)",
)

fig7.update_traces(
    hovertemplate="%{label}<br>편수: %{value}편<extra></extra>"
)

st.plotly_chart(fig7, use_container_width=True, key="fig7_nation_genre_sunburst")

st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽을 수 있는 한 문장을 적어주세요)")

st.divider()

# ══════════════════════════════════════════════
# 섹션 8. 10위권에 오래 머문 영화는 총 관객도 많은가
# ══════════════════════════════════════════════
st.header("8. 10위권에 오래 머문 영화는 총 관객도 많은가")

fig8 = px.scatter(
    df,
    x="days_in_top10",
    y="total_audi",
    hover_name="movieNm",  # 마우스를 올리면 영화명이 맨 위에 굵게 보입니다.
    title="10위권에 오래 머문 영화는 총 관객도 많은가",
    labels={"days_in_top10": "10위권에 머문 날수(일)", "total_audi": "총 관객수(명)"},
)

fig8.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>10위권에 머문 날수: %{x}일<br>총 관객: %{y:,}명<extra></extra>"
)

st.plotly_chart(fig8, use_container_width=True, key="fig8_days_vs_audi_scatter")

st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽을 수 있는 한 문장을 적어주세요)")

st.divider()

# ══════════════════════════════════════════════
# 섹션 9. (다음 '분포와 관계' 그래프는 여기에 추가하세요)
# ══════════════════════════════════════════════
# 예시:
# st.header("9. ...")
# fig9 = px.scatter(...)
# st.plotly_chart(fig9, use_container_width=True, key="fig9_...")
# st.info("💡 **이 그래프로 알 수 있는 것:** ...")
# st.divider()
