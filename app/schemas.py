from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


LISTING_RECOMMENDATION_REQUEST_EXAMPLE = {
    "user_message": "비건 디저트 팝업에 맞는 공간을 추천해줘",
    "conversation_history": [
        {"role": "user", "content": "성수에서 3일 정도 운영하고 싶어"},
        {"role": "assistant", "content": "예산과 원하는 시설을 알려주세요."},
    ],
    "business_item": "비건 디저트 팝업",
    "business_description": "20~30대 여성 대상의 감성형 디저트 팝업",
    "target_audience": "20~30대 여성, 주말 데이트 방문객",
    "desired_region": "성수",
    "region_summary": "감도 높은 F&B와 쇼룸형 팝업이 자주 열리는 트렌디한 상권",
    "foot_traffic_profile": "주말 유동인구가 많고 사진 촬영 수요가 높음",
    "nearby_businesses": ["카페", "쇼룸", "편집숍"],
    "region_strengths": ["MZ 방문객 비중 높음", "SNS 확산 유리"],
    "region_risks": ["임대료 부담", "주말 경쟁 심화"],
    "festival_info": [
        {
            "name": "로컬 디저트 페스타",
            "location": "성수",
            "date": "2026-09-15",
            "summary": "MZ 방문객이 많은 디저트 중심 행사",
        }
    ],
    "budget_limit_per_day": 250000,
    "budget_limit_deposit": 2000000,
    "desired_popup_duration": "3~5일",
    "desired_count": 2,
    "listings": [
        {
            "listing_id": "prop-001",
            "title": "성수 메인 골목 1층 쇼룸",
            "address": "서울 성동구 성수이로 00",
            "price_per_day": 220000,
            "deposit": 1500000,
            "area_sqm": 48.0,
            "summary": "통유리 전면과 촬영 동선이 좋은 1층 공간",
            "facilities": ["와이파이", "조명", "테이블"],
            "restrictions": ["육류 취급 불가"],
            "hashtags": ["#성수", "#1층", "#쇼룸"],
            "available_from": "2026-08-01",
            "available_to": "2026-08-31",
        },
        {
            "listing_id": "prop-002",
            "title": "성수 복합문화공간 2층",
            "address": "서울 성동구 연무장길 00",
            "price_per_day": 280000,
            "deposit": 2500000,
            "area_sqm": 65.0,
            "summary": "전시와 클래스 운영이 가능한 넓은 공간",
            "facilities": ["조명", "음향", "빔프로젝터"],
            "restrictions": [],
            "hashtags": ["#성수", "#복합공간"],
            "available_from": "2026-08-05",
            "available_to": "2026-08-20",
        },
    ],
    "additional_constraints": "브랜딩 촬영이 가능하고 1층이면 더 좋아요",
}

LISTING_RECOMMENDATION_RESPONSE_EXAMPLE = {
    "assistant_message": "성수의 주말 방문객과 촬영 수요를 고려해 가장 잘 맞는 공간 2곳을 골랐어요.",
    "region_analysis": "성수는 감도 높은 팝업 경험을 찾는 방문객이 많아 비건 디저트 브랜딩 실험에 유리합니다.",
    "recommended_listings": [
        {
            "listing_id": "prop-001",
            "title": "성수 메인 골목 1층 쇼룸",
            "fit_score": 91,
            "summary": "브랜딩형 디저트 팝업에 적합한 전면 노출형 공간입니다.",
            "match_reasons": [
                "MZ 방문객과 사진 촬영 수요가 높은 지역 특성과 잘 맞음",
                "예산 범위 안에서 쇼룸형 연출이 가능함",
            ],
            "caution_points": ["주말 경쟁이 강해 사전 홍보가 필요함"],
        },
        {
            "listing_id": "prop-002",
            "title": "성수 복합문화공간 2층",
            "fit_score": 78,
            "summary": "체험형 팝업으로 확장하기 좋은 넓은 공간입니다.",
            "match_reasons": [
                "전시와 클래스 운영이 가능해 체류 시간을 늘리기 좋음",
                "복합문화공간 콘셉트가 브랜드 스토리 전달에 유리함",
            ],
            "caution_points": ["예산 상한에 가까워 추가 비용 검토가 필요함"],
        },
    ],
    "reason_if_none": None,
}

