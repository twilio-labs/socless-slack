import uuid, os
from slack_helpers import slack_client, find_user, get_channel_id
from socless import (
    socless_bootstrap,
    socless_dispatch_outbound_message,
    socless_template_string,
    init_human_interaction,
)
from socless.utils import gen_id

TARGET_TYPE_PREFIX = {"channel": "#", "user": "@"}

SLACK_SLASH_COMMAND = os.environ.get("SLACK_SLASH_COMMAND", "")


def handle_state(
    context,
    target,
    target_type,
    message_template,
    receiver="",
    response_desc="[response]",
):
    """Send a Slack Message and store the message id for the message
    """

    if not message_template:
        raise Exception("No text was supplied to Slack message")

    USE_NEW_INTERACTION = "task_token" in context

    message_id = gen_id(6)

    context["_message_id"] = message_id
    extended_template = f"{message_template}\n```{SLACK_SLASH_COMMAND} {context['_message_id']} {response_desc}```\n"
    message = socless_template_string(extended_template, context)
    target_id = get_channel_id(target, target_type)

    if USE_NEW_INTERACTION:
        init_human_interaction(context, message, message_id)

    r = slack_client.chat_postMessage(channel=target_id, text=message, as_user=True)

    if not r.data["ok"]:
        raise Exception(
            f"Human Reponse workflow failed to initiate because slack_client failed to send message: {r.data}"
        )

    if not USE_NEW_INTERACTION:
        investigation_id = context["artifacts"]["event"]["investigation_id"]
        execution_id = context.get("execution_id")
        socless_dispatch_outbound_message(
            receiver, message_id, investigation_id, execution_id, message
        )

    return {"response": r.data, "message_id": message_id, "slack_id": target_id}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state, include_event=True)
