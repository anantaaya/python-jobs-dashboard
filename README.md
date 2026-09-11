# 📊 Анализ Python-вакансий с портала «Работа России»

Интерактивный дашборд для анализа рынка вакансий для Python-разработчиков в России.

## 🚀 О проекте

Проект собирает данные о вакансиях с портала «Работа России», очищает их и представляет в виде наглядных графиков. Данные собираются по 78 регионам РФ.

## 🛠 Технологии

- **Python** (Requests, Pandas)
- **Streamlit** (веб-интерфейс)
- **Plotly** (интерактивные графики)

## 📈 Возможности дашборда

- Общее количество вакансий, средняя и медианная зарплата
- Распределение вакансий по регионам и компаниям
- Зависимость зарплаты от требуемого опыта
- Топ-15 самых востребованных навыков
- Фильтры: исключение Москвы и СПб, диапазон зарплат

## 📂 Структура проекта
```commandline
hh-parser/
├── dashboard.py # Дашборд Streamlit
├── vacancies.py # Парсер вакансий
├── requirements.txt # Зависимости
├── README.md # Описание проекта
└── results/
    ├── raw_vacancies.json # Сырые данные
    └── python_vacancies.json # Отфильтрованные Python-вакансии
```

## 🚀 Как запустить локально


# Клонировать репозиторий
git clone https://github.com/anantaaya/python-jobs-dashboard.git
cd python-jobs-dashboard

# Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate         # Windows
source venv/bin/activate      # Linux/Mac

# Установить зависимости
pip install -r requirements.txt

# Запустить парсер (соберёт данные)
python vacancies.py

# Запустить дашборд
streamlit run dashboard.py

## 🔗 Ссылка на дашборд

(будет добавлена после деплоя)

##📊 Источник данных

«Работа России» — государственный портал вакансий. API: opendata.trudvsem.ru.

## 👤 Автор

GitHub: [@anantaaya](https://github.com/anantaaya)
