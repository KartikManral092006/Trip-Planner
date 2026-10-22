import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app import runner
from app.api.schemas import ApprovalRequest, TripRequest


router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/trips", status_code=202)
def create_trip(request: TripRequest, background_tasks: BackgroundTasks):
    thread_id = str(uuid.uuid4())
    runner.mark_running(thread_id)
    background_tasks.add_task(runner.start_trip, thread_id, request.to_trip())
    return {"thread_id": thread_id, "status": "running"}


@router.get("/trips/{thread_id}")
def get_trip(thread_id: str):
    trip = runner.get_trip(thread_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found.")
    return trip


@router.post("/trips/{thread_id}/approval", status_code=202)
def approve_trip(thread_id: str, decision: ApprovalRequest, background_tasks: BackgroundTasks):
    trip = runner.get_trip(thread_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found.")
    if trip["status"] != "waiting_for_approval":
        raise HTTPException(
            status_code=409,
            detail=f"Trip is '{trip['status']}', not waiting for approval.",
        )

    runner.mark_running(thread_id)
    background_tasks.add_task(runner.resume_trip, thread_id, decision.model_dump())
    return {"thread_id": thread_id, "status": "running"}


@router.post("/trips/{thread_id}/retry", status_code=202)
def retry_trip(thread_id: str, background_tasks: BackgroundTasks):
    trip = runner.get_trip(thread_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found.")
    if trip["status"] != "failed":
        raise HTTPException(status_code=409, detail=f"Trip is '{trip['status']}', not failed.")

    runner.mark_running(thread_id)
    background_tasks.add_task(runner.retry_trip, thread_id)
    return {"thread_id": thread_id, "status": "running"}
