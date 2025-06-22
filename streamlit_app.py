# streamlit_app.py
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

st.set_page_config(layout="wide", page_title="진주시 CCTV 현황")
st.title("🗺 부산광역시 CCTV 현황")

# 1) 엑셀 읽기
df = pd.read_excel("12_04_08_E_CCTV정보.xlsx", engine="openpyxl")

# 2) 컬럼 자동 탐색
cols = df.columns.tolist()
find = lambda kw: next((c for c in cols if kw in c), None)

purpose_col = find("설치목적")       # e.g. "설치목적구분"
address_col = find("도로명주소")      # e.g. "소재지도로명주소"
lat_col     = find("위도")            # e.g. "WGS84위도"
lon_col     = find("경도")            # e.g. "WGS84경도"
year_col    = find("설치연")          # e.g. "설치연월"
count_col   = find("카메라대수")      # e.g. "카메라대수"

# 3) 필수 컬럼 누락 체크
missing = [name for name,var in [
    ("설치목적",purpose_col),
    ("도로명주소",address_col),
    ("위도",lat_col),
    ("경도",lon_col),
    ("설치연월",year_col),
    ("카메라대수",count_col),
] if var is None]
if missing:
    st.error(f"다음 키워드를 포함하는 컬럼을 찾을 수 없습니다: {missing}")
    st.write("현재 컬럼명:", cols)
    st.stop()

# 4) 보기 편하게 간소화
df_vis = df.rename(columns={
    purpose_col: "목적",
    address_col:"설치장소",
    lat_col:    "위도",
    lon_col:    "경도",
    year_col:   "설치연도",
    count_col:  "대수",
})

# (선택) 위경도 누락 행 제거
df_vis = df_vis.dropna(subset=["위도","경도"])

# 5) 데이터 테이블
st.subheader("▶ CCTV 데이터 ")
st.dataframe(
    df_vis[["목적","설치장소","위도","경도","설치연도","대수"]],
    use_container_width=True
)

# 6) 지도 생성 & 클러스터링
m = folium.Map(
    location=[df_vis["위도"].mean(), df_vis["경도"].mean()],
    zoom_start=11,
    tiles="OpenStreetMap"
)
marker_cluster = MarkerCluster().add_to(m)

for _, row in df_vis.iterrows():
    popup = (
        f"<b>목적:</b> {row['목적']}<br>"
        f"<b>장소:</b> {row['설치장소']}<br>"
        f"<b>연도:</b> {row['설치연도']}<br>"
        f"<b>대수:</b> {row['대수']}"
    )
    folium.Marker(
        location=[row["위도"], row["경도"]],
        popup=folium.Popup(popup, max_width=300)
    ).add_to(marker_cluster)

# 7) Streamlit에 출력
st.subheader("▶ CCTV 위치 분포도")
st_folium(m, width=900, height=600)
