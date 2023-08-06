from __future__ import annotations

from io import BytesIO

from databases import Database
from imagehash import ImageHash, average_hash
from PIL import Image
from sqlalchemy import insert, select  # type: ignore[import]

from bayan_bot.tables import ImageHash as ImageHashModel


class ImageChecker:
    def __init__(self, database: Database, cutoff: int) -> None:
        self.database = database
        self.cutoff = cutoff
        self.hashes: list[ImageHash] = []

    @staticmethod
    def get_hash_from_photo(photo: BytesIO) -> ImageHash:
        """Computes average hash from photo that can be used to compare images"""
        return average_hash(Image.open(photo))

    async def load_hashes(self) -> None:
        """Loads hashes from database"""
        query = select(ImageHashModel.hash)
        hashes = await self.database.fetch_all(query)
        self.image_hashes = [
            ImageHash(hash.hash) for hash in hashes  # type: ignore[attr-defined]
        ]

    async def _save_hash(self, image_hash: ImageHash) -> None:
        """Saves hash to database and local state"""
        query = insert(ImageHashModel).values(hash=image_hash.hash)
        await self.database.execute(query)
        self.hashes.append(image_hash)

    async def match_photo_against_other(self, photo: BytesIO) -> bool:
        """Matches photo's hash against other hashes in local state.

        If match is not found - hash is saved to database and local state.

        Returns `True` if match found, otherwise - `False`
        """
        image_hash = ImageChecker.get_hash_from_photo(photo)
        for saved_hash in self.hashes:
            if image_hash - saved_hash < self.cutoff:
                return True

        await self._save_hash(image_hash)
        return False
