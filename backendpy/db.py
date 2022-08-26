from __future__ import annotations

import asyncio
import importlib
from collections.abc import Mapping

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from .app import App
from .logging import get_logger

LOGGER = get_logger(__name__)
Base = declarative_base()


def set_database_hooks(app):
    """Attach Sqlalchemy engine and session to the project with hooks."""

    @app.event('startup')
    async def on_startup():
        app.context['db_engine'] = get_db_engine(config=app.config['database'], echo=False)
        app.context['db_session'] = get_db_session(engine=app.context['db_engine'], scope_func=app.get_current_request)

    @app.event('shutdown')
    async def on_shutdown():
        await app.context['db_engine'].dispose()

    @app.event('request_end')
    async def on_request_end():
        await app.context['db_session'].remove()


def get_db_engine(config: Mapping, echo: bool = False):
    """Create a new Sqlalchemy async engine instance."""

    return create_async_engine(
        'postgresql+asyncpg://{username}:{password}@{host}:{port}/{name}'.format(**config),
        echo=echo, future=True, isolation_level='SERIALIZABLE')


def get_db_session(engine: AsyncEngine, scope_func: callable):
    """Construct a new Sqlalchemy async scoped session."""

    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return async_scoped_session(async_session_factory, scopefunc=scope_func)


def create_database(app_config: Mapping):
    """Create Backendpy project database and tables based on applications models."""

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_create_database(app_config))
    loop.run_until_complete(_create_tables(app_config))


async def _create_database(app_config: Mapping):
    try:
        LOGGER.info('Start creating database …')
        engine = create_async_engine(
            'postgresql+asyncpg://{username}:{password}@{host}:{port}'.format(**app_config['database']),
            echo=True, future=True, isolation_level='AUTOCOMMIT')
        async with engine.connect() as conn:
            await conn.execute(text('CREATE DATABASE {}'.format(app_config['database']['name'])))
            LOGGER.info('Database creation completed successfully!')
        await engine.dispose()
    except Exception as e:
        LOGGER.error(e)
        LOGGER.warning('Database creation excepted')


async def _create_tables(app_config: Mapping):
    try:
        LOGGER.info('Start creating tables …')
        engine = create_async_engine(
            'postgresql+asyncpg://{username}:{password}@{host}:{port}/{name}'.format(**app_config['database']),
            echo=True, future=True)
        async with engine.begin() as conn:
            _import_models(app_config)
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()
        LOGGER.info('Tables creation completed successfully!')
    except Exception as e:
        LOGGER.error(e)


def _import_models(app_config: Mapping):
    try:
        for package_name in app_config['apps']['active']:
            try:
                app = getattr(importlib.import_module(f'{package_name}.main'), 'app')
                if isinstance(app, App):
                    for model_path in app.models:
                        try:
                            importlib.import_module(model_path)
                        except ImportError:
                            LOGGER.error(f'models "{model_path}" import error')
                else:
                    LOGGER.error(f'app "{package_name}" instance error')
            except (ImportError, AttributeError):
                LOGGER.error(f'app "{package_name}" instance import error')
    except Exception as e:
        LOGGER.error(f'Failed to get app models: {e}')
