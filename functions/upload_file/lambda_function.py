from typing import Optional
from socless import socless_bootstrap, socless_template_string
from slack_helpers import SlackError, SlackHelper


def handle_state(
    context,
    target: str,
    target_type: str,
    content: Optional[str] = "",
    file: Optional[str] = "",
    filename: Optional[str] = "",
    title: Optional[str] = "",
    initial_comment: Optional[str] = "",
    token: Optional[str] = "",
    **kwargs,
):
    """Send a Slack message without expecting a response https://api.slack.com/methods/files.upload
    Args:
        content : Provide EITHER `content` OR `file`. CONTENT: A string
        file    : Provide EITHER `content` OR `file`. FILE: file path pointing to location in the lambda's local environment.
        filename: Filename of the file.
        initial_comment : The message text introducing the file.
        title : Title of the file
        target           : the username or slack id to send this message to
        target_type      : "slack_id" | "user" | "channel"
        token            : you can pass an alternate token via Jinja template in playbook.json (ssm, environment, etc)
    """
    helper = SlackHelper(token)

    if all([content, file]) or not any([content, file]):
        raise SlackError("Please provide EITHER a `file` OR a `content` argument.")

    if not all([target_type, target]):
        raise SlackError(
            "Incomplete parameters supplied. Please `supply target`, `target_type`"
        )

    content = socless_template_string(content, context)

    slack_target = helper.resolve_slack_target(target, target_type)

    # NOTE: this api supports multiple targets, with channel as a comma separated list
    file_upload_args = {"channels": slack_target}

    if content:
        file_upload_args["content"] = content
    if file:
        file_upload_args["file"] = file
    if filename:
        file_upload_args["filename"] = filename
    if initial_comment:
        file_upload_args["initial_comment"] = initial_comment
    if title:
        file_upload_args["title"] = title

    file_upload_args = {**file_upload_args, **kwargs}

    resp = helper.client.files_upload(**file_upload_args)

    if not resp.data["ok"]:
        raise SlackError(
            f"Slack error during file_upload to {target}: {resp.data['error']}"
        )

    return {"response": resp.data, "slack_id": slack_target}  # type: ignore


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state, include_event=True)
