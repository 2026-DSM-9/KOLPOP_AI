from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.config import settings
from app.schemas import (
    BUSINESS_ITEM_RECOMMENDATION_REQUEST_EXAMPLE,
    BUSINESS_ITEM_RECOMMENDATION_RESPONSE_EXAMPLE,
    CHAT_BUSINESS_ITEM_REQUEST_EXAMPLE,
    CHAT_BUSINESS_ITEM_RESPONSE_EXAMPLE,
    CHAT_LISTING_RECOMMENDATION_REQUEST_EXAMPLE,
    CHAT_LISTING_RECOMMENDATION_RESPONSE_EXAMPLE,
    CHAT_MARKETING_REQUEST_EXAMPLE,
    CHAT_MARKETING_RESPONSE_EXAMPLE,
    BusinessItemRecommendationRequest,
    BusinessItemRecommendationResponse,
    ChatBusinessItemRecommendationRequest,
    ChatBusinessItemRecommendationResponse,
    ChatListingRecommendationRequest,
    ChatListingRecommendationResponse,
    ChatMarketingRequest,
    ChatMarketingResponse,
    HealthResponse,
    HEALTH_RESPONSE_EXAMPLE,
    LISTING_INPUT_WARNING_RESPONSE_EXAMPLE,
    LISTING_RECOMMENDATION_REQUEST_EXAMPLE,
    LISTING_RECOMMENDATION_RESPONSE_EXAMPLE,
    MARKETING_AUTOMATION_REQUEST_EXAMPLE,
    MARKETING_AUTOMATION_RESPONSE_EXAMPLE,
    REGION_RECOMMENDATION_REQUEST_EXAMPLE,
    REGION_RECOMMENDATION_RESPONSE_EXAMPLE,
    ListingRecommendationRequest,
    ListingRecommendationResponse,
    MarketingAutomationRequest,
    MarketingAutomationResponse,
    RegionRecommendationRequest,
    RegionRecommendationResponse,
)
from app.services.claude import ClaudeRecommendationService, ClaudeServiceError


APP_DESCRIPTION = """
KOLPOP AI API는 로컬 상권 팝업 플랫폼을 위한 Claude 기반 추천/마케팅 백엔드입니다.

- 채팅형 매물 추천
- 채팅형 창업 아이템 추천
- 채팅형 마케팅 문구 생성
- 사업 아이템 기반 지역 추천
- 상권 기반 팝업 아이템 추천
- 채널별 마케팅 문구 자동 생성

실제 추천 결과는 Claude 응답에 따라 달라지며, 502 오류가 발생하면 API 키, 모델명, 외부 네트워크 연결 상태를 함께 확인해 주세요.
""".strip()

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "서버 상태와 현재 설정된 Claude 모델명을 확인합니다.",
    },
    {
        "name": "chat",
        "description": "프론트 채팅 UI에서 사용하는 message 중심 추천/마케팅 API입니다.",
    },
    {
        "name": "recommendation",
        "description": "매물, 지역, 사업 아이템 추천 관련 API입니다.",
    },
    {
        "name": "marketing",
        "description": "로컬 팝업 홍보용 마케팅 문구와 운영 일정을 생성합니다.",
    },
]

UPSTREAM_ERROR_EXAMPLE = {
    "detail": 'Claude API 요청이 실패했습니다: {"type":"error","error":{"type":"not_found_error","message":"model: claude-sonnet-4-20250514"}}'
}


