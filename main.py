import sys
sys.stdout.reconfigure(encoding="utf-8")

from deepagents import create_deep_agent
from skills.stock_analysis.tools import collect_yfinance_data
from skills.fundamental_analysis.tools import collect_fundamental_indicators
from skills.technical_analysis.tools import collect_technical_indicators
from skills.asset_comparison.tools import compare_assets
from skills.macro_brasil.tools import get_bcb_series, get_ptax_dolar_periodo, get_market_expectations
from skills.macro_global.tools import get_world_bank_indicator, search_world_bank_indicator, compare_countries_latest
from skills.cripto.tools import get_crypto_price, get_crypto_ohlcv, get_crypto_order_book, list_available_exchanges

from dotenv import load_dotenv
load_dotenv()

from deepagents.backends.filesystem import FilesystemBackend

backend = FilesystemBackend(
    root_dir=".",
    virtual_mode=False,   # evita o warning
)

agent = create_deep_agent(
    model="openai:gpt-5-nano",
    tools=[
        collect_yfinance_data,
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
    ],
    skills=["skills"],
    backend=backend,
)

inputs = {"messages": [{"role": "user", "content": "PETR4 está cara ou barata pelos fundamentos?"}]}
# inputs = {"messages": [{"role": "user", "content": "Me dá o RSI e MACD da VALE3"}]}
# inputs = {"messages": [{"role": "user", "content": "Compara PETR4, VALE3 e ITUB4 pra mim"}]}

config = {"configurable": {"thread_id": "investidor_01"}}

for chunk in agent.stream(inputs, config):
    print(chunk)