LISTING_INPUT_WARNING_RESPONSE_EXAMPLE = {
    "assistant_message": "추천 정확도를 높이려면 몇 가지 정보가 더 필요해요. 사업 설명, 타깃 고객, 지역 특성, 예산, 후보 매물 정보를 조금 더 정확하게 입력해 주세요.",
    "region_analysis": "입력된 정보가 충분하지 않아 지역 특성과 후보 매물을 안정적으로 비교하기 어려운 상태입니다.",
    "recommended_listings": None,
    "reason_if_none": "현재 요청에는 사업 설명 또는 타깃 고객 정보, 지역 특성 정보, 예산 또는 운영 기간 정보, 후보 매물 상세 정보가 부족합니다. 매물의 주소, 가격, 면적, 시설 같은 정보도 함께 보내주시면 더 정확하게 추천해드릴 수 있어요.",
}

REGION_RECOMMENDATION_REQUEST_EXAMPLE = {
    "business_item": "비건 디저트 팝업",
    "business_description": "20대 여성 대상, 감성 브랜딩 중심",
    "target_audience": "20~30대 여성",
    "budget_level": "중간",
    "preferred_popup_duration": "3~5일",
    "desired_region_count": 3,
    "region_candidates": ["성수", "홍대", "연남"],
    "festival_info": [
        {
            "name": "로컬 디저트 페스타",
            "location": "성수",
            "date": "2026-09-15",
            "summary": "MZ 방문객이 많은 디저트 중심 행사",
        }
    ],
    "additional_constraints": "팝업 첫 운영이라 테스트 수요가 높은 곳이면 좋음",
}

REGION_RECOMMENDATION_RESPONSE_EXAMPLE = {
    "analysis_summary": "브랜드 감도와 테스트 수요를 함께 고려하면 성수, 연남, 홍대 순으로 검토하는 것이 유리합니다.",
    "recommended_regions": [
        {
            "region": "성수",
            "score": 92,
            "summary": "감도 높은 소비자와 팝업 친화적 분위기가 강점입니다.",
            "reasons": ["SNS 확산력이 높음", "브랜딩형 F&B 팝업 적합도 높음"],
            "recommended_strategy": ["주말 중심 운영", "포토존 중심 공간 연출"],
            "caution_points": ["임대료 부담", "주말 경쟁 심화"],
        },
        {
            "region": "연남",
            "score": 84,
            "summary": "산책형 방문객이 많아 소규모 체험형 팝업에 적합합니다.",
            "reasons": ["체류형 동선에 유리", "감성 브랜드 선호도 높음"],
            "recommended_strategy": ["평일 저녁 프로모션", "로컬 카페와 협업"],
            "caution_points": ["공간 규모가 작을 수 있음"],
        },
    ],
}

BUSINESS_ITEM_RECOMMENDATION_REQUEST_EXAMPLE = {
    "district_name": "연남",
    "district_description": "감성 카페와 편집숍이 밀집한 골목 상권",
    "target_customer": "20~30대 여성과 주말 데이트 방문객",
    "foot_traffic_profile": "오후부터 저녁까지 체류 시간이 긴 편",
    "nearby_businesses": ["카페", "소품숍", "공방"],
    "strengths": ["감성 소비 강함", "SNS 인증 수요 높음"],
    "festival_info": [
        {
            "name": "로컬 크리에이터 위크",
            "location": "연남",
            "date": "2026-10-03",
            "summary": "수공예와 라이프스타일 브랜드 중심 행사",
        }
    ],
    "space_profile": "20~30평대, 체험존 구성 가능",
    "desired_item_count": 3,
}

BUSINESS_ITEM_RECOMMENDATION_RESPONSE_EXAMPLE = {
    "area_summary": "연남은 감성 소비와 산책형 유입이 강해 체험형 라이프스타일 팝업에 유리합니다.",
    "recommended_items": [
        {
            "item_name": "핸드메이드 디저트 체험 팝업",
            "fit_score": 89,
            "target_customer": "20~30대 여성, 커플 방문객",
            "summary": "체험과 구매를 함께 유도하기 좋은 아이템입니다.",
            "reasons": ["체류형 상권과 잘 맞음", "SNS 인증 요소를 만들기 쉬움"],
            "execution_tips": ["소규모 클래스 운영", "한정판 패키지 구성"],
        }
    ],
}

