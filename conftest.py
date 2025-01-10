# Copyright (c) 2024 Blue Brain Project/EPFL
#
# SPDX-License-Identifier: Apache-2.0


import logging
import os
import sys
from io import BytesIO

import pytest
from PIL import Image
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from pages.login_page import LoginPage
from util.util_base import load_config


@pytest.fixture(scope="class", autouse=True)
def setup(request, pytestconfig):
    """Fixture to set up the browser/webdriver"""
    environment = pytestconfig.getoption("env")
    env_url = pytestconfig.getoption("env_url")
    browser_name = pytestconfig.getoption("--browser-name")
    print(f"Environment passed: {environment}")
    print(f"Environment passed: {env_url}")
    print(f"Environment passed: {browser_name}")
    browser = None
    base_url = None

    if environment == "sauce-labs":

        print("Setting up Sauce Labs environment")
        if not os.environ.get("SAUCE_USERNAME") or not os.environ.get("SAUCE_ACCESS_KEY"):
            raise ValueError("Sauce Labs credentials (SAUCE_USERNAME, SAUCE_ACCESS_KEY) are required")
        options = ChromeOptions()
        options.browser_version = 'latest'
        options.platform_name = 'Windows 10'

        sauce_options = {
            'username': os.environ["SAUCE_USERNAME"],
            'accessKey': os.environ["SAUCE_ACCESS_KEY"],
            'name': request.node.name  # Sauce job name
        }

        print(f"SAUCE_USERNAME: {os.environ.get('SAUCE_USERNAME')}")
        print(f"SAUCE_ACCESS_KEY: {os.environ.get('SAUCE_ACCESS_KEY')}")

        options.set_capability('sauce:options', sauce_options)
        print(f"Sauce Labs Options: {options.to_capabilities()}")
        if environment == "sauce-labs" and env_url == "staging":
            base_url = "https://staging.openbrainplatform.com"
        elif environment == "sauce-labs" and env_url == "production":
            base_url = "https://openbluebrain.com/"
        else:
            raise ValueError(f"Invalid `--env_url` for Sauce Labs: {env_url}")

        sauce_url = "https://ondemand.eu-central-1.saucelabs.com:443/wd/hub"
        print(f"Using Sauce Labs URL: {sauce_url}")
        browser = webdriver.Remote(command_executor=sauce_url, options=options)

    else:
        if browser_name == "chrome":
            options = ChromeOptions()
            if pytestconfig.getoption("--headless"):
                options.add_argument("--headless")
            browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        elif browser_name == "firefox":
            options = FirefoxOptions()
            if pytestconfig.getoption("--headless"):
                options.add_argument("--headless")
            browser = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

        elif browser_name == "safari":
            options = SafariOptions()
            if pytestconfig.getoption("--headless"):
                options.add_argument("--headless")
            browser = webdriver.Safari(service=SafariService(), options=options)
        else:
            raise ValueError(f"Unsupported browser: {browser_name}")

        if environment == "staging":
            base_url = "https://staging.openbrainplatform.com/"
        elif environment == "production":
            base_url = "https://openbluebrain.com/"
        else:
            raise ValueError(f"Invalid `--env_url` for Sauce Labs: {env_url}")

    browser.set_page_load_timeout(60)
    wait = WebDriverWait(browser, 20)

    if browser is not None:
        browser.set_window_position(-1000, 0)
        browser.maximize_window()
    browser.delete_all_cookies()

    request.cls.browser = browser
    request.cls.wait = wait
    request.cls.base_url = base_url
    yield browser, wait, base_url

    if browser is not None:
        if environment == "sauce-labs":
            sauce_result = "failed" if request.session.testsfailed == 1 else "passed"
            browser.execute_script(f"sauce:job-result={sauce_result}")
        browser.quit()


