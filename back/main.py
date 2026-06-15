from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()

class UserProfile(BaseModel):
    is_agreed: bool
    currency: str
    horizon: str
    mental: str
    sector_bias: str
    tech_sub_sectors: List[str] = [] # 🚀 N개의 테마를 배열로 받음
    defense: str
    region: str

# 할당된 퍼센트를 N등분하여 포트폴리오에 넣어주는 마법의 분배기 함수
def allocate_sub_sectors(portfolio: dict, sub_sectors: list, total_ratio: int, etfs: dict):
    if not sub_sectors:
        sub_sectors = ["semi"] # 기본값 방어
    
    # N등분 계산 (소수점 1자리까지)
    ratio_per_sector = round(total_ratio / len(sub_sectors), 1)
    
    for sec in sub_sectors:
        key = f"tech_{sec}"
        if key in etfs:
            portfolio[etfs[key]] = ratio_per_sector

@app.post("/api/recommend")
async def recommend_portfolio(profile: UserProfile):
    if not profile.is_agreed:
        return {"error": "투자자 책임 고지에 동의해야 서비스를 이용할 수 있습니다."}
    
    if profile.horizon == "10Min":
        return {
            "is_exception": True,
            "portfolio": {},
            "comment": "🚨 초단기 단타(10분) 성향은 분산 투자 및 장기 자산 배분을 기본으로 하는 ETF 포트폴리오와는 원칙적으로 전혀 맞지 않습니다! 이 지표는 적립식 투자가 무의미하므로 차라리 SOXL(미국 반도체 3배 레버리지) 같은 초고위험 레버리지 상품이나 당일 급등주 테마로 진입하시는 것을 권장합니다."
        }

    portfolio = {}
    comment = ""
    
    if profile.currency == "USD":
        etfs = {
            "market": "VOO", "tech_core": "QQQ", "dividend": "SCHD", "value": "XLF", 
            "bond_long": "TLT", "bond_short": "SHY", "gold": "IAU",
            "world": "VT", "ex_us": "VXUS", "emerging": "VWO",
            # 🚀 세부 혁신 테마 티커 등록
            "tech_semi": "SMH", "tech_aero": "UFOX", "tech_robo": "BOTZ", "tech_cloud": "CLOU"
        }
    else:
        etfs = {
            "market": "TIGER 미국S&P500", "tech_core": "TIGER 나스닥100", "dividend": "ACE 미국배당다우존스", 
            "value": "TIGER 미국S&P500금융섹터", "bond_long": "ACE 미국30년국채액티브(H)",
            "bond_short": "KODEX 미국채1~3년", "gold": "TIGER 골드선물(H)",
            "world": "KODEX 선진국MSCI World", "ex_us": "TIGER 유로스탁스50(합성 H)", "emerging": "ARIRANG 신흥국MSCI(합성 H)",
            # 🚀 원화 세부 혁신 테마 티커 등록
            "tech_semi": "KODEX 미국반도체MV", "tech_aero": "ARIRANG 우주항공&UAM iSelect", 
            "tech_robo": "TIGER 글로벌AI&로보틱스INDXX", "tech_cloud": "TIGER 글로벌클라우드컴퓨팅INDXX"
        }

    if profile.region == "All_World":
        etfs["market"] = etfs["world"]

    # 멘탈 및 투자 기간에 따른 포트폴리오 뼈대 구성 및 N등분 함수 호출
    if profile.mental == "Weak" or profile.horizon in ["3Years", "5Years"]:
        if profile.horizon == "Forever":
            portfolio = {etfs["dividend"]: 50, etfs["bond_short"]: 30, etfs["gold"]: 20}
        else:
            portfolio = {etfs["market"]: 40, etfs["bond_short"]: 40, etfs["gold"]: 20}
        comment = "변동성 방어에 최우선 목표를 둔 안정형 포트폴리오입니다."
            
    elif profile.mental == "Strong":
        if profile.sector_bias == "Tech":
            portfolio = {etfs["tech_core"]: 20, etfs["market"]: 30, etfs["bond_long"]: 30}
            # 🚀 할당된 20%를 선택한 N개의 테마로 균등 분할!
            allocate_sub_sectors(portfolio, profile.tech_sub_sectors, 20, etfs)
            comment = "시장 지수를 주축으로 삼고, 선택하신 혁신 테마를 위성 자산으로 섞어 알파 수익을 노리는 스마트 밸런스 포트폴리오입니다."
        else:
            portfolio = {etfs["market"]: 50, etfs["dividend"]: 30, etfs["bond_long"]: 20}
            comment = "시장 전체 지수와 우량 배당성장주를 결합하여 안정적인 복리 효과를 노리는 포트폴리오입니다."
            
    else: # Beast
        if profile.sector_bias == "Tech":
            portfolio = {etfs["tech_core"]: 40, etfs["market"]: 20}
            # 🚀 야수의 심장답게 무려 40%의 파이를 선택한 N개의 테마로 균등 분할!
            allocate_sub_sectors(portfolio, profile.tech_sub_sectors, 40, etfs)
            comment = "나스닥 100을 코어로 삼고, 선택하신 혁신 테마에 자산을 집중하여 장기 복리 극대화를 노리는 초공격형 포트폴리오입니다."
        else:
            portfolio = {etfs["tech_core"]: 50, etfs["value"]: 30, etfs["market"]: 20}
            comment = "정보기술과 가치 금융섹터의 상호 보완 관계를 활용하는 공격적 포트폴리오입니다."

    if profile.region == "Global_Mix":
        max_etf = max(portfolio, key=portfolio.get)
        portfolio[max_etf] -= 15
        portfolio[etfs["ex_us"]] = 10
        portfolio[etfs["emerging"]] = 5

    if profile.defense == "Gold" and etfs["gold"] not in portfolio:
        max_etf = max(portfolio, key=portfolio.get)
        portfolio[max_etf] -= 10
        portfolio[etfs["gold"]] = 10
    elif profile.defense == "Bond" and etfs["bond_long"] not in portfolio and etfs["bond_short"] not in portfolio:
        max_etf = max(portfolio, key=portfolio.get)
        portfolio[max_etf] -= 10
        portfolio[etfs["bond_short"]] = 10

    return {"portfolio": portfolio, "comment": comment}

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)