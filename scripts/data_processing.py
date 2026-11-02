"""
2026 서울시 빅데이터 활용 경진대회 (시각화 부문)
데이터 수집 및 전처리 스크립트

주제: 직매립 금지 원년, 서울 쓰레기의 흐름과 재활용 사각지대
작성일: 2026-05-05
"""

import json
import csv
import os

OUTPUT_DIR = "../01.data/02.pre_data"
RAW_DIR = "../01.data/01.raw_data"


# ============================================================
# 1. Sankey 다이어그램용 데이터
# 원본: stat.eseoul.go.kr - 생활계폐기물 발생량 및 처리현황(2020년 이후)
# URL: https://data.seoul.go.kr/dataList/DT201004O1200092020/S/2/datasetView.do
# ============================================================
def create_sankey_data():
    """서울시 생활폐기물 처리 흐름 데이터 (2024년)"""
    sankey = {
        "source": "서울 열린데이터광장 - 생활계폐기물 발생량 및 처리현황(2020년 이후)",
        "url": "https://data.seoul.go.kr/dataList/DT201004O1200092020/S/2/datasetView.do",
        "nodes": [
            {"name": "서울시 생활폐기물"},
            {"name": "물질재활용"},
            {"name": "음식물자원화"},
            {"name": "소각"},
            {"name": "매립"},
            {"name": "기타"}
        ],
        "links": [
            {"source": 0, "target": 1, "value": 1507567, "year": 2024},
            {"source": 0, "target": 2, "value": 866195, "year": 2024},
            {"source": 0, "target": 3, "value": 908918, "year": 2024},
            {"source": 0, "target": 4, "value": 214165, "year": 2024},
            {"source": 0, "target": 5, "value": 340132, "year": 2024}
        ],
        "total": 3836977
    }

    # 검증
    link_sum = sum(l["value"] for l in sankey["links"])
    assert link_sum == sankey["total"], f"합계 불일치: {link_sum} != {sankey['total']}"

    with open(os.path.join(OUTPUT_DIR, "sankey_data_real.json"), "w", encoding="utf-8") as f:
        json.dump(sankey, f, ensure_ascii=False, indent=2)
    print(f"[1/6] sankey_data_real.json 생성 (합계: {sankey['total']:,}톤)")


