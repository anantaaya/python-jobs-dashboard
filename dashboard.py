import json
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Анализ Python-вакансий", layout="wide")
st.title("📊 Анализ Python-вакансий с «Работы России»")

# --- Загрузка данных ---
with open("results/python_vacancies.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

df = pd.DataFrame(raw)
df["region_name"] = df["region"].apply(lambda x: x.get("name") if isinstance(x, dict) else None)
df["company_name"] = df["company"].apply(lambda x: x.get("name") if isinstance(x, dict) else None)
df["experience"] = df["requirement"].apply(
    lambda x: x.get("experience") if isinstance(x, dict) else None
)

# ============================================================
# 🎛 БОКОВАЯ ПАНЕЛЬ С ФИЛЬТРАМИ
# ============================================================
st.sidebar.header("🎛 Фильтры")

st.sidebar.subheader("Исключить регионы")
exclude_moscow = st.sidebar.checkbox("Исключить Москву", value=False)
exclude_spb = st.sidebar.checkbox("Исключить Санкт-Петербург", value=False)

st.sidebar.subheader("Зарплата")
max_salary = int(df["salary_min"].max()) if df["salary_min"].max() > 0 else 100000
salary_range = st.sidebar.slider(
    "Диапазон (минимальная ЗП), ₽",
    min_value=0,
    max_value=max_salary,
    value=(0, max_salary),
    step=10000,
)

# ============================================================
# 🧹 ПРИМЕНЯЕМ ФИЛЬТРЫ
# ============================================================
filtered = df.copy()

if exclude_moscow:
    filtered = filtered[~filtered["region_name"].str.contains("Москва", na=False)]

if exclude_spb:
    filtered = filtered[~filtered["region_name"].str.contains("Санкт-Петербург", na=False)]

filtered = filtered[
    (filtered["salary_min"] >= salary_range[0]) &
    (filtered["salary_min"] <= salary_range[1])
    ]

df_salary = filtered[filtered["salary_min"] > 0]

# ============================================================
# 📊 МЕТРИКИ
# ============================================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Вакансий", len(filtered))
col2.metric("Средняя ЗП", f"{df_salary['salary_min'].mean():,.0f} ₽" if len(df_salary) else "—")
col3.metric("Медианная ЗП", f"{df_salary['salary_min'].median():,.0f} ₽" if len(df_salary) else "—")
col4.metric("Компаний", filtered["company_name"].nunique())

st.divider()

# ============================================================
# 📈 ФУНКЦИЯ ДЛЯ ГОРИЗОНТАЛЬНОГО ГРАФИКА
# ============================================================
def horizontal_bar(data, color="#4A90E2"):
    fig = px.bar(
        x=data.values,
        y=data.index,
        orientation="h",
        labels={"x": "Количество", "y": ""},
        color_discrete_sequence=[color],
    )
    fig.update_layout(
        height=max(400, len(data) * 40),
        margin=dict(l=250, r=20, t=20, b=20),
        yaxis=dict(autorange="reversed"),
        showlegend=False,
    )
    return fig

# ============================================================
# 🏙 ТОП-10 РЕГИОНОВ
# ============================================================
st.subheader("🏙 Топ-10 регионов")
top_regions = filtered["region_name"].value_counts().head(10)
if len(top_regions):
    st.plotly_chart(horizontal_bar(top_regions), use_container_width=True)
else:
    st.info("Нет данных после применения фильтров")

st.divider()

# ============================================================
# 🏢 ТОП-10 КОМПАНИЙ
# ============================================================
st.subheader("🏢 Топ-10 компаний")
top_companies = filtered["company_name"].value_counts().head(10)
if len(top_companies):
    st.plotly_chart(horizontal_bar(top_companies), use_container_width=True)
else:
    st.info("Нет данных после применения фильтров")

st.divider()

# ============================================================
# 💰 ЗАРПЛАТА ПО ОПЫТУ
# ============================================================
def plural_years(n):
    n = int(n)
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} год"
    elif n % 10 in [2, 3, 4] and n % 100 not in [12, 13, 14]:
        return f"{n} года"
    else:
        return f"{n} лет"

st.subheader("💰 Медианная зарплата по опыту работы")
salary_by_exp = df_salary.groupby("experience")["salary_min"].median()

if len(salary_by_exp) > 0:
    fig_exp = px.bar(
        x=salary_by_exp.index,
        y=salary_by_exp.values,
        labels={"x": "Опыт работы", "y": "Медианная ЗП, ₽"},
        color_discrete_sequence=["#50C878"],
    )
    fig_exp.update_layout(
        height=450,
        xaxis=dict(
            tickmode="array",
            tickvals=salary_by_exp.index,
            ticktext=[plural_years(x) for x in salary_by_exp.index],
        ),
    )
    st.plotly_chart(fig_exp, use_container_width=True)
else:
    st.info("Нет данных после применения фильтров")

st.divider()

# ============================================================
# 🛠 ТОП-15 НАВЫКОВ
# ============================================================
st.subheader("🛠 Топ-15 навыков")

NORMALIZE = {
    "навык работы с linux": "linux",
    "навык работы с sql": "sql",
    "написание запросов": "sql",
    "навык работы с git": "git",
    "навык работы с microsoft excel": "excel",
    "написание тестов и тестирование программного кода": "тестирование",
    "разработка нового функционала": "разработка",
    "умение разбираться и работать с чужим кодом": "чтение чужого кода",
    "ответственность , добросовестность": "ответственность",
}

all_skills = []
for skills_list in filtered["skills"]:
    if isinstance(skills_list, list):
        for skill in skills_list:
            if isinstance(skill, str):
                clean = skill.strip().lower()
                if clean:
                    clean = NORMALIZE.get(clean, clean)
                    all_skills.append(clean)

if all_skills:
    skills_series = pd.Series(all_skills)
    top_skills = skills_series.value_counts().head(15)
    st.plotly_chart(horizontal_bar(top_skills, color="#E67E22"), use_container_width=True)
else:
    st.info("Нет данных о навыках после применения фильтров")