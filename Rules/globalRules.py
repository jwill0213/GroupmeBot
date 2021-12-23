import logging


def run(data, botID, send):
    message = data['text']

    try:
        match message.split(' '):
            case ['!test']:
                send(
                    "Hi there! Your bot is working, you should start customizing it now.", botID)
                return True
    except Exception:
        logging.error(
            f"Unhandled exception with command {data}", exc_info=True)
        send("Problem executing your command. Paging ", botID, [
             {'tag': '@Jordan Williams', 'id': 7405778}])

    return False
