import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

def check_scam_message(message, seen_num):
    logger.debug('check_scam_message function called')
    pass

def generate_check_scam_prompt(scam_message: str, seen_num: int) -> str:
    logger.debug('generate_check_scam_prompt function called')

    prompt = f""""
    I need help discerning if the following message is a scam message or not. You are a helpful scam detection bot working within a scam detection program.
    As part of this program, many people ask you for help regarding scams and also send you possible scam messages.
    You have a database that tracks all the possible scam messages that all your users have ever submitted and the following submitted message has been seen a total of {seen_num} time(s).
    This is the following message which was received either on a social media platform, text, or other common messaging platforms: {scam_message}
    Please tell me whether or not you think this is indeed a scam message depending on the contents of the message and the number of times it has been submitted by other users.
    """
    return prompt