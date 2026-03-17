# ebay-automation


python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
playwright install
playwright install-deps
psycopg2


Параллельный запуск (Требование №1):

Теперь вы можете запустить тесты командой: pytest -n 3 --alluredir=reports/allure-results.

Параметр -n 3 (из плагина pytest-xdist) создаст 3 воркера. Каждый воркер вызовет conftest.py, прочитает appsettings.json и создаст свою изолированную сессию.

Матрица браузеров:

Вы можете запускать этот конфиг с разными браузерами через CLI:
pytest --browser chromium
pytest --browser firefox
Когда вы установили pytest-playwright, у вас появились новые команды в терминале.
Если вы напишете pytest --browser chromium --browser firefox, то Pytest запустит каждый ваш тест дважды: один раз в Хроме, другой в Фаерфоксе.

На уровне Senior это часто выносится в CI (GitHub Actions / GitLab CI), где одна и та же папка с тестами запускается в 3 параллельных Job с разными параметрами браузера.


