"""MCP server exposing FinBrain's skills as tools for any MCP-compatible client."""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

import functools
from contextlib import asynccontextmanager

from fastapi import FastAPI
from langfuse import get_client, observe
from mcp.server.fastmcp import FastMCP

from skills.stock_analysis.tools import collect_yfinance_data
from skills.sentiment_analysis.tools import fetch_discount_coupon
from skills.fundamental_analysis.tools import collect_fundamental_indicators
from skills.technical_analysis.tools import collect_technical_indicators
from skills.asset_comparison.tools import compare_assets
from skills.macro_brasil.tools import get_bcb_series, get_ptax_dolar_periodo, get_market_expectations
from skills.macro_global.tools import get_world_bank_indicator, search_world_bank_indicator, compare_countries_latest
from skills.cripto.tools import get_crypto_price, get_crypto_ohlcv, get_crypto_order_book, list_available_exchanges

mcp = FastMCP("finbrain", stateless_http=True)

LANGCHAIN_TOOLS = [
    collect_yfinance_data,
    fetch_discount_coupon,
    collect_fundamental_indicators,
    collect_technical_indicators,
    compare_assets,
    get_bcb_series,
    get_ptax_dolar_periodo,
    get_market_expectations,
    get_world_bank_indicator,
    search_world_bank_indicator,
    compare_countries_latest,
    get_crypto_price,
    get_crypto_ohlcv,
    get_crypto_order_book,
    list_available_exchanges,
]


def _with_tracing(func, name: str):
    """Wrap a tool function so each call is traced as a Langfuse tool observation."""
    traced_func = observe(name=name, as_type="tool")(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return traced_func(*args, **kwargs)
        finally:
            get_client().flush()

    return wrapper


for langchain_tool in LANGCHAIN_TOOLS:
    mcp.tool(name=langchain_tool.name)(_with_tracing(langchain_tool.func, langchain_tool.name))

mcp_asgi_app = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield


app = FastAPI(lifespan=lifespan)
app.mount("/", mcp_asgi_app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
