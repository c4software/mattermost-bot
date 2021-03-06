# -*- coding: utf-8 -*-
from commands.libs.decorators import register_as_command
import random
import codecs
import operator
import difflib

from commands.libs.context import mark_for_awaiting_response, get_awaiting_response
from tools.libs import username_or_channel, get_username


class quizz():
    quizz_question = ""
    quizz_reponse = ""
    quizz_tabscore = {}


def get_question():
    f = codecs.open("data/quizz_general.txt", 'r', "iso-8859-1")
    questions = f.read().splitlines()
    choice = random.choice(questions).split("\\")
    quizz.quizz_question = choice[0]
    quizz.quizz_reponse = choice[1].lstrip().rstrip()
    f.close()
    return "> " + quizz.quizz_question


def say_indice():
    if quizz.quizz_question:
        try:
            indice = ''.join(i if random.randint(0, 1) else '_' for i in quizz.quizz_reponse)
            return "Un indice: ``` {0} ```".format(indice)
        except:
            return "Pas d'indice..."
    else:
        return "Aucun quizz en cours"


@register_as_command("question", "C'est parti ! (Pour répondre ! r ma réponse", "Quizz")
def cmd_quizzstart(msg):
    mark_for_awaiting_response(username_or_channel(msg), "r")
    return get_question()


@register_as_command("indice", "Quizz un indice", "Quizz")
def cmd_indice(msg):
    mark_for_awaiting_response(username_or_channel(msg), "r")
    return say_indice()


@register_as_command("stop", "Quizz un indice", "Quizz")
def cmd_stop(msg):
    quizz.quizz_reponse = ""
    quizz.quizz_question = ""
    return "Arret du quizz"


@register_as_command("r", "r votre réponse", "Quizz")
def cmd_quizzreponse(msg):
    mark_for_awaiting_response(username_or_channel(msg), "r")
    username = get_username(msg)

    reponse = msg["query"]

    if reponse.strip().lower() == quizz.quizz_reponse.strip().lower():
        try:
            score = quizz.quizz_tabscore[username]
            quizz.quizz_tabscore[username] = score + 1
        except:
            quizz.quizz_tabscore[username] = 1

        return 'Bravo! Bonne reponse {0} \r\nQuestion suivante : \r\n {1}'.format(username, get_question())
    else:
        # Test si la reponse s'approche
        if difflib.SequenceMatcher(None, quizz.quizz_reponse.strip().lower(), reponse.strip().lower()).ratio() > 0.7:
            return 'Ah {0} pas loin!'.format(username)
        else:
            # Si ce n'est pas la bonne reponse et que la reponse est eloigne
            if random.randint(0, 20) == 10:  # pragma: no cover
                # tous les quelques messages on diffuse soit un indice, soit la question
                if random.choice(['indice', 'question']) == "indice":
                    return say_indice()
                else:
                    return quizz.quizz_question
            else:
                return ""


@register_as_command("score", "Affiche les scores", "Quizz")
def cmd_quizzscore(msg):
    mark_for_awaiting_response(username_or_channel(msg), "r")
    string_score = ""
    for user in quizz.quizz_tabscore:
        string_score = string_score + " \r\n " + str(user) + " : " + str(quizz.quizz_tabscore[user])

    if string_score:
        return "Score : {0}".format(string_score)
    else:
        return "Aucun historique de quizz."
