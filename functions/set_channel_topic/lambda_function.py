from socless import *
import slack
import os

def handle_state(channel_id, topic):
    """
    Set topic for a channel
    Args:
        channel_id(str): channel_id for the targeted channel
        topic(str): topic to set to channel
    """
    topic = topic or ""
    SOCLESS_USER_TOKEN = os.environ['SOCLESS_USER_TOKEN']
    slack_api_client = slack.WebClient(SOCLESS_USER_TOKEN)
    res = slack_api_client.conversations_setTopic(channel=channel_id, topic=topic)
    if not res["ok"]:
        slack_api_client.error("Failed to update topic for channel '%s" % channel_id)
        slack_api_client.chat_postMessage(
            channel=channel_id,
            text="Failed to update topic for channel '%s" % channel_id,
            as_user=True
        )
        return {"ok", False}
    return {"ok": True}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)