app = FastAPI(
    title="KOLPOP AI API",
    version="0.1.0",
    description=APP_DESCRIPTION,
    openapi_tags=OPENAPI_TAGS,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = ClaudeRecommendationService()


@app.get("/", include_in_schema=False)
async def docs_redirect() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="헬스 체크",
    description="서버가 정상 기동 중인지와 현재 설정된 Claude 모델명을 반환합니다.",
    responses={
        200: {
            "description": "서버 상태 확인 성공",
            "content": {"application/json": {"example": HEALTH_RESPONSE_EXAMPLE}},
        }
    },
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", model=settings.claude_model)


@app.post(
    "/api/v1/recommend/listings/",
    response_model=ListingRecommendationResponse,
    tags=["recommendation"],
    include_in_schema=False,
)
@app.post(
    "/api/v1/recommend/listings",
    response_model=ListingRecommendationResponse,
    tags=["recommendation"],
    summary="일반 매물 추천",
    description=(
        "사업 아이템, 지역 특성, 예산, 후보 매물 목록을 바탕으로 1~3개의 추천 매물을 반환합니다. "
        "후보 목록에 없는 listing_id는 응답으로 허용되지 않습니다."
    ),
    responses={
        200: {
            "description": "매물 추천 성공",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "추천 성공 예시",
                            "value": LISTING_RECOMMENDATION_RESPONSE_EXAMPLE,
                        },
                        "warning": {
                            "summary": "입력 정보가 부족한 경우 안내 예시",
                            "value": LISTING_INPUT_WARNING_RESPONSE_EXAMPLE,
                        },
                    }
                }
            },
        },
        502: {
            "description": "Claude API 호출 실패 또는 모델/키 설정 오류",
            "content": {"application/json": {"example": UPSTREAM_ERROR_EXAMPLE}},
        },
    },
)
async def recommend_listings(
    payload: ListingRecommendationRequest = Body(
        ...,
        description="사용자 메시지, 지역 특성, 예산, 후보 매물 목록을 포함한 추천 요청 데이터",
        openapi_examples={
            "basic": {
                "summary": "비건 디저트 팝업 매물 추천 예시",
                "value": LISTING_RECOMMENDATION_REQUEST_EXAMPLE,
            }
        },
    )
) -> ListingRecommendationResponse:
    try:
        return await service.recommend_listings(payload)
    except ClaudeServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post(
    "/api/v1/chat/listings/",
    response_model=ChatListingRecommendationResponse,
    tags=["chat"],
    include_in_schema=False,
)
@app.post(
    "/api/v1/chat/listings",
    response_model=ChatListingRecommendationResponse,
    tags=["chat"],
    summary="채팅형 매물 추천",
    description=(
        "프론트에서 전달한 message와 전체 모집중 매물 목록만으로 Claude가 적합한 매물을 고르는 API입니다. "
        "message 안의 지역, 업종, 예산, 기간 같은 의미 해석은 AI 서버가 담당합니다."
    ),
    responses={
        200: {
            "description": "채팅형 매물 추천 성공",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "추천 성공 예시",
                            "value": CHAT_LISTING_RECOMMENDATION_RESPONSE_EXAMPLE,
                        },
                        "warning": {
                            "summary": "추가 정보 요청 예시",
                            "value": {
                                "assistant_message": "지금 정보만으로도 일부 추론은 가능하지만, 운영 예산이나 선호 시설이 있으면 더 정확하게 골라드릴 수 있어요.",
                                "recommended_listings": None,
                                "reason_if_none": "사용자 의도는 파악되지만 비교 기준이 더 있으면 추천 정확도가 높아집니다.",
                            },
                        },
                    }
                }
            },
        },
        502: {
            "description": "Claude API 호출 실패 또는 모델/키 설정 오류",
            "content": {"application/json": {"example": UPSTREAM_ERROR_EXAMPLE}},
        },
    },
)
async def chat_recommend_listings(
    payload: ChatListingRecommendationRequest = Body(
        default=ChatListingRecommendationRequest(),
        description="사용자 자연어 message와 전체 매물 목록",
        openapi_examples={
            "basic": {
                "summary": "프론트 연동용 매물 추천 예시",
                "value": CHAT_LISTING_RECOMMENDATION_REQUEST_EXAMPLE,
            }
        },
    )
) -> ChatListingRecommendationResponse:
    try:
        return await service.chat_recommend_listings(payload)
    except ClaudeServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post(
    "/api/v1/recommend/regions/",
    response_model=RegionRecommendationResponse,
    response_model_exclude_none=True,
    tags=["recommendation"],
    include_in_schema=False,
)
@app.post(
    "/api/v1/recommend/regions",
    response_model=RegionRecommendationResponse,
    response_model_exclude_none=True,
    tags=["recommendation"],
    summary="지역 추천",
    description="창업 아이템, 타깃 고객, 예산, 팝업 기간을 바탕으로 적합한 지역을 우선순위로 추천합니다.",
    responses={
        200: {
            "description": "지역 추천 성공",
            "content": {"application/json": {"example": REGION_RECOMMENDATION_RESPONSE_EXAMPLE}},
        },
        502: {
            "description": "Claude API 호출 실패 또는 모델/키 설정 오류",
            "content": {"application/json": {"example": UPSTREAM_ERROR_EXAMPLE}},
        },
    },
)
async def recommend_regions(
    payload: RegionRecommendationRequest = Body(
        ...,
        description="사업 아이템과 지역 후보 정보를 포함한 지역 추천 요청 데이터",
        openapi_examples={
            "basic": {
                "summary": "비건 디저트 팝업 지역 추천 예시",
                "value": REGION_RECOMMENDATION_REQUEST_EXAMPLE,
            }
        },
    )
) -> RegionRecommendationResponse:
    try:
        return await service.recommend_regions(payload)
    except ClaudeServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post(
    "/api/v1/recommend/business-items/",
    response_model=BusinessItemRecommendationResponse,
    response_model_exclude_none=True,
    tags=["recommendation"],
    include_in_schema=False,
)
@app.post(
    "/api/v1/recommend/business-items",
    response_model=BusinessItemRecommendationResponse,
    response_model_exclude_none=True,
    tags=["recommendation"],
    summary="상권 기반 사업 아이템 추천",
    description="선택한 상권의 분위기와 방문객 특성을 바탕으로 잘 맞는 팝업 또는 사업 아이템을 추천합니다.",
    responses={
        200: {
            "description": "사업 아이템 추천 성공",
            "content": {"application/json": {"example": BUSINESS_ITEM_RECOMMENDATION_RESPONSE_EXAMPLE}},
        },
        502: {
            "description": "Claude API 호출 실패 또는 모델/키 설정 오류",
            "content": {"application/json": {"example": UPSTREAM_ERROR_EXAMPLE}},
        },
    },
)
async def recommend_business_items(
    payload: BusinessItemRecommendationRequest = Body(
        ...,
        description="상권 정보와 방문객 특성을 포함한 사업 아이템 추천 요청 데이터",
        openapi_examples={
            "basic": {
                "summary": "연남 상권 기반 아이템 추천 예시",
                "value": BUSINESS_ITEM_RECOMMENDATION_REQUEST_EXAMPLE,
            }
        },
    ),
) -> BusinessItemRecommendationResponse:
    try:
        return await service.recommend_business_items(payload)
    except ClaudeServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post(
    "/api/v1/chat/business-items/",
    response_model=ChatBusinessItemRecommendationResponse,
    tags=["chat"],
    include_in_schema=False,
)
@app.post(
    "/api/v1/chat/business-items",
    response_model=ChatBusinessItemRecommendationResponse,
    tags=["chat"],
    summary="채팅형 창업 아이템 추천",
    description=(
        "사용자 message에서 지역 또는 상권을 해석해 그곳에 맞는 팝업/창업 아이템을 추천하는 API입니다. "
        "정보가 모자라면 422 대신 assistant_message로 추가 질문을 반환합니다."
    ),
    responses={
        200: {
            "description": "채팅형 사업 아이템 추천 성공",
            "content": {"application/json": {"example": CHAT_BUSINESS_ITEM_RESPONSE_EXAMPLE}},
        },
        502: {
            "description": "Claude API 호출 실패 또는 모델/키 설정 오류",
            "content": {"application/json": {"example": UPSTREAM_ERROR_EXAMPLE}},
        },
    },
)
async def chat_recommend_business_items(
    payload: ChatBusinessItemRecommendationRequest = Body(
        default=ChatBusinessItemRecommendationRequest(),
        description="사용자 자연어 message",
        openapi_examples={
            "basic": {
                "summary": "프론트 연동용 사업 아이템 추천 예시",
                "value": CHAT_BUSINESS_ITEM_REQUEST_EXAMPLE,
            }
        },
    ),
) -> ChatBusinessItemRecommendationResponse:
    try:
        return await service.chat_recommend_business_items(payload)
    except ClaudeServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post(
    "/api/v1/marketing/automation/",
    response_model=MarketingAutomationResponse,
    response_model_exclude_none=True,
    tags=["marketing"],
    include_in_schema=False,
)
@app.post(
    "/api/v1/marketing/automation",
    response_model=MarketingAutomationResponse,
    response_model_exclude_none=True,
    tags=["marketing"],
    summary="마케팅 자동화 문구 생성",
    description="사업 아이템, 지역, 타깃 고객, 채널 정보를 기반으로 채널별 홍보 문구와 운영 일정을 생성합니다.",
    responses={
        200: {
            "description": "마케팅 자동화 성공",
            "content": {"application/json": {"example": MARKETING_AUTOMATION_RESPONSE_EXAMPLE}},
        },
        502: {
            "description": "Claude API 호출 실패 또는 모델/키 설정 오류",
            "content": {"application/json": {"example": UPSTREAM_ERROR_EXAMPLE}},
        },
    },
)
async def marketing_automation(
    payload: MarketingAutomationRequest = Body(
        ...,
        description="홍보 목적과 채널 정보를 포함한 마케팅 자동화 요청 데이터",
        openapi_examples={
            "basic": {
                "summary": "인스타그램 중심 마케팅 문구 생성 예시",
                "value": MARKETING_AUTOMATION_REQUEST_EXAMPLE,
            }
        },
    )
) -> MarketingAutomationResponse:
    try:
        return await service.generate_marketing_plan(payload)
    except ClaudeServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post(
    "/api/v1/chat/marketing/",
    response_model=ChatMarketingResponse,
    tags=["chat"],
    include_in_schema=False,
)
@app.post(
    "/api/v1/chat/marketing",
    response_model=ChatMarketingResponse,
    tags=["chat"],
    summary="채팅형 마케팅 문구 생성",
    description=(
        "사용자 한 문장을 받아 상품, 지역, 톤, 목적을 해석하고 마케팅 문구와 채널별 카피, 운영 일정을 생성합니다."
    ),
    responses={
        200: {
            "description": "채팅형 마케팅 초안 생성 성공",
            "content": {"application/json": {"example": CHAT_MARKETING_RESPONSE_EXAMPLE}},
        },
        502: {
            "description": "Claude API 호출 실패 또는 모델/키 설정 오류",
            "content": {"application/json": {"example": UPSTREAM_ERROR_EXAMPLE}},
        },
    },
)
async def chat_marketing(
    payload: ChatMarketingRequest = Body(
        default=ChatMarketingRequest(),
        description="사용자 자연어 message",
        openapi_examples={
            "basic": {
                "summary": "프론트 연동용 마케팅 생성 예시",
                "value": CHAT_MARKETING_REQUEST_EXAMPLE,
            }
        },
    )
) -> ChatMarketingResponse:
    try:
        return await service.generate_chat_marketing_plan(payload)
    except ClaudeServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
