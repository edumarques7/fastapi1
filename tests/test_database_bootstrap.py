"""Execute apenas em banco de teste, com TEST_DATABASE_URL definida."""
import asyncio
import os
from pathlib import Path
import subprocess
import sys
import unittest
import uuid

import asyncpg


@unittest.skipUnless(os.getenv('TEST_DATABASE_URL'), 'Defina TEST_DATABASE_URL para um banco de teste')
class DatabaseBootstrapTest(unittest.TestCase):
    def test_repeated_bootstrap_preserves_user_and_article(self):
        async def scenario():
            url = os.environ['TEST_DATABASE_URL']
            env = dict(os.environ, DB_URL=url, JWT_SECRET='bootstrap-test-secret',
                       PYTHONDONTWRITEBYTECODE='1')

            def bootstrap():
                subprocess.run(
                    [sys.executable, 'criar_tabelas.py'],
                    cwd=Path(__file__).resolve().parents[1], env=env, check=True,
                )

            bootstrap()
            conn = await asyncpg.connect(url.replace('postgresql+asyncpg://', 'postgresql://', 1))
            user_id = article_id = None
            try:
                user_id = await conn.fetchval(
                    'INSERT INTO usuarios (nome, sobrenome, email, senha, eh_admin) '
                    'VALUES ($1, $2, $3, $4, false) RETURNING id',
                    'Bootstrap', 'Teste', f'{uuid.uuid4()}@example.com', 'test-only-hash',
                )
                article_id = await conn.fetchval(
                    'INSERT INTO artigos (titulo, descricao, url_fonte, usuario_id) '
                    'VALUES ($1, $2, $3, $4) RETURNING id',
                    'Preservar', 'Conteúdo de teste', 'https://example.com/test', user_id,
                )
                bootstrap()
                bootstrap()
                self.assertEqual(await conn.fetchval('SELECT nome FROM usuarios WHERE id=$1', user_id), 'Bootstrap')
                article = await conn.fetchrow('SELECT titulo, usuario_id FROM artigos WHERE id=$1', article_id)
                self.assertIsNotNone(article)
                self.assertEqual(article['titulo'], 'Preservar')
                self.assertEqual(article['usuario_id'], user_id)
            finally:
                if article_id is not None:
                    await conn.execute('DELETE FROM artigos WHERE id=$1', article_id)
                if user_id is not None:
                    await conn.execute('DELETE FROM usuarios WHERE id=$1', user_id)
                await conn.close()

        asyncio.run(scenario())
