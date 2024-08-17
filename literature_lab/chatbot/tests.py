from django.test import TestCase
from .presenters import ChatbotPresenter

class ChatbotPresenterTestCase(TestCase):
    def test_get_response(self):
        # Create an instance of the presenter
        presenter = ChatbotPresenter()
        # Call the method you want to test
        response = presenter.get_response("Hello")
        # Print the response (optional, usually you'd assert something here)
        print(response)
        # Check if the response is as expected
        self.assertEqual(response, "Received your input: Hello")

