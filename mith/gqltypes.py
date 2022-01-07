from pydantic import BaseModel
from typing import Optional, List, Union, TypeVar


class ErrorType(BaseModel):
    reason: Optional[str] = None
    message: Optional[str] = None


class NotFoundErrorType(ErrorType):
    ...


class AuthorizationErrorType(ErrorType):
    ...


class Success(BaseModel):
    id: Optional[str] = None
    info: Optional[str] = None


GQLAnnotation = TypeVar("GQLAnnotation")


def GraphQLUnion(type_: GQLAnnotation, name: str) -> GQLAnnotation:
    type_.__mith_gql_name__ = name
    type_.__mith_gql_type__ = "UNION"
    return type_


ErrorTypes = GraphQLUnion(
    Union[ErrorType, NotFoundErrorType, AuthorizationErrorType], "ErrorTypes"
)
GenericResponseType = GraphQLUnion(
    Union[ErrorType, NotFoundErrorType, AuthorizationErrorType, Success],
    "GenericResponseType",
)


class Node(BaseModel):
    ...


class BaseEdge(BaseModel):
    node: Node
    cursor: str


class PageInfo(BaseModel):
    hasNextPage: bool
    endCursor: Optional[str] = None


class Pagination(BaseModel):
    totalCount: Optional[int] = None
    pageInfo: PageInfo
    edges: List[BaseEdge]
