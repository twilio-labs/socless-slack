from socless import *
from slack_helpers import slack_client, paginated_api_call


def handle_state(user_id, target_channel_id):
    """
    Check if user is in certain slack channel
     :param user_id: user id of the user invoking the slash command
     :param target_channel_id: the channel id to be checked if user is in
     :return boolean value indicating whether the user is in the channel
    """

    ret = paginated_api_call(slack_client.conversations_members,
                             'members',
                             target_channel_id
                             )
    if user_id not in ret['members']:
        return {"ok": False}
    else:
        return {"ok": True}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state)
