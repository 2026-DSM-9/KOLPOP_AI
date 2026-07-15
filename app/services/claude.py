import json
from dataclasses import dataclass
from typing import Optional

import httpx

from app.config import settings
from app.schemas import (
    BusinessItemRecommendationRequest,
    BusinessItemRecommendationResponse,
    ChatBusinessItemRecommendationRequest,
    ChatBusinessItemRecommendationResponse,
    ChatListingRecommendationRequest,
    ChatListingRecommendationResponse,
    ChatMarketingRequest,
    ChatMarketingResponse,
    ListingRecommendationRequest,
    ListingRecommendationResponse,
    ListingCandidate,
    MarketingAutomationRequest,
    MarketingAutomationResponse,
    RegionRecommendationRequest,
    RegionRecommendationResponse,
)


class ClaudeServiceError(RuntimeError):
    pass


@dataclass
class ClaudeMessageResult:
    text: str


class ClaudeRecommendationService:
    def __init__(self) -> None:
        self.api_url = "https://api.anthropic.com/v1/messages"

    async def recommend_listings(self, payload: ListingRecommendationRequest) -> ListingRecommendationResponse:
        input_warning = self._build_listing_input_warning_response(payload)
        if input_warning is not None:
            return input_warning

        response_schema = {
            "assistant_message": "사용자에게 보여줄 자연스러운 한국어 답변. 추천 결과를 1~3문장으로 안내",
            "region_analysis": "지역 특성과 수요를 요약한 문자열",
            "recommended_listings": [
                {
                    "listing_id": "listing-001",
                    "title": "추천 매물명",
                    "fit_score": 91,
                    "summary": "이 매물이 왜 맞는지 한 줄 요약",
                    "match_reasons": ["추천 이유 1", "추천 이유 2"],
                    "caution_points": ["주의 포인트 1", "주의 포인트 2"],
                }
            ],
            "reason_if_none": None,
        }

        prompt = self._build_prompt(
            task_name="지역 특성 기반 매물 추천",
            task_description=(
                "입력된 사업 아이템, 타깃 고객, 지역 특성, 유동인구, 축제 정보, 후보 매물 목록을 함께 보고 "
                f"가장 적합한 매물을 1개 이상 {payload.desired_count}개 이하로 선별해 주세요. "
                "반드시 지역 특성을 먼저 분석한 뒤 후보 매물 각각을 비교 평가해야 합니다. "
                "예산, 운영 기간, 시설, 업종 제한, 주변 상권 적합성을 모두 반영해 주세요. "
                "적합한 매물이 1개도 없으면 recommended_listings를 null로 반환하고, "
                "reason_if_none에 왜 추천하지 않는지 구체적으로 작성하세요. "
                "recommended_listings에는 입력된 후보 매물의 listing_id만 사용할 수 있습니다. "
                "현재 사용자 메시지와 최근 대화가 있다면 그 맥락을 반영하고, assistant_message에는 "
                "사용자가 읽기 편한 친근한 답변을 1~3문장으로 작성하세요. "
                "매물이 있으면 추천 개수와 핵심 이유를, 없으면 조건에 맞는 매물이 없다는 점과 이유를 안내하세요. "
                "억지 추천은 금지합니다."
            ),
            request_data=payload.model_dump(mode="json"),
            response_schema=response_schema,
        )

        data = await self._request_json(prompt)
        response = ListingRecommendationResponse.model_validate(data)
        return self._normalize_listing_recommendations(payload, response)

    async def chat_recommend_listings(
        self, payload: ChatListingRecommendationRequest
    ) -> ChatListingRecommendationResponse:
        input_warning = self._build_chat_listing_input_warning_response(payload)
        if input_warning is not None:
            return input_warning

        response_schema = {
            "assistant_message": "사용자에게 보여줄 자연스러운 한국어 답변. 추천 결과 또는 추가 질문을 1~3문장으로 안내",
            "recommended_listings": [
                {
                    "listing_id": "listing-001",
                    "title": "추천 매물명",
                    "fit_score": 91,
                    "summary": "이 매물이 왜 맞는지 한 줄 요약",
                    "match_reasons": ["추천 이유 1", "추천 이유 2"],
                    "caution_points": ["주의 포인트 1", "주의 포인트 2"],
                }
            ],
            "reason_if_none": None,
        }

        prompt = self._build_prompt(
            task_name="자연어 기반 매물 추천",
            task_description=(
                "프론트에서 전달한 사용자 message와 전체 매물 목록을 보고 가장 적합한 공간을 추천해 주세요. "
                "message 안에 들어 있는 지역, 업종, 예산, 운영 방식, 시설 선호, 기간, 톤 등의 의미는 모두 스스로 해석해야 합니다. "
                "추천할 때는 전체 매물 중 최대 3개만 고르고, 추천 이유와 주의점을 함께 작성하세요. "
                "recommended_listings에는 입력으로 받은 listings 안의 listing_id만 사용할 수 있고, 존재하지 않는 매물은 절대 만들면 안 됩니다. "
                "사용자 의도가 어느 정도 파악되면 일부 정보가 부족해도 합리적으로 추론해 추천할 수 있습니다. "
                "다만 추천 근거가 너무 약하거나 비교에 필요한 정보가 부족하면 422처럼 실패하지 말고 assistant_message로 짧게 되물어 주세요. "
                "이 경우 recommended_listings는 null로, reason_if_none에는 어떤 정보가 더 필요하거나 왜 지금은 추천이 어려운지 구체적으로 작성하세요. "
                "조건에 맞는 공간이 실제로 없다면 억지 추천하지 말고 recommended_listings를 null로 반환하세요."
            ),
            request_data=payload.model_dump(mode="json"),
            response_schema=response_schema,
        )

        data = await self._request_json(prompt)
        response = ChatListingRecommendationResponse.model_validate(data)
        return self._normalize_chat_listing_recommendations(payload, response)

    def _build_listing_input_warning_response(
        self, payload: ListingRecommendationRequest
    ) -> Optional[ListingRecommendationResponse]:
        missing_fields: list[str] = []

        if not payload.user_message.strip() and not payload.conversation_history:
            missing_fields.append("사용자 요청 메시지")
        if not payload.business_item.strip():
            missing_fields.append("사업 아이템명")
        if not payload.desired_region.strip():
            missing_fields.append("희망 지역")
        if not payload.business_description.strip() and not payload.target_audience.strip():
            missing_fields.append("사업 설명 또는 타깃 고객 정보")
        if (
            not payload.region_summary.strip()
            and not payload.foot_traffic_profile.strip()
            and not payload.nearby_businesses
            and not payload.region_strengths
            and not payload.region_risks
            and not payload.festival_info
        ):
            missing_fields.append("지역 특성 정보")
        if (
            payload.budget_limit_per_day is None
            and payload.budget_limit_deposit is None
            and not payload.desired_popup_duration.strip()
        ):
            missing_fields.append("예산 또는 운영 기간 정보")
        if all(self._is_listing_too_sparse(candidate) for candidate in payload.listings):
            missing_fields.append("후보 매물 상세 정보")

        if not missing_fields:
            return None

        formatted_fields = ", ".join(missing_fields)
        return ListingRecommendationResponse(
            assistant_message=(
                "추천 정확도를 높이려면 몇 가지 정보가 더 필요해요. "
                f"{formatted_fields}를 조금 더 정확하게 입력해 주시면 다시 바로 추천해드릴게요."
            ),
            region_analysis="입력된 정보가 충분하지 않아 지역 특성과 후보 매물을 안정적으로 비교하기 어려운 상태입니다.",
            recommended_listings=None,
            reason_if_none=(
                f"현재 요청에는 {formatted_fields}가 부족합니다. "
                "사업 설명, 타깃 고객, 지역 특성, 예산, 운영 기간과 함께 매물의 주소, 가격, 면적, 시설 같은 상세 정보를 보내주시면 더 정확하게 추천해드릴 수 있어요."
            ),
        )

    def _build_chat_listing_input_warning_response(
        self, payload: ChatListingRecommendationRequest
    ) -> Optional[ChatListingRecommendationResponse]:
        if not payload.message.strip():
            return ChatListingRecommendationResponse(
                assistant_message="어떤 팝업을 하고 싶은지 한 문장으로 알려주시면, 전체 매물 중에서 맞는 공간을 골라드릴게요.",
                recommended_listings=None,
                reason_if_none="사용자 message가 비어 있어 업종, 지역, 예산, 운영 목적을 해석할 수 없습니다.",
            )

        if not payload.listings:
            return ChatListingRecommendationResponse(
                assistant_message="추천은 가능하지만 지금은 비교할 매물 목록이 없어요. 모집 중인 매물 요약본을 함께 보내주시면 바로 골라드릴게요.",
                recommended_listings=None,
                reason_if_none="비교 대상이 되는 listings 데이터가 없어 추천 결과를 만들 수 없습니다.",
            )

        if all(self._is_listing_too_sparse(candidate) for candidate in payload.listings):
            return ChatListingRecommendationResponse(
                assistant_message="매물은 받았지만 비교에 필요한 정보가 조금 더 있으면 정확도가 훨씬 좋아져요. 주소, 가격, 면적, 시설 같은 요약 정보를 더 보내주실 수 있을까요?",
                recommended_listings=None,
                reason_if_none="모든 매물 정보가 매우 간략해 공간 적합도를 안정적으로 비교하기 어렵습니다.",
            )

        return None

    def _is_listing_too_sparse(self, candidate: ListingCandidate) -> bool:
        detail_count = 0

        if candidate.address.strip() or candidate.detail_address.strip():
            detail_count += 1
        if candidate.price_per_day is not None or candidate.deposit is not None:
            detail_count += 1
        if candidate.area_sqm is not None:
            detail_count += 1
        if candidate.summary.strip():
            detail_count += 1
        if candidate.facilities:
            detail_count += 1
        if candidate.available_from.strip() or candidate.available_to.strip():
            detail_count += 1

        return detail_count < 2

    def _normalize_listing_recommendations(
        self,
        payload: ListingRecommendationRequest,
        response: ListingRecommendationResponse,
    ) -> ListingRecommendationResponse:
        recommendations = response.recommended_listings

        if recommendations is None:
            if not response.reason_if_none:
                raise ClaudeServiceError("추천 매물이 없지만 reason_if_none이 반환되지 않았습니다.")
            return response

        candidates_by_id = {candidate.listing_id: candidate for candidate in payload.listings}
        seen_ids: set[str] = set()
        normalized = []

        for item in recommendations[: payload.desired_count]:
            candidate = candidates_by_id.get(item.listing_id)
            if candidate is None:
                raise ClaudeServiceError(f"후보 목록에 없는 매물이 반환되었습니다: {item.listing_id}")
            if item.listing_id in seen_ids:
                continue

            seen_ids.add(item.listing_id)
            normalized.append(item.model_copy(update={"title": candidate.title}))

        if not normalized:
            raise ClaudeServiceError("유효한 추천 매물이 반환되지 않았습니다.")

        return response.model_copy(
            update={
                "recommended_listings": normalized,
                "reason_if_none": None,
            }
        )

    def _normalize_chat_listing_recommendations(
        self,
        payload: ChatListingRecommendationRequest,
        response: ChatListingRecommendationResponse,
    ) -> ChatListingRecommendationResponse:
        recommendations = response.recommended_listings

        if recommendations is None:
            return response

        candidates_by_id = {candidate.listing_id: candidate for candidate in payload.listings}
        seen_ids: set[str] = set()
        normalized = []

        for item in recommendations[:3]:
            candidate = candidates_by_id.get(item.listing_id)
            if candidate is None:
                raise ClaudeServiceError(f"후보 목록에 없는 매물이 반환되었습니다: {item.listing_id}")
            if item.listing_id in seen_ids:
                continue

            seen_ids.add(item.listing_id)
            normalized.append(item.model_copy(update={"title": candidate.title}))

        if not normalized:
            raise ClaudeServiceError("유효한 추천 매물이 반환되지 않았습니다.")

        return response.model_copy(
            update={
                "recommended_listings": normalized,
                "reason_if_none": None,
            }
        )

    async def recommend_regions(self, payload: RegionRecommendationRequest) -> RegionRecommendationResponse:
        response_schema = {
            "analysis_summary": "전체 분석 요약 문자열",
            "recommended_regions": [
                {
                    "region": "추천 지역명",
                    "score": 92,
                    "summary": "한 줄 요약",
                    "reasons": ["추천 이유 1", "추천 이유 2"],
                    "recommended_strategy": ["운영 전략 1", "운영 전략 2"],
                    "caution_points": ["주의 포인트 1", "주의 포인트 2"],
                }
            ],
        }

        prompt = self._build_prompt(
            task_name="사업 아이템 기반 지역 추천",
            task_description=(
                "청년 창업자의 사업 아이템과 타깃 고객, 예산, 팝업 기간, 축제 정보를 보고 "
                "국내 로컬 상권 중 적합한 지역을 우선순위로 추천해 주세요. "
                "특히 골목상권 활성화와 단기 팝업 적합성을 중요하게 평가해 주세요."
            ),
            request_data=payload.model_dump(mode="json"),
            response_schema=response_schema,
        )

        data = await self._request_json(prompt)
        return RegionRecommendationResponse.model_validate(data)

    async def recommend_business_items(
        self, payload: BusinessItemRecommendationRequest
    ) -> BusinessItemRecommendationResponse:
        response_schema = {
            "area_summary": "상권 요약 문자열",
            "recommended_items": [
                {
                    "item_name": "추천 사업 아이템",
                    "fit_score": 88,
                    "target_customer": "핵심 고객층",
                    "summary": "한 줄 요약",
                    "reasons": ["추천 이유 1", "추천 이유 2"],
                    "execution_tips": ["실행 팁 1", "실행 팁 2"],
                }
            ],
        }

        prompt = self._build_prompt(
            task_name="상권 기반 사업 아이템 추천",
            task_description=(
                "선택된 상권의 유동인구, 주변 업종, 축제 정보, 공간 특성을 바탕으로 "
                "가장 잘 맞는 팝업/사업 아이템을 추천해 주세요. "
                "짧은 운영 기간 안에 반응을 보기 좋은 아이템을 우선 고려해 주세요."
            ),
            request_data=payload.model_dump(mode="json"),
            response_schema=response_schema,
        )

        data = await self._request_json(prompt)
        return BusinessItemRecommendationResponse.model_validate(data)

    async def chat_recommend_business_items(
        self, payload: ChatBusinessItemRecommendationRequest
    ) -> ChatBusinessItemRecommendationResponse:
        if not payload.message.strip():
            return ChatBusinessItemRecommendationResponse(
                assistant_message="어느 지역이나 상권을 생각하고 있는지 한 문장으로 알려주시면, 그 분위기에 맞는 팝업 아이템을 추천해드릴게요.",
                recommended_items=None,
            )

        response_schema = {
            "assistant_message": "사용자에게 보여줄 자연스러운 한국어 답변. 추천 결과 또는 추가 질문을 1~3문장으로 안내",
            "recommended_items": [
                {
                    "item_name": "추천 사업 아이템",
                    "fit_score": 89,
                    "summary": "연남 상권 특성과 잘 맞는 아이템입니다.",
                    "reasons": ["추천 이유 1", "추천 이유 2"],
                    "execution_tips": ["실행 팁 1", "실행 팁 2"],
                }
            ],
        }

        prompt = self._build_prompt(
            task_name="자연어 기반 상권별 창업 아이템 추천",
            task_description=(
                "사용자 message만 보고 지역 또는 상권, 업종 선호, 예산 뉘앙스, 운영 목적을 해석한 뒤 그 지역에 잘 맞는 팝업 또는 창업 아이템을 추천해 주세요. "
                "핵심은 상권 분위기, 유입 동선, 체류 성격, SNS 확산 가능성, 충동구매 적합도를 함께 고려하는 것입니다. "
                "message에 지역이 비교적 명확하면 1~5개의 아이템을 추천하고, 각 아이템마다 이유와 실행 팁을 적어 주세요. "
                "지역이나 상권이 불명확해 유의미한 추천이 어렵다면 422처럼 실패하지 말고 assistant_message로 짧게 되물어 주세요. "
                "이 경우 recommended_items는 null로 반환하세요. "
                "정보가 조금 부족해도 일반적인 상권 특성을 바탕으로 추론 가능한 범위에서는 먼저 추천해도 됩니다."
            ),
            request_data=payload.model_dump(mode="json"),
            response_schema=response_schema,
        )

        data = await self._request_json(prompt)
        return ChatBusinessItemRecommendationResponse.model_validate(data)

    async def generate_marketing_plan(self, payload: MarketingAutomationRequest) -> MarketingAutomationResponse:
        response_schema = {
            "campaign_summary": "캠페인 요약 문자열",
            "target_hook": "핵심 소구 포인트",
            "recommended_schedule": ["일정 제안 1", "일정 제안 2"],
            "contents": [
                {
                    "channel": "instagram",
                    "headline": "채널용 헤드라인",
                    "primary_copy": "채널 본문",
                    "bullet_points": ["포인트 1", "포인트 2"],
                    "hashtags": ["태그1", "태그2"],
                }
            ],
        }

        prompt = self._build_prompt(
            task_name="소상공인 마케팅 자동화",
            task_description=(
                "사업 아이템, 지역, 타깃 고객, 홍보 목적을 바탕으로 채널별 마케팅 문구를 생성해 주세요. "
                "로컬 팝업 특성에 맞는 문체와 후킹 포인트, 해시태그를 함께 제안해 주세요."
            ),
            request_data=payload.model_dump(mode="json"),
            response_schema=response_schema,
        )

        data = await self._request_json(prompt)
        return MarketingAutomationResponse.model_validate(data)

    async def generate_chat_marketing_plan(self, payload: ChatMarketingRequest) -> ChatMarketingResponse:
        if not payload.message.strip():
            return ChatMarketingResponse(
                assistant_message="홍보할 상품이나 팝업, 그리고 가능하면 지역까지 한 문장으로 알려주시면 바로 마케팅 문구를 만들어드릴게요.",
                campaign_summary=None,
                target_hook=None,
                recommended_schedule=[],
                contents=[],
            )

        response_schema = {
            "assistant_message": "사용자에게 보여줄 자연스러운 한국어 답변. 결과 안내 또는 추가 질문을 1~3문장으로 작성",
            "campaign_summary": "캠페인 요약 문자열 또는 정보 부족 시 null",
            "target_hook": "핵심 소구 포인트 또는 정보 부족 시 null",
            "recommended_schedule": ["일정 제안 1", "일정 제안 2"],
            "contents": [
                {
                    "channel": "instagram",
                    "headline": "채널용 헤드라인",
                    "primary_copy": "채널 본문",
                    "bullet_points": ["포인트 1", "포인트 2"],
                    "hashtags": ["태그1", "태그2"],
                }
            ],
        }

        prompt = self._build_prompt(
            task_name="자연어 기반 마케팅 문구 생성",
            task_description=(
                "사용자 message 한 문장만 보고 상품, 지역, 톤앤매너, 타깃 고객, 목적을 해석해서 바로 쓸 수 있는 마케팅 초안을 만들어 주세요. "
                "assistant_message에는 무엇을 준비했는지 자연스럽게 안내하고, campaign_summary에는 전체 캠페인 방향을 요약하세요. "
                "target_hook에는 한 줄 핵심 소구 포인트를 작성하고, recommended_schedule에는 오픈 전후 운영 일정을 2~6개 제안하세요. "
                "contents에는 채널별 문구를 1~4개 제안하되 headline, primary_copy, bullet_points, hashtags를 모두 채워 주세요. "
                "정보가 조금 부족해도 일반적인 팝업 홍보 전제를 두고 먼저 초안을 만들어도 됩니다. "
                "다만 상품 또는 지역 또는 홍보 목적이 거의 드러나지 않아 유의미한 초안이 어렵다면 422처럼 실패하지 말고 assistant_message로 짧게 되물어 주세요. "
                "이 경우 campaign_summary와 target_hook은 null로, recommended_schedule과 contents는 빈 배열로 반환하세요."
            ),
            request_data=payload.model_dump(mode="json"),
            response_schema=response_schema,
        )

        data = await self._request_json(prompt)
        return ChatMarketingResponse.model_validate(data)

    async def _request_json(self, prompt: str) -> dict:
        result = await self._send_message(prompt)
        return self._parse_json_text(result.text)

    async def _send_message(self, prompt: str) -> ClaudeMessageResult:
        if not settings.anthropic_api_key:
            raise ClaudeServiceError("ANTHROPIC_API_KEY 또는 CLAUDE_API_KEY가 설정되지 않았습니다.")
        if not settings.claude_model:
            raise ClaudeServiceError("CLAUDE_MODEL이 설정되지 않았습니다.")

        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": settings.claude_model,
            "max_tokens": settings.claude_max_tokens,
            "temperature": settings.claude_temperature,
            "system": (
                "당신은 한국 로컬 상권, 팝업스토어, 청년 창업 지원에 특화된 AI 비서입니다. "
                "모든 답변은 반드시 한국어 JSON만 반환해야 하며, 마크다운이나 설명 문장을 절대 추가하지 마세요."
            ),
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ClaudeServiceError(f"Claude API 요청이 실패했습니다: {exc.response.text}") from exc
        except httpx.HTTPError as exc:
            raise ClaudeServiceError(f"Claude API 연결에 실패했습니다: {exc}") from exc

        body = response.json()
        text_blocks = [block.get("text", "") for block in body.get("content", []) if block.get("type") == "text"]
        text = "\n".join(part for part in text_blocks if part).strip()

        if not text:
            raise ClaudeServiceError("Claude 응답에서 텍스트를 찾지 못했습니다.")

        return ClaudeMessageResult(text=text)

    def _build_prompt(self, task_name: str, task_description: str, request_data: dict, response_schema: dict) -> str:
        return (
            f"작업명: {task_name}\n"
            f"작업 설명: {task_description}\n\n"
            "입력 데이터(JSON):\n"
            f"{json.dumps(request_data, ensure_ascii=False, indent=2)}\n\n"
            "반드시 아래 구조의 JSON만 반환하세요. 설명 문장, 코드블록, 마크다운은 금지합니다.\n"
            f"{json.dumps(response_schema, ensure_ascii=False, indent=2)}"
        )

    def _parse_json_text(self, text: str) -> dict:
        candidate = text.strip()

        if candidate.startswith("```"):
            candidate = candidate.strip("`")
            candidate = candidate.replace("json", "", 1).strip()

        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            start = candidate.find("{")
            end = candidate.rfind("}")
            if start == -1 or end == -1:
                raise ClaudeServiceError("Claude 응답에서 JSON 본문을 찾지 못했습니다.")

            try:
                return json.loads(candidate[start : end + 1])
            except json.JSONDecodeError as exc:
                raise ClaudeServiceError(f"Claude JSON 파싱에 실패했습니다: {exc}") from exc
