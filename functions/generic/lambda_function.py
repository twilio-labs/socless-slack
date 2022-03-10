from socless import socless_bootstrap
from slack_sdk.web.client import WebClient
from slack_sdk.web.internal_utils import _parse_web_class_objects

from slack_helpers import SOCLESS_BOT_TOKEN


def handle_state(
    api_method: str,
    http_verb: str = "POST",
    params: dict = None,  # type: ignore
    json: dict = None,  # type: ignore
    token: str = "",
):
    """Create slack channel and invite any provided slack_ids.
    Args:
        api_method : Slack method. Example: `chat.postEphemeral`
        http_verb  : defaults to POST
        params     : used for URL Encoded Params
        json       : used for json encoded data

    Note:
        - See https://api.slack.com/methods
    """
    if not token:
        token = SOCLESS_BOT_TOKEN
    client = WebClient(token)

    if json:
        _parse_web_class_objects(json)

    response = client.api_call(
        api_method, http_verb=http_verb, params=params, json=json
    )

    return {"ok": True, "data": response.data}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
