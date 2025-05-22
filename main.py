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


def get_vacancies_hh(search_text, page):
    url_hh = "https://api.hh.ru/vacancies/"
    params_hh = {
    "area": 1,
    "period": 30,
    "page": page,
    }
    params_hh["text"] = search_text
    response_hh = get(url=url_hh, params=params_hh)
    response_hh.raise_for_status()
    return response_hh.json()

def get_vacancies_info_sj(search_text, page, api_key):
    url_sj = "https://api.superjob.ru/2.0/vacancies/"
    headers_sj = {
        "X-Api-App-Id": api_key
    }
    params_sj = {
        "keyword": search_text,
        "town": "Moscow",
        "page": page,
    }
    response_sj = get(url=url_sj, headers=headers_sj, params=params_sj)
    response_sj.raise_for_status()
    return response_sj.json()

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

def main():
    for language in languages:
    # Headhunter
        salaries = []
        vacancies_info = get_vacancies_hh(language, 0)
        for page in range(vacancies_info["pages"] - 1):
            for vacancy in get_vacancies_hh(language, page)["items"]:
                if vacancy["salary"]:
                    salaries.append(predict_rub_salary(vacancy["salary"]["from"],vacancy["salary"]["to"]))
            sleep(0.3)
        table_hh.append([language, vacancies_info["found"], len(salaries), int(sum(salaries)/len(salaries))])
    # SuperJob
        salaries = []
        vacancies_found = get_vacancies_info_sj(language, 0, getenv("SECRET_KEY"))["total"]
        for page in count(0,1):
            vacancies_info = get_vacancies_info_sj(language, page, getenv("SECRET_KEY")) 
            if not vacancies_info["objects"]:
                break
            for vacancy in vacancies_info["objects"]:
                if predict_rub_salary(vacancy["payment_from"], vacancy["payment_to"]):
                    salaries.append(predict_rub_salary(vacancy["payment_from"], vacancy["payment_to"]))
        
        if len(salaries):
            table_sj.append([language, vacancies_found, len(salaries), int(sum(salaries)/len(salaries))])
            continue
        table_sj.append([language, vacancies_found, 0, None])


    print("HeadHunter", AsciiTable(table_hh).table)
    print("SuperJob", AsciiTable(table_sj).table)


if __name__ == "__main__":
    main()