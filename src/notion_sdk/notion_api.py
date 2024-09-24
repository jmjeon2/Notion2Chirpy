from pprint import pprint
from typing import Optional
from notion_client import Client


class NotionAPI:
    def __init__(self, api_key: str):
        self.client = Client(auth=api_key)

    def page_name_to_id(self, database_id: str, name: str, property: str) -> Optional[str]:
        """
        Get page id from page name.
        Args:
            database_id: database id
            name: 찾을 페이지 이름
            property: 페이지의 속성(컬럼) 이름 (이 속성의 데이터 중 name과 일치하는 것을 찾음)
        Returns:
            page id: (if page exists)
        """

        filters = {
            "property": property,
            "rich_text": {
                "contains": name,
            },
        }
        resp = self.get_pages(database_id=database_id, filters=filters, page_size=10)
        pages = resp["results"]

        if len(pages) == 0:
            return None
        if len(pages) > 1:
            print(f"Warning: {len(pages)} pages found with name {name}.")

        return pages[0]["id"]

    def get_pages(self, database_id: str, filters: Optional[dict] = None, page_size: int = 10) -> dict:
        """
        Get pages from database.

        Args:
            database_id: database id
            filters:
            page_size:

        Returns:
            pages: list of pages
        """
        query = {
            "database_id": database_id,
            "page_size": page_size,
        }
        if filters:
            query["filter"] = filters

        return self.client.databases.query(**query)

    def get_page(self, page_id: str) -> dict:
        return self.client.pages.retrieve(**{"page_id": page_id})

    def update(self, page_id: str, properties: dict):
        """
        Update a page.
        Args:
            page_id: page id to update
            properties: properties to update
                e.g. {"컬럼명": "내용"}
        """
        properties = self._prop_dict_to_notion(properties)

        return self.client.pages.update(
            **{
                "page_id": page_id,
                "properties": properties,
            }
        )

    def create(self, database_id: str, properties: Optional[dict] = None) -> str:
        """
        Create a page.
        Args:
            database_id: database id
            properties:  e.g. {"컬럼명": "내용", ...}
        Returns:
            page id
        """
        if properties is None:
            properties = {}
        properties = self._prop_dict_to_notion(properties)

        resp = self.client.pages.create(
            **{
                "parent": {"database_id": database_id},
                "properties": properties,
            }
        )
        return resp["id"]

    def remove(self, page_id: str):
        """
        Remove a page.
        Args:
            page_id: page id to remove
        """
        return self.client.pages.update(
            **{
                "page_id": page_id,
                "archived": True,
            }
        )

    @staticmethod
    def _prop_dict_to_notion(d: dict):
        """
        Convert a dict to notion property format.
        Every value are converted to string.

        Args:
            d: e.g. {"컬럼명": "내용", ...}

        Returns:
            e.g. {"컬럼명": [{"text": {"content": "내용"}}]}
        """
        return {k: [{"text": {"content": str(v)}}] for k, v in d.items()}

    @staticmethod
    def parse_id_by_pages(pages: dict) -> list:
        """
        Get page id from page.
        """
        pages = pages['results']
        id_list = []
        for page in pages:
            id_list.append(page['id'])
        return id_list


