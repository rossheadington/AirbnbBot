import time
import logging
import random
import json
from datetime import datetime
from config import AIRBNB_USERNAME, AIRBNB_PASSWORD
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class AirbnbScraper:
    def __init__(self):
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service)
            self.driver.maximize_window()
            logging.info("WebDriver initialized successfully.")
        except WebDriverException as e:
            logging.error("Failed to initialize WebDriver.")
            raise e

    def login(self, email, password):
        try:
            self.driver.get('https://www.airbnb.co.uk/')
            logging.info("Navigated to Airbnb website.")
            time.sleep(random.uniform(1, 5))

            # Wait for the "Accept all" button to be clickable and click it
            accept_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept all')]"))
            )
            accept_button.click()

            # Click the profile menu button
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'cnky2vc'))
            ).click()
            logging.info("Profile menu button clicked.")
            time.sleep(random.uniform(1, 5))

            # Locate and click the "Log in" link
            parent_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'simple-header-profile-menu'))
            )
            child_a_element = parent_element.find_element(By.XPATH, ".//a[@data-testid='cypress-headernav-login']")
            child_a_element.click()
            logging.info("Clicked on the 'Log in' link.")
            time.sleep(random.uniform(1, 5))

            # Click "Continue with email"
            continue_with_email_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='social-auth-button-email']"))
            )
            continue_with_email_button.click()
            logging.info("Clicked on 'Continue with email' button.")
            time.sleep(random.uniform(1, 5))

            # Enter email
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email-login-email"))
            )
            for char in email:
                email_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            logging.info("Entered email address.")
            time.sleep(random.uniform(1, 2))

            # Click "Continue"
            continue_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='signup-login-submit-btn']"))
            )
            continue_button.click()
            logging.info("Clicked on the 'Continue' button.")
            time.sleep(random.uniform(1, 5))

            # Enter password
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email-signup-password"))
            )
            for char in password:
                password_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            logging.info("Entered password.")
            time.sleep(random.uniform(1, 5))

            # Click "Log in"
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='signup-login-submit-btn']"))
            )
            login_button.click()
            time.sleep(random.uniform(10, 15))
            logging.info("Clicked on the 'Log in' button.")
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            logging.error("Error during login process.")
            logging.error(str(e))
            self.driver.quit()
            raise e

    def get_message_ids(self):
        try:
            self.driver.get('https://www.airbnb.co.uk/guest/messages/')
            time.sleep(random.uniform(10, 15))

            messages = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a.pg07rzn'))
            )

            message_info = []
            for message in messages:
                message_info.append({
                    'message_id': int(message.get_attribute('data-testid').replace('inbox_list_','')),
                    'message_index': int(message.get_attribute('data-item-index')),
                })

            logging.info("Collected message IDs.")
            return message_info
        except (TimeoutException, NoSuchElementException) as e:
            logging.error("Error while retrieving message IDs.")
            logging.error(str(e))
            return []

    def get_all_messages(self):
        try:
            outer_div = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 't1xp0zmn'))
            )

            message_divs = outer_div[1].find_elements(By.CLASS_NAME, 'fwqd6yv')
            formatted_message_data = []

            for div in message_divs:
                aria_label = div.get_attribute('aria-label')
                data_item_id = div.get_attribute('data-item-id')
                is_last_message = div.get_attribute('data-islastmessage') == 'true'

                # Extract the sender's name dynamically
                if 'sent' in aria_label:
                    sender_end_index = aria_label.index(' sent')
                    sender = aria_label[:sender_end_index].strip()
                else:
                    sender = 'Unknown'

                # Extract the message content
                try:
                    content_start = aria_label.index('sent ') + len('sent ')
                    content_end = aria_label.index('. Sent', content_start)
                    message_content = aria_label[content_start:content_end].strip()
                except ValueError:
                    message_content = 'Content not found'

                # Extract the date and time
                try:
                    dt_start = aria_label.rindex('Sent ') + len('Sent ')
                    dt_string = aria_label[dt_start:].strip()
                    message_dt = datetime.strptime(dt_string, '%d %b %Y, %H:%M')
                except ValueError:
                    message_dt = 'Date not found'

                # Append formatted data to the list
                formatted_data = {
                    'sender': sender,
                    'message': message_content,
                    'datetime': message_dt,
                    'is_last_message': is_last_message
                }
                formatted_message_data.append(formatted_data)

            # Print or return the formatted message data
            for message in formatted_message_data:
                print(message)

            logging.info("Collected all message data.")
            return message_data
        except (TimeoutException, NoSuchElementException) as e:
            logging.error("Error while retrieving messages.")
            logging.error(str(e))
            return []

    def save_messages_to_json(self, messages, filename='output.json'):
        try:
            with open(filename, 'w') as f:
                json.dump({"messages": messages}, f, indent=4)
            logging.info(f"Messages saved to {filename}")
        except Exception as e:
            logging.error("Error while saving messages to JSON.")
            logging.error(str(e))

    def close(self):
        if self.driver:
            self.driver.quit()
            logging.info("WebDriver closed.")

# Usage example:
if __name__ == "__main__":
    scraper = AirbnbScraper()
    try:
        scraper.login(email=AIRBNB_USERNAME, password=AIRBNB_PASSWORD)
        message_ids = scraper.get_message_ids()
        print(message_ids)
        all_messages = scraper.get_all_messages()
        print(all_messages)
        scraper.save_messages_to_json(all_messages)
    finally:
        scraper.close()