@pytest.fixture(scope="function")
def logger(request):
    """Fixture to initialize the logger object"""
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)

    project_root = os.path.abspath(os.path.dirname(__file__))
    allure_reports_dir = os.path.join(project_root, "allure_reports")
    log_file_path = os.path.join(allure_reports_dir, "report.log")
    if not os.path.exists(allure_reports_dir):
        os.makedirs(allure_reports_dir)

    # Check if logger already has handlers
    if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
        file_handler = logging.FileHandler(filename=log_file_path)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter("%(levelname)s : %(asctime)s : %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_formatter = logging.Formatter("\n%(levelname)s : %(asctime)s : %(message)s")
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)

    logger.info('Test started')

    def log_test_finish():
        logger.info('Test finished')

    request.addfinalizer(log_test_finish)

    return logger


@pytest.fixture(scope="function")
def navigate_to_login(setup):
    """Fixture that navigates to the login page"""
    browser, wait, base_url = setup
    login_page = LoginPage(browser, wait, base_url)

    username = os.environ.get("OBI_USERNAME")
    password = os.environ.get("OBI_PASSWORD")

    if not username or not password:
        raise ValueError("Missing USERNAME or PASSWORD environment variables.")

    target_url = login_page.navigate_to_homepage()
    browser.execute_script("window.stop();")
    print(f"conftest.py fixture - Navigated to: {target_url}")

    login_button = login_page.find_login_button()
    assert login_button.is_displayed()
    login_button.click()
    wait.until(EC.url_contains("auth"))
    return login_page


@pytest.fixture(scope="function")
def login(setup, navigate_to_login):
    """Fixture to log in and ensure user is authenticated."""
    browser, wait, base_url = setup
    login_page = navigate_to_login

    config = load_config()
    if not config:
        raise ValueError("Failed to load configuration")
    username = config.get('username')
    password = config.get('password')

    if not username or not password:
        raise ValueError("Username or password is missing in the configuration!")

    login_page.perform_login(username, password)
    login_page.wait_for_login_complete()
    assert "/app/explore" in browser.current_url, f"Login failed, current URL: {browser.current_url}"
    print("Login successful. Current URL:", browser.current_url)
    yield browser, wait
    login_page.browser.delete_all_cookies()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """
    Pytest hook implementation to handle test reporting.

    - Captures screenshots when a test fails.
    - Embeds the screenshot into the HTML report.
    """
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])

    if report.when == 'call' or report.when == "setup":
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            print("Test failed - handling it")

            project_root = os.path.abspath(os.path.dirname(__file__))
            error_logs_dir = os.path.join(project_root, "latest_logs", "errors")
            os.makedirs(error_logs_dir, exist_ok=True)

            test_name = report.nodeid.replace("::", "_").split("/")[-1]
            file_name = os.path.join(error_logs_dir, test_name + ".png")
            print(f"Intended screenshot path: {file_name}")

            browser = None
            if hasattr(item, "cls"):
                browser = getattr(item.cls, "browser", None)
            if not browser:
                browser = getattr(item, "_browser", None)
                print(f"Browser found in item attribute")

            if browser:
                try:
                    print("Browser object found - making screenshot")
                    _capture_screenshot(file_name, browser)
                    if os.path.exists(file_name):
                        print(f"Screenshot successfully saved at: {file_name}")
                        html = ('<div><img src="%s" alt="screenshot" '
                                'style="width:304px;height:228px;" onclick="window.open(this.src)" '
                                'align="right"/></div>') % os.path.relpath(file_name)
                        extra.append(pytest_html.extras.html(html))
                    else:
                        print(f"Screenshot not found at: {file_name}")
                except Exception as e:
                    print(f"Exception occurred while capturing screenshot: {e}")
            else:
                print("No browser object found - skipping screenshot capture")

        report.extra = extra


def _capture_screenshot(name, browser):
    """
        Helper function to capture and save a screenshot.

        - Ensures the target directory exists.
        - Uses the browser object to capture a full-page screenshot.
        :param name: The full path where the screenshot will be saved.
        :param browser: The browser object used for screenshot capture.
        """
    try:
        print(f"Creating error  directory at:{os.path.dirname(name)}")
        os.makedirs(os.path.dirname(name), exist_ok=True)
        print(f"Saving screenshot to: {name}")
        # browser.get_full_page_screenshot_as_file(name)
        browser.save_screenshot(name)
        print(f"Screenshot captured: {name}")
    except Exception as e:
        print(f"Failed to capture screenshot '{name}': {e}")


