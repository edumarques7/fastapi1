"""Cria somente tabelas ausentes; preserva os dados existentes."""
import asyncio

from core.configs import settings
from core.database import engine


async def create_tables() -> None:
    import models._all_models  # Registra os modelos no metadata.

    print('Verificando tabelas do banco de dados...')
    try:
        async with engine.begin() as conn:
            await conn.run_sync(settings.DBBaseModel.metadata.create_all)
    finally:
        await engine.dispose()
    print('Tabelas prontas; dados existentes preservados.')


if __name__ == '__main__':
    asyncio.run(create_tables())
