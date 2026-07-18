from fastapi import APIRouter

from ..data_access import list_queue_items
from ..schemas import QueueItemResponse

router = APIRouter(tags=["queue"])


@router.get("/queue", response_model=list[QueueItemResponse])
def list_queue() -> list[QueueItemResponse]:
    return [QueueItemResponse.model_validate(item) for item in list_queue_items()]


@router.delete("/queue")
def clear_queue() -> dict[str, object]:
    from ..dependencies import runs_dir
    queue_path = runs_dir() / "queue.jsonl"
    deleted = 0
    if queue_path.exists():
        from ..data_access import _queue_from_jsonl
        deleted = len(_queue_from_jsonl(queue_path))
        queue_path.unlink()
    return {"deleted": deleted, "message": f"Đã xóa {deleted} hồ sơ khỏi hàng đợi."}
