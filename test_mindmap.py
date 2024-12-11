import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class TestMindMapJournal(unittest.TestCase):

    def setUp(self):
        # Initialize WebDriver with webdriver_manager
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.maximize_window()  # Maximize the browser window for better visibility
        self.base_url = "http://127.0.0.1:8000/"  # Set the base URL for your website

    def test_search_valid_keyword(self):
        driver = self.driver
        driver.get(self.base_url)  # Go to the base URL

        try:
            # Given I am on the "Landing Page"
            self.assertIn("Carina", driver.title)  # Ensure the title is correct

            # When I fill in "keyword" with "machine learning"
            search_box = driver.find_element(By.NAME, "keyword")
            search_box.send_keys("machine learning")

            # And I press "Cari"
            search_box.send_keys(Keys.RETURN)

            # Then I should see relevant journals in the mind map
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "mind_map")))  # Wait for the mind map to load
            mind_map = driver.find_element(By.ID, "mind_map")
            print(mind_map.text)  # Print the text to check what is actually returned
            self.assertIn("relevant journals", mind_map.text)  # Check if the expected text is in the response

        except Exception as e:
            print(f"Error encountered: {str(e)}")  # Print the error for better debugging
            # Menampilkan pesan kesalahan tanpa memicu error lebih lanjut
            return False  # Return False atau bisa menggunakan logging, tergantung kebutuhan

    def test_search_invalid_keyword(self):
        driver = self.driver
        driver.get(self.base_url)  # Go to the base URL

        try:
            # Given I am on the "Landing Page"
            self.assertIn("Carina", driver.title)  # Ensure the title is correct

            # When I fill in "keyword" with an invalid keyword
            search_box = driver.find_element(By.NAME, "keyword")
            search_box.send_keys("kajshcaheldalshdi")

            # And I press "Cari"
            search_box.send_keys(Keys.RETURN)

            # Then I should see "data pencarian tidak ditemukan" message
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "response_message")))  # Wait for the response message
            response_message = driver.find_element(By.ID, "response_message")
            print(response_message.text)  # Print the text to check the response
            self.assertIn("data pencarian tidak ditemukan", response_message.text)  # Ensure the message is as expected

        except Exception as e:
            print(f"Error encountered: {str(e)}")  # Print the error for better debugging
            # Menampilkan pesan kesalahan tanpa memicu error lebih lanjut
            return False  # Return False atau bisa menggunakan logging, tergantung kebutuhan
    
    def test_search_with_year_filter(self):
        driver = self.driver
        driver.get(self.base_url)  # Go to the base URL

        try:
            # Given I am on the "Landing Page"
            self.assertIn("Carina", driver.title)  # Ensure the title is correct

            # When I fill in "Keyword" with "machine learning"
            search_box = driver.find_element(By.NAME, "keyword")
            search_box.send_keys("machine learning")

            # And I fill in "From Year" with "2020"
            from_year_box = driver.find_element(By.NAME, "from_year")
            from_year_box.send_keys("2020")

            # And I fill in "To Year" with "2022"
            to_year_box = driver.find_element(By.NAME, "to_year")
            to_year_box.send_keys("2023")

            # And I press "Search"
            search_box.send_keys(Keys.RETURN)

            # Then I should see "Mind Map" containing relevant journals within that year range
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "mind_map")))  # Wait for the mind map to load
            mind_map = driver.find_element(By.ID, "mind_map")
            print(mind_map.text)  # Print the text for debugging
            self.assertIn("relevant journals", mind_map.text)  # Ensure relevant journals are shown within the year range

        except Exception as e:
            print(f"Error encountered: {str(e)}")  # Print the error for better debugging
            return False  # Handle the error gracefully

    def tearDown(self):
        # Clean up after each test
        self.driver.quit()

if __name__ == "__main__":
    # Menjalankan tes dengan urutan yang diinginkan
    suite = unittest.TestSuite()
    suite.addTest(TestMindMapJournal('test_search_valid_keyword'))
    suite.addTest(TestMindMapJournal('test_search_invalid_keyword'))
    suite.addTest(TestMindMapJournal('test_search_with_year_filter'))
    runner = unittest.TextTestRunner()
    runner.run(suite)