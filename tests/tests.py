import io
import unittest
from unittest.mock import patch

from src.main import *


class TestAnimalFunctions(unittest.TestCase):

    def test_remove_numbered_elements(self):
        input_data = ['smth1', '[94]', 'smth2', '[94]', 'smth3', '[94]']
        expected_output = ['smth1', 'smth2', 'smth3']
        self.assertEqual(remove_numbered_elements(input_data), expected_output)

    def test_remove_words_in_parentheses(self):
        input_string = 'Test (woah)'
        expected_output = 'Test '
        self.assertEqual(remove_words_in_parentheses(input_string), expected_output)

    def test_clean_string_from_numbers(self):
        input_string = 'abc [123]'
        expected_output = 'abc'
        self.assertEqual(clean_string_from_numbers(input_string), expected_output)

    def test_html_table_to_dict(self):
        html = """
            <table>
                <tr>
                    <th>Animal</th>
                    <th>Collateral adjective</th>
                </tr>
                <tr>
                    <td><a href="/wiki/Elephant">Elephant</a></td>
                    <td>[1] Large</td>
                </tr>
                <tr>
                    <td><a href="/wiki/Lion">Lion</a></td>
                    <td>Roaring [2]</td>
                </tr>
            </table>
        """
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')
        expected_output = [
            {'Animal': 'Elephant', 'Collateral adjective': 'Large'},
            {'Animal': 'Lion', 'Collateral adjective': 'Roaring'}
        ]
        self.assertEqual(html_table_to_dict(table), expected_output)

        ########

        table_html = """
            <table>
                <tr>
                    <th>Animal</th>
                    <th>Collateral adjective</th>
                </tr>
            </table>
        """
        expected_output = []
        self.assertEqual(html_table_to_dict(BeautifulSoup(table_html, 'html.parser')), expected_output)

        ########

        table_html = """
            <table>
                <tr>
                    <th>Animal</th>
                    <th>Collateral adjective</th>
                </tr>
                <tr>
                    <td><a href="/wiki/Elephant">Elephant</a></td>
                    <td>Large</td>
                </tr>
                <tr>
                    <td><a href="/wiki/Lion">Lion</a></td>
                    <td>Roaring</td>
                </tr>
                <tr>
                    <td><a href="/wiki/Tiger">Tiger</a></td>
                    <td>Fierce</td>
                </tr>
            </table>
        """
        expected_output = [
            {'Animal': 'Elephant', 'Collateral adjective': 'Large'},
            {'Animal': 'Lion', 'Collateral adjective': 'Roaring'},
            {'Animal': 'Tiger', 'Collateral adjective': 'Fierce'}
        ]
        self.assertEqual(html_table_to_dict(BeautifulSoup(table_html, 'html.parser')), expected_output)

        ########

        table_html = """
                <table>
                    <tr>
                        <th>Animal</th>
                        <th>Collateral adjective</th>
                    </tr>
                    <tr>
                        <td><a href="/wiki/Elephant">Elephant</a></td>
                        <td></td>
                    </tr>
                    <tr>
                        <td></td>
                        <td>Roaring</td>
                    </tr>
                </table>
            """
        expected_output = [
            {'Animal': 'Elephant', 'Collateral adjective': ''},
            {'Animal': '_', 'Collateral adjective': 'Roaring'}
        ]
        self.assertEqual(html_table_to_dict(BeautifulSoup(table_html, 'html.parser')), expected_output)

        #########

        table_html = """
            <table>
                <tr>
                    <th>Animal</th>
                    <th>Collateral adjective</th>
                </tr>
                <tr>
                    <td><a href="/wiki/Elephant">Elephant</a></td>
                    <td>Large<br/>Big</td>
                </tr>
                <tr>
                    <td><a href="/wiki/Lion">Lion</a></td>
                    <td>Roaring</td>
                </tr>
            </table>
        """
        expected_output = [
            {'Animal': 'Elephant', 'Collateral adjective': ['Large', 'Big']},
            {'Animal': 'Lion', 'Collateral adjective': 'Roaring'}
        ]
        self.assertEqual(html_table_to_dict(BeautifulSoup(table_html, 'html.parser')), expected_output)

    def test_get_animal_image(self):
        animal_name = 'Elephant'
        img_src = get_animal_image(animal_name)
        self.assertTrue(img_src.startswith('https://'))

    def test_dict_to_html_table(self):
        data = [
            {'Animal': 'Elephant', 'Collateral adjective': 'Large'},
            {'Animal': 'Lion', 'Collateral adjective': 'Roaring'}
        ]
        expected_output = """
            <table>
                <tr>
                    <th>Animal</th>
                    <th>Collateral adjective</th>
                </tr>
                <tr>
                    <td>Elephant</td>
                    <td>Large</td>
                </tr>
                <tr>
                    <td>Lion</td>
                    <td>Roaring</td>
                </tr>
            </table>
        """
        generated_html = dict_to_html_table(data)

        expected_soup = BeautifulSoup(expected_output, 'html.parser')
        generated_soup = BeautifulSoup(generated_html, 'html.parser')

        self.assertEqual(expected_soup.prettify(), generated_soup.prettify())

    def test_download_file(self):
        url = 'https://www.example.com'
        filename = download_file(url)
        self.assertTrue(filename is not None and os.path.exists(filename))
        os.remove(filename)

    def test_save_file(self):
        data = 'Hello, this is some data.'
        filename = 'example.txt'
        success = save_file(data, filename)
        self.assertTrue(success and os.path.exists(f'/tmp/{filename}'))
        os.remove(f'/tmp/{filename}')

    def test_display_animals(self):
        data = [
            [{'Animal': 'Elephant', 'Collateral adjective': 'Large'}],
            [{'Animal': 'Lion', 'Collateral adjective': 'Roaring'}]
        ]
        expected_output = "Processing Elephant...\nLarge Elephant\nProcessing Lion...\nRoaring Lion\n"
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            display_animals(data)
            self.assertEqual(mock_stdout.getvalue(), expected_output)


if __name__ == '__main__':
    unittest.main()
