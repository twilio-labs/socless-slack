import uuid, os
from slack_helpers import slack_client, resolve_slack_target, slack_post_msg_wrapper
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
    as_user=True,
):
    """Send a Slack Message and store the message id for the message.
    Args:

    Returns:

    """

    if not message_template:
        raise Exception("No text was supplied to Slack message")

    USE_NEW_INTERACTION = "task_token" in context

    message_id = gen_id(6)

    context["_message_id"] = message_id
    extended_template = "{message_template}\n```{slash_command} {context[_message_id]} {response_desc}```\n".format(
        message_template=message_template,
        slash_command=SLACK_SLASH_COMMAND,
        context=context,
        response_desc=response_desc,
    )
    message = socless_template_string(extended_template, context)
    target_id = resolve_slack_target(target, target_type)

    if USE_NEW_INTERACTION:
        init_human_interaction(context, message, message_id)

    resp = slack_post_msg_wrapper(target, target_type, text=message, as_user=as_user)

    if not USE_NEW_INTERACTION:
        investigation_id = context["artifacts"]["event"]["investigation_id"]
        execution_id = context.get("execution_id")
        socless_dispatch_outbound_message(
            receiver, message_id, investigation_id, execution_id, message
        )

    return {
        "response": resp.data,
        # "response": r.data,
        "message_id": message_id,
        "slack_id": resp["channel"],
    }


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state, include_event=True)
