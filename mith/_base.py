import abc


class BaseRepository:
    @abc.abstractmethod
    async def initialize(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def finalize(self) -> None:
        raise NotImplementedError
