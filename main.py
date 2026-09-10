import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

# 메인 타이틀
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown("---")

# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    df = pd.read_csv(url)
    
    # 날짜 열을 진짜 날짜(datetime) 형식으로 변환 (YYYYMMDD -> datetime)
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d')
    return df

try:
    df = load_data()
    
    # ----------------------------------------------------
    # Section 1: 특정 영화의 날짜별 일관객 변화
    # ----------------------------------------------------
    st.header("📌 Section 1. 개별 영화의 일일 관객수 추이")
    
    # 영화 선택 드롭다운 (가나다 순 정렬)
    movie_list = sorted(df['영화명'].unique())
    selected_movie = st.selectbox("영화를 선택하세요", movie_list)
    
    # 선택한 영화 데이터 필터링
    filtered_df = df[df['영화명'] == selected_movie].sort_values('날짜')
    
    # Plotly 선 그래프 생성
    fig1 = px.line(
        filtered_df,
        x='날짜',
        y='일관객',
        title=f"[{selected_movie}] 날짜별 일관객 변화",
        labels={'날짜': '날짜', '일관객': '일일 관객수 (명)'},
        markers=True
    )
    
    # 마우스 오버(툴팁) 및 레이아웃 설정
    fig1.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>"
    )
    fig1.update_layout(
        xaxis_title="날짜",
        yaxis_title="일일 관객수 (명)",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    # 그래프 출력
    st.plotly_chart(fig1, use_container_width=True)
    
    # 설명문 구역
    st.info(f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 상영 기간에 따른 일일 관객 수 증가 및 감소 흐름과 흥행 전성기 시점을 파악할 수 있습니다.")
    
    st.markdown("---")
    
    # ----------------------------------------------------
    # Section 2: 총 관객수 상위 5개 영화의 일관객 추이 비교
    # ----------------------------------------------------
    st.header("📌 Section 2. 총 관객수 TOP 5 영화의 일일 관객수 비교")
    
    # 기간 내 일관객 합계가 가장 큰 상위 5개 영화 추출
    top5_movies = df.groupby('영화명')['일관객'].sum().nlargest(5).index.tolist()
    top5_df = df[df['영화명'].isin(top5_movies)].sort_values('날짜')
    
    # Plotly 선 그래프 생성 (영화명별 색상 구분)
    fig2 = px.line(
        top5_df,
        x='날짜',
        y='일관객',
        color='영화명',
        title="기간 내 총 관객수 상위 5개 영화의 날짜별 일관객 비교",
        labels={'날짜': '날짜', '일관객': '일일 관객수 (명)', '영화명': '영화 제목'},
        markers=True
    )
    
    # 툴팁 및 레이아웃 설정
    fig2.update_traces(
        hovertemplate="<b>영화명:</b> %{fullData.name}<br><b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>"
    )
    fig2.update_layout(
        xaxis_title="날짜",
        yaxis_title="일일 관객수 (명)",
        hovermode="closest",
        legend_title_text="영화 제목 (클릭하여 토글)",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    # 그래프 출력
    st.plotly_chart(fig2, use_container_width=True)
    
    # Top 5 영화 이름 텍스트 가공
    top5_names_str = ", ".join([f"'{m}'" for m in top5_movies])
    
    # 설명문 구역
    st.info(f"💡 **이 그래프로 알 수 있는 것:** 기간 내 가장 흥행한 상위 5개 영화({top5_names_str})의 일일 관객 수 변동을 한눈에 비교할 수 있으며, 서로 다른 시기별 흥행 경쟁 구도와 흥행 피크(스파이크)의 차이를 파악할 수 있습니다. (오른쪽 범례 항목을 클릭하여 원하는 영화의 선을 켜거나 끌 수 있습니다.)")

    st.markdown("---")
    
    # ----------------------------------------------------
    # Section 3: 일별 10위권 관객수 합계 영역 그래프 (TOP 3 피크일 표시)
    # ----------------------------------------------------
    st.header("📌 Section 3. 일별 TOP 10 총 관객수 추이 및 피크 데이")
    
    # 날짜별 10위권 일관객 합계 구하기
    daily_sum = df.groupby('날짜')['일관객'].sum().reset_index()
    daily_sum.columns = ['날짜', '총일관객']
    daily_sum = daily_sum.sort_values('날짜')
    
    # 관객 수 합계가 가장 컸던 날 상위 3일 추출
    top3_days = daily_sum.nlargest(3, '총일관객').sort_values('날짜')
    
    # Plotly 영역 그래프 (area chart) 생성
    fig3 = px.area(
        daily_sum,
        x='날짜',
        y='총일관객',
        title="날짜별 TOP 10 전체 일일 관객수 합계 추이",
        labels={'날짜': '날짜', '총일관객': 'TOP 10 총 관객수 (명)'}
    )
    
    fig3.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>TOP 10 총 관객수:</b> %{y:,}명<extra></extra>",
        fillcolor='rgba(31, 119, 180, 0.3)',
        line_color='rgb(31, 119, 180)'
    )
    
    # 상위 3일 피크 포인트 및 주석(어노테이션) 추가
    for idx, row in top3_days.iterrows():
        date_str = row['날짜'].strftime('%Y-%m-%d')
        val = row['총일관객']
        
        fig3.add_annotation(
            x=row['날짜'],
            y=val,
            text=f"<b>TOP {top3_days.index.get_loc(idx)+1}<br>{date_str}</b><br>({val:,}명)",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="red",
            ax=0,
            ay=-45,
            bordercolor="red",
            borderwidth=1,
            borderpad=4,
            bgcolor="white",
            opacity=0.9
        )
    
    fig3.update_layout(
        xaxis_title="날짜",
        yaxis_title="TOP 10 총 관객수 (명)",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    # 그래프 출력
    st.plotly_chart(fig3, use_container_width=True)
    
    # TOP 3 날짜 문구 조합
    top3_str_list = [f"{r['날짜'].strftime('%Y년 %m월 %d일')}({r['총일관객']:,}명)" for _, r in top3_days.iterrows()]
    top3_summary_str = ", ".join(top3_str_list)
    
    # 설명문 구역
    st.info(f"💡 **이 그래프로 알 수 있는 것:** 극장가 전체의 일별 관객 동원력 변화와 연중 최고 대목(명절, 연휴, 방학 시즌 등)을 파악할 수 있으며, 특히 총관객수가 가장 많았던 상위 3일({top3_summary_str})을 통해 대표적인 극장가 성수기 날짜를 확인할 수 있습니다.")

    st.markdown("---")

    # ----------------------------------------------------
    # Section 4: 기간 내 관객수 TOP 10 영화 가로 막대그래프
    # ----------------------------------------------------
    st.header("📌 Section 4. 기간 내 누적 관객수 TOP 10 영화 순위")
    
    # 영화별 일관객 합계 및 10위권 진입 일수(날짜 수) 집계
    movie_stats = df.groupby('영화명').agg(
        총관객=('일관객', 'sum'),
        진입일수=('날짜', 'nunique')
    ).reset_index()
    
    # 상위 10개 영화 정렬 및 추출
    top10_movies = movie_stats.nlargest(10, '총관객')
    
    # Plotly 가로 막대그래프 생성
    fig4 = px.bar(
        top10_movies,
        x='총관객',
        y='영화명',
        orientation='h',
        title="기간 내 총 관객수 TOP 10 영화 (10위권 진입 일수 포함)",
        labels={'총관객': '총 관객수 (명)', '영화명': '영화 제목', '진입일수': '10위권 차트인 일수'},
        hover_data={'총관객': ':,d', '진입일수': True, '영화명': True},
        color='총관객',
        color_continuous_scale='Blues'
    )
    
    # 마우스 호버(툴팁) 및 y축 정렬 설정
    fig4.update_traces(
        hovertemplate="<b>영화명:</b> %{y}<br><b>총 관객수:</b> %{x:,}명<br><b>10위권 진입 일수:</b> %{customdata[1]}일<extra></extra>"
    )
    fig4.update_layout(
        yaxis={'categoryorder': 'total ascending'},  # 관객수가 많은 영화가 위쪽에 오도록 설정
        xaxis_title="총 관객수 (명)",
        yaxis_title="영화 제목",
        coloraxis_showscale=False,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    # 그래프 출력
    st.plotly_chart(fig4, use_container_width=True)
    
    top1_movie = top10_movies.iloc[0]
    
    # 설명문 구역
    st.info(f"💡 **이 그래프로 알 수 있는 것:** 해당 기간 최고 흥행작인 '{top1_movie['영화명']}'({top1_movie['총관객']:,}명, {top1_movie['진입일수']}일간 TOP 10 유지)을 비롯한 총 관객수 상위 10개 영화의 전체 규모를 비교할 수 있으며, 막대에 마우스를 올리면 각 영화가 박스오피스 10위권 내에 며칠 동안 머물렀는지(흥행 롱런 여부) 확인할 수 있습니다.")

    st.markdown("---")
    
    # ----------------------------------------------------
    # Section 5: 추후 그래프 추가 구역 (확장용)
    # ----------------------------------------------------
    st.header("📌 Section 5. [추가 예정 그래프 구역]")
    st.caption("앞으로 시간 축 기반의 새로운 영화 분석 그래프가 이곳에 추가될 예정입니다.")
    st.info("💡 **이 그래프로 알 수 있는 것:** (그래프 추가 후 해석 문구가 들어갈 자리입니다.)")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
