from src.config import config
from src.db_manager import DBManager


def main():
    params = config()
    db_name = "hh_vacancies"
    db = DBManager(db_name, params)

    while True:
        print("\n===== МЕНЮ =====")
        print("1 - Компании и количество вакансий")
        print("2 - Все вакансии")
        print("3 - Средняя зарплата")
        print("4 - Вакансии выше средней зарплаты")
        print("5 - Поиск вакансий по ключевому слову")
        print("0 - Выход")

        choice = input("Выберите пункт меню: ").strip()

        if choice == "1":
            for name, count in db.get_companies_and_vacancies_count():
                print(f"{name}: {count}")

        elif choice == "2":
            vacancies = db.get_all_vacancies()
            for company, title, s_min, s_max, url in vacancies[:20]:  # только первые 20
                print(f"{company} | {title} | {s_min}-{s_max} | {url}")

        elif choice == "3":
            avg = db.get_avg_salary()
            print(f"Средняя зарплата: {round(avg, 2)}" if avg else "Нет данных")

        elif choice == "4":
            vacancies = db.get_vacancies_with_higher_salary()
            for company, title, s_min, s_max, url in vacancies[:20]:
                print(f"{company} | {title} | {s_min}-{s_max} | {url}")

        elif choice == "5":
            keyword = input("Введите ключевое слово: ").strip()
            vacancies = db.get_vacancies_with_keyword(keyword)
            for company, title, s_min, s_max, url in vacancies[:20]:
                print(f"{company} | {title} | {s_min}-{s_max} | {url}")

        elif choice == "0":
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор, попробуйте снова.")


if __name__ == "__main__":
    main()

