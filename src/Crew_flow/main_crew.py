from crewai import Crew, Task, LLM
from crewai.flow.flow import Flow, listen, start,router
from src.Crew_flow.state import PostState
from src.Crew_flow.config import get_llm
from src.Crew_flow.provider import WebhookProvider
from src.Linkedin_post_generator.linked_in_crew import LinkedInCrew

from crewai.flow import HumanFeedbackResult, human_feedback

import os
from dotenv import load_dotenv
load_dotenv()



MAX_ITERATIONS = 3
class LinkedInPostGenerator(Flow[PostState]):

    llm = get_llm()

    # ── Step 1: Entry point ───────────────────
    @start("retry")
    def get_topic(self):
        print(f"\n📝 Topic: {self.state.topic}\n")
        return self.state.topic

    # ── Step 2: Crew runs here ONLY ───────────
    @listen(get_topic)
    def generate_blog(self, topic):

        self.state.iteration += 1
        print(f"\n🔁 Iteration: {self.state.iteration}\n")

        result = LinkedInCrew().crew().kickoff(
            inputs={
                "topic": self.state.topic,
                "feedback": self.state.feedback  # ✅ pass feedback
            }
        )

        self.state.post_content = result.raw
        print("\n📄 Blog generated\n")

        return self.state.post_content

    # ── Step 3: HITL node ONLY ────────────────
    @listen(generate_blog)
    @human_feedback(
        message="Review the blog. Type 'approved' or provide revision feedback:",
        emit=["approved", "needs_revision"],
        llm=llm,
        default_outcome="needs_revision",
        provider=WebhookProvider(),               # ← clean, from provider.py
    )
    def review_post(self, post_content):
        return self.state.post_content


    # ✅ No @router needed!
    @listen("approved")
    def publish(self, result):
        print(result)
        self.state.approved = True
        print(f"\n✅ Published!\n")

    @listen("needs_revision")
    def on_needs_revision(self, result):
        print(result)
        self.state.feedback = result.feedback
        if self.state.iteration >= MAX_ITERATIONS:
            return "max_retry_exceeded"
        return "retry"





# (class) HumanFeedbackResult
# Result from a @human_feedback decorated method.

# This dataclass captures all information about a human feedback interaction, including the original method output, the human's feedback, and any collapsed outcome for routing purposes.

# Attributes
# output
# The original return value from the decorated method that was shown to the human for review.

# feedback
# The raw text feedback provided by the human. Empty string if no feedback was provided.

# outcome
# The collapsed outcome string when emit is specified. This is determined by the LLM based on the human's feedback. None if emit was not specified.

# timestamp
# When the feedback was received.

# method_name
# The name of the decorated method that triggered feedback.

# metadata
# Optional metadata for enterprise integrations. Can be used to pass additional context like channel, assignee, etc.

# Examples
#     @listen("approved")
#     def handle_approval(self):
#         result = self.human_feedback
#         print(f"Output: {result.output}")
#         print(f"Feedback: {result.feedback}")
#         print(f"Outcome: {result.outcome}")