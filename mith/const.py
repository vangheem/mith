import enum


class EndpointType(str, enum.Enum):
    QUERY = "QUERY"
    MUTATION = "MUTATION"
    RESOLVE_REFERENCE = "RESOLVE_REFERENCE"
