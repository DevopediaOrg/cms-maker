from json import JSONEncoder
import json

class AuthorDateFormat:
    PRINT_TEMPLATE = """
    Author, Year, Title : {author}, {year}, {title}
    Details, Publisher, Date: {details}, {publisher}, {date}
    Date Updated, Access Date, URL: {date_updated}, {access_date}, {url}
    """

    def __init__(self):
        self.author_name = None
        self.year_of_publication = None
        self.title = None
        self.details = None
        self.publisher_name = None
        self.date_of_publication = None
        self.date_updated = None
        self.access_date = None
        self.url = None

    def __str__(self):
        print(self.PRINT_TEMPLATE.format(
            author=self.author_name,
            year=self.year_of_publication,
            title=self.title,
            details=self.details,
            publisher=self.publisher_name,
            date=self.date_of_publication,
            date_updated=self.date_updated,
            access_date=self.access_date,
            url=self.url
        ))

    def encode(self, formatString):
        return json.dumps(self.__dict__).encode(formatString)

from json import JSONEncoder


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
