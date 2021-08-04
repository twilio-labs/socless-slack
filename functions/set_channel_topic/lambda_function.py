from socless import socless_bootstrap
from slack_helpers import SlackHelper


def handle_state(channel_id, topic: str, token=""):
    """Set topic for a channel.
    Args:
        channel_id(str): channel_id for the targeted channel
        topic(str): topic to set to channel

    Returns:
        ok : (bool) True if topic was changed
    """
    helper = SlackHelper(token)

    _ = helper.client.conversations_setTopic(channel=channel_id, topic=topic)

    return {"ok": True, "topic": topic}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
