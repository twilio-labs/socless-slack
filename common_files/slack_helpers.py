import slack
import os
import boto3

CACHE_USERS_TABLE = os.environ.get("CACHE_USERS_TABLE")
SOCLESS_BOT_TOKEN = os.environ["SOCLESS_BOT_TOKEN"]

slack_client = slack.WebClient(SOCLESS_BOT_TOKEN)


class SlackError(Exception):
    pass


def find_user(name: str, page_limit=1000, include_locale="false"):
    """Find a user's Slack profile based on their full or display name.
    Args:
        name: A user's Full Name or Display Name
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


def get_slack_id_from_username(username: str):
    """Fetch user's slack_id from their username.
    Checks against the dynamoDB cache (if enabled), or paginates through slack API users.list
        looking for the supplied username. If cache enabled, saves the found slack_id
    Args:
        username : (string) slack username (usually display_name)
    Returns:
        slack_id
    """
    slack_id = get_id_from_cache(username) if CACHE_USERS_TABLE else ""

    if not slack_id:
        search = find_user(username)
        if not search["found"]:
            raise Exception(f"Unable to find user: {username}")

        slack_id = search["user"]["id"]
        if CACHE_USERS_TABLE:
            save_user_to_cache(username=username, slack_id=slack_id)

    return slack_id


def get_user_info_via_id(slack_id):
    """
    API Docs https://api.slack.com/methods/users.info
    """
    resp = slack_client.users_info(user=slack_id)
    return resp["user"]


def resolve_slack_target(target_name: str, target_type: str) -> str:
    """Fetches the ID of a Slack Channel or User.
    Args:
        target_name: (string) The name of the channel / name of user / slack id of channel/user
        target_type: (string) The Channel type, either "user" or "channel" or "slack_id"
    Returns:
        (string) A Slack ID that can be used to message the channel directly
    """

    if target_type == "slack_id":
        slack_id = target_name
    elif target_type == "user":
        slack_id = get_slack_id_from_username(target_name)
    elif target_type == "channel":
        slack_id = target_name if target_name.startswith("#") else f"#{target_name}"
    else:
        raise Exception(
            f"target_type is not 'channel|user|slack_id'. failed target_type: {target_type} for target: {target_name}"
        )

    return slack_id


def paginated_api_call(api_method, response_objects_name, **kwargs):
    """Calls api method and cycles through all pages to get all objects.
    Args:
        api_method: api method to call
        response_objects_name: name of collection in response json
        kwargs: url params to pass to call, additionally to limit and cursor which will be added automatically
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
                if isinstance(channel, str):
                    channel_name = channel
                else:
                    channel_name = channel.get("name")

                ret.append(channel_name)
        metadata = r.get("response_metadata")
        if metadata is not None:
            cursor = metadata["next_cursor"]
        else:
            cursor = ""

    return ret


def slack_post_msg_wrapper(target, target_type, **kwargs):
    target_id = resolve_slack_target(target, target_type)
    resp = slack_client.chat_postMessage(channel=target_id, **kwargs)

    if not resp.data["ok"]:
        raise SlackError(
            f"Slack error during post_message to {target}: {resp.data['error']}"
        )
    print(f'returned channel: {resp["channel"]}')
    return resp


def get_id_from_cache(username: str) -> str:
    """Check if username exists in cache, return their slack_id.
    Args:
        username: slack username
    Returns:
        slack_id
    """
    dynamodb = boto3.resource("dynamodb")
    if not CACHE_USERS_TABLE:
        raise Exception(
            "env var CACHE_USERS_TABLE is not set, please check socless-slack serverless.yml"
        )
    table_resource = dynamodb.Table(CACHE_USERS_TABLE)
    key_obj = {"username": username}
    response = table_resource.get_item(TableName=CACHE_USERS_TABLE, Key=key_obj)

    return response["Item"]["slack_id"] if "Item" in response else False


def save_user_to_cache(username: str, slack_id: str):
    """Save a username -> slack_id mapping to the cache table
    Args:
        username: slack username
        slack_id: user's slack id
    """
    dynamodb = boto3.resource("dynamodb")
    if not CACHE_USERS_TABLE:
        raise Exception(
            "env var CACHE_USERS_TABLE is not set, please check socless-slack serverless.yml"
        )
    table_resource = dynamodb.Table(CACHE_USERS_TABLE)
    new_item = {"username": username, "slack_id": slack_id}
    response = table_resource.put_item(TableName=CACHE_USERS_TABLE, Item=new_item)
    print(response)
