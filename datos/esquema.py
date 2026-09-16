"""
Capa de Datos - Actualización del esquema de bases existentes

db.create_all() crea las tablas que faltan, pero no agrega columnas nuevas a
tablas que ya existen. Sin este módulo, cualquier columna agregada a un modelo
dejaría inutilizable la base local de quien ya tenía un qsec.db creado: las
consultas fallarían con "no such column" hasta borrar la base a mano.
"""
from sqlalchemy import String, inspect, text


def _columnas_en_base(engine, tabla):
    """Mapa columna -> metadata (dict de SQLAlchemy) de una tabla existente."""
    return {columna['name']: columna for columna in inspect(engine).get_columns(tabla)}


def _es_ensanche_seguro(columna_en_base, columna_modelo):
    """True si el modelo sólo agranda un VARCHAR existente, nunca lo angosta
    ni le cambia el tipo: eso sí puede hacerse sin arriesgar los datos."""
    tipo_en_base = columna_en_base['type']
    if not (isinstance(columna_modelo.type, String) and isinstance(tipo_en_base, String)):
        return False
    if columna_modelo.type.length is None or tipo_en_base.length is None:
        return False
    return columna_modelo.type.length > tipo_en_base.length


def _ensanchar_columna(engine, preparador, nombre_tabla, columna):
    """Agranda un VARCHAR existente al tamaño que pide el modelo.

    Sólo se llama para Postgres y MySQL (ver ``agregar_columnas_faltantes``):
    SQLite no impone la longitud declarada (por eso el propio modelo la
    documenta como best-effort) y tampoco soporta ALTER COLUMN TYPE.
    """
    tipo = columna.type.compile(dialect=engine.dialect)
    tabla_q = preparador.quote(nombre_tabla)
    columna_q = preparador.quote(columna.name)

    if engine.dialect.name == 'postgresql':
        sentencia = text(f'ALTER TABLE {tabla_q} ALTER COLUMN {columna_q} TYPE {tipo}')
    else:  # mysql
        nullable = '' if columna.nullable else ' NOT NULL'
        sentencia = text(f'ALTER TABLE {tabla_q} MODIFY COLUMN {columna_q} {tipo}{nullable}')

    with engine.begin() as conexion:
        conexion.execute(sentencia)


def agregar_columnas_faltantes(engine, metadata):
    """
    Agrega a las tablas existentes las columnas del modelo que la base no
    tiene, y ensancha los VARCHAR que se quedaron cortos.

    Nunca borra columnas ni angosta tipos, así que los datos existentes no se
    tocan. Es idempotente: si no falta ni sobra nada, no hace nada.

    Args:
        engine: engine de SQLAlchemy de la base a actualizar
        metadata: metadata con la definición de los modelos

    Returns:
        list: columnas agregadas o ensanchadas, como 'tabla.columna'
    """
    tablas_existentes = set(inspect(engine).get_table_names())
    preparador = engine.dialect.identifier_preparer
    # SQLite no soporta ALTER COLUMN TYPE y tampoco impone la longitud
    # declarada de un VARCHAR, así que ahí ensanchar columnas no tiene sentido.
    soporta_ensanche = engine.dialect.name in ('postgresql', 'mysql')
    cambiadas = []

    for tabla in metadata.sorted_tables:
        if tabla.name not in tablas_existentes:
            continue

        # Una sola consulta de introspección por tabla: antes se repetía por
        # cada columna del modelo, un round-trip evitable en cada boot.
        columnas_en_base = _columnas_en_base(engine, tabla.name)

        for columna in tabla.columns:
            existente = columnas_en_base.get(columna.name)

            if existente is not None:
                if soporta_ensanche and _es_ensanche_seguro(existente, columna):
                    _ensanchar_columna(engine, preparador, tabla.name, columna)
                    cambiadas.append(f'{tabla.name}.{columna.name}')
                continue

            if not columna.nullable:
                # Las filas existentes recibirían la columna vacía, lo que
                # viola un NOT NULL. Se falla explícitamente en lugar de dejar
                # una base a medio actualizar.
                raise RuntimeError(
                    f'No se puede agregar automáticamente {tabla.name}.{columna.name}: '
                    'las columnas nuevas de un modelo existente tienen que ser '
                    'nullable=True.'
                )

            tipo = columna.type.compile(dialect=engine.dialect)
            sentencia = text(
                f'ALTER TABLE {preparador.quote(tabla.name)} '
                f'ADD COLUMN {preparador.quote(columna.name)} {tipo}'
            )
            try:
                with engine.begin() as conexion:
                    conexion.execute(sentencia)
                cambiadas.append(f'{tabla.name}.{columna.name}')
            except Exception:
                # Con varios procesos arrancando a la vez (gunicorn con más de
                # un worker) otro pudo agregarla primero. Sólo es un error si
                # la columna sigue faltando.
                if columna.name not in _columnas_en_base(engine, tabla.name):
                    raise

    return cambiadas
