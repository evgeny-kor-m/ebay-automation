# ebay-automation

## Prerequisite
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
playwright install
playwright install-deps
# psycopg2
```

## To Learn
```
Параллельный запуск (Требование №1):
Теперь вы можете запустить тесты командой: pytest -n 3 --alluredir=reports/allure-results.
Параметр -n 3 (из плагина pytest-xdist) создаст 3 воркера. Каждый воркер вызовет conftest.py, прочитает appsettings.json и создаст свою изолированную сессию.
Матрица браузеров:
Вы можете запускать этот конфиг с разными браузерами через CLI:
pytest --browser chromium
pytest --browser firefox
Когда вы установили pytest-playwright, у вас появились новые команды в терминале.
Если вы напишете pytest --browser chromium --browser firefox, то Pytest запустит каждый ваш тест дважды: один раз в Хроме, другой в Фаерфоксе.

это часто выносится в CI (GitHub Actions / GitLab CI), где одна и та же папка с тестами запускается в 3 параллельных Job с разными параметрами браузера.
```

## To run
python -m pytest tests/test_search_cart.py --alluredir=reports/allure-results
```
```







# EXECUTION

1. Installation (in WSL)

Must install it inside WSL, in the same location as your project:
```
curl -fsSL https://claude.ai/install.sh | bash
# open a new terminal
claude --version
claude doctor                           # installation diagnostics
```
2. Playwright MCP

Required for DOM exploration in Phase 3. It necessitates Node (npx):

```
node --version       # if not installed, set up Node LTS via nvm
claude mcp add --scope project playwright -- npx @playwright/mcp@latest
```

Using the --scope project flag, the configuration is saved to a .mcp.json file in the repository root. 
You should commit this file; it represents the visible component of your agentic workflow.

