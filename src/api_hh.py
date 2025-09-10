import requests
from requests.adapters import HTTPAdapter, Retry
from typing import Any

# --- сессия с ретраями и заголовками ---
session = requests.Session()
session.headers.update({
    "User-Agent": "course-work-hh/1.0 (contact: olga.tolba@gmail.com)",
    "Accept": "application/json",
})

retry = Retry(
    total=5,             # до 5 повторов
    backoff_factor=0.5,  # экспоненциальная пауза: 0.5, 1, 2, ...
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    raise_on_status=False,
)

adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)
session.mount("http://", adapter)

DEFAULT_TIMEOUT = 40  # увеличим таймаут


def _check(resp: requests.Response) -> dict[str, Any]:
    """Проверка ответа API и возврат JSON"""
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}") from e
    return resp.json()


def get_company_data(company_id: int) -> dict[str, Any]:
    """Получить данные компании по её id"""
    url = f"https://api.hh.ru/employers/{company_id}"
    resp = session.get(url, timeout=DEFAULT_TIMEOUT)
    return _check(resp)


def get_company_vacancies(
    company_id: int,
    per_page: int = 100,
    max_pages: int = 5,
) -> list[dict[str, Any]]:
    """Получить список вакансий компании (ограничим по страницам)"""
    url = "https://api.hh.ru/vacancies"
    all_vacancies: list[dict[str, Any]] = []

    for page in range(max_pages):
        params = {
            "employer_id": company_id,
            "per_page": per_page,
            "page": page,
        }
        resp = session.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        data = _check(resp)

        items = data.get("items", [])
        if not items:
            break

        all_vacancies.extend(items)

        # Если пришло меньше, чем per_page — значит, вакансии закончились
        if len(items) < per_page:
            break

    return all_vacancies

