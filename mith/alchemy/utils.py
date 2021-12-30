import typing

from sqlalchemy.dialects.postgresql import pypostgresql
from sqlalchemy.sql.elements import ClauseElement

sqlalchemy_dialect = pypostgresql.dialect(paramstyle="pyformat")
sqlalchemy_dialect.implicit_returning = True
sqlalchemy_dialect.supports_native_enum = True
sqlalchemy_dialect.supports_smallserial = True
sqlalchemy_dialect._backslash_escapes = False  # type: ignore
sqlalchemy_dialect.supports_sane_multi_rowcount = True
sqlalchemy_dialect._has_native_hstore = True  # type: ignore
sqlalchemy_dialect.supports_native_decimal = True


def compile_sql(
    query: ClauseElement, schema: typing.Optional[str] = None
) -> typing.Tuple[str, list, tuple]:

    compile_kwargs = {}
    if schema is not None:
        compile_kwargs.update(
            {
                "schema_translate_map": {None: schema},
                "render_schema_translate": True,
            }
        )

    compiled = query.compile(
        dialect=sqlalchemy_dialect,
        compile_kwargs={"render_postcompile": True},
        **compile_kwargs
    )
    compiled_params = sorted(compiled.params.items())

    mapping = {key: "$" + str(i) for i, (key, _) in enumerate(compiled_params, start=1)}
    compiled_query = compiled.string % mapping

    processors = compiled._bind_processors  # type: ignore
    args = [
        processors[key](val) if key in processors else val
        for key, val in compiled_params
    ]

    result_map = compiled._result_columns  # type: ignore

    return compiled_query, args, result_map
