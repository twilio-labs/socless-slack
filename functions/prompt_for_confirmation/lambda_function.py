from socless import socless_template_string, socless_dispatch_outbound_message, socless_bootstrap
from socless.utils import gen_id
from slack_helpers import find_user, get_channel_id, slack_client


def handle_state(context, receiver, target_type, target, text, prompt_text='', yes_text='Yes', no_text='No'):
    """
    Send a Slack Message and store the message id for the message
    """
    if not all([target_type, target, text]):
        raise Exception("Incomplete inputs: target, target_type and text must be supplied")
    target_id = get_channel_id(target, target_type)

    ATTACHMENT_YES_ACTION = {
        "name": "yes_text",
        "style": "default",
        "text": "",
        "type": "button",
        "value": "true"
    }
    ATTACHMENT_NO_ACTION = {
        "name": "no_text",
        "style": "danger",
        "text": "",
        "type": "button",
        "value": "false"
    }

    ATTACHMENT_TEMPLATE = {
        "text": "",
        "mrkdwn_in": ["text"],
        "fallback": "New message",
        "callback_id": "",
        "color": "#3AA3E3",
        "attachment_type": "default",
        "actions": []
    }

    message_id = gen_id(6)
    context['_message_id'] = message_id
    text = socless_template_string(text, context)
    prompt_text = socless_template_string(prompt_text, context)

    ATTACHMENT_TEMPLATE['text'] = "*{}*".format(prompt_text)
    ATTACHMENT_TEMPLATE['callback_id'] = message_id
    ATTACHMENT_YES_ACTION['text'] = yes_text
    ATTACHMENT_NO_ACTION['text'] = no_text
    ATTACHMENT_TEMPLATE['actions'] = [ATTACHMENT_YES_ACTION, ATTACHMENT_NO_ACTION]

    resp = slack_client.chat_postMessage(channel=target_id, text=text, attachments=[ATTACHMENT_TEMPLATE], as_user=True)
    investigation_id = context['artifacts']['event']['investigation_id']
    execution_id = context.get('execution_id')
    if resp.data['ok']:
        socless_dispatch_outbound_message(receiver, message_id, investigation_id, execution_id, resp.data)
        return {"response": resp.data, "message_id": message_id, "slack_id" : target_id}
    else:
        raise Exception(f"Failed to initiate human response workflow: {resp.data}")


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state, include_event=True)
