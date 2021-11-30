import json
import logging
from Utils.redisUtils import getRedisClient

from Utils.cryptoUtils import addDefaultToRedis


def askQuestion(questionObject, botID):
    r = getRedisClient()
    if r.exists(f'openQuestion:{botID}'):
        return "There can only be one question active at a time. Please use !pick to answer the question."
    else:
        r.set(f'openQuestion:{botID}', json.dumps(questionObject))
        questionMessage = [questionObject['text']]
        for option in questionObject['options']:
            questionMessage.append(option['text'])
        questionMessage.append(
            "Respond with !pick followed by the option that should be default.")
        return "\n".join(questionMessage)


def answerQuestion(selectedOption, botID):
    r = getRedisClient()
    if r.exists(f'openQuestion:{botID}'):
        questionObject = json.loads(r.get(f'openQuestion:{botID}'))
        if 'params' in questionObject:
            if len(questionObject['params'].split(',')) > 1:
                raise Exception("Too many params.")
            else:
                param = questionObject['params']
                option = questionObject['options'][selectedOption - 1]
                logging.info(
                    f"Running function {questionObject['callback']}({option[param]})")
                eval(f"{questionObject['callback']}({option[param]})")
                r.delete(f'openQuestion:{botID}')
                return f"Set the default option to {option['text']}. Try your pervious command again."
        else:
            raise Exception("Must pass parameter when answering a question")
    else:
        return "No question has been asked yet"
