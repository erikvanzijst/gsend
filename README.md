# Send email from the cli using gmail

## Create a Google Cloud Platform project

1. Set up a Google Cloud Project
2. Go to [Google Cloud Console](https://console.cloud.google.com)
3. Create a new project
4. Go to APIs & Services → Library → search for "Gmail API" and enable
5. Go to OAuth Consent Screen → configure (external)
6. Go to Data Access → Add scopes → check scope "https://www.googleapis.com/auth/gmail.send"
7. Go to Audience and add yourself as a test user
8. Download the JSON with client_id and client_secret and save as `credentials.json`

Make sure you have [uv](https://docs.astral.sh/uv/getting-started/installation/) installed.

```shell
$ ./gsend.py 
usage: gsend.py [-h] {auth,send} ...

Gmail OAuth + Send via msmtp

positional arguments:
  {auth,send}
    auth       Authenticate with Gmail
    send       Send email

options:
  -h, --help   show this help message and exit
```

## Generate Google OAuth token

With your Google `credentials.json` in the current directory, you can authenticate with Gmail and send an email:

```shell
$ ./gsend.py auth --credentials credentials.json
Please visit this URL to authorize this application: https://accounts.google.com/o/oauth2/auth?....
✅ Auth complete. Token saved to: /Users/erik/.gmail_token.json
```

## Send an email

```shell
$ ./gsend.py send -s "Test email from python" erik@deprutser.be << EOF
> Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
> tempor incididunt ut labore et dolore magna aliqua.
> Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
> aliquip ex ea commodo consequat.
> EOF
✅ Email sent. ID: 196644ff80dd601f
```
