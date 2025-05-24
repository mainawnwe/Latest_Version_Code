from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import unittest
import time

class TodoAppSeleniumTests(unittest.TestCase):
    def setUp(self):
        # Setup Chrome WebDriver (make sure chromedriver is in PATH)
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)
        self.base_url = "http://localhost:8000"

    def tearDown(self):
        self.driver.quit()

    def test_login_and_create_task(self):
        driver = self.driver
        driver.get(self.base_url + "/login/")

        # Login
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        username_input.send_keys("testuser")
        password_input.send_keys("testpass")
        password_input.send_keys(Keys.RETURN)

        time.sleep(2)  # wait for redirect

        # Navigate to create task page
        driver.get(self.base_url + "/task_create/")

        # Fill in task form
        title_input = driver.find_element(By.NAME, "title")
        description_input = driver.find_element(By.NAME, "description")
        title_input.send_keys("Selenium Test Task")
        description_input.send_keys("Task created by Selenium test.")

        # Submit form
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        time.sleep(2)  # wait for redirect

        # Verify task appears in task list
        driver.get(self.base_url + "/task_list/")
        body_text = driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("Selenium Test Task", body_text)

    def test_update_task(self):
        driver = self.driver
        driver.get(self.base_url + "/login/")

        # Login
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        username_input.send_keys("testuser")
        password_input.send_keys("testpass")
        password_input.send_keys(Keys.RETURN)

        time.sleep(2)  # wait for redirect

        # Navigate to task list page
        driver.get(self.base_url + "/task_list/")

        # Click on the first task's edit link (assuming it exists)
        edit_links = driver.find_elements(By.LINK_TEXT, "Edit")
        if edit_links:
            edit_links[0].click()
        else:
            self.fail("No edit links found on task list page")

        time.sleep(2)  # wait for page load

        # Update the title field
        title_input = driver.find_element(By.NAME, "title")
        title_input.clear()
        title_input.send_keys("Updated Selenium Test Task")

        # Submit form
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        time.sleep(2)  # wait for redirect

        # Verify updated task appears in task list
        driver.get(self.base_url + "/task_list/")
        body_text = driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("Updated Selenium Test Task", body_text)

    def test_delete_task(self):
        driver = self.driver
        driver.get(self.base_url + "/login/")

        # Login
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        username_input.send_keys("testuser")
        password_input.send_keys("testpass")
        password_input.send_keys(Keys.RETURN)

        time.sleep(2)  # wait for redirect

        # Navigate to task list page
        driver.get(self.base_url + "/task_list/")

        # Click on the first task's delete link (assuming it exists)
        delete_links = driver.find_elements(By.LINK_TEXT, "Delete")
        if delete_links:
            delete_links[0].click()
        else:
            self.fail("No delete links found on task list page")

        time.sleep(2)  # wait for page load

        # Confirm deletion by clicking the delete button on confirmation page
        delete_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        delete_button.click()

        time.sleep(2)  # wait for redirect

        # Verify task no longer appears in task list
        driver.get(self.base_url + "/task_list/")
        body_text = driver.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("Updated Selenium Test Task", body_text)

if __name__ == "__main__":
    unittest.main()
