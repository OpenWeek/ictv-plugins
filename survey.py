# -*- coding: utf-8 -*-
#
#    This file belongs to the ICTV project, written by Nicolas Detienne,
#    Francois Michel, Maxime Piraux, Pierre Reinbold and Ludovic Taffin
#    at Universite Catholique de Louvain.
#
#    Copyright (C) 2017  Universite Catholique de Louvain (UCL, Belgium)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import web
from urllib.parse import urlparse

from pyquery import PyQuery

from ictv.ORM.channel import Channel
from ictv.plugin_manager.plugin_capsule import PluginCapsule
from ictv.plugin_manager.plugin_manager import get_logger
from ictv.plugin_manager.plugin_slide import PluginSlide
from ictv.plugin_manager.plugin_utils import MisconfiguredParameters
import json
from pprint import pprint


def get_content(channel_id):
    channel = Channel.get(channel_id)
    logger_extra = {'channel_name': channel.name, 'channel_id': channel.id}
    logger = get_logger('survey', channel)
    question = channel.get_config_param('question')
    author = channel.get_config_param('author')
    answers = channel.get_config_param('answers')
    secret = channel.get_config_param('secret')
    if not question or not answers:
        logger.warning('Some of the required parameters are empty', extra=logger_extra)
        return []
    return [SurveyCapsule(question, author, answers, secret)]


class SurveyCapsule(PluginCapsule):
    def __init__(self, question, author, answers, secret):
        self._slides = [SurveySlide(question, author, answers, secret, channel_id)]

    def get_slides(self):
        return self._slides

    def get_theme(self): #TODO : change that ?
        return None

    def __repr__(self):
        return str(self.__dict__)

class SurveySlide(PluginSlide):
    def __init__(self, question, author, answers, secret):
        current = {
            "id":1,
            "question": question,
            "1": 0,
            "2": 0
        }
        test = True
        try:
            data_file = open('./plugins/survey/survey_questions.json', 'r')
            data = json.load(data_file)
        except IOError:
            data = {
                "questions": [current]
            }
        else:
            nextID = data["questions"][-1]["id"]
            current["id"] = nextID+1
            data["questions"].append(current)

        towrite = open('./plugins/survey/survey_questions.json', 'w')
        #TODO : make flexible

        json.dump(data, towrite, indent=4)
        towrite.close()

        self._duration = 10000000
        self._nb_answers = len(answers)
        if self._nb_answers >= 6:
            self._nb_answers = 5
        self._content = {'title-1': {'text': question}, 'text-0': {'text': author}}
        i = 1
        for answer in answers:
            self._content['text-'+str(i)] = {'text': answer}
            self._content['image-'+str(i)] = {'qrcode': 'web.ctx.homedomain+'/channel/'+str(channel_id)+'/result/'+str(i)'}
            i += 1

        if secret:
            pass #TODO

    def get_duration(self):
        return self._duration

    def get_content(self):
        return self._content

    def get_template(self) -> str:
        if self._nb_answers == 1:
            return 'template-survey-1-answer'
        return 'template-survey-'+str(self._nb_answers)+'-answers'

    def __repr__(self):
        return str(self.__dict__)