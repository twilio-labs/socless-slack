import simplejson as json, urllib.request, urllib.parse, urllib.error, os, copy
from urllib.parse import parse_qsl
from socless import end_human_interaction, socless_log
from slack_helpers import (
    SlackError,
    get_bot_friendly_name_from_endpoint_query_params,
    is_event_from_slack,
)


NO_MESSAGE_ID = "no_message_id"
NO_RESPONSE = "no_user_response"


# TODO: Multiple instances of copy.deepcopy may make this slow. Timeit
# TODO: Log an error for every exception raised. Otherwise it just disapears into the ether


class BaseResponseHandler(object):
    """Parent class for all Slack Response Handlers"""

    def __init__(self, payload):
        """
        Args:
            payload (dict): Contains the Slack response
        Note:
            Should be used after the message from Slack has already been validated
        """
        self.payload = copy.deepcopy(payload)

    def make_apig_response(self, resp_template="", fields={}):
        """Create the necessary response for API Gateway"""
        raise NotImplementedError("make_apig_response")

    def parse_human_response(self):
        """Parse the human response from the payload"""
        raise NotImplementedError("parse_human_response")

    def execute(self):
        """Execute the handler to address the message"""
        ERROR_TEMPLATES = {
            "message_id_query_failed": {"source": "server"},
            "message_id_not_found": {
                "source": "client",
                "resp_template": "Error - The code you supplied is invalid",
            },
            "message_id_used": {
                "source": "client",
                "resp_template": "Error - The code you suppied has already been used",
            },
            "await_token_not_found": {"source": "server"},
            "execution_id_not_found": {"source": "server"},
            "receiver_not_found": {"source": "server"},
            "execution_results_query_failed": {"source": "server"},
            "execution_results_not_found": {"source": "server"},
            "response_delivery_timed_out": {
                "source": "client",
                "resp_template": "Error - the time window to respond to this message has expired",
            },
            "response_delivery_failed": {"source": "server"},
            "message_status_update_failed": {"source": "server"},
            NO_MESSAGE_ID: {
                "source": "client",
                "resp_template": "Error - you did not supply a message code in your response. Please try again",
            },
            NO_RESPONSE: {
                "source": "client",
                "resp_template": "Error - you did not supply a response after the message code. Please try again",
            },
        }
        try:
            self.parse_human_response()
            end_human_interaction(self.message_id, self.human_response)
        except Exception as e:
            HELP_TEXT = os.environ.get("HELP_TEXT", "")
            err_code = f"{e}"
            if err_code in ERROR_TEMPLATES:
                socless_log.error(err_code, {"error": f"{e}"})
                if ERROR_TEMPLATES[err_code]["source"] == "server":
                    resp_template = "*internal server error - {}. {}*".format(
                        err_code, HELP_TEXT
                    )
                else:
                    resp_template = "*{}. {}*".format(
                        ERROR_TEMPLATES[err_code]["resp_template"], HELP_TEXT
                    )
            else:
                socless_log.error("unknown_server_error", {"error": f"{e}"})
                resp_template = "*unknown server error. {}*".format(HELP_TEXT)

            return self.make_apig_response(resp_template)
        else:
            return self.make_apig_response()


class SlashCommandHandler(BaseResponseHandler):
    """Handle slash command messages and returns a payload similar to the below
        to the relevant playbook
        ```
            {
                "user_id": "U********",
                "response_url": "https://hooks.slack.com/commands/T******/3*******/G************",
                "text": "07-11-2018",
                "trigger_id": "3*******.2******.4*********************v*********",
                "channel_id": "D********",
                "team_id": "T********",
                "command": "/slash-command",
                "team_domain": "s******",
                "user_name": "u*******",
                "channel_name": "directmessage"
            }
        ```

    Note:
        No __init__ method should be created as __init__ lives in BaseResponseHandler
    """

    def parse_human_response(self):
        self.message_id, _, user_resp = self.payload["text"].partition(" ")
        if not self.message_id:
            raise Exception(NO_MESSAGE_ID)

        if not user_resp:
            raise Exception(NO_RESPONSE)

        self.human_response = copy.deepcopy(self.payload)
        self.human_response["text"] = user_resp

    def make_apig_response(self, resp_template="One moment please", fields={}):
        """ """
        return {
            "statusCode": 200,
            "body": json.dumps(
                {"text": resp_template.format(**fields), "response_type": "in_channel"}
            ),
        }


