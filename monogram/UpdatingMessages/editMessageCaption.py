from typing import Optional, Union, List

def editMessageCaption(
    chat_id: Optional[Union[int, str]] = None,
    message_id: Optional[int] = None,
    inline_message_id: Optional[str] = None,
    caption: Optional[str] = None,
    parse_mode: Optional[str] = None,
    caption_entities: Optional[List[dict]] = None,
    reply_markup: Optional[dict] = None,
) -> Union[bool, dict]:
    """
    Use this method to edit captions of messages.
    On success, if the edited message is not an inline message, the edited Message is returned,
    otherwise True is returned.

    :param chat_id: Required if inline_message_id is not specified.
                    Unique identifier for the target chat or username of the target channel (in the format @channelusername)
    :param message_id: Required if inline_message_id is not specified.
                       Identifier of the message to edit
    :param inline_message_id: Required if chat_id and message_id are not specified.
                              Identifier of the inline message
    :param caption: New caption of the message, 0-1024 characters after entities parsing
    :param parse_mode: Mode for parsing entities in the message caption. See formatting options for more details.
    :param caption_entities: A JSON-serialized list of special entities that appear in the caption,
                             which can be specified instead of parse_mode
    :param reply_markup: A JSON-serialized object for an inline keyboard.
    :return: If the edited message is not an inline message, the edited Message is returned,
             otherwise True is returned.
    """
    # Your implementation here
    pass