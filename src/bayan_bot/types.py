from __future__ import annotations

from typing import NotRequired, Required

from typing_extensions import TypedDict


class ChatData(TypedDict):
    id: Required[int]


class FromData(TypedDict):
    is_bot: Required[bool]


class PhotoData(TypedDict):
    file_size: Required[int]
    file_id: Required[str]


# Using functional syntax because of "from" key, which is a keyword
MessageData = TypedDict(
    "MessageData",
    {
        "chat": Required[ChatData],
        "from": Required[FromData],
        "message_id": Required[int],
        "photo": NotRequired[list[PhotoData]],
        "text": NotRequired[str],
    },
)


class UpdateResult(TypedDict):
    update_id: Required[int]
    message: NotRequired[MessageData]


class UpdatesResponse(TypedDict):
    ok: Required[bool]
    result: Required[list[UpdateResult]]


class FileResult(TypedDict):
    file_path: Required[str]


class FileResponse(TypedDict):
    ok: Required[bool]
    result: Required[FileResult]
