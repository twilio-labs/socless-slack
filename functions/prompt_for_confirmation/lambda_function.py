from socless import socless_template_string, socless_dispatch_outbound_message, socless_bootstrap, init_human_interaction
from socless.utils import gen_id
from slack_helpers import get_channel_id, slack_client


def handle_state(context, target_type, target, text, receiver='', prompt_text='', yes_text='Yes', no_text='No'):
    """
    Send a Slack Message and store the message id for the message
    """
    USE_NEW_INTERACTION = 'task_token' in context

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

    payload = {
        "text": text,
        "ATTACHMENT_TEMPLATE" : ATTACHMENT_TEMPLATE
    }

    if USE_NEW_INTERACTION:
        init_human_interaction(context,payload, message_id)

    resp = slack_client.chat_postMessage(channel=target_id, text=text, attachments=[ATTACHMENT_TEMPLATE], as_user=True)

    if not resp.data['ok']:
        raise Exception(resp.data['error'])

    if not USE_NEW_INTERACTION:
        investigation_id = context['artifacts']['event']['investigation_id']
        execution_id = context.get('execution_id')
        socless_dispatch_outbound_message(receiver,message_id,investigation_id,execution_id,payload)
    
    return {'response': resp.data, "message_id": message_id, "slack_id" : target_id}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state, include_event=True)
