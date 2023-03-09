# StreamSavior

This Python program uses the Twitch Application API to communicate on your stream's tchat, and display elements on your screen. The reason why I developped it is because Twitch extensions either don't work, or require a Partner Twitch account to work properly. This solution provides almost the same for free.

## Installation

1. You must create a Twitch application on the [Twitch Dev website](https://dev.twitch.tv/console/apps/).
2. Put `https://twitchapps.com/tmi/` as the redirection OAuth URL.
3. Get your client ID from your application's parameter view
4. Fill the empty fields in `config.json` file (*channel*) and `creds.json` (*bot_client_id* & *bot_secret*). **Leave the irc_token field empty**. You may also change the other parameters if you want to (check the config file explanation).
5. Launch the program for the first time `python twitch_app.py`, and follow the given link printed on the console. Get your **IRC token** from there, and put it in `creds.json`.
6. Run the program with `python twitch_app.py`. Add any [argument](#usage) you want.
7. Finally, to be able to see and hear elements on the stream, you have to add the Web source on your streaming software (OBS studio for me). The url is by default `http://localhost:5000`, but you can change the port in the script's arguments. **If the webpage does not work, you must refresh the Source. Most of the time, you must do it after launching the Bot.**

#### **NB:**
- When you stop the bot, it saves all your users with their money in `viewers.json`, so that when you launch it again, it will get back the data for each viewer.
- The bot name doesn't seem to be properly used (problem comes from the Python module used). When the bot connects, it uses your Nickname instead. But this does not change the bot's behaviour.
- There are errors displayed when you stop the bot. Don't worry, they come from the looping routines used by the Bot. The most important thing is that your viewers are correctly saved in `viewers.json` (confirmation message should be before the said errors).

## Usage

```powershell
usage: twitch_app.py [-h] [-p PORT] [-v] [-vv]

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  defines the Flask server port
  -v, --verbose         adds verbosity
  -vv, --mega-verbose   adds maximum verbosity
```

![Example](example.gif)

## Config file explanation (or how can you change things)

### Messages
- `regular_message`: defines the message displayed regularly on the tchat (will not repeat itself if it already sent the message before).
- `regular_message_frequency`: the frequency in **minutes** for the regular_message to be displayed.

### Money system
- `passive_earn`: defines the amount of money a user earn by being on the stream. This is enabled when a user uses the tchat at least once.
- `passive_earn_frequency`: the frequency in **seconds** for the passive_earn to be applied on users.
- `earn_amount`: the amount of money a user get by using the **earn** command.
- `earn_frequency`: the frequency for the **earn** command to be reused by a user.

### Commands
- `gif_price`: the amount of money required to send a gif on the stream.
- `audio_commands`: list of all audio commands, syntaxed like so:
```json
"the_command_name": {
         "price": 100,
         "gif": "the link to a .gif file",
         "audio": "the audio file located in the audio folder"
      }
```

Therefore, if you want to add an audio command, simply add an audio file in the `audio` folder of the repository, and fill a new Json inside `audio_commands`.

## How does it work?

- Basically it connects to the stream with the IRC token, and is able to read and send messages with the Twitch API.
- Furthermore, it launches a local web server (Flask) to serve as a source for any streaming software (the one I used being OBS Studio).
- The web page opened by the streaming software constantly checks for changes to display by sending POST request to the web app.
- When a user uses a command, it is sent to the main Python script. Then the script valids it, and sends a POST request to the web app to apply the changes on the content returned to the web page.