# coding: utf-8


class DummyMemcache(object):

    def get(self, key):
        return None

    def set(self, key, value):
        return True

    def delete(self, value):
        return True
