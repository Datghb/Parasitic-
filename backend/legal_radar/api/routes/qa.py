from fastapi import APIRouter, Depends

from backend.legal_radar.api.rate_limit import enforce_qa_rate_limit
from backend.legal_radar.pipeline import analyze_comment
from backend.legal_radar.api.schemas import QuestionRequest, QueueItemResponse

router = APIRouter(tags=["qa"])


@router.post(
    "/qa",
    response_model=QueueItemResponse,
    dependencies=[Depends(enforce_qa_rate_limit)],
)
def ask_question(request: QuestionRequest) -> QueueItemResponse:
    return QueueItemResponse.model_validate(analyze_comment(request.question), from_attributes=True)
