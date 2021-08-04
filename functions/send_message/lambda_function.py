from socless import socless_bootstrap, socless_template_string
from slack_helpers import SlackHelper


def handle_state(
    context, message_template, target, target_type, as_user=True, token=""
):
    """Send a Slack message without expecting a response.
    Args:
        message_template : (str) A string to send to the target. SOCless template
            notation will unpack any references in the string
        target           : (str) the username or slack id to send this message to
        target_type      : (str) "slack_id" | "user" | "channel"
    """
    helper = SlackHelper(token)

    if not all([target_type, target, message_template]):
        raise Exception(
            "Incomplete parameters supplied. Please supply target, target_type and message_template"
        )

    # target_id = resolve_slack_target(target, target_type)
    message = socless_template_string(message_template, context)

    resp = helper.slack_post_msg_wrapper(
        target, target_type, text=message, as_user=as_user
    )

    return {"response": resp.data, "slack_id": resp["channel"]}  # type: ignore


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state, include_event=True)
