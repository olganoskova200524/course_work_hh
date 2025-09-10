import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from src.api_hh import get_company_data, get_company_vacancies


def create_database(db_name: str, params: dict) -> None:
    """Создает БД, если ее нет. Без дропа (чтобы не ловить блокировки)."""
    conn = psycopg2.connect(dbname="postgres", **params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
            exists = cur.fetchone() is not None
            if not exists:
                cur.execute(f"CREATE DATABASE {db_name}")
    finally:
        conn.close()


def create_tables(db_name: str, params: dict) -> None:
    """Создаёт таблицы companies и vacancies."""
    with psycopg2.connect(dbname=db_name, **params) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    company_id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    city TEXT,
                    description TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS vacancies (
                    vacancy_id SERIAL PRIMARY KEY,
                    company_id INT REFERENCES companies(company_id),
                    title VARCHAR(255) NOT NULL,
                    salary_min INT,
                    salary_max INT,
                    url TEXT NOT NULL
                )
            """)
        conn.commit()


def truncate_tables(db_name: str, params: dict) -> None:
    """Очищает таблицы перед новой загрузкой данных."""
    with psycopg2.connect(dbname=db_name, **params) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE vacancies RESTART IDENTITY CASCADE;")
            cur.execute("TRUNCATE TABLE companies RESTART IDENTITY CASCADE;")
        conn.commit()


def save_data_to_database(db_name: str, params: dict, companies: list[int]) -> None:
    """Сохраняет данные о компаниях и вакансиях в БД."""
    with psycopg2.connect(dbname=db_name, **params) as conn:
        with conn.cursor() as cur:
            for company_id in companies:
                try:
                    company = get_company_data(company_id)
                except Exception as e:
                    print(f"[WARN] Ошибка при получении компании {company_id}: {e}")
                    continue

                cur.execute(
                    """
                    INSERT INTO companies (name, city, description)
                    VALUES (%s, %s, %s)
                    RETURNING company_id
                    """,
                    (company.get("name"),
                     (company.get("area") or {}).get("name"),
                     company.get("description")),
                )
                new_company_id = cur.fetchone()[0]

                try:
                    vacancies = get_company_vacancies(company_id)
                except Exception as e:
                    print(f"[WARN] Ошибка при получении вакансий для {company_id}: {e}")
                    vacancies = []

                for v in vacancies:
                    salary = v.get("salary") or {}
                    cur.execute(
                        """
                        INSERT INTO vacancies (company_id, title, salary_min, salary_max, url)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            new_company_id,
                            v.get("name"),
                            salary.get("from"),
                            salary.get("to"),
                            v.get("alternate_url"),
                        ),
                    )
        conn.commit()