if __name__ == '__main__':
    NOTION_TOKEN = 'secret_fwhbiVhmFePiiIMX94tWs9IkMgK3NHPy6lk9v5KMDd7'
    DB_ID = '4fd549c6e1a940a787ea5c123cf4222d'  # notion database 페이지에서 링크 복사 후 id만 붙여넣기

    client = NotionAPI(api_key=NOTION_TOKEN)  # notion api 사이트에서 발급받기

    # filter는 document 참고: https://developers.notion.com/reference/post-database-query-filter
    filters = {
        "property": "status",
        "select": {
            "equals": "테스트"
        }
    }

    pages = client.get_pages(database_id=DB_ID, filters=filters, page_size=10)
    pprint(pages)
    pages_id = client.parse_id_by_pages(pages)
    print(pages_id)

    # page name 찾기
    print(pages['results'][0]['properties']['name']['title'][0]['plain_text'])

    # get_pages() 결과 예시
    """
    
{'has_more': False,
 'next_cursor': None,
 'object': 'list',
 'page_or_database': {},
 'request_id': '7bd80472-0b86-4588-a7f9-2cb89e56e29a',
 'results': [{'archived': False,
              'cover': None,
              'created_by': {'id': '14415648-97c4-432e-80a7-9a9d0b7a57cb',
                             'object': 'user'},
              'created_time': '2024-09-23T09:00:00.000Z',
              'icon': None,
              'id': '10a48a6e-55fc-804a-894c-e097d6b7c445',
              'in_trash': False,
              'last_edited_by': {'id': '14415648-97c4-432e-80a7-9a9d0b7a57cb',
                                 'object': 'user'},
              'last_edited_time': '2024-09-23T09:46:00.000Z',
              'object': 'page',
              'parent': {'database_id': '4fd549c6-e1a9-40a7-87ea-5c123cf4222d',
                         'type': 'database_id'},
              'properties': {'Created Time': {'created_time': '2024-09-23T09:00:00.000Z',
                                              'id': '%40%5EZw',
                                              'type': 'created_time'},
                             'Last Edited Time': {'id': 'qaiv',
                                                  'last_edited_time': '2024-09-23T09:46:00.000Z',
                                                  'type': 'last_edited_time'},
                             'categories': {'id': '_%5BpW',
                                            'multi_select': [{'color': 'green',
                                                              'id': '3174ec02-1ac2-4c01-8590-1213d8fd8e74',
                                                              'name': 'Python'},
                                                             {'color': 'default',
                                                              'id': '3205be96-88d5-42c1-924e-5c852ab03f8d',
                                                              'name': '알고리즘'}],
                                            'type': 'multi_select'},
                             'date': {'date': {'end': None,
                                               'start': '2024-09-17',
                                               'time_zone': None},
                                      'id': '%7CDr%3A',
                                      'type': 'date'},
                             'linked': {'checkbox': False,
                                        'id': '%3C%5B~%3B',
                                        'type': 'checkbox'},
                             'status': {'id': 'UPmd',
                                        'select': {'color': 'orange',
                                                   'id': '14ddadbb-66da-4745-842e-e6ab8d8faee9',
                                                   'name': '테스트'},
                                        'type': 'select'},
                             'tags': {'id': 'Oek%7C',
                                      'multi_select': [{'color': 'gray',
                                                        'id': 'd2f4f99e-ce91-4293-8742-6278afa1ceef',
                                                        'name': 'wandb'},
                                                       {'color': 'yellow',
                                                        'id': '80d64052-4881-4990-8ca6-cc3a84ba822f',
                                                        'name': 'sweep'},
                                                       {'color': 'gray',
                                                        'id': 'f886f533-8185-4eec-a086-635d8a1e5a67',
                                                        'name': '하이퍼파라미터'},
                                                       {'color': 'pink',
                                                        'id': '1e8d35c9-c451-42dd-a7d9-567cb962360b',
                                                        'name': 'pytorch'},
                                                       {'color': 'red',
                                                        'id': '44a4191c-d956-48f4-b99d-7d69d13acde5',
                                                        'name': '딥러닝'}],
                                      'type': 'multi_select'},
                             'title': {'id': 'rEVg',
                                       'rich_text': [{'annotations': {'bold': False,
                                                                      'code': False,
                                                                      'color': 'default',
                                                                      'italic': False,
                                                                      'strikethrough': False,
                                                                      'underline': False},
                                                      'href': None,
                                                      'plain_text': 'Notion '
                                                                    'Test Page',
                                                      'text': {'content': 'Notion '
                                                                          'Test '
                                                                          'Page',
                                                               'link': None},
                                                      'type': 'text'}],
                                       'type': 'rich_text'},
                             'url': {'id': 'yGoe', 'type': 'url', 'url': None},
                             '도서링크': {'has_more': False,
                                      'id': 'YUZb',
                                      'relation': [],
                                      'type': 'relation'},
                             '이름': {'id': 'title',
                                    'title': [{'annotations': {'bold': False,
                                                               'code': False,
                                                               'color': 'default',
                                                               'italic': False,
                                                               'strikethrough': False,
                                                               'underline': False},
                                               'href': None,
                                               'plain_text': 'Notion2GithubPages',
                                               'text': {'content': 'Notion2GithubPages',
                                                        'link': None},
                                               'type': 'text'}],
                                    'type': 'title'}},
              'public_url': None,
              'url': 'https://www.notion.so/Notion2GithubPages-10a48a6e55fc804a894ce097d6b7c445'},
             {'archived': False,
              'cover': None,
              'created_by': {'id': '14415648-97c4-432e-80a7-9a9d0b7a57cb',
                             'object': 'user'},
              'created_time': '2024-09-21T04:22:00.000Z',
              'icon': None,
              'id': '10848a6e-55fc-805a-89e4-d746d4352b25',
              'in_trash': False,
              'last_edited_by': {'id': '14415648-97c4-432e-80a7-9a9d0b7a57cb',
                                 'object': 'user'},
              'last_edited_time': '2024-09-21T05:16:00.000Z',
              'object': 'page',
              'parent': {'database_id': '4fd549c6-e1a9-40a7-87ea-5c123cf4222d',
                         'type': 'database_id'},
              'properties': {'Created Time': {'created_time': '2024-09-21T04:22:00.000Z',
                                              'id': '%40%5EZw',
                                              'type': 'created_time'},
                             'Last Edited Time': {'id': 'qaiv',
                                                  'last_edited_time': '2024-09-21T05:16:00.000Z',
                                                  'type': 'last_edited_time'},
                             'categories': {'id': '_%5BpW',
                                            'multi_select': [{'color': 'green',
                                                              'id': '3174ec02-1ac2-4c01-8590-1213d8fd8e74',
                                                              'name': 'Python'}],
                                            'type': 'multi_select'},
                             'date': {'date': {'end': None,
                                               'start': '2024-09-21',
                                               'time_zone': None},
                                      'id': '%7CDr%3A',
                                      'type': 'date'},
                             'linked': {'checkbox': False,
                                        'id': '%3C%5B~%3B',
                                        'type': 'checkbox'},
                             'status': {'id': 'UPmd',
                                        'select': {'color': 'orange',
                                                   'id': '14ddadbb-66da-4745-842e-e6ab8d8faee9',
                                                   'name': '테스트'},
                                        'type': 'select'},
                             'tags': {'id': 'Oek%7C',
                                      'multi_select': [{'color': 'gray',
                                                        'id': 'd2f4f99e-ce91-4293-8742-6278afa1ceef',
                                                        'name': 'wandb'},
                                                       {'color': 'yellow',
                                                        'id': '80d64052-4881-4990-8ca6-cc3a84ba822f',
                                                        'name': 'sweep'},
                                                       {'color': 'gray',
                                                        'id': 'f886f533-8185-4eec-a086-635d8a1e5a67',
                                                        'name': '하이퍼파라미터'},
                                                       {'color': 'pink',
                                                        'id': '1e8d35c9-c451-42dd-a7d9-567cb962360b',
                                                        'name': 'pytorch'},
                                                       {'color': 'red',
                                                        'id': '44a4191c-d956-48f4-b99d-7d69d13acde5',
                                                        'name': '딥러닝'}],
                                      'type': 'multi_select'},
                             'title': {'id': 'rEVg',
                                       'rich_text': [{'annotations': {'bold': False,
                                                                      'code': False,
                                                                      'color': 'default',
                                                                      'italic': False,
                                                                      'strikethrough': False,
                                                                      'underline': False},
                                                      'href': None,
                                                      'plain_text': '[MLOps] '
                                                                    'WandB '
                                                                    'Sweep '
                                                                    '사용방법 '
                                                                    '(pytorch '
                                                                    '하이퍼 파라미터 '
                                                                    '튜닝)',
                                                      'text': {'content': '[MLOps] '
                                                                          'WandB '
                                                                          'Sweep '
                                                                          '사용방법 '
                                                                          '(pytorch '
                                                                          '하이퍼 '
                                                                          '파라미터 '
                                                                          '튜닝)',
                                                               'link': None},
                                                      'type': 'text'}],
                                       'type': 'rich_text'},
                             'url': {'id': 'yGoe', 'type': 'url', 'url': None},
                             '도서링크': {'has_more': False,
                                      'id': 'YUZb',
                                      'relation': [],
                                      'type': 'relation'},
                             '이름': {'id': 'title',
                                    'title': [{'annotations': {'bold': False,
                                                               'code': False,
                                                               'color': 'default',
                                                               'italic': False,
                                                               'strikethrough': False,
                                                               'underline': False},
                                               'href': None,
                                               'plain_text': 'WandB Sweep(test '
                                                             'del)',
                                               'text': {'content': 'WandB '
                                                                   'Sweep(test '
                                                                   'del)',
                                                        'link': None},
                                               'type': 'text'}],
                                    'type': 'title'}},
              'public_url': None,
              'url': 'https://www.notion.so/WandB-Sweep-test-del-10848a6e55fc805a89e4d746d4352b25'}],
 'type': 'page_or_database'}
[{'archived': False,
  'cover': None,
  'created_by': {'id': '14415648-97c4-432e-80a7-9a9d0b7a57cb',
                 'object': 'user'},
  'created_time': '2024-09-23T09:00:00.000Z',
  'icon': None,
  'id': '10a48a6e-55fc-804a-894c-e097d6b7c445',
  'in_trash': False,
  'last_edited_by': {'id': '14415648-97c4-432e-80a7-9a9d0b7a57cb',
                     'object': 'user'},
  'last_edited_time': '2024-09-23T09:46:00.000Z',
  'object': 'page',
  'parent': {'database_id': '4fd549c6-e1a9-40a7-87ea-5c123cf4222d',
             'type': 'database_id'},
  'properties': {'Created Time': {'created_time': '2024-09-23T09:00:00.000Z',
                                  'id': '%40%5EZw',
                                  'type': 'created_time'},
                 'Last Edited Time': {'id': 'qaiv',
                                      'last_edited_time': '2024-09-23T09:46:00.000Z',
                                      'type': 'last_edited_time'},
                 'categories': {'id': '_%5BpW',
                                'multi_select': [{'color': 'green',
                                                  'id': '3174ec02-1ac2-4c01-8590-1213d8fd8e74',
                                                  'name': 'Python'},
                                                 {'color': 'default',
                                                  'id': '3205be96-88d5-42c1-924e-5c852ab03f8d',
                                                  'name': '알고리즘'}],
                                'type': 'multi_select'},
                 'date': {'date': {'end': None,
                                   'start': '2024-09-17',
                                   'time_zone': None},
                          'id': '%7CDr%3A',
                          'type': 'date'},
                 'linked': {'checkbox': False,
                            'id': '%3C%5B~%3B',
                            'type': 'checkbox'},
                 'status': {'id': 'UPmd',
                            'select': {'color': 'orange',
                                       'id': '14ddadbb-66da-4745-842e-e6ab8d8faee9',
                                       'name': '테스트'},
                            'type': 'select'},
                 'tags': {'id': 'Oek%7C',
                          'multi_select': [{'color': 'gray',
                                            'id': 'd2f4f99e-ce91-4293-8742-6278afa1ceef',
                                            'name': 'wandb'},
                                           {'color': 'yellow',
                                            'id': '80d64052-4881-4990-8ca6-cc3a84ba822f',
                                            'name': 'sweep'},
                                           {'color': 'gray',
                                            'id': 'f886f533-8185-4eec-a086-635d8a1e5a67',
                                            'name': '하이퍼파라미터'},
                                           {'color': 'pink',
                                            'id': '1e8d35c9-c451-42dd-a7d9-567cb962360b',
                                            'name': 'pytorch'},
                                           {'color': 'red',
                                            'id': '44a4191c-d956-48f4-b99d-7d69d13acde5',
                                            'name': '딥러닝'}],
                          'type': 'multi_select'},
                 'title': {'id': 'rEVg',
                           'rich_text': [{'annotations': {'bold': False,
                                                          'code': False,
                                                          'color': 'default',
                                                          'italic': False,
                                                          'strikethrough': False,
                                                          'underline': False},
                                          'href': None,
                                          'plain_text': 'Notion Test Page',
                                          'text': {'content': 'Notion Test '
                                                              'Page',
                                                   'link': None},
                                          'type': 'text'}],
                           'type': 'rich_text'},
                 'url': {'id': 'yGoe', 'type': 'url', 'url': None},
                 '도서링크': {'has_more': False,
                          'id': 'YUZb',
                          'relation': [],
                          'type': 'relation'},
                 '이름': {'id': 'title',
                        'title': [{'annotations': {'bold': False,
                                                   'code': False,
                                                   'color': 'default',
                                                   'italic': False,
                                                   'strikethrough': False,
                                                   'underline': False},
                                   'href': None,
                                   'plain_text': 'Notion2GithubPages',
                                   'text': {'content': 'Notion2GithubPages',
                                            'link': None},
                                   'type': 'text'}],
                        'type': 'title'}},
  'public_url': None,
  'url': 'https://www.notion.so/Notion2GithubPages-10a48a6e55fc804a894ce097d6b7c445'},
 {'archived': False,
  'cover': None,
  'created_by': {'id': '14415648-97c4-432e-80a7-9a9d0b7a57cb',
                 'object': 'user'},
  'created_time': '2024-09-21T04:22:00.000Z',
  'icon': None,
  'id': '10848a6e-55fc-805a-89e4-d746d4352b25',
  'in_trash': False,
  'last_edited_by': {'id': '14415648-97c4-432e-80a7-9a9d0b7a57cb',
                     'object': 'user'},
  'last_edited_time': '2024-09-21T05:16:00.000Z',
  'object': 'page',
  'parent': {'database_id': '4fd549c6-e1a9-40a7-87ea-5c123cf4222d',
             'type': 'database_id'},
  'properties': {'Created Time': {'created_time': '2024-09-21T04:22:00.000Z',
                                  'id': '%40%5EZw',
                                  'type': 'created_time'},
                 'Last Edited Time': {'id': 'qaiv',
                                      'last_edited_time': '2024-09-21T05:16:00.000Z',
                                      'type': 'last_edited_time'},
                 'categories': {'id': '_%5BpW',
                                'multi_select': [{'color': 'green',
                                                  'id': '3174ec02-1ac2-4c01-8590-1213d8fd8e74',
                                                  'name': 'Python'}],
                                'type': 'multi_select'},
                 'date': {'date': {'end': None,
                                   'start': '2024-09-21',
                                   'time_zone': None},
                          'id': '%7CDr%3A',
                          'type': 'date'},
                 'linked': {'checkbox': False,
                            'id': '%3C%5B~%3B',
                            'type': 'checkbox'},
                 'status': {'id': 'UPmd',
                            'select': {'color': 'orange',
                                       'id': '14ddadbb-66da-4745-842e-e6ab8d8faee9',
                                       'name': '테스트'},
                            'type': 'select'},
                 'tags': {'id': 'Oek%7C',
                          'multi_select': [{'color': 'gray',
                                            'id': 'd2f4f99e-ce91-4293-8742-6278afa1ceef',
                                            'name': 'wandb'},
                                           {'color': 'yellow',
                                            'id': '80d64052-4881-4990-8ca6-cc3a84ba822f',
                                            'name': 'sweep'},
                                           {'color': 'gray',
                                            'id': 'f886f533-8185-4eec-a086-635d8a1e5a67',
                                            'name': '하이퍼파라미터'},
                                           {'color': 'pink',
                                            'id': '1e8d35c9-c451-42dd-a7d9-567cb962360b',
                                            'name': 'pytorch'},
                                           {'color': 'red',
                                            'id': '44a4191c-d956-48f4-b99d-7d69d13acde5',
                                            'name': '딥러닝'}],
                          'type': 'multi_select'},
                 'title': {'id': 'rEVg',
                           'rich_text': [{'annotations': {'bold': False,
                                                          'code': False,
                                                          'color': 'default',
                                                          'italic': False,
                                                          'strikethrough': False,
                                                          'underline': False},
                                          'href': None,
                                          'plain_text': '[MLOps] WandB Sweep '
                                                        '사용방법 (pytorch 하이퍼 '
                                                        '파라미터 튜닝)',
                                          'text': {'content': '[MLOps] WandB '
                                                              'Sweep 사용방법 '
                                                              '(pytorch 하이퍼 '
                                                              '파라미터 튜닝)',
                                                   'link': None},
                                          'type': 'text'}],
                           'type': 'rich_text'},
                 'url': {'id': 'yGoe', 'type': 'url', 'url': None},
                 '도서링크': {'has_more': False,
                          'id': 'YUZb',
                          'relation': [],
                          'type': 'relation'},
                 '이름': {'id': 'title',
                        'title': [{'annotations': {'bold': False,
                                                   'code': False,
                                                   'color': 'default',
                                                   'italic': False,
                                                   'strikethrough': False,
                                                   'underline': False},
                                   'href': None,
                                   'plain_text': 'WandB Sweep(test del)',
                                   'text': {'content': 'WandB Sweep(test del)',
                                            'link': None},
                                   'type': 'text'}],
                        'type': 'title'}},
  'public_url': None,
  'url': 'https://www.notion.so/WandB-Sweep-test-del-10848a6e55fc805a89e4d746d4352b25'}]


    """
