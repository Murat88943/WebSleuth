import asyncio
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

async def check_site_status(url):
    """Асинхронно проверяет статус код сайта."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return response.status
    except aiohttp.ClientError as e:
        print(f"Ошибка при запросе к сайту: {e}")
        return None

async def find_admin_panel(base_url):
    """Асинхронно пытается подобрать префикс для админ-панели."""
    prefixes = [
        "admin", "dashboard", "panel", "login", "manager",
        "control", "backend", "administrator", "wp-admin", "user"
    ]

    print("Начинаем подбор префиксов для админ-панели...")
    for prefix in prefixes:
        admin_url = f"{base_url}/{prefix}"
        status_code = await check_site_status(admin_url)
        if status_code == 200:
            print(f"Найден префикс: {prefix}, статус код: {status_code}")
            return admin_url
        else:
            print(f"Префикс {prefix} не подошел, статус код: {status_code}")
    print("Подходящий префикс не найден.")
    return None

async def check_favicon(base_url):
    """Асинхронно проверяет наличие favicon."""
    favicon_url = f"{base_url}/favicon.ico"
    status_code = await check_site_status(favicon_url)
    if status_code == 200:
        print(f"Favicon найден: {favicon_url}")
        return True
    else:
        print(f"Favicon не найден, статус код: {status_code}")
        return False

async def check_robots_txt(base_url):
    """Асинхронно проверяет наличие robots.txt."""
    robots_url = f"{base_url}/robots.txt"
    status_code = await check_site_status(robots_url)
    if status_code == 200:
        print(f"robots.txt найден: {robots_url}")
        return True
    else:
        print(f"robots.txt не найден, статус код: {status_code}")
        return False

async def check_sitemap_xml(base_url):
    """Асинхронно проверяет наличие sitemap.xml."""
    sitemap_url = f"{base_url}/sitemap.xml"
    status_code = await check_site_status(sitemap_url)
    if status_code == 200:
        print(f"sitemap.xml найден: {sitemap_url}")
        return True
    else:
        print(f"sitemap.xml не найден, статус код: {status_code}")
        return False

async def download_html(url):
    """Асинхронно скачивает HTML-разметку сайта."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    print(f"HTML-разметка сайта {url} успешно скачана.")
                    return html
                else:
                    print(f"Не удалось скачать HTML-разметку. Статус код: {response.status}")
                    return None
    except aiohttp.ClientError as e:
        print(f"Ошибка при скачивании HTML-разметки: {e}")
        return None

async def test_site(browser):
    if browser == "chrome":
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    elif browser == "firefox":
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    elif browser == "edge":
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
    else:
        print("Неподдерживаемый браузер.")
        return

    # Открываем сайт
    site = input("Введите URL сайта (например, https://example.com): ").strip("/")

    # Создаем словарь для хранения результатов тестов
    test_results = {
        "site_status": None,
        "admin_panel_found": False,
        "favicon_found": False,
        "robots_txt_found": False,
        "sitemap_found": False,
        "admin_panel_url": None,
        "html_downloaded": False,
    }

    # Проверяем статус сайта
    status_code = await check_site_status(site)
    if status_code:
        print(f"Статус код сайта: {status_code}")
        test_results["site_status"] = status_code
    else:
        print("Не удалось получить статус код сайта.")

    # Выполняем 10 тестовых запросов
    print("Выполняем 10 тестовых запросов...")
    for i in range(1, 11):
        status_code = await check_site_status(site)
        if status_code:
            print(f"Запрос {i}: Статус код {status_code}")
        else:
            print(f"Запрос {i}: Не удалось получить статус код.")
        await asyncio.sleep(1)  # Асинхронная пауза между запросами

    # Пытаемся подобрать префикс для админ-панели
    admin_panel_url = await find_admin_panel(site)
    if admin_panel_url:
        print(f"Админ-панель найдена: {admin_panel_url}")
        test_results["admin_panel_found"] = True
        test_results["admin_panel_url"] = admin_panel_url
        # Открываем админ-панель в браузере
        driver.get(admin_panel_url)
        print("Заголовок админ-панели:", driver.title)
    else:
        print("Админ-панель не найдена.")

    # Проверяем наличие favicon
    test_results["favicon_found"] = await check_favicon(site)

    # Проверяем наличие robots.txt
    test_results["robots_txt_found"] = await check_robots_txt(site)

    # Проверяем наличие sitemap.xml
    test_results["sitemap_found"] = await check_sitemap_xml(site)

    # Скачиваем HTML-разметку сайта
    html = await download_html(site)
    if html:
        test_results["html_downloaded"] = True
        # Можно сохранить HTML в файл
        with open("site_html.html", "w", encoding="utf-8") as file:
            file.write(html)
        print("HTML-разметка сохранена в файл site_html.html")
    else:
        print("Не удалось скачать HTML-разметку.")

    # Закрываем браузер
    driver.quit()

    # Выводим сводку тестов
    print("\n=== Сводка тестов ===")
    print(f"Статус код сайта: {test_results['site_status']}")
    print(f"Админ-панель найдена: {test_results['admin_panel_found']}")
    if test_results["admin_panel_found"]:
        print(f"URL админ-панели: {test_results['admin_panel_url']}")
    print(f"Favicon найден: {test_results['favicon_found']}")
    print(f"robots.txt найден: {test_results['robots_txt_found']}")
    print(f"sitemap.xml найден: {test_results['sitemap_found']}")
    print(f"HTML-разметка скачана: {test_results['html_downloaded']}")

async def main():
    # Выбор браузера
    print("Выберите браузер:")
    print("1 - Chrome")
    print("2 - Firefox")
    print("3 - Edge")

    choice = input("Ваш выбор (1/2/3): ")

    if choice == "1":
        await test_site("chrome")
    elif choice == "2":
        await test_site("firefox")
    elif choice == "3":
        await test_site("edge")
    else:
        print("Неправильный выбор.")

# Запуск асинхронной программы
if __name__ == "__main__":
    asyncio.run(main())