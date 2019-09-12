import uuid, os
from slack_helpers import slack_client, find_user, get_channel_id
from socless import socless_bootstrap, socless_dispatch_outbound_message, socless_template_string
from socless.utils import gen_id

TARGET_TYPE_PREFIX = {
    "channel": "#",
    "user": "@"
}

SLACK_SLASH_COMMAND = os.environ.get('SLACK_SLASH_COMMAND','')

def handle_state(context,receiver,target,target_type,message_template,response_desc='[response]'):
    """
    Send a Slack Message and store the message id for the message
    """
    if not message_template:
        raise Exception("No text was supplied to Slack message")

    message_id = gen_id(6)
    context['_message_id'] = message_id
    extended_template = "{message_template}\n```{slash_command} {context[_message_id]} {response_desc}```\n".format(message_template=message_template,slash_command=SLACK_SLASH_COMMAND,context=context,response_desc=response_desc)
    message = socless_template_string(extended_template,context)
    target_id = get_channel_id(target, target_type)
    r = slack_client.chat_postMessage(channel=target_id,text=message,as_user=True)
    investigation_id = context['artifacts']['event']['investigation_id']
    execution_id = context.get('execution_id')
    if r.data['ok']:
        socless_dispatch_outbound_message(receiver,message_id,investigation_id,execution_id,message)
    else:
        raise Exception(f"Human Reponse workflow failed to initiate because slack_client failed to send message: {r.data}")
    return {"response": r.data, "message_id": message_id}


def lambda_handler(event,context):
    return socless_bootstrap(event,context,handle_state,include_event=True)