def pytest_html_results_table_row(report, cells):
    """Styling for html report
    Hook to customize the HTML report table row cells
    """
    if report.failed:
        cells.insert(1, ("✘", "fail"))
    else:
        cells.insert(1, ("?", "skipped"))


def pytest_sessionstart(session):
    """ Hook to delete previous allure reports before running the tests"""
    try:
        project_root = os.path.abspath(os.path.dirname(__file__))
        folder_path = os.path.join(project_root, "allure_reports")
        if os.path.exists(folder_path) and os.listdir(folder_path):
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
    except Exception as e:
        print(f"Failed to clear allure reports: {e}")


def pytest_addoption(parser):
    parser.addoption(
        "--browser-name",
        action="store",
        default="chrome",
        choices=["firefox", "chrome", "safari", "edge"],
        help="Specify the browser to run the tests in",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run tests in headless mode"
    )
    parser.addoption(
        "--log-file-path",
        action="store",
        default=None,
        help="Specify the log file path"
    )
    parser.addoption(
        "--base-url",
        action="store",
        default="http://localhost:4444/wd/hub",
        help="BAse URL for the Selenium Webdriver server")

    parser.addoption(
        "--env",
        action="store",
        default="local",
        choices=["local", "staging", "production", "sauce-labs"],
        help="Specify the environment to run the tests in"
    )
    parser.addoption(
        "--env_url",
        action="store",
        default="production",
        choices=["staging", "production"],
        help="Specify the environment URL: staging or production"
    )


def make_full_screenshot(browser, savename):
    """Performs a full screenshot of the entire page.
    Taken from https://gist.github.com/fabtho/13e4a2e7cfbfde671b8fa81bbe9359fb
    """
    logger.debug('Making full-page screenshot')
    # initiate value
    img_list = []  # to store image fragment
    offset = 0  # where to start

    # js to get height of the window
    try:
        height = browser.execute_script(
            "return Math.max("
            "document.documentElement.clientHeight, window.innerHeight);"
        )
    except exceptions.WebDriverException:
        return

    max_window_height = browser.execute_script(
        "return Math.max("
        "document.body.scrollHeight, "
        "document.body.offsetHeight, "
        "document.documentElement.clientHeight, "
        "document.documentElement.scrollHeight, "
        "document.documentElement.offsetHeight);"
    )

    header_height = 0
    while offset < max_window_height:
        browser.execute_script(f"window.scrollTo(0, {offset});")

        # get the screenshot of the current window
        img = Image.open(BytesIO((browser.driver.get_screenshot_as_png())))
        img_list.append(img)
        offset += height - header_height

    # Stitch image into one, set up the full screen frame
    img_frame_height = sum([img_frag.size[1] for img_frag in img_list])
    img_frame = Image.new("RGB", (img_list[0].size[0], img_frame_height))

    offset = 0  # offset used to create the snapshots
    img_loc = 0  # offset used to create the final image
    for img_frag in img_list:
        # image fragment must be cropped in case the page is a jupyter notebook;
        # also make sure the last image fragment gets added correctly to avoid overlap.
        offset1 = offset + height
        if offset1 > max_window_height:
            top_offset = offset + height - max_window_height
            box = (0, top_offset, img_frag.size[0], img_frag.size[1])
        else:
            box = (0, header_height, img_frag.size[0], img_frag.size[1])
        img_frame.paste(img_frag.crop(box), (0, img_loc))
        img_loc += img_frag.size[1] - header_height
        offset += height - header_height

    # Save the final image
    img_frame.save(savename)


@pytest.fixture(scope="session", autouse=True)
def check_skip_condition():
    """ Skips a test file from running"""
    import os
    if os.getenv("SKIP_MODULES") == "1":
        pytest.skip("Skipping tests due to global configuration.", allow_module_level=True)
