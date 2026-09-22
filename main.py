import streamlit as st
import pandas as pd
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
    """
    df = pd.read_csv(DATA_URL)

    df["openDt"] = pd.to_datetime(df["openDt"], format="%Y%m%d")

    # genre가 "공포(호러)|미스터리" 처럼 되어 있으면 첫 번째 "공포(호러)"만 사용합니다.
    df["대표장르"] = df["genre"].astype(str).str.split("|").str[0]

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
# 섹션 2. (다음 '분포와 관계' 그래프는 여기에 추가하세요)
# ══════════════════════════════════════════════
# 예시:
# st.header("2. ...")
# fig2 = px.scatter(...)
# st.plotly_chart(fig2, use_container_width=True, key="fig2_...")
# st.info("💡 **이 그래프로 알 수 있는 것:** ...")
# st.divider()
