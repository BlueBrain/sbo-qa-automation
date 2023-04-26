import logging
import time

import pytest
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pages.home_page import HomePage
from pages.login_page import LoginPage
from util.util_base import load_config


# The setup fixture used throughout the project
@pytest.fixture(scope="class")
def setup(request):

    # Initialize webdriver object
    browser = webdriver.Chrome()

    # Setting explicit wait
    wait = WebDriverWait(browser, 10)
    request.cls.browser = browser
    request.cls.wait = wait
    yield browser, wait

    browser.quit()


# Logger object fixture
@pytest.fixture(scope="module")
def logger():

    # Initializing the logger object
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter("%(levelname)s : %(asctime)s : %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(filename='test.log')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter("%(levelname)s : %(asctime)s : %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


# Fixture that navigates to the login page
@pytest.fixture(scope="function")
def login(setup, navigate_to_login):
    login_page = LoginPage(*setup)
    login_page.go_to_login_page(navigate_to_login)
    yield login_page

# Login & credentials fixture that is used throughout the project
@pytest.fixture(scope="class")
def navigate_to_login(setup):
    browser, wait = setup
    browser.get("https://bbp.epfl.ch/mmb-beta")
    home_page = HomePage(*setup)
    login_button = home_page.find_login_button()
    assert login_button.is_displayed()
    login_button.click()
    wait.until(EC.url_contains("auth"))
    login_url = browser.current_url
    yield login_url


# Create the login_explore fixture with username/password so that it can be re-used.
@pytest.fixture(scope="function")
def login_explore(setup, navigate_to_login):
    browser, wait = setup
    login_page = LoginPage(*setup)
    login_page.go_to_login_page(navigate_to_login)
    login_page.find_username_field().send_keys(load_config()['username'])
    login_page.find_password_field().send_keys(load_config()['password'])
    login_page.find_signin_button().click()
    # time.sleep(5)
    wait.until(EC.url_contains("mmb-beta"))
    yield browser, wait





