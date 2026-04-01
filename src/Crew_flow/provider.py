from crewai.flow import (
    HumanFeedbackProvider,
    HumanFeedbackPending,
    PendingFeedbackContext,
)

class WebhookProvider(HumanFeedbackProvider):

    def request_feedback(self, context: PendingFeedbackContext, flow):
        
        # pause flow execution + save state + save metadata
        raise HumanFeedbackPending(
            context=context,
            callback_info={
                "webhook_url": f"http://localhost:8000/feedback/{context.flow_id}"
            }
        )