# InfinityBot
A Discord bot to help people learn the rules of the Infinity RPG.  Requires Python 3.  It is assumed that you know how to create a bot on the Discord side of things and get an API token.  You can find the guide that I followed [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token), but bear in mind that it is now out of date. Breaking changes have been made to the Discord library for Python. 

It is very unlikely that I will respond to support requests.  I coded this up while drunk on a Friday night and then fixed it hungover on a Saturday morning.  It's probably not great code, but it's functional.  Go forth and make it better.

To get the bot up and running on Linux, it's recommended to use <code>virtualenv</code> to set up its own environment.  To get the bot up and running on Windows, you're on your own.  Sorry.  :(

<pre><code>$ mkdir bot && cd bot
$ virtualenv -p python3 envnamevenv
$ source venv/bin/activate
$ pip install discord
</pre></code>

That should be the dependencies set up.  Now clone in the script.

<pre><code>$ git clone https://github.com/fado/InfinityBot.git
$ cd InfinityBot
</pre></code>

Now you need to add your bot's API token to your environment variables.
<pre><code>$ export TOKEN=YourTokenHere
</pre></code>

And you're done.  Just run <code>python bot.py</code> to start the bot.  Note that your token will only be in your environment variables for the duration of your current session.  If you want to add it permanently, you'll need to add it to your <code>.bash_profile</code>.

To add more questions, add a new line to <code>questions.txt</code> in the following format:
<pre><code>Question ID | Question | Answer</pre></code>
FYI, I was too lazy to add any checks to make sure the question IDs were unique.  I probably should have it create the IDs programatically, but like I said, I was drunk.  