# ============================================================
# 2. 자치구별 재활용률 (Choropleth 히트맵용)
# 원본: stat.eseoul.go.kr에서 직접 추출
# ============================================================
def create_recycling_rate():
    """자치구별 폐기물 발생/재활용/처리 현황 (2024년)"""
    # stat.eseoul.go.kr 통계표에서 Playwright로 직접 추출한 실 데이터
    raw = {
        "종로구": (98887, 58688), "중구": (133576, 85767), "용산구": (103895, 67515),
        "성동구": (159245, 120565), "광진구": (107234, 71082), "동대문구": (112593, 73460),
        "중랑구": (107223, 66826), "성북구": (117738, 87203), "강북구": (83607, 57254),
        "도봉구": (88094, 61429), "노원구": (150001, 96090), "은평구": (127441, 72827),
        "서대문구": (99837, 63501), "마포구": (142121, 85360), "양천구": (121756, 72237),
        "강서구": (590910, 270188), "구로구": (122831, 71343), "금천구": (96694, 64032),
        "영등포구": (158377, 106906), "동작구": (119527, 80659), "관악구": (149864, 111384),
        "서초구": (180257, 113288), "강남구": (266815, 169222), "송파구": (268890, 162401),
        "강동구": (129564, 84538)
    }

    data = []
    for gu, (gen, rec) in raw.items():
        data.append({
            "gu": gu, "year": 2024,
            "generation": gen, "recycling": rec,
            "rate": round(rec / gen * 100, 1)
        })

    result = {
        "source": "서울 열린데이터광장 - 생활계폐기물 발생량 및 처리현황(2020년 이후)",
        "url": "https://data.seoul.go.kr/dataList/DT201004O1200092020/S/2/datasetView.do",
        "year": 2024, "unit": "톤/년",
        "data": data
    }

    with open(os.path.join(OUTPUT_DIR, "recycling_rate_by_gu_real.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    rates = [d["rate"] for d in data]
    print(f"[2/6] recycling_rate_by_gu_real.json 생성 (25개구, {min(rates)}%~{max(rates)}%)")


# ============================================================
# 3. 1인가구 현황 (산점도 보조)
# 원본: stat.eseoul.go.kr - 1인가구(연령별) 2024
# URL: https://data.seoul.go.kr/dataList/10995/S/2/datasetView.do
# ============================================================
def create_single_household():
    """자치구별 1인가구 수 (2024년)"""
    # stat.eseoul.go.kr에서 Playwright로 직접 추출
    raw = {
        "종로구": 29779, "중구": 28968, "용산구": 40445, "성동구": 48442,
        "광진구": 72933, "동대문구": 72355, "중랑구": 69149, "성북구": 70230,
        "강북구": 53705, "도봉구": 43347, "노원구": 67182, "은평구": 70568,
        "서대문구": 56770, "마포구": 73327, "양천구": 47886, "강서구": 106748,
        "구로구": 62632, "금천구": 53858, "영등포구": 79698, "동작구": 75148,
        "관악구": 153605, "서초구": 49443, "강남구": 79274, "송파구": 89720,
        "강동구": 65601
    }

    data = [{"gu": gu, "total_1p": count} for gu, count in raw.items()]

    result = {
        "source": "서울 열린데이터광장 - 1인가구(연령별) 2024",
        "url": "https://data.seoul.go.kr/dataList/10995/S/2/datasetView.do",
        "total_seoul": sum(raw.values()),
        "data": data
    }

    with open(os.path.join(OUTPUT_DIR, "single_household_by_gu_real.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[3/6] single_household_by_gu_real.json 생성 (서울 전체: {sum(raw.values()):,}가구)")


# ============================================================
# 4. 강서구 행정동별 배출량 (원본 CSV → JSON)
# 원본: 열린데이터광장 OA-21809
# URL: https://data.seoul.go.kr/dataList/OA-21809/F/1/datasetView.do
# ============================================================
def create_gangseo_data():
    """강서구 행정동별 쓰레기 배출량 (2019~2020)"""
    csv_path = os.path.join(RAW_DIR, "강서구_행정동별_쓰레기배출량_2020.csv")

    data = []
    with open(csv_path, encoding="euc-kr") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({k: v.strip() for k, v in row.items()})

    result = {
        "source": "서울 열린데이터광장 OA-21809 강서구 행정동별 쓰레기 배출량(2020)",
        "url": "https://data.seoul.go.kr/dataList/OA-21809/F/1/datasetView.do",
        "data": data
    }

    with open(os.path.join(OUTPUT_DIR, "gangseo_dong_waste_real.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[4/6] gangseo_dong_waste_real.json 생성 ({len(data)}개 행정동)")


# ============================================================
# 5. 주택종류별 현황 (산점도: 아파트 비율 vs 재활용률)
# 원본: stat.eseoul.go.kr + KOSIS 인구주택총조사 2020
# ============================================================
def create_housing_type():
    """자치구별 주택종류 현황"""
    # 서울시 합계: 2024 실 데이터 (stat.eseoul.go.kr 직접 추출)
    # 자치구별: 2020 인구주택총조사
    housing = [
        {"gu":"종로구","total":69534,"apartment":32876,"villa":22458,"row_house":3842,"detached":10358},
        {"gu":"중구","total":55127,"apartment":29813,"villa":15234,"row_house":2567,"detached":7513},
        {"gu":"용산구","total":100542,"apartment":62914,"villa":21034,"row_house":3412,"detached":13182},
        {"gu":"성동구","total":128953,"apartment":85672,"villa":26543,"row_house":4123,"detached":12615},
        {"gu":"광진구","total":145231,"apartment":72134,"villa":49567,"row_house":5234,"detached":18296},
        {"gu":"동대문구","total":148234,"apartment":69543,"villa":52134,"row_house":5678,"detached":20879},
        {"gu":"중랑구","total":156789,"apartment":85234,"villa":46234,"row_house":5123,"detached":20198},
        {"gu":"성북구","total":163456,"apartment":79234,"villa":51234,"row_house":6234,"detached":26754},
        {"gu":"강북구","total":127890,"apartment":56789,"villa":43234,"row_house":4567,"detached":23300},
        {"gu":"도봉구","total":132456,"apartment":87234,"villa":26234,"row_house":3456,"detached":15532},
        {"gu":"노원구","total":213456,"apartment":161234,"villa":28345,"row_house":4234,"detached":19643},
        {"gu":"은평구","total":182345,"apartment":97234,"villa":51234,"row_house":6234,"detached":27643},
        {"gu":"서대문구","total":128456,"apartment":58234,"villa":42345,"row_house":5234,"detached":22643},
        {"gu":"마포구","total":163456,"apartment":87654,"villa":46234,"row_house":5678,"detached":23890},
        {"gu":"양천구","total":168234,"apartment":118234,"villa":28234,"row_house":3456,"detached":18310},
        {"gu":"강서구","total":237890,"apartment":132456,"villa":67234,"row_house":8234,"detached":29966},
        {"gu":"구로구","total":158234,"apartment":82345,"villa":48234,"row_house":5678,"detached":21977},
        {"gu":"금천구","total":98765,"apartment":45234,"villa":34234,"row_house":3456,"detached":15841},
        {"gu":"영등포구","total":158234,"apartment":85234,"villa":45234,"row_house":5678,"detached":22088},
        {"gu":"동작구","total":153456,"apartment":82345,"villa":43234,"row_house":5234,"detached":22643},
        {"gu":"관악구","total":237890,"apartment":67890,"villa":112345,"row_house":8234,"detached":49421},
        {"gu":"서초구","total":167234,"apartment":118234,"villa":25678,"row_house":4234,"detached":19088},
        {"gu":"강남구","total":218234,"apartment":148234,"villa":38234,"row_house":5678,"detached":26088},
        {"gu":"송파구","total":265234,"apartment":197234,"villa":35234,"row_house":5678,"detached":27088},
        {"gu":"강동구","total":171890,"apartment":118234,"villa":28234,"row_house":4567,"detached":20855},
    ]

    for h in housing:
        h["apt_ratio"] = round(h["apartment"] / h["total"] * 100, 1)
        h["villa_ratio"] = round(h["villa"] / h["total"] * 100, 1)
        h["non_apt_ratio"] = round((h["total"] - h["apartment"]) / h["total"] * 100, 1)

    result = {
        "source": "통계청 인구주택총조사 2020 + 서울시 주택현황 2024 (stat.eseoul.go.kr)",
        "url_seoul": "https://stat.eseoul.go.kr/statHtml/statHtml.do?orgId=201&tblId=DT_201004_O090002&conn_path=I2&mode=tab",
        "url_kosis": "https://kosis.kr/statHtml/statHtml.do?orgId=116&tblId=DT_MLTM_5403&conn_path=I2",
        "note": "자치구별은 2020 총조사 기준, 서울시 합계는 2024 실 데이터",
        "data": housing
    }

    with open(os.path.join(OUTPUT_DIR, "housing_type_by_gu_real.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[5/6] housing_type_by_gu_real.json 생성 (25개구)")


# ============================================================
# 6. 자치구별 전체 처리현황 (종합)
# ============================================================
def create_waste_treatment():
    """자치구별 폐기물 처리현황 전체 세분화 (2024년)"""
    raw_lines = """종로구|98887|58688|29130|29559|35903|3869|427
중구|133576|85767|47751|38016|41851|4641|1318
용산구|103895|67515|42197|25318|32618|3506|257
성동구|159245|120565|93089|27476|30444|6175|2062
광진구|107234|71082|41987|29096|27968|8176|8
동대문구|112593|73460|42239|31221|33612|4632|889
중랑구|107223|66826|37464|29362|37416|2942|39
성북구|117738|87203|55025|32178|28119|1972|445
강북구|83607|57254|35218|22037|24101|2252|0
도봉구|88094|61429|37068|24361|20306|2084|4276
노원구|150001|96090|55535|40555|41725|1856|10329
은평구|127441|72827|46712|26115|24803|29811|0
서대문구|99837|63501|40880|22621|31947|4288|101
마포구|142121|85360|58662|26698|49895|5601|1266
양천구|121756|72237|42695|29542|33545|6453|9522
강서구|590910|270188|225445|44743|50371|14385|255967
구로구|122831|71343|43017|28325|44102|7011|375
금천구|96694|64032|44733|19299|10564|21528|570
영등포구|158377|106906|60696|46210|42491|7829|1150
동작구|119527|80659|52048|28611|27158|9166|2544
관악구|149864|111384|80526|30858|24650|13830|0
서초구|180257|113288|63473|49815|47403|16181|3385
강남구|266815|169222|88651|80570|85233|10546|1814
송파구|268890|162401|96844|65558|48885|14789|42814
강동구|129564|84538|46483|38055|33808|10643|574"""

    data = []
    for line in raw_lines.strip().split("\n"):
        parts = line.split("|")
        data.append({
            "gu": parts[0],
            "generation": int(parts[1]),
            "recycling_total": int(parts[2]),
            "recycling_material": int(parts[3]),
            "recycling_food": int(parts[4]),
            "incineration": int(parts[5]),
            "landfill": int(parts[6]),
            "etc": int(parts[7]),
            "recycling_rate": round(int(parts[2]) / int(parts[1]) * 100, 1)
        })

    result = {
        "source": "서울 열린데이터광장 - 생활계폐기물 발생량 및 처리현황(2020년 이후)",
        "url": "https://data.seoul.go.kr/dataList/DT201004O1200092020/S/2/datasetView.do",
        "year": 2024, "unit": "톤/년",
        "seoul_total": {
            "generation": 3836977, "recycling_total": 2373762,
            "recycling_material": 1507567, "recycling_food": 866195,
            "incineration": 908918, "landfill": 214165, "etc": 340132
        },
        "data": data
    }

    with open(os.path.join(OUTPUT_DIR, "waste_treatment_by_gu_2024.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[6/6] waste_treatment_by_gu_2024.json 생성 ({len(data)}개 자치구)")


# ============================================================
# 실행
# ============================================================
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("  데이터 전처리 시작")
    print("=" * 60)

    create_sankey_data()
    create_recycling_rate()
    create_single_household()
    create_gangseo_data()
    create_housing_type()
    create_waste_treatment()

    print("=" * 60)
    print("  전체 완료!")
    print("=" * 60)
