def run(data, botID, send):
    message = data['text']

    if message == '!test':
        send(
            "Hi there! Your bot is working, you should start customizing it now.", botID)
        return True

    return False
