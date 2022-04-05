from socless import socless_bootstrap
from slack_helpers import SlackHelper


def handle_state(
    context,
    message_template: str,
    target: str,
    target_type: str,
    as_user: bool = True,
    token: str = "",
):
    """Send a Slack message without expecting a response.
    Args:
        message_template : A string to send to the target. SOCless template
            notation will unpack any references in the string
        target           : the username or slack id to send this message to
        target_type      : "slack_id" | "user" | "channel"
        token            : you can pass an alternate token via Jinja template in playbook.json (ssm, environment, etc)
    """
    helper = SlackHelper(token)

    if not all([target_type, target, message_template]):
        raise Exception(
            "Incomplete parameters supplied. Please supply target, target_type and message_template"
        )

    message = message_template

    resp = helper.slack_post_msg_wrapper(
        target, target_type, text=message, as_user=as_user
    )

    return {"response": resp.data, "slack_id": resp["channel"]}  # type: ignore


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state, include_event=True)
