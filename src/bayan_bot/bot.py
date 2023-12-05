from __future__ import annotations

import re
from io import BytesIO
from logging import getLogger
from typing import Any

from databases import Database
from httpx import AsyncClient
from sqlalchemy import select, update  # type: ignore[import]

from bayan_bot.image_hashes import ImageChecker
from bayan_bot.tables import State
from bayan_bot.types import FileResponse, MessageData, UpdateResult, UpdatesResponse

logger = getLogger("bayan_bot")


def filter_messages_with_photos(messages: list[MessageData]) -> list[MessageData]:
    """Filters out messages without photos from all bot's relevant messages"""
    messages_with_photos: list[MessageData] = []
    for message in messages:
        if "photo" not in message:
            logger.debug("Message without photo(s), ignoring")
            continue

        messages_with_photos.append(message)

    return messages_with_photos


_makar_regex = re.compile(r".*макар.*", re.IGNORECASE)


def filter_messages_with_makar_mention(
    messages: list[MessageData],
) -> list[MessageData]:
    """Filters out messages that don't mention Makar
    from all bot's relevant messages
    """
    messages_with_makar: list[MessageData] = []
    for message in messages:
        if not re.match(_makar_regex, message.get("text", "")):
            logger.debug("Message without Makar mention, ignoring")
            continue

        messages_with_makar.append(message)

    return messages_with_makar


class KabakBot:
    def __init__(
        self,
        token: str,
        chat_id: int,
        database: Database,
        checker: ImageChecker,
    ) -> None:
        self.offset: int = 0
        self.token: str = token
        self.chat_id: int = chat_id
        self.database = database
        self.checker = checker
        self.api_client = AsyncClient(
            http2=True, base_url=f"https://api.telegram.org/bot{token}"
        )
        self.files_client = AsyncClient(
            http2=True, base_url=f"https://api.telegram.org/file/bot{token}/"
        )

    async def load_state(self) -> None:
        """Loads bot's state from database"""
        query = select(State).where(State.id == 1)
        state = await self.database.fetch_one(query)
        # FOR CHECKERS. We are certain that state exists (if migrations are done)
        assert state is not None  # nosec: B101
        self.offset = state.offset  # type: ignore[attr-defined]

    @property
    def updates_request_params(self) -> dict[str, Any]:
        """Creates query parameters for getUpdates request.

        If offset is set - it will be added to parameters
        """
        params: dict[str, Any] = {
            "allowed_updates": "message",
            "offset": self.offset + 1,
        }
        if not self.offset:
            del params["offset"]

        return params

    async def update_offset(self, offset: int) -> None:
        """Updates offset in database and local state"""
        query = update(State).values(offset=offset).where(State.id == 1)
        await self.database.execute(query)
        self.offset = offset

    def is_relevant_update(self, update: UpdateResult) -> bool:
        """Checks whether update is relevant to bot's functionality.

        Update is relevant if it:
        - is a message
        - is from group chat bot attached to
        - is from real person
        """
        if "message" not in update:
            logger.debug("Not a message update, ignoring")
            return False

        message_data = update["message"]
        if message_data["chat"]["id"] != self.chat_id:
            logger.debug("Message not from group chat, ignoring")
            return False

        if message_data["from"]["is_bot"]:
            logger.debug("Message not from real person, ignoring")
            return False

        if (
            "forward_date" in message_data
            or "forward_from" in message_data
            or "forward_from_chat" in message_data
        ):
            logger.debug("Message is forwarded, ignoring")
            return False

        return True

    async def get_messages(self) -> list[MessageData]:
        """Gets latest relevant messages bot can work with.

        If `getUpdates` request returns not OK status - empty list is returned
        """
        response = await self.api_client.get(
            "/getUpdates", params=self.updates_request_params
        )
        data: UpdatesResponse = response.json()
        if not data["ok"]:
            logger.error("getUpdates response is not OK: %r", data)
            return []

        if not data["result"]:
            logger.debug("No updates...")
            return []

        relevant_messages: list[MessageData] = []
        for upd in data["result"]:
            await self.update_offset(upd["update_id"])
            if not self.is_relevant_update(upd):
                continue

            relevant_messages.append(upd["message"])

        return relevant_messages

    async def get_photo_from_message(self, message: MessageData) -> BytesIO:
        """Finds and downloads biggest photo from message.

        First it finds `file_path` via `getFile` API endpoint,
        then it downloads the file via `api.telegram.org/file` API.

        Returns photo bytes wrapped into `io.BytesIO`.

        Raises `RuntimeError` if something went wrong with `getFile` request
        """
        biggest_photo = max(message["photo"], key=lambda p: p["file_size"])
        response = await self.api_client.get(
            "/getFile", params={"file_id": biggest_photo["file_id"]}
        )
        data: FileResponse = response.json()
        if not data["ok"]:
            logger.error("getFile response is not OK: %r", data)
            raise RuntimeError("getFile response is not OK!")

        file_path = data["result"]["file_path"]
        file_response = await self.files_client.get(file_path)
        # TODO: This may raise if request above failed, handle?
        return BytesIO(file_response.content)

    async def send_warning(self, message: MessageData) -> None:
        """Sends warning as response to message that the meme is not original"""
        logger.warning("Sending warning to: %s", message["message_id"])
        await self.api_client.get(
            "/sendMessage",
            params={
                "chat_id": self.chat_id,
                "reply_to_message_id": message["message_id"],
                "text": "удоли 🪗",
            },
        )

    async def send_marat_correction(self, message: MessageData) -> None:
        """Sends correction as response to message that mentions Makar"""
        logger.warning("Sending correction to: %s", message["message_id"])
        await self.api_client.get(
            "/sendMessage",
            params={
                "chat_id": self.chat_id,
                "reply_to_message_id": message["message_id"],
                "text": "наверное ты имел в виду 'Марат'?🤓",
            },
        )

    async def loop_iteration(self) -> None:
        messages = await self.get_messages()
        if not messages:
            return

        messages_with_photos = filter_messages_with_photos(messages)
        for message in messages_with_photos:
            photo = await self.get_photo_from_message(message)
            if not await self.checker.match_photo_against_other(photo):
                logger.info("Unique photo encountered, ignoring")
                continue

            logger.info("Duplicate photo encountered")
            await self.send_warning(message)

        messages_with_makar = filter_messages_with_makar_mention(messages)
        for message in messages_with_makar:
            logger.info("Correcting user about Makar")
            await self.send_marat_correction(message)
