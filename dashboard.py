import json
import pandas as pd
import streamlit as st
import plotly.express as px

# ============================================================
# 🎨 ВСЕ СТИЛИ — В ОДНОМ МЕСТЕ
# ============================================================
st.markdown("""
<style>
/* ------------------------------------------------------------
   Акцентный цвет (красный — как у чекбоксов Streamlit)
   Меняй здесь один раз — применится ко всем иконкам сайдбара.
   ------------------------------------------------------------ */
:root {
    --accent: #FF4B4B;
    --color-regions: #4A90E2;
    --color-companies: #4A90E2;
    --color-salary: #50C878;
    --color-skills: #E67E22;
    --color-table: #9B59B6;
}

/* Базовое выравнивание иконок */
.fa-solid { vertical-align: middle; }

/* ------------------------------------------------------------
   Заголовок приложения
   ------------------------------------------------------------ */
.app-title {
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.app-title i { color: var(--accent); }

/* ------------------------------------------------------------
   Заголовки разделов в основном контенте
   ------------------------------------------------------------ */
.section-heading {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 1rem 0 0.5rem 0;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.section-heading.regions   i { color: var(--color-regions); }
.section-heading.companies i { color: var(--color-companies); }
.section-heading.salary    i { color: var(--color-salary); }
.section-heading.skills    i { color: var(--color-skills); }
.section-heading.table     i { color: var(--color-table); }

/* ------------------------------------------------------------
   Главные заголовки в сайдбаре (Набор данных, Фильтры)
   ------------------------------------------------------------ */
.sidebar-heading {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding-left: 1rem;
}
.sidebar-heading i { color: var(--accent); }

/* ------------------------------------------------------------
   Подзаголовки в сайдбаре (Регионы, Опыт, Зарплата)
   Увеличен padding-left и gap, чтобы иконка не сливалась с текстом.
   ------------------------------------------------------------ */
.sidebar-subheading {
    font-size: 1rem;
    font-weight: 600;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    padding-left: 1rem;
    display: flex;
    align-items: center;
    gap: 0.9rem;
}
.sidebar-subheading i {
    color: var(--accent);
    min-width: 1.2rem;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Подключаем Font Awesome
st.markdown(
    '<link rel="stylesheet" '
    'href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">',
    unsafe_allow_html=True,
)

# ============================================================
# 🎨 ФУНКЦИИ-ОБЁРТКИ
# ============================================================
def app_title(icon, text):
    st.markdown(
        f'<div class="app-title"><i class="fa-solid fa-{icon}"></i>{text}</div>',
        unsafe_allow_html=True,
    )

def heading(icon, text, css_class=""):
    st.markdown(
        f'<div class="section-heading {css_class}"><i class="fa-solid fa-{icon}"></i>{text}</div>',
        unsafe_allow_html=True,
    )

def sidebar_heading(icon, text):
    st.sidebar.markdown(
        f'<div class="sidebar-heading"><i class="fa-solid fa-{icon}"></i>{text}</div>',
        unsafe_allow_html=True,
    )

def sidebar_subheading(icon, text):
    st.sidebar.markdown(
        f'<div class="sidebar-subheading"><i class="fa-solid fa-{icon}"></i>{text}</div>',
        unsafe_allow_html=True,
    )

# ============================================================
# 📊 ЗАГОЛОВОК ПРИЛОЖЕНИЯ
# ============================================================
st.set_page_config(page_title="Анализ Python-вакансий", layout="wide")
app_title("chart-line", "Анализ Python-вакансий с «Работы России»")

# ============================================================
# 📂 ПЕРЕКЛЮЧАТЕЛЬ НАБОРА ДАННЫХ
# ============================================================
sidebar_heading("database", "Набор данных")

dataset_choice = st.sidebar.radio(
    "Набор данных",
    options=["Только Python", "Все с упоминанием Python"],
    index=0,
    help="Строгий режим — только вакансии, где Python указан в названии. "
         "Широкий режим — все вакансии, где Python упоминается хоть где-то.",
    label_visibility="collapsed",
)

if dataset_choice == "Только Python":
    data_file = "results/python_vacancies.json"
else:
    data_file = "results/raw_vacancies.json"

with open(data_file, "r", encoding="utf-8") as f:
    raw = json.load(f)

st.caption(f"Загружено вакансий: **{len(raw)}**")

# --- Функция склонения лет ---
def plural_years(n):
    n = int(n)
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} год"
    elif n % 10 in [2, 3, 4] and n % 100 not in [12, 13, 14]:
        return f"{n} года"
    else:
        return f"{n} лет"

df = pd.DataFrame(raw)
df["region_name"] = df["region"].apply(lambda x: x.get("name") if isinstance(x, dict) else None)
df["company_name"] = df["company"].apply(lambda x: x.get("name") if isinstance(x, dict) else None)
df["experience"] = df["requirement"].apply(
    lambda x: x.get("experience") if isinstance(x, dict) else None
)

all_regions = sorted(df["region_name"].dropna().unique().tolist())
all_exp = sorted(df["experience"].dropna().unique().tolist())

# ============================================================
# 🎛 ФИЛЬТРЫ
# ============================================================
st.sidebar.divider()
sidebar_heading("sliders", "Фильтры")

if st.sidebar.button("Сбросить все фильтры", use_container_width=True):
    for key in ["regions_filter", "exp_filter", "salary_filter", "chk_all_regions", "chk_all_exp"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

st.sidebar.divider()

# --- Регионы ---
sidebar_subheading("city", "Регионы")

if "regions_filter" not in st.session_state:
    st.session_state.regions_filter = all_regions

def on_all_regions_change():
    if st.session_state.chk_all_regions:
        st.session_state.regions_filter = all_regions
    else:
        st.session_state.regions_filter = []

st.sidebar.checkbox(
    "Выбрать все",
    value=True,
    key="chk_all_regions",
    on_change=on_all_regions_change,
)

selected_regions = st.sidebar.multiselect(
    "Регионы",
    options=all_regions,
    key="regions_filter",
    label_visibility="collapsed",
)

# --- Опыт ---
sidebar_subheading("calendar-days", "Опыт работы")

if "exp_filter" not in st.session_state:
    st.session_state.exp_filter = all_exp

def on_all_exp_change():
    if st.session_state.chk_all_exp:
        st.session_state.exp_filter = all_exp
    else:
        st.session_state.exp_filter = []

st.sidebar.checkbox(
    "Выбрать все",
    value=True,
    key="chk_all_exp",
    on_change=on_all_exp_change,
)

selected_exp = st.sidebar.multiselect(
    "Опыт",
    options=all_exp,
    key="exp_filter",
    format_func=plural_years,
    label_visibility="collapsed",
)

# --- Зарплата ---
sidebar_subheading("money-bill-wave", "Зарплата")

max_salary = int(df["salary_min"].max()) if df["salary_min"].max() > 0 else 100000
salary_range = st.sidebar.slider(
    "Минимальная ЗП, ₽",
    min_value=0,
    max_value=max_salary,
    value=(0, max_salary),
    step=10000,
    key="salary_filter",
    label_visibility="collapsed",
)

# ============================================================
# 🧹 ПРИМЕНЯЕМ ФИЛЬТРЫ
# ============================================================
filtered = df.copy()

if selected_regions:
    filtered = filtered[filtered["region_name"].isin(selected_regions)]

if selected_exp:
    filtered = filtered[filtered["experience"].isin(selected_exp)]

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
# 📈 ФУНКЦИЯ ГОРИЗОНТАЛЬНОГО ГРАФИКА
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
heading("city", "Топ-10 регионов", "regions")
top_regions = filtered["region_name"].value_counts().head(10)
if len(top_regions):
    st.plotly_chart(horizontal_bar(top_regions, color="#4A90E2"), use_container_width=True)
else:
    st.info("Нет данных после применения фильтров")

st.divider()

# ============================================================
# 🏢 ТОП-10 КОМПАНИЙ
# ============================================================
heading("building", "Топ-10 компаний", "companies")
top_companies = filtered["company_name"].value_counts().head(10)
if len(top_companies):
    st.plotly_chart(horizontal_bar(top_companies, color="#4A90E2"), use_container_width=True)
else:
    st.info("Нет данных после применения фильтров")

st.divider()

# ============================================================
# 💰 ЗАРПЛАТА ПО ОПЫТУ
# ============================================================
heading("money-bill-wave", "Медианная зарплата по опыту работы", "salary")
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
heading("tools", "Топ-15 навыков", "skills")

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

st.divider()

# ============================================================
# 📋 ТАБЛИЦА ВАКАНСИЙ
# ============================================================
heading("table", "Все вакансии", "table")

table_df = filtered[[
    "job-name", "company_name", "region_name",
    "salary_min", "salary_max", "experience", "vac_url"
]].copy()

table_df.columns = ["Вакансия", "Компания", "Регион", "ЗП от", "ЗП до", "Опыт (лет)", "Ссылка"]

table_df["ЗП от"] = table_df["ЗП от"].apply(lambda x: x if x > 0 else None)
table_df["ЗП до"] = table_df["ЗП до"].apply(lambda x: x if x > 0 else None)

table_df["Опыт (лет)"] = table_df["Опыт (лет)"].apply(
    lambda x: plural_years(x) if pd.notna(x) else "—"
)

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Ссылка": st.column_config.LinkColumn("Ссылка", display_text="Открыть ↗"),
        "ЗП от": st.column_config.NumberColumn("ЗП от, ₽", format="%d"),
        "ЗП до": st.column_config.NumberColumn("ЗП до, ₽", format="%d"),
    },
)

# ============================================================
# 📥 СКАЧАТЬ CSV
# ============================================================
heading("download", "Скачать данные", "table")

csv = table_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    "Скачать CSV",
    data=csv,
    file_name="python_vacancies.csv",
    mime="text/csv",
)