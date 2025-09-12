import psycopg2
from typing import Any


class DBManager:
    def __init__(self, db_name: str, params: dict[str, Any]):
        self.db_name = db_name
        self.params = params

    def _execute_query(self, query: str, values: tuple = ()) -> list[tuple]:
        """Вспомогательный метод для выполнения SQL-запроса"""
        with psycopg2.connect(dbname=self.db_name, **self.params) as conn:
            with conn.cursor() as cur:
                cur.execute(query, values)
                return cur.fetchall()

    def get_companies_and_vacancies_count(self) -> list[tuple]:
        query = """
            SELECT c.name, COUNT(v.vacancy_id)
            FROM companies c
            LEFT JOIN vacancies v ON c.company_id = v.company_id
            GROUP BY c.name
        """
        return self._execute_query(query)

    def get_all_vacancies(self) -> list[tuple]:
        query = """
            SELECT c.name, v.title, v.salary_min, v.salary_max, v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.company_id
        """
        return self._execute_query(query)

    def get_avg_salary(self) -> float:
        query = "SELECT AVG((salary_min + salary_max)/2.0) FROM vacancies WHERE salary_min IS NOT NULL AND salary_max IS NOT NULL"
        result = self._execute_query(query)
        return result[0][0] if result and result[0][0] else 0

    def get_vacancies_with_higher_salary(self) -> list[tuple]:
        query = """
            SELECT c.name, v.title, v.salary_min, v.salary_max, v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.company_id
            WHERE (salary_min + salary_max)/2.0 > (
                SELECT AVG((salary_min + salary_max)/2.0)
                FROM vacancies
                WHERE salary_min IS NOT NULL AND salary_max IS NOT NULL
            )
        """
        return self._execute_query(query)

    def get_vacancies_with_keyword(self, keyword: str) -> list[tuple]:
        query = """
            SELECT c.name, v.title, v.salary_min, v.salary_max, v.url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.company_id
            WHERE v.title ILIKE %s
        """
        return self._execute_query(query, (f"%{keyword}%",))
