Startup for create Slack APP
============================

Creating App
------------
1. Log in `Slack API page <https://api.slack.com/apps/>`_ and click `Create new app` button.
2. Select `From scratch`.
3. Enter your new app name and select install workspace.


App Token
----------
On your Application site.

1. Move to `Basic Information` tab.
2. Down to `App-Level Tokens`.
3. Click `Generate Token and Scope` button and enter token name.
4. Copy token

    .. image:: ./img/applvl.png
        :scale: 50%
        :align: left

5. Move `OAuth & Permissions` tab.
6. Add permission `Bot Token Scopes`, `User Token Scopes`.
7. Reinstall your app to your workspace.
8. Copy both tokens (User Oauth Token, Bot User Oauth Token).

    .. image:: ./img/oauth.png
        :scale: 50%
        :align: left

9. Paste `slack#Client(...)`

