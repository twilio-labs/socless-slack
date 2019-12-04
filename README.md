# socless-slack

Slack chatbot integrations for the [SOCless framework](https://twilio-labs.github.io/socless). Visit the SOCless framework tutorial on Slack integrations to get started https://twilio-labs.github.io/socless/tutorial-interacting-with-humans-via-slack/

# Deployment Instructions

## Prerequisites

- A Slack instance
- Permissions to create a Slack bot
- Socless Automation Framework deployed in an AWS Account

## Setting up a Slack bot

This integration requires a Slack bot setup and configured.
To setup a Slack bot:

1. In a web browser, log into the Slack instance you want your bot to exist in
2. Navigate to [api.slack.com/apps](https://api.slack.com/apps) and hit "Create New App"
3. Enter a name for your application. The tutorial will use `socless-bot`
4. Select your development workspace. It should be the workspace you want your bot to be in
5. Hit "Create App"
6. On the "Basic Information" page for your app, click "Bots"
7. Click "Add Bot User"
8. Set a display name of your choice for your bot e.g. `socless-bot`
9. Set a default username for your bot e.g `socless-bot`
10. Set "Always Show My Bot as Online" to "On"
11. Click "Add Bot User" again to save the changes
12. In the left sidebar, select "Oauth & Permissions"
13. Click "Install App to Workspace". Click "Authorize" to add the bot to your Slack Workspace
14. Once authorization is complete, you will be redirected back to the "Oauth & Permissions" page, which will now display a "Bot User OAuth Access Token". Note this token down. Our integration will need this token

*Tip:* Consider configuring one Slack bot for each Socless environment you have. Doing so will simplify playbook testing

## Configure Parameters in AWS SSM Parameter Store

Configure the below parameters in [AWS Systems Manager (SSM) Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) in the region(s) you plan to deploy your Socless Slack integrations

| Key                               | Value description                                                                                                                                                         | Parameter Type |
|-----------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|
| /socless/slack/bot_token          | Bot User OAuth Access Token from your installed bot                                                                                                                       | SecureString   |
| /socless/slack/slash_command      | The name you'll give the slash command for your bot e.g /socless-bot                                                                                                      | String         |
| /socless/slack/signing_secret     | The signing secret for your bot found on the "App Credentials" section of the "Basic Information" page for your app                                                       | SecureString   |
| /socless/slack_endpoint/help_text | Help text that your Socless Slack endpoints will respond with in case of failure e.g. "socless-bot experienced an error. Please contact the security team for assistance" | SecureString   |


To configure the parameters,
1. Log into your AWS Account in the regions(s) you're deploying socless-slack to
2. In the left sidebar of the Systems Manager page, select "Parameters Store" (you may need to scroll down to see it)
3. On the Parameter Store page, click "Create Parameter"
4. Enter the name of your parameter
5. Add a description for the parameter.
6. Under `Type`, select the appropriate type for the parameter being configured
7. Under KMS Key ID, select `alias/socless/lambdaKmsKey`
8. Under value, paste the appropriate value
9. Click "Create Parameter"

Repeat the process for all parameters that need to be configured.

## Deploy socless-slack

Clone this repository to your projects folder using the command below

```
git clone git@github.com:twilio-labs/socless-slack.git
```

Change into the `socless-slack` repository and setup deployment dependencies by running the commands below

```
npm install
virtualenv venv
. venv/bin/activate
```

## (Optional) Ensure Your Dev/Prod environment matches your Socless Dev/Prod regions
Open the package.json and ensure your `config` and `scripts` match what you have configured for your Socless deployment

## Deploy to Dev and Prod
Deploy your application to dev and prod by running the commands below.
To dev:
```
npm run dev
```

To prod:
```
npm run prod
```
Feel free to deploy to any other Socless environment you have configured

If your Socless deployment is successful, you will see a URL that ends in `/slack` in your `endpoints` section. This is your `Slack Endpoint URL`. Copy this URL. You will need it in the next section

## Configure Interactive Components
1. Return to the "Basic Information" page for your Slackbot on api.slack.com
2. Under "Add Features & Functionality", click "Interactive Components"
3. Turn on "Interactive Components" and turn on "Interactivity"
4. In the "Request URL" section, paste your `Slack Endpoint URL` and click "Save Changes"

## Configure Slash Commands
1. On the "Basic Information" page, click "Slash Commands"
2. In the `Command` section, type the name of the slash command for your bot. It should match what you configured in your SSM Parameter Store
3. In the `Request URL` section, paste your `Slack Endpoint URL`
4. Fill out the `Short Description` and `Usage Hint` sections as desired
5. Click save


Your Slack Bot is now completely configured for use within Socless