class InteractiveMessageHandler(BaseResponseHandler):
    """Handle interactive message responses and a
        payload similar to the below to the relevant playbook
        ```
            {
                "attachment_id": "1",
                "response_url": "https://hooks.slack.com/commands/T******/3*******/G************",
                "action_ts": "1531182850.731818",
                "original_message": {
                    "attachments": [{
                        "color": "3AA3E3",
                        "text": "*Did you login from Fordham?*",
                        "actions": [{
                                "style": "default",
                                "name": "yes_text",
                                "text": "Yes",
                                "value": "true",
                                "type": "button",
                                "id": "1"
                            },
                            {
                                "style": "danger",
                                "name": "no_text",
                                "text": "No",
                                "value": "false",
                                "type": "button",
                                "id": "2"
                            }
                        ],
                        "callback_id": "9a4ea4",
                        "mrkdwn_in": [
                            "text"
                        ],
                        "fallback": "New message",
                        "id": 1
                    }],
                    "text": "Hi Ubani!\nI detected that your account, `u*******`, logged into the VPN from `Fordham` around `2016-05-24T09:05:17Z`.",
                    "ts": "1531182847.000063",
                    "user": "U********",
                    "type": "message",
                    "bot_id": "B70CWJCTC"
                },
                "actions": {
                    "type": "button",
                    "name": "yes_text",
                    "value": "true"
                },
                "callback_id": "9a4ea4",
                "is_app_unfurl": false,
                "trigger_id": "3***********.2***********.0**********************",
                "team": {
                    "domain": "s*******",
                    "id": "T024FJ1MS"
                },
                "type": "interactive_message",
                "message_ts": "1531182847.000063",
                "channel": {
                    "id": "D******",
                    "name": "directmessage"
                },
                "user": {
                    "id": "U*******",
                    "name": "u*******"
                }
            }
        ```

    Note:
        No __init__ method should be created as __init__ lives in BaseResponseHandler
    """

    def parse_human_response(self):
        self.message_id = self.payload.get("callback_id")
        if not self.message_id:
            raise Exception(NO_MESSAGE_ID)

        self.human_response = copy.deepcopy(self.payload)
        self.human_response["actions"] = self.human_response["actions"][0]

    def make_apig_response(self, resp_template="You responded with *{}*", fields={}):
        """ """
        original_text = self.payload["original_message"]["text"]
        original_attachment = copy.deepcopy(
            self.payload["original_message"]["attachments"][0]
        )
        original_actions = original_attachment["actions"]
        chosen_action_name = self.human_response["actions"]["name"]
        chosen_action_text = ""
        for each in original_actions:
            if each["name"] == chosen_action_name:
                chosen_action_text = each["text"]
                break

        new_fields = [{"value": resp_template.format(chosen_action_text)}]
        new_attachment = original_attachment
        new_attachment["fields"] = new_fields
        new_attachment.pop("actions", "")
        new_attachment["mrkdwn_in"] = ["fields", "text"]
        results = {"text": original_text, "attachments": [new_attachment]}
        return {"statusCode": 200, "body": json.dumps(results)}


class DialogSubmissionHandler(BaseResponseHandler):
    """Handles dialog responses.
        When a user submits a dialog, it returns a payload similar to the below to
        the relevant playbook
        ```
            {
                "type": "dialog_submission",
                "submission": {
                    "name": "Sigourney Dreamweaver",
                    "email": "sigdre@example.com",
                    "phone": "+1 800-555-1212",
                    "meal": "burrito",
                    "comment": "No sour cream please",
                    "team_channel": "C0LFFBKPB",
                    "who_should_sing": "U0MJRG1AL"
                },
                "callback_id": "employee_offsite_1138b",
                "team": {
                    "id": "T1ABCD2E12",
                    "domain": "coverbands"
                },
                "user": {
                    "id": "W12A3BCDEF",
                    "name": "dreamweaver"
                },
                "channel": {
                    "id": "C1AB2C3DE",
                    "name": "coverthon-1999"
                },
                "action_ts": "936893340.702759",
                "response_url": "https://hooks.slack.com/app/T012AB0A1/123456789/JpmK0yzoZDeRiqfeduTBYXWQ"
            }
    ```

    When a user cancels a dialog, the returned payload is similar to the below
    ```
        {
            "type": "dialog_cancellation",
            "response_url": "https://hooks.slack.com/commands/T******/3*******/G************",
            "action_ts": "1531430286.072469",
            "callback_id": "24a208e6-c293-4192-b6a1-b556b8cfbf75",
            "user": {
                "id": "U0A27UBNK",
                "name": "u*******"
            },
            "team": {
                "domain": "s********",
                "id": "T024FJ1MS"
            },
            "channel": {
                "id": "D71J0QK7H",
                "name": "directmessage"
            }
        }
    ```

    Note:
        No __init__ method should be created as __init__ lives in BaseResponseHandler
    """

    def parse_human_response(self):
        self.message_id = self.payload.get("callback_id")
        if not self.message_id:
            raise Exception(NO_MESSAGE_ID)
        self.human_response = self.payload

    def make_apig_response(self, resp_template="", fields={}):
        """ """
        # TODO: Determine how to handle rudimentary validation of returned values
        return {"statusCode": 200}


def lambda_handler(event, context):
    """
    Handles the following types of Slack messages:
    - Slash Command Responses
    - Interactive Message Responses
    - Dialog submissions
    """

    # Check if function was executed to prevent cold starts
    if event.get("_keepwarm") is True:
        return {"statusCode": 200}

    bot_name = get_bot_friendly_name_from_endpoint_query_params(event)
    signing_secret_env_key = f"{bot_name}_SECRET".upper()

    try:
        signing_secret = os.environ[signing_secret_env_key]
    except KeyError as e:
        raise SlackError(f"No signing secret found for {signing_secret_env_key}. {e}")

    # Validate that the message came from Slack
    if not is_event_from_slack(event, signing_secret):
        return {"statusCode": 200, "body": "Invalid Auth"}

    # Since signature is valid, process the response
    form_encoded_payload = event.get("body")
    parsed_payload = dict(parse_qsl(form_encoded_payload))
    if "payload" in parsed_payload:
        parsed_payload = json.loads(parsed_payload["payload"])

    parsed_payload.pop("token", "")
    if "type" in parsed_payload:
        response_type = parsed_payload["type"]
        if (
            response_type == "dialog_submission"
            or response_type == "dialog_cancellation"
        ):
            handler = DialogSubmissionHandler(parsed_payload)
        elif response_type == "interactive_message":
            handler = InteractiveMessageHandler(parsed_payload)
    else:
        handler = SlashCommandHandler(parsed_payload)

    apig_resp = handler.execute()
    return apig_resp
