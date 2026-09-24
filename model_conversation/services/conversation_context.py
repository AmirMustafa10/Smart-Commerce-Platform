from model_conversation.models import ChatMessage, Conversation

DEFAULT_RECENT_MESSAGES_LIMIT = 10


def build_conversation_context(
    conversation: Conversation,
    before_message_id: int,
    recent_limit: int = DEFAULT_RECENT_MESSAGES_LIMIT,
) -> dict:
    """
    Build the conversational context needed by the final AI response.

    The context contains:
    - Long-term conversation summary.
    - Recent messages before the current pending messages.

    The current user message is intentionally not queried here because
    it is already available to the task processing the conversation.
    """

    recent_messages = ChatMessage.objects.filter(
        conversation=conversation,
        id__lt=before_message_id,
    ).order_by("-id")[:recent_limit]

    recent_messages = list(reversed(recent_messages))

    formatted_messages = []

    for message in recent_messages:
        role = "Customer" if message.sender == "user" else "Assistant"

        formatted_messages.append(
            {
                "role": role,
                "text": message.text,
            }
        )

    return {
        "summary": conversation.summary or "",
        "recent_messages": formatted_messages,
    }
