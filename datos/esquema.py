"""
Capa de Datos - Actualización del esquema de bases existentes

db.create_all() crea las tablas que faltan, pero no agrega columnas nuevas a
tablas que ya existen. Sin este módulo, cualquier columna agregada a un modelo
dejaría inutilizable la base local de quien ya tenía un qsec.db creado: las
consultas fallarían con "no such column" hasta borrar la base a mano.
"""
from sqlalchemy import inspect, text


def _columnas_en_base(engine, tabla):
    return {columna['name'] for columna in inspect(engine).get_columns(tabla)}


def agregar_columnas_faltantes(engine, metadata):
    """
    Agrega a las tablas existentes las columnas del modelo que la base no tiene.

    Sólo agrega: nunca borra ni modifica columnas, así que los datos existentes
    no se tocan. Es idempotente: si no falta nada, no hace nada.

    Args:
        engine: engine de SQLAlchemy de la base a actualizar
        metadata: metadata con la definición de los modelos

    Returns:
        list: columnas agregadas, como 'tabla.columna'
    """
    tablas_existentes = set(inspect(engine).get_table_names())
    preparador = engine.dialect.identifier_preparer
    agregadas = []

    for tabla in metadata.sorted_tables:
        if tabla.name not in tablas_existentes:
            continue

        for columna in tabla.columns:
            if columna.name in _columnas_en_base(engine, tabla.name):
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
                agregadas.append(f'{tabla.name}.{columna.name}')
            except Exception:
                # Con varios procesos arrancando a la vez (gunicorn con más de
                # un worker) otro pudo agregarla primero. Sólo es un error si
                # la columna sigue faltando.
                if columna.name not in _columnas_en_base(engine, tabla.name):
                    raise

    return agregadas
