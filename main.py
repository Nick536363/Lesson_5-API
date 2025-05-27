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


def get_vacancies_hh(programming_language, page, CITY_ID, DAYS_PERIOD):
    url_hh = "https://api.hh.ru/vacancies/"
    params_hh = {
        "area": CITY_ID,
        "period": DAYS_PERIOD,
        "page": page,
    }
    params_hh["text"] = programming_language
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

def get_stats_hh(languages, output_table):
     for language in languages:
        salaries = []
        vacancies_info = get_vacancies_hh(language, 0, 1, 30)
        for page in range(vacancies_info["pages"] - 1):
            for vacancy in get_vacancies_hh(language, page, 1, 30)["items"]:
                if vacancy["salary"]:
                    salaries.append(predict_rub_salary(vacancy["salary"]["from"], vacancy["salary"]["to"]))
            sleep(1)
        output_table.append([language, vacancies_info["found"], len(salaries), int(sum(salaries)/len(salaries))])

def get_stats_sj(languages, output_table):
    for language in languages:
        salaries = []
        vacancies_found = get_vacancies_sj(language, 0, getenv("SUPERJOB_API"))["total"]
        for page in count(0, 1):
            vacancies_info = get_vacancies_sj(language, page, getenv("SUPERJOB_API")) 
            if not vacancies_info["objects"]:
                break
            for vacancy in vacancies_info["objects"]:
                vacancy_salary = predict_rub_salary(vacancy["payment_from"], vacancy["payment_to"])
                if vacancy_salary:
                    salaries.append(vacancy_salary)
        
        if len(salaries):
            output_table.append([language, vacancies_found, len(salaries), int(sum(salaries)/len(salaries))])
            continue
        output_table.append([language, vacancies_found, 0, None])


def main():
    languages = [
        "JavaScript",
        "Java",
        "Python",
        "Ruby",
        "PHP",
        "C++",
        "C#",
        "Objective-C",
        "GoLang",
    ]
    table_hh = [
        ["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"]
    ]
    table_sj = [
        ["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"]
    ]      
    AsciiTable(table_sj).title = "SuperJob"
    AsciiTable(table_hh).title = "HeadHunter"
    load_dotenv(find_dotenv())
    get_stats_hh(languages, table_hh)
    get_stats_sj(languages, table_sj)
    print("HeadHunter", AsciiTable(table_hh).table)
    print("SuperJob", AsciiTable(table_sj).table)


if __name__ == "__main__":
    main()
