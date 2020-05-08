import slack
import os

SOCLESS_BOT_TOKEN = os.environ["SOCLESS_BOT_TOKEN"]

slack_client = slack.WebClient(SOCLESS_BOT_TOKEN)


def find_user(name, page_limit=1000, include_locale="false"):
    """Find a user's Slack profile based on their full or display name.
    """
    name_lower = name.lower()
    paginate = True
    next_cursor = ""
    while paginate:
        resp = slack_client.users_list(
            cursor=next_cursor, limit=page_limit, include_locale=include_locale
        )
        data = resp.data
        next_cursor = resp.data["response_metadata"].get("next_cursor", "")
        if not next_cursor:
            paginate = False

        for user in data["members"]:
            user_names = list(
                map(
                    str.lower,
                    [
                        user.get("name", ""),
                        user.get("real_name", ""),
                        user.get("profile", {}).get("real_name", ""),
                    ],
                )
            )
            if name_lower in user_names:
                return {"found": True, "user": user}

    return {"found": False}


def get_profile_via_id(slack_id):
    """Fetch user's slack profile with their slack_id.
    Args:
        slack_id : (string) slack user id ex. W1234567
    """
    resp = slack_client.users_profile_get(user=slack_id)
    return resp["profile"]


def get_channel_id(channel_name, channel_type):
    """
    Fetches the ID of a Slack Channel or User
    Args:
        channel_name: (string) The name of the channel / name of user / slack id of channel/user
        channel_type: (string) The Channel type, either "user" or "channel" or "slack_id"
    Returns:
        (string) A Slack ID that can be used to message the channel directly
    """
    if channel_type == "slack_id":
        channel_id = channel_name
    elif channel_type == "user":
        user = find_user(channel_name)
        channel_id = user["user"]["id"] if user["found"] else False
        if not channel_id:
            raise Exception(f"Unable to find user: {channel_name}")
    else:
        channel_id = f"#{channel_name}"

    return channel_id


def paginated_api_call(api_method, response_objects_name, **kwargs):
    """
    Calls api method and cycles through all pages to get all objects
    :param method: api method to call
    :param response_objects_name: name of collection in response json
    :param kwargs: url params to pass to call, additionally to limit and cursor which will be added automatically
    """

    ret = list()
    cursor = None
    call_limit = 1000
    while cursor != "":
        if cursor is not None:
            r = api_method(limit=call_limit, cursor=cursor, **kwargs)
        else:
            r = api_method(limit=call_limit, **kwargs)
        response_objects = r.get(response_objects_name)
        if response_objects is not None:
            for channel in r[response_objects_name]:
                channel_name = channel.get("name")
                ret.append(channel_name)
        metadata = r.get("response_metadata")
        if metadata is not None:
            cursor = metadata["next_cursor"]
        else:
            cursor = ""
    return ret
