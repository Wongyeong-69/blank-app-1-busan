# streamlit_app.py 또는 main.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import urllib.request
import os
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# ✅ 한글 폰트 설정
def set_korean_font():
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/naver/nanumfont/blob/master/ttf/NanumGothic.ttf?raw=true"
            urllib.request.urlretrieve(url, font_path)
        except Exception as e:
            st.error(f"❌ 한글 폰트 다운로드 실패: {e}")
            return
    fm.fontManager.addfont(font_path)
    font_name = fm.FontProperties(fname=font_path).get_name()
    plt.rc('font', family=font_name)
    plt.rcParams['axes.unicode_minus'] = False

# ✅ CCTV 데이터 로드
@st.cache_data
def load_cctv_data():
    df = pd.read_excel("12_04_08_E_CCTV정보.xlsx", engine="openpyxl")
    cols = df.columns.tolist()
    find = lambda kw: next((c for c in cols if kw in c), None)
    return df.rename(columns={
        find("설치목적"): "목적",
        find("도로명주소"): "설치장소",
        find("위도"): "위도",
        find("경도"): "경도",
        find("설치연"): "설치연도",
        find("카메라대수"): "대수"
    }).dropna(subset=["위도", "경도"])

# ✅ CCTV 지도 시각화
def show_cctv_map():
    set_korean_font()
    st.title("📍 부산시 CCTV 위치 지도")

    df = load_cctv_data()
    df_sample = df.sample(frac=0.3, random_state=42)

    m = folium.Map(
        location=[df_sample["위도"].mean(), df_sample["경도"].mean()],
        zoom_start=11,
        tiles="CartoDB positron"
    )

    marker_cluster = MarkerCluster().add_to(m)
    for _, row in df_sample.iterrows():
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

    st_folium(m, width=800, height=600)

# ✅ Streamlit 앱 실행 시 바로 호출
show_cctv_map()
