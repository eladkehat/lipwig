# Lipwig - Post SNS messages to external services

Lipwig is an AWS SAM/Lambda application that posts SNS messages to external services, like Slack or Pushover.


## Use Case

Publishing a message to an SNS topics is a common way to notify subscribers of some event in your system.
For example, a dead letter queue topic lets publish events that your lambda function failed to handle.

But what if you want a person or team of people to know of the message? Out of the box, SNS only supports email (slow),
push messages to an app _that you own_, or SMS (not free).

Lipwig provides a number of lambda functions that you can subscribe to an SNS topic in order to publish its events to
additional services that you use.


## Why "Lipwig"?
The name is a reference to [Moist von Lipwig](https://en.wikipedia.org/wiki/Moist_von_Lipwig), the Ankh-Morpork
Postmaster General in Terry Pratchett's novel [Going Postal](https://en.wikipedia.org/wiki/Going_Postal).

Lipwig can post message anywhere, just like the revitalized Ankh-Morpork postal service under von Lipwig.
