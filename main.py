from requests import get
from terminaltables import AsciiTable
from itertools import count
from time import sleep
from os import getenv
from dotenv import load_dotenv, find_dotenv


def predict_rub_salary(salary_from=None, salary_to=None):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif not salary_from:
        return salary_to * 1.2
    elif not salary_to:
        return salary_from * 0.8
    else: 
        return None


def get_vacancies_hh(programming_language, page, city_id, days_period):
    url_hh = "https://api.hh.ru/vacancies/"
    params_hh = {
        "area": city_id,
        "period": days_period,
        "page": page,
        "text": programming_language
    }
    response_hh = get(url=url_hh, params=params_hh)
    response_hh.raise_for_status()
    return response_hh.json()


def get_vacancies_sj(programming_language, page, api_key):
    url_sj = "https://api.superjob.ru/2.0/vacancies/"
    headers_sj = {
        "X-Api-App-Id": api_key
    }
    params_sj = {
        "keyword": programming_language,
        "town": "Moscow",
        "page": page,
    }
    response_sj = get(url=url_sj, headers=headers_sj, params=params_sj)
    response_sj.raise_for_status()
    return response_sj.json()


def fill_table(source_tables, destination_table):
    for string in source_tables:
        destination_table.append(string)

def get_stats_hh(languages, city_id, days_period):
    all_stats = []
    for language in languages:
        salaries = []
        for page in count(0,1):
            vacancies = get_vacancies_hh(language, page, city_id, days_period)
            pages = vacancies["pages"]
            vacancies_found = vacancies["found"]
            for vacancy in vacancies["items"]:
                if vacancy["salary"]:
                    salaries.append(predict_rub_salary(vacancy["salary"]["from"], vacancy["salary"]["to"]))
            if page+1 == pages:
                break
            sleep(1)
        if len(salaries):
            all_stats.append([language, vacancies_found, len(salaries), f"{round(sum(salaries) / len(salaries))} ₽"])
            continue
        all_stats.append([language, vacancies_found, len(salaries), None])
    return all_stats
        

def get_stats_sj(languages, api_key):
    all_stats = []
    for language in languages:
        salaries = []
        for page in count(0, 1):
            vacancies = get_vacancies_sj(language, page, api_key) 
            vacancies_found = vacancies["total"]
            if not vacancies["objects"]:
                break
            for vacancy in vacancies["objects"]:
                vacancy_salary = predict_rub_salary(vacancy["payment_from"], vacancy["payment_to"])
                if vacancy_salary:
                    salaries.append(vacancy_salary)       
        if len(salaries):
            all_stats.append([language, vacancies_found, len(salaries), f"{round(sum(salaries) / len(salaries))} ₽" ])
            continue
        all_stats.append([language, vacancies_found, len(salaries), None])
    return all_stats


def main():
    load_dotenv(find_dotenv())
    city_id = 1
    period_in_days = 30
    api_key_sj = getenv("SUPERJOB_API_KEY")
    languages = [
        "JavaScript",
        "Java",
        "Python",
        "Haskell",
        "PHP",
        "C++",
        "TypeScript",
        "Swift",
        "GoLang",
    ]
    header =["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"]
    table_hh, table_sj = [header.copy()], [header.copy()]
    statistics_hh = get_stats_hh(languages, city_id, period_in_days)
    statistics_sj = get_stats_sj(languages, api_key_sj)
    fill_table(statistics_hh, table_hh)
    fill_table(statistics_sj, table_sj)
    print("HeadHunter", AsciiTable(table_hh).table)
    print("SuperJob", AsciiTable(table_sj).table)


if __name__ == "__main__":
    main()
