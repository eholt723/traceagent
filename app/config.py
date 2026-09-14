from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str = ""
    tavily_api_key: str = ""
    database_url: str = ""
    groq_model: str = "openai/gpt-oss-120b"
    max_search_loops: int = 3
    search_results_per_query: int = 5

    # Per-IP rate limit on run-creating endpoints (POST /runs, /runs/{id}/fork).
    # Set run_rate_limit to 0 to disable.
    run_rate_limit: int = 3
    run_rate_limit_window_seconds: int = 600

    # AWS / CloudWatch — optional, only active when credentials are set
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    cloudwatch_log_group: str = "traceagent"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
