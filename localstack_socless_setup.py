import boto3
import urllib
from urllib.request import urlopen
from time import sleep

MOCK_KMS_ID = "mock_key_id"
SSM_PARAMS = [ 
    {
        "name" : "/socless/slack/bot_token_user", 
        "value" : "mock"
    },
    {
        "name" : "/socless/slack/bot_token", 
        "value" : "mock"
    },
        {
        "name" : "/socless/slack/slash_command", 
        "value" : "mock"
    },
    {
        "name" : "/socless/slack/signing_secret",
        "value" : "mock"
    },
    {
        "name" : "/socless/slack_endpoint/help_text",
        "value" : "mock"
    },
    {
        "name" : "/socless/slack/slash_command",
        "value" : "mock"
    }
]

def wait_for_internet_connection():
    count = 0
    while True:
        try:
            # response = urlopen('http://localhost:4583',timeout=1)
            response = urlopen("http://localstack_container:8080",timeout=1)
            print(response)
            return
        except urllib.error.URLError:
            count += 1
            print(f'no connection yet. attempts: {count}')
            sleep(3)
            # pass

def main():
    try:
        session = boto3.Session(region_name='us-west-1')
        # ssm = session.client('ssm', endpoint_url="http://localhost:4583")
        ssm = session.client('ssm', endpoint_url="http://localstack_container:4583")
        print(ssm)
        for param in SSM_PARAMS:
            resp = ssm.put_parameter(
                Name=param["name"], 
                Value=param["value"], 
                KeyId=MOCK_KMS_ID, 
                Type="SecureString", 
                Overwrite=True)
            print(resp)
    except Exception as e:
        print(e)
        sleep(10)
        main()

    


wait_for_internet_connection()
main()





# kms_client = session.client('kms', endpoint_url="http://localhost:4599")
# response = kms_client.create_key(Description="mock_key_id", KeyUsage="ENCRYPT_DECRYPT", Origin="AWS_KMS")
# print(f"response: {response}")


