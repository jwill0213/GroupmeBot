import json
import logging
from Utils.redisUtils import getRedisClient

from Utils.cryptoUtils import addDefaultToRedis


def askQuestion(questionObject, botID):
    r = getRedisClient()
    if r.hexists(botID, "openQuestion"):
        return "There can only be one question active at a time. Please use !pick to answer the question."
    else:
        r.hset(botID, "openQuestion", json.dumps(questionObject))
        questionMessage = [questionObject["text"]]
        for option in questionObject["options"]:
            questionMessage.append(option["text"])
        questionMessage.append(
            "Respond with !pick followed by the option that should be default."
        )
        return "\n".join(questionMessage)


def answerQuestion(selectedOption, botID):
    r = getRedisClient()
    if r.hexists(botID, "openQuestion"):
        questionObject = json.loads(r.hget(botID, "openQuestion"))
        option = questionObject["options"][selectedOption - 1]
        logging.info(
            f"Running function {questionObject['callback']}({option['params']})"
        )
        eval(f"{questionObject['callback']}(*{option['params']})")
        r.hdel(botID, "openQuestion")
        return f"Set the default option to {option['text']}. Try your pervious command again."
    else:
        return "No question has been asked yet"
