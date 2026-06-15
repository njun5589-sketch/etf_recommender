import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI 맞춤형 ETF 포트폴리오", page_icon="📈", layout="centered")

st.title("📈 내 성향에 딱 맞는 ETF 포트폴리오 찾기")
st.markdown("몇 가지 질문을 통해 당신에게 가장 적합한 자산 배분 전략을 제안해 드립니다.")
st.divider()

# ✨ 새로 추가된 혁신 테마 ETF 설명 포함
ETF_DESCRIPTIONS = {
    "VOO": "Vanguard S&P 500 ETF: 미국 대형주 500개 기업에 투자하며 미국 경제 전체의 우상향에 베팅하는 대표 지수형 ETF입니다.",
    "QQQ": "Invesco QQQ Trust: 나스닥 100 지수를 추종하며 애플, 마이크로소프트, 엔비디아 등 기술 성장을 주도하는 빅테크 중심의 스타일형 ETF입니다.",
    "SMH": "VanEck Semiconductor ETF: 엔비디아, TSMC 등 글로벌 반도체 시장의 절대 강자들을 집중적으로 담은 테마형 반도체 ETF입니다.",
    "UFOX": "Defiance Connective Technologies ETF: 우주항공, 5G/6G 네트워크, 위성통신 등 차세대 우주 및 연결 인프라에 투자합니다.",
    "BOTZ": "Global X Robotics & Artificial Intelligence ETF: 산업용 로봇, 자율주행 및 AI 기술을 현실로 구현하는 피지컬 AI 기업들에 집중 투자합니다.",
    "CLOU": "Global X Cloud Computing ETF: 아마존, 마이크로소프트 등 AI의 집이 되는 글로벌 클라우드 및 데이터센터 인프라에 투자합니다.",
    "SCHD": "Schwab U.S. Dividend Equity ETF: 10년 연속 배당을 지급한 미국 우량 배당성장주에 투자하여 탄탄한 현금흐름을 만듭니다.",
    "XLF": "Financial Select Sector SPDR Fund: 미국의 금융 섹터 기업들에 투자하여 경기 회복 수혜와 꾸준한 배당을 노립니다.",
    "TLT": "iShares 20+ Year Treasury Bond ETF: 미국 20년 이상 장기 국채에 투자하여, 주식 하락장의 완충재 역할을 수행합니다.",
    "SHY": "iShares 1-3 Year Treasury Bond ETF: 미국 단기 국채에 투자하여 금리 민감도가 낮고 변동성 리스크가 적은 안전 자산입니다.",
    "IAU": "iShares Gold Trust: 금 현물을 추종하는 대표적인 저비용 ETF로 강력한 하락장 방어력을 가집니다.",
    "VT": "Vanguard Total World Stock ETF: 전 세계 선진국 및 신흥국 주식 시장 전체를 단 하나의 종목으로 통째로 매수합니다.",
    "VXUS": "iShares Core MSCI Total International Stock ETF: 미국을 제외한 전 세계 대형주에 분산 투자하여 국가별 리스크를 낮춥니다.",
    "VWO": "Vanguard FTSE Emerging Markets ETF: 대만, 인도, 브라질 등 잠재력을 가진 글로벌 신흥국 시장에 투자합니다.",
    "TIGER 미국S&P500": "환전 없이 국내 계좌(연금/ISA)에서 미국 S&P 500 지수 전체에 투자할 수 있는 국내 대표 상품입니다.",
    "TIGER 나스닥100": "미국 나스닥 100 지수를 추종하며 글로벌 혁신 기술 성장주에 투자할 수 있는 섹터형 상품입니다.",
    "KODEX 미국반도체MV": "글로벌 반도체 메이저 기업들에 집중 투자하는 한국 상장 테마형 반도체 ETF입니다.",
    "ARIRANG 우주항공&UAM iSelect": "다가오는 우주 시대와 도심항공교통(UAM) 산업을 이끌어갈 국내외 우주항공 핵심 기업에 투자합니다.",
    "TIGER 글로벌AI&로보틱스INDXX": "글로벌 AI 소프트웨어와 피지컬 로보틱스 산업의 성장을 주도하는 전 세계 혁신 기업에 투자합니다.",
    "TIGER 글로벌클라우드컴퓨팅INDXX": "AI 인프라의 핵심인 글로벌 클라우드 컴퓨팅 기업들에 환전 없이 간편하게 투자할 수 있습니다.",
    "ACE 미국배당다우존스": "미국의 대표 배당성장 ETF인 SCHD의 한국 상장 버전으로 장기 적립식 복리 효과를 누리기에 최적화되었습니다.",
    "TIGER 미국S&P500금융섹터": "미국 S&P500 지수 내 금융/은행주 섹터 우량 기업들에 분산 투자하는 가치주 기반 ETF입니다.",
    "ACE 미국30년국채액티브(H)": "미국 장기 국채에 투자하며 환율 변동 리스크를 제거(환헤지)하여 금리 인하 시 수익을 추구합니다.",
    "KODEX 미국채1~3년": "미국 단기 국채에 투자하여 포트폴리오의 변동성을 완화하는 안전 자산형 ETF입니다.",
    "TIGER 골드선물(H)": "국내 상장된 금 선물 추종 상품으로 환헤지가 적용되어 원자재 자산 배분 헷지 효과를 냅니다.",
    "KODEX 선진국MSCI World": "전 세계 선진국 주식 시장 전체에 투자하여 글로벌 자산 배분 기초 자산으로 활용됩니다.",
    "TIGER 유로스탁스50(합성 H)": "유럽을 대표하는 초우량 기업 50개에 분산 투자하여 포트폴리오의 국가를 다변화합니다.",
    "ARIRANG 신흥국MSCI(합성 H)": "성장 잠재력을 지닌 글로벌 신흥국 시장의 메이저 기업들에 투자하여 수익률을 끌어올립니다."
}