MARKETING_AUTOMATION_REQUEST_EXAMPLE = {
    "business_item": "비건 디저트 팝업",
    "business_description": "로컬 제철 재료를 활용한 감성형 디저트 브랜드",
    "region": "성수",
    "target_audience": "20~30대 여성, 주말 데이트 방문객",
    "tone": "친근하고 감도 높은",
    "promotion_goal": "방문 유도",
    "channels": ["instagram", "blog", "flyer"],
    "differentiators": ["비건 레시피", "사진이 잘 나오는 쇼룸형 공간"],
    "festival_context": "성수 일대 로컬 디저트 행사 시즌",
    "call_to_action": "이번 주말에 방문해 보세요",
}

MARKETING_AUTOMATION_RESPONSE_EXAMPLE = {
    "campaign_summary": "성수 상권의 감도 높은 방문객을 겨냥해 비건 디저트의 차별점을 강조하는 캠페인입니다.",
    "target_hook": "맛과 분위기를 모두 챙긴 비건 디저트 팝업",
    "recommended_schedule": ["오픈 5일 전 인스타 예고", "오픈 2일 전 블로그 상세 소개"],
    "contents": [
        {
            "channel": "instagram",
            "headline": "성수에서 만나는 비건 디저트 팝업",
            "primary_copy": "이번 주말, 성수에서 감성적인 비건 디저트를 경험해 보세요.",
            "bullet_points": ["사진이 잘 나오는 쇼룸형 공간", "한정 수량 시그니처 메뉴"],
            "hashtags": ["#성수팝업", "#비건디저트", "#주말데이트"],
        }
    ],
}

HEALTH_RESPONSE_EXAMPLE = {"status": "ok", "model": "claude-sonnet-4-20250514"}


class FestivalInfo(BaseModel):
    name: str = Field(..., description="축제명")
    location: str = Field(..., description="축제 지역")
    date: str = Field(..., description="축제 날짜 또는 기간")
    summary: str = Field(..., description="축제/행사 요약")


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=2000)


class RegionRecommendationRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": REGION_RECOMMENDATION_REQUEST_EXAMPLE})

    business_item: str = Field(..., description="창업 아이템 이름")
    business_description: str = Field(default="", description="아이템 상세 설명")
    target_audience: str = Field(default="", description="타깃 고객층")
    budget_level: str = Field(default="", description="예산 수준")
    preferred_popup_duration: str = Field(default="", description="희망 팝업 기간")
    desired_region_count: int = Field(default=3, ge=1, le=5)
    region_candidates: list[str] = Field(default_factory=list, description="후보 지역 목록")
    festival_info: list[FestivalInfo] = Field(default_factory=list, description="연계 축제 정보")
    additional_constraints: str = Field(default="", description="추가 제약 조건")


class RegionRecommendationItem(BaseModel):
    region: str
    score: int = Field(..., ge=0, le=100)
    summary: str
    reasons: list[str]
    recommended_strategy: list[str]
    caution_points: list[str]


class RegionRecommendationResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": REGION_RECOMMENDATION_RESPONSE_EXAMPLE})

    analysis_summary: str
    recommended_regions: list[RegionRecommendationItem]


class ListingCandidate(BaseModel):
    listing_id: str = Field(..., description="매물 고유 ID")
    title: str = Field(..., description="매물명")
    address: str = Field(default="", description="주소")
    detail_address: str = Field(default="", description="상세 주소")
    price_per_day: Optional[float] = Field(default=None, description="하루 이용료")
    deposit: Optional[float] = Field(default=None, description="보증금")
    area_sqm: Optional[float] = Field(default=None, description="면적(m²)")
    summary: str = Field(default="", description="매물 요약")
    facilities: list[str] = Field(default_factory=list, description="시설 목록")
    restrictions: list[str] = Field(default_factory=list, description="업종/운영 제한")
    hashtags: list[str] = Field(default_factory=list, description="해시태그")
    available_from: str = Field(default="", description="운영 가능 시작일")
    available_to: str = Field(default="", description="운영 가능 종료일")


class ListingRecommendationRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": LISTING_RECOMMENDATION_REQUEST_EXAMPLE})

    user_message: str = Field(default="", max_length=2000, description="현재 사용자가 보낸 채팅 메시지")
    conversation_history: list[ConversationMessage] = Field(
        default_factory=list,
        max_length=10,
        description="최근 대화 내역. 오래된 순서로 전달",
    )
    business_item: str = Field(..., description="창업 아이템")
    business_description: str = Field(default="", description="사업 아이템 상세 설명")
    target_audience: str = Field(default="", description="타깃 고객층")
    desired_region: str = Field(..., description="선택한 지역/상권명")
    region_summary: str = Field(default="", description="지역 특성 요약")
    foot_traffic_profile: str = Field(default="", description="유동인구 특성")
    nearby_businesses: list[str] = Field(default_factory=list, description="주변 업종")
    region_strengths: list[str] = Field(default_factory=list, description="지역 강점")
    region_risks: list[str] = Field(default_factory=list, description="지역 리스크")
    festival_info: list[FestivalInfo] = Field(default_factory=list, description="축제/행사 정보")
    budget_limit_per_day: Optional[float] = Field(default=None, description="하루 이용료 예산 상한")
    budget_limit_deposit: Optional[float] = Field(default=None, description="보증금 예산 상한")
    desired_popup_duration: str = Field(default="", description="희망 팝업 기간")
    desired_count: int = Field(default=3, ge=1, le=3, description="반환 희망 개수")
    listings: list[ListingCandidate] = Field(..., min_length=1, description="후보 매물 목록")
    additional_constraints: str = Field(default="", description="추가 조건")


class ListingRecommendationItem(BaseModel):
    listing_id: str
    title: str
    fit_score: int = Field(..., ge=0, le=100)
    summary: str
    match_reasons: list[str]
    caution_points: list[str]


class ListingRecommendationResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": LISTING_RECOMMENDATION_RESPONSE_EXAMPLE})

    assistant_message: str = Field(..., min_length=1, description="프론트 말풍선에 표시할 AI 답변")
    region_analysis: str
    recommended_listings: Optional[list[ListingRecommendationItem]] = Field(default=None, min_length=1, max_length=3)
    reason_if_none: Optional[str] = None


class BusinessItemRecommendationRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": BUSINESS_ITEM_RECOMMENDATION_REQUEST_EXAMPLE})

    district_name: str = Field(..., description="선택한 상권/지역명")
    district_description: str = Field(default="", description="상권 설명")
    target_customer: str = Field(default="", description="주요 방문객/고객층")
    foot_traffic_profile: str = Field(default="", description="유동인구 특성")
    nearby_businesses: list[str] = Field(default_factory=list, description="주변 업종")
    strengths: list[str] = Field(default_factory=list, description="상권 강점")
    festival_info: list[FestivalInfo] = Field(default_factory=list, description="지역 행사 정보")
    space_profile: str = Field(default="", description="공간 크기/조건")
    desired_item_count: int = Field(default=3, ge=1, le=5)


class BusinessItemRecommendation(BaseModel):
    item_name: str
    fit_score: int = Field(..., ge=0, le=100)
    target_customer: str
    summary: str
    reasons: list[str]
    execution_tips: list[str]


class BusinessItemRecommendationResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": BUSINESS_ITEM_RECOMMENDATION_RESPONSE_EXAMPLE})

    area_summary: str
    recommended_items: list[BusinessItemRecommendation]


class MarketingAutomationRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": MARKETING_AUTOMATION_REQUEST_EXAMPLE})

    business_item: str
    business_description: str = ""
    region: str
    target_audience: str = ""
    tone: str = Field(default="친근하고 전문적인")
    promotion_goal: str = Field(default="방문 유도")
    channels: list[Literal["instagram", "blog", "flyer", "notice", "sms"]] = Field(
        default_factory=lambda: ["instagram", "blog", "flyer"]
    )
    differentiators: list[str] = Field(default_factory=list)
    festival_context: str = ""
    call_to_action: str = Field(default="지금 방문해 보세요")


class MarketingChannelContent(BaseModel):
    channel: str
    headline: str
    primary_copy: str
    bullet_points: list[str]
    hashtags: list[str]


class MarketingAutomationResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": MARKETING_AUTOMATION_RESPONSE_EXAMPLE})

    campaign_summary: str
    target_hook: str
    recommended_schedule: list[str]
    contents: list[MarketingChannelContent]


class HealthResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": HEALTH_RESPONSE_EXAMPLE})

    status: str
    model: str
