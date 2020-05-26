from socless import (
    socless_bootstrap,
    socless_dispatch_outbound_message,
    init_human_interaction,
)
from socless.utils import gen_id
from slack_helpers import slack_client
import os

# import requests


SLACK_BOT_TOKEN = os.environ["SOCLESS_BOT_TOKEN"]


def handle_state(
    context,
    trigger_id,
    title,
    blocks=[],
    receiver="",
    submit_label="Submit",
    state="n/a",
):
    """Send a modal (view) into Slack, using the Blocks API

    SOCless Playbook Step Type: 'Interaction'

    Args:
        context (dict): [ignore] The state context object. This is included automatically by Socless Core and SHOULD NOT be supplied by the user when creating a playbook
        trigger_id (str): trigger_id required to open a modal, (use PromptForConfirmation, PromptForResponse, Slash Command)
        title (str): Modal title
        blocks (list) : An array of valid Blocks API dictionaries
        submit_label (str): Label for Modal's submit button
        state (str): this string simply echoes back what your app passed to modal.open. Use it as a pointer that references sensitive data stored elsewhere.

    Note:
        - See https://api.slack.com/surfaces/modals/using for more details
        - This integration starts a Human Response workflow. When used in a playbook, it needs to be followed by a Task state that uses the _socless_outbound_message_response Activity to receive the response from a user
        - A user can respond to a modal by either submitting it or cancelling it. #! The response payload contains a key named `type` that can be either `modal_submission` or `modal_cancellation`. In your playboks,
            be sure to check what type of response a user provided before acting on it.
    """
    USE_NEW_INTERACTION = "task_token" in context

    message_id = gen_id()

    modal = {
        "title": title,
        "blocks": blocks,
        "submit_label": submit_label,
        "notify_on_cancel": True,
        "callback_id": message_id,
        "state": state,
    }

    payload = {"trigger_id": trigger_id, "modal": modal}

    # url = "https://slack.com/api/views.open"
    # headers = {
    #     "content-type": "application/json",
    #     "Authorization": "Bearer {}".format(SLACK_BOT_TOKEN),
    # }

    if USE_NEW_INTERACTION:
        init_human_interaction(context, payload, message_id)

    response = slack_client.views_open(
        trigger_id=trigger_id,
        view={
            "type": "modal",
            "callback_id": "modal-id",
            "title": {"type": "plain_text", "text": title},
            "submit": {"type": "plain_text", "text": submit_label},
            "close": {"type": "plain_text", "text": "Cancel"},
            "blocks": blocks,
        },
    )

    print(response)

    if not USE_NEW_INTERACTION:
        investigation_id = context["artifacts"]["event"]["investigation_id"]
        execution_id = context.get("execution_id")
        socless_dispatch_outbound_message(
            receiver, message_id, investigation_id, execution_id, payload
        )

    return {"message_id": message_id, "trigger_id": trigger_id, "response": response}


def lambda_handler(event, context):
    # warm start
    if event.get("_keepwarm") is True:
        return {}
    return socless_bootstrap(event, context, handle_state, include_event=True)
