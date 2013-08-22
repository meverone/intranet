# coding: utf-8

class MockOAuth2FlowSampleData(object):
    def __init__(self):
        self.access_token = "1234567899"
        self.refresh_token = "1233456567"


def mock_get(name, email):
    class MockRequestSampleData(object):
        def __init__(self, name, email):
            self.json = {
                'name': name,
                'email': email
            }

    return MockRequestSampleData(name, email)


class MockApplicationConfig(object):

    def get_current_config(self, allow_empty=True):
        return self

    def get_freelancers(self):
        return []
