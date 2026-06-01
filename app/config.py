from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # The only thing that selects the backend. Override in .env.
    #   SQLite: sqlite:///./flask_app.db            (default — zero setup)
    #   MySQL:  mysql+pymysql://<user>:<password>@<host>:<port>/<database>
    database_url: str = "sqlite:///./flask_app.db"


settings = Settings()
