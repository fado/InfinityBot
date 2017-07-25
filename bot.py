"""
    InfinityBot - A Discord bot to help people learn the rules of the Infinity RPG.
    Copyright (C) 2017 Padraig Donnelly
    pdonnelly@runbox.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    https://opensource.org/licenses/GPL-3.0
"""

import discord
import logging
import os
import random
import time

from discord.ext import commands

# BOT STUFF
log = logging.getLogger()
description = '''InfinityBot!  Learning is fun!'''
# You can set the command prefix here.  In the default cause '.quiz' will invoke the bot.
bot = commands.Bot(command_prefix='.', description=description, pm_help=True)
client = discord.Client()

# QUIZ STUFF
lines = []
recent_questions  = []
question_pending = False
current_question = ""
current_answer = ""
scores = {}
pass_pending = False


@bot.event
async def on_ready():
    log.info("Logged in as {0} with ID {1}".format(bot.user.name, bot.user.id))
    bot.start_time = time.time()


@bot.event
async def on_message(message):
    """
    Parses all incoming messages.  Ignores itself.  Checks to see if the last message was the answer to the
    current question, otherwise it does some other bits of fun parsing.
    :param message: The last message typed into the channel.
    :return:
    """
    global question_pending, current_answer, punch_counter, scores, player_passing, pass_pending

    # Stop the bot from responding to its own utterences.
    if message.author.bot:
        return

    # Only run this block if there is a question pending.
    if question_pending:

        # Check if the answer was correct.
        await check_answer(message)

        # Or check if someone is trying to initiate a skip.
        if str(message.content).lower() == 'yes':
            await skip_question(message)

    # Otherwise just process as normal.
    await bot.process_commands(message)


@bot.command()
async def quiz():
    """
    Handles the behaviour of the .quiz command.  Will select a question at random, then remove it from the list
    so that it doesn't get asked again in the current round.  If there is already a question pending, it will
    let the players know and repeat the question in case they missed it.
    :return:
    """
    global question_pending, current_question, current_answer, lines

    # Make sure we're not waiting for an answer already.
    if question_pending:
        await bot.say("You haven't answered my last question yet:")
        await bot.say(current_question)
    else:
        # Pick one of the remaining questions at random.
        random_line = random.choice(lines)

        # Tokenize the line.
        tokens = random_line.split('|')
        question_id = str(tokens[0])
        current_question = str(tokens[1])
        current_answer = str(tokens[2])

        # Let's see the answer in the console just for the hell of it.
        log.info(current_answer.split(','))

        # Verify which question we picked.
        log.info("Chose question "+ question_id +" at random.")

        # Now remove it from the list so it doesn't get asked again soon.
        log.info("Removing question from the list.")
        lines.remove(random_line)

        # Verify that it's gone.
        remaining_question_ids = []
        for line in lines:
            remaining_question_ids.append(line.split('|')[0])

        # We now have a question pending so let's make a note of that.
        question_pending = True

        # Ask the question.
        await bot.say(current_question)


@bot.command(pass_context=True)
async def score(ctx):
    """
    Show the current score.
    :return:
    """
    await show_scores(ctx.message)


@bot.command(pass_context=True)
async def skip(ctx):
    """
    Allows the player to skip a question.
    :return:
    """
    global pass_pending, player_passing

    if question_pending:
        await bot.say("Are you sure you want to skip this question?  It will cost you 1 point!  (Type 'yes' to skip.)")
        pass_pending = True
        player_passing = ctx.message.author.name
    else:
        await bot.say("I haven't asked you a question yet...  (Type '.quiz'.)")


async def check_answer(message):
    """
    Tests if the current message is the answer to the current question.
    :param message:
    :return:
    """
    global scores, question_pending, pass_pending

    # Check if the current message is the answer to the question.
    if str(message.content).lower() in str(current_answer.split(',')).lower():

        # Let's just get their name to make the following code a bit cleaner.
        scorer = str(message.author.name)

        # If they're not already in the scores dict, add them.
        if scorer not in scores.keys():
            scores[scorer] = 1

        # Otherwise just increase their score by one.
        else:
            scores[scorer] = scores[scorer] + 1

        # Let's clean up.
        question_pending = False
        pass_pending = False

        # And show the scores.
        await show_scores(message)

        # Report that the correct answer has been given.
        log.info("Correct answer given.")
        await bot.send_message(message.channel, "Correct!")
        await bot.send_message(message.channel, "This is the part where I give **" +
                               str(message.author.name) + "** a point.")

        # Make sure the size of the question pool isn't zero.  If it is, announce winner and reset.
        if len(lines) == 0:
            await bot.send_message(message.channel, "All the questions have been answered!")
            await bot.send_message(message.channel, "Winner is: " + str(max(scores, key=scores.get)))
            await bot.send_message(message.channel, "Resetting!")

            # Add all the questions back in.
            init_questions()

            # Reset the scores.
            scores = {}


async def skip_question(message):
    """
    Skip the current question. Deduct a point from the player skipping.
    :return:
    """
    global question_pending, pass_pending

    # Make sure the person reasponding is the person who initiated the skip.
    if str(message.author.name) == player_passing:
        await bot.send_message(message.channel, "Alright.  Skipping this question.  Will deduct one point"
                                                " from **" + str(message.author.name) + "**.")

        # Let's just get their name to make the following code a bit cleaner.
        scorer = str(message.author.name)

        # If they're not already on the board, start them with -1 points.
        if scorer not in scores.keys():
            scores[scorer] = -1

        # Otherwise just decrease their score by one.
        else:
            scores[scorer] = scores[scorer] - 1

        # Let's clean up.
        question_pending = False
        pass_pending = False

        # Again, can't figure out how to do this the DRY wait yet, so repeating myself.  Sorry.
        # Announce the current scores.
        score_string = ""
        for scorer in scores.keys():
            score_string += "**" + scorer + "**: " + str(scores[scorer]) + " "
        await bot.send_message(message.channel, "Scores: " + score_string)

        # Tell them the answer.
        await bot.send_message(message.channel, "Answer was: **" + current_answer + "**.")
    else:
        await bot.send_message(message.channel, "You did not initiate this skip " + str(message.author.name) + "!")


async def show_scores(message):
    """
    Announce the current scores.
    :return:
    """
    if len(scores) == 0:
        await bot.say("No scores yet!")
    else:
        score_string = ""
        for scorer in scores.keys():
            score_string += "**" + scorer + "**: " + str(scores[scorer]) + " "
        await bot.send_message(message.channel, "Scores: " + score_string)


def init_questions():
    """
    Reads the questions in from a text file.  Catches FileNotFoundError.
    :return:
    """
    global lines

    try:
        lines = open('questions.txt').read().splitlines()
    # Make sure the file is actually there.
    except FileNotFoundError:
        log.warn('Question file not found.')


if __name__ == '__main__':
    formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    log.addHandler(consoleHandler)

    logging.getLogger("discord").setLevel(logging.WARN)
    log.setLevel(logging.INFO)
    log.info('Starting InfinityBot.')

    init_questions()

    try:
        # Replace 'TOKEN' here with the name of the environment variable you are using to store your API token.
        bot.run(os.environ['TOKEN'])
    except KeyError:
        log.warn('Environment variable not found.')
    except KeyboardInterrupt:
        log.warn('Stopping InfinityBot.')
