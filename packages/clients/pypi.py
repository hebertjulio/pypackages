from requests import get


class PyPi:

    __URL = 'https://pypi.org/pypi/{}/json'

    @staticmethod
    def get_info(project):
        resp = get(PyPi.__URL.format(project))
        if resp.status_code < 200 and resp.status_code > 299:
            raise resp.raise_for_status
        return resp.json()
