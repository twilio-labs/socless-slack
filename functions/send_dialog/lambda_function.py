from socless import (
    socless_bootstrap,
    socless_dispatch_outbound_message,
    init_human_interaction,
)
from socless.utils import gen_id
from slack_helpers import SOCLESS_BOT_TOKEN
import requests


def handle_state(
    context,
    trigger_id: str,
    title: str,
    elements: list,
    receiver: str = "",
    submit_label: str = "Submit",
    state: str = "n/a",
    token: str = "",
):
    """Send a dialog into Slack

    Args:
        receiver     : The name of the State in the playbook that will receive the dialog response
        trigger_id   : trigger_id required to open a Dialog
        title        : Dialog title
        elements     : Dialog elements
        submit_label : Label for Dialog's submit button
        state        : this string simply echoes back what your app passed to dialog.open. Use it as a pointer that references sensitive data stored elsewhere.
        token        : you can pass an alternate token via Jinja template in playbook.json (ssm, environment, etc)

    Note:
        - See https://api.slack.com/dialogs for more details on to create elements for a slack dialog
        - This integration starts a Human Response workflow. When used in a playbook, it needs to be followed by a Task state that uses the _socless_outbound_message_response Activity to receive the response from a user
        - A user can respond to a dialog by either submitting it or cancelling it. The response payload contains a key named `type` that can be either `dialog_submission` or `dialog_cancellation`. In your playboks,
            be sure to check what type of response a user provided before acting on it.
    """
    if not token:
        token = SOCLESS_BOT_TOKEN

    USE_NEW_INTERACTION = "task_token" in context

    message_id = gen_id()

    dialog = {
        "title": title,
        "elements": elements,
        "submit_label": submit_label,
        "notify_on_cancel": True,
        "callback_id": message_id,
        "state": state,
    }

    payload = {"trigger_id": trigger_id, "dialog": dialog}

    url = "https://slack.com/api/dialog.open"
    headers = {
        "content-type": "application/json",
        "Authorization": "Bearer {}".format(token),
    }
    if USE_NEW_INTERACTION:
        init_human_interaction(context, payload, message_id)

    resp = requests.post(url, json=payload, headers=headers)
    json_resp = resp.json()

    if not json_resp["ok"]:
        raise Exception(json_resp["error"])

    if not USE_NEW_INTERACTION:
        investigation_id = context["artifacts"]["event"]["investigation_id"]
        execution_id = context.get("execution_id")
        socless_dispatch_outbound_message(
            receiver, message_id, investigation_id, execution_id, payload
        )
    return {"response": json_resp, "message_id": message_id}


def lambda_handler(event, context):
    # warm start
    if event.get("_keepwarm") is True:
        return {}
    return socless_bootstrap(event, context, handle_state, include_event=True)
