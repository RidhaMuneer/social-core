from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    aws_access_key_id: str
    aws_secret_access_key: str
    bucket_name: str
    image_url_domain: str
    redis_hostname: str
    redis_port: int
    redis_username: str
    redis_password: str

    class Config:
        env_file = ".env"
