from socless import socless_bootstrap
from slack_helpers import slack_client
import os


def handle_state(channel_id, topic: str):
    """Set topic for a channel.
    Args:
        channel_id(str): channel_id for the targeted channel
        topic(str): topic to set to channel

    Returns:
        ok : (bool) True if topic was changed
    """
    response = slack_client.conversations_setTopic(channel=channel_id, topic=topic)

    return {"ok": True, "topic": topic}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