with st.form("portfolio_form"):
    st.subheader("📝 투자 성향 분석")
    
    currency_input = st.radio("1. 통화 환경:", ("원화 (연금/ISA 계좌)", "달러 (미국 주식 직접 투자)"))
    
    horizon_input = st.select_slider(
        "2. 이 돈, 최소 언제까지 보유(투자)할 생각이신가요?",
        options=["10분", "3년", "5년", "10년", "평생"]
    )
    
    mental_input = st.radio(
        "3. 내 포트폴리오가 -20% 폭락했을 때 심정은?",
        ("너무 불안해서 잠이 안 온다. 당장 판다.", "원래 주식은 오르내리는 법. 일상에 집중한다.", "바겐세일이다! 마이너스 통장 뚫어서 더 산다.")
    )
    
    sector_input = st.radio(
        "4. 가장 돈이 몰릴 것 같은 시대의 흐름은?",
        ("세상을 바꿀 AI, 반도체, 우주항공 등 혁신 기술", "든든한 금융, 에너지 등 전통 가치주", "잘 모르겠고 미국 전체 시장 다 살래")
    )
    
    # ✨ [핵심 기능] 4번에서 혁신 기술을 선택했을 때만 나타나는 조건부 다중 선택 (Multi-select)
    tech_sub_sectors = []
    if "혁신 기술" in sector_input:
        st.info("💡 혁신 기술을 선택하셨군요! 세부 테마를 복수로 선택하시면 비중을 똑같이 나누어 담아 드립니다.")
        tech_sub_sectors = st.multiselect(
            "4-1. 집중 투자하고 싶은 세부 섹터를 모두 골라주세요.",
            ["반도체", "우주항공", "로보틱스/AI", "클라우드"],
            default=["반도체"] # 기본값
        )
    
    defense_input = st.radio(
        "5. 위기가 왔을 때, 쿠션 역할을 해줄 자산은?",
        ("이자가 나오는 '미국 국채'", "인플레이션에 강한 '금'", "투자하지 않고 현금 관망")
    )

    region_input = st.radio(
        "6. 투자 지역(국가) 구성은?",
        ("오직 미국!", "선진국/신흥국 분산", "전 세계 통합(All World)")
    )
    
    st.divider()
    is_agreed = st.checkbox("투자의 최종 책임은 본인에게 있음에 동의합니다.")
    submitted = st.form_submit_button("🚀 포트폴리오 추천받기")

if submitted:
    if not is_agreed:
        st.warning("⚠️ 투자자 책임 고지에 동의해 주세요.")
    else:
        with st.spinner('AI가 테마 분산 비율을 계산 중입니다...'):
            horizon_map = {"10분": "10Min", "3년": "3Years", "5년": "5Years", "10년": "10Years", "평생": "Forever"}
            
            # 다중 선택된 한글 값을 백엔드용 영문 코드로 변환
            sub_sector_map = {"반도체": "semi", "우주항공": "aero", "로보틱스": "robo", "클라우드": "cloud"}
            selected_techs = [sub_sector_map[tech] for tech in tech_sub_sectors] if tech_sub_sectors else ["semi"]
            
            payload = {
                "is_agreed": is_agreed,
                "currency": "KRW" if "원화" in currency_input else "USD",
                "horizon": horizon_map[horizon_input],
                "mental": "Weak" if "불안" in mental_input else "Strong" if "일상" in mental_input else "Beast",
                "sector_bias": "Tech" if "혁신 기술" in sector_input else "Value" if "전통" in sector_input else "Market",
                "tech_sub_sectors": selected_techs,  # 🚀 백엔드로 선택된 배열 전송!
                "defense": "Bond" if "국채" in defense_input else "Gold" if "금" in defense_input else "Cash",
                "region": "US" if "미국!" in region_input else "Global_Mix" if "분산" in region_input else "All_World"
            }
            
            try:
                response = requests.post("http://localhost:8000/api/recommend", json=payload)
                response.raise_for_status()
                result = response.json()
                
                if "is_exception" in result and result["is_exception"]:
                    st.error("🎉 분석 결과 알림")
                    st.subheader("💡 AI 특별 가이드")
                    st.warning(result.get("comment"))
                else:
                    st.success("🎉 분석이 완료되었습니다!")
                    st.info(result.get("comment"))
                    
                    portfolio = result.get("portfolio", {})
                    if portfolio:
                        df = pd.DataFrame(list(portfolio.items()), columns=['ETF 티커 / 종목명', '비중(%)'])
                        fig = px.pie(df, values='비중(%)', names='ETF 티커 / 종목명', hole=0.4, 
                                     color_discrete_sequence=px.colors.sequential.Teal)
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                        st.table(df.set_index('ETF 티커 / 종목명'))
                        
                        st.divider()
                        st.subheader("🔍 추천 ETF 종목별 상세 가이드")
                        for ticker in portfolio.keys():
                            st.markdown(f"**💡 {ticker}**")
                            st.caption(ETF_DESCRIPTIONS.get(ticker, ""))
                            st.write("")
            except requests.exceptions.ConnectionError:
                st.error("🚨 백엔드 서버(FastAPI)와 연결할 수 없습니다.")