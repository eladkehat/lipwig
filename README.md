# Lipwig - Post SNS messages to external services

Lipwig is an AWS SAM/Lambda application that posts SNS messages to external services, like Slack.


## Use Case

Publishing a message to an SNS topics is a common way to notify subscribers of some event in your system.
For example, a dead letter queue topic lets publish events that your lambda function failed to handle.

But what if you want a person or team of people to know of the message? Out of the box, SNS only supports email (slow),
push messages to an app _that you own_, or SMS (not free).

Lipwig provides lambda functions that you can subscribe to an SNS topic in order to publish its events to
additional services that you use.


## How to Use

1. Deploy the Lipwig app in your environment. You can use:
```bash
S3_BUCKET=your_deploy_bucket make publish
```
1. Either subscribe Lipwig lambda functions directly to SNS topics via the AWS console or CLI, or use `Fn::ImportValue`
to add the subscription in your own CloudFormation template (see
[this walkthrough](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/walkthrough-crossstackref.html)
for an example).


## Services

### CloudWatch Logs
Log SNS messages to CloudWatch Logs.

No additional configuration is needed for this function. Look for its log stream in CloudWatch to see the messages.

The CloudWatch function is exported as `lipwig-CloudWatchLogsFunction`.


### Slack
Post SNS messages to Slack.

1. Create a [Slack app](https://api.slack.com/apps).
1. Give your app the `chat:write:bot` [permission scope](https://api.slack.com/docs/oauth-scopes).
1. Make the app's **OAuth access token** available to Lipwig:
    * Either add it to the lambda function's environment variables, **as an encrypted variable**, with the key `SLACK_TOKEN`.
    * Or add it to SSM ParameterStore, **as an encrypted parameter**, with the key `/Lipwig/SlackToken`.
1. You can control the channel that messages are posted to by adding an environment variable with the key
`SLACK_CHANNEL`.
    If you do not specify a channel, then `#lipwig` is used by default.

The Slack function is exported as `lipwig-SlackFunction`.


## Why "Lipwig"?
The name is a reference to [Moist von Lipwig](https://en.wikipedia.org/wiki/Moist_von_Lipwig), the Ankh-Morpork
Postmaster General in Terry Pratchett's novel [Going Postal](https://en.wikipedia.org/wiki/Going_Postal).

Lipwig can post message anywhere, just like the revitalized Ankh-Morpork postal service under von Lipwig.
