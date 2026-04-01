from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from crewai.flow import Flow, start, human_feedback, HumanFeedbackProvider, HumanFeedbackPending, PendingFeedbackContext
from src.Crew_flow.main_crew import LinkedInPostGenerator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# 🔹 Request models
# ─────────────────────────────────────────────
class GenerateRequest(BaseModel):
    topic: str

class FeedbackRequest(BaseModel):
    feedback: str


# ─────────────────────────────────────────────
# 🔹 Endpoints
# ─────────────────────────────────────────────

# 1️⃣ Start flow
@app.post("/generate")
async def generate(request: GenerateRequest):

    flow = LinkedInPostGenerator()
    result = flow.kickoff(inputs={"topic": request.topic})


    if isinstance(result, HumanFeedbackPending):
        return {
            "flow_id": result.context.flow_id,
            "content": flow.state.post_content,
            "iteration": flow.state.iteration,
        }

    raise HTTPException(status_code=500, detail="Flow did not pause as expected")


# 2️⃣ Resume with feedback
@app.post("/feedback/{flow_id}")
async def feedback(flow_id: str, request: FeedbackRequest):

    flow = LinkedInPostGenerator.from_pending(flow_id)
    result = await flow.resume_async(request.feedback)

    # Flow paused again — another revision needed
    if isinstance(result, HumanFeedbackPending):
        return {
            "flow_id": result.context.flow_id,
            "content": flow.state.post_content,
            "iteration": flow.state.iteration,
            "status": "needs_revision",
        }

    # Flow completed
    return {
        "status": "completed",
        "approved": flow.state.approved,
        "content": flow.state.post_content,
    }