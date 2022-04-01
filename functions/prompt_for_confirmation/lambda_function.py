from socless import (
    socless_template_string,
    socless_dispatch_outbound_message,
    socless_bootstrap,
    init_human_interaction,
)
from socless.utils import gen_id
from slack_helpers import SlackHelper


def handle_state(
    context,
    target_type: str,
    target: str,
    text: str,
    receiver: str = "",
    prompt_text: str = "",
    yes_text: str = "Yes",
    no_text: str = "No",
    as_user: bool = True,
    token: str = "",
):
    """Send a Slack Message and store the message id for the message.
    Args:
        target         : the username or slack id to send this message to
        target_type    : "slack_id" | "user" | "channel"
        token          : you can pass an alternate token via Jinja template in playbook.json (ssm, environment, etc)
    Returns:

    """
    helper = SlackHelper(token)
    USE_NEW_INTERACTION = "task_token" in context

    if not all([target_type, target, text]):
        raise Exception(
            "Incomplete inputs: target, target_type and text must be supplied"
        )

    ATTACHMENT_YES_ACTION = {
        "name": "yes_text",
        "style": "default",
        "text": "",
        "type": "button",
        "value": "true",
    }
    ATTACHMENT_NO_ACTION = {
        "name": "no_text",
        "style": "danger",
        "text": "",
        "type": "button",
        "value": "false",
    }

    ATTACHMENT_TEMPLATE = {
        "text": "",
        "mrkdwn_in": ["text"],
        "fallback": "New message",
        "callback_id": "",
        "color": "#3AA3E3",
        "attachment_type": "default",
        "actions": [],
    }

    message_id = gen_id(6)
    context["_message_id"] = message_id
    text = socless_template_string(text, context)
    prompt_text = socless_template_string(prompt_text, context)

    ATTACHMENT_TEMPLATE["text"] = "*{}*".format(prompt_text)
    ATTACHMENT_TEMPLATE["callback_id"] = message_id
    ATTACHMENT_YES_ACTION["text"] = yes_text
    ATTACHMENT_NO_ACTION["text"] = no_text
    ATTACHMENT_TEMPLATE["actions"] = [ATTACHMENT_YES_ACTION, ATTACHMENT_NO_ACTION]

    payload = {"text": text, "ATTACHMENT_TEMPLATE": ATTACHMENT_TEMPLATE}

    if USE_NEW_INTERACTION:
        init_human_interaction(context, payload, message_id)

    resp = helper.slack_post_msg_wrapper(
        target,
        target_type,
        text=text,
        attachments=[ATTACHMENT_TEMPLATE],
        as_user=as_user,
    )

    if not USE_NEW_INTERACTION:
        investigation_id = context["artifacts"]["event"]["investigation_id"]
        execution_id = context.get("execution_id")
        socless_dispatch_outbound_message(
            receiver, message_id, investigation_id, execution_id, payload
        )

    return {
        "response": resp.data,  # type: ignore
        "message_id": message_id,
        "slack_id": resp["channel"],  # type: ignore
    }


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state, include_event=True)
