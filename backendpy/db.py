import importlib
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from .configuration import parse_list
from .app import App
from .logging import logging

LOGGER = logging.getLogger(__name__)
Base = declarative_base()


def set_database_hooks(app):

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


def get_db_engine(config, echo=False):
    return create_async_engine(
        'postgresql+asyncpg://{username}:{password}@{host}:{port}/{name}'.format(**config),
        echo=echo, future=True, isolation_level='SERIALIZABLE')


def get_db_session(engine, scope_func):
    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return async_scoped_session(async_session_factory, scopefunc=scope_func)


def create_database(app_config):
    _create_database(app_config)
    _create_tables(app_config)


def _create_database(app_config):
    try:
        LOGGER.info('Start creating database …')
        engine = create_engine('postgresql://{username}:{password}@{host}:{port}'
                               .format(**app_config['database']), echo=True, future=True)
        # Todo: postgresql+asyncpg://
        with engine.connect() as conn:
            conn.connection.connection.set_isolation_level(0)
            conn.execute(text('CREATE DATABASE {}'.format(app_config['database']['name'])))
            conn.commit()
            LOGGER.info('Database creation completed successfully!')
    except Exception as e:
        LOGGER.error(e)
        LOGGER.warning('Database creation excepted')


def _create_tables(app_config):
    try:
        LOGGER.info('Start creating tables …')
        engine = create_engine('postgresql://{username}:{password}@{host}:{port}/{name}'
                               .format(**app_config['database']), echo=True, future=True)
        # Todo: postgresql+asyncpg://
        _import_models(app_config)
        Base.metadata.create_all(bind=engine)
        LOGGER.info('Tables creation completed successfully!')
    except Exception as e:
        LOGGER.error(e)


def _import_models(app_config):
    try:
        for package_name in parse_list(app_config['apps']['active']):
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
