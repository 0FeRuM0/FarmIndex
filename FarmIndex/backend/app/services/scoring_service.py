import pandas as pd


def to_float(value, default=0.0) -> float:
    try:
        if pd.isna(value):
            return default
        if isinstance(value, str):
            value = value.replace(" ", "").replace("\xa0", "").replace(",", ".")
        return float(value)
    except Exception:
        return default


def calculate_score(row: pd.Series) -> dict:
    score = 50.0
    positive_factors = []
    negative_factors = []
    risk_flags = []

    status = str(row.get("Статус заявки", "")).strip().lower()
    subsidy_name = str(row.get("Наименование субсидирования", "")).strip()
    direction = str(row.get("Направление водства", "")).strip()
    region = str(row.get("Район хозяйства", "")).strip()
    akimat = str(row.get("Акимат", "")).strip()

    norm = to_float(row.get("Норматив"))
    amount = to_float(row.get("Причитающаяся сумма"))

    if "исполнена" in status:
        score += 15
        positive_factors.append("Заявка исполнена")
    else:
        negative_factors.append("Статус заявки требует внимания")
        risk_flags.append("Нестандартный статус заявки")

    if norm >= 100000:
        score += 12
        positive_factors.append("Высокий норматив субсидирования")
    elif norm >= 10000:
        score += 7
        positive_factors.append("Устойчивый норматив субсидирования")
    elif norm > 0:
        score += 3
        positive_factors.append("Норматив указан")
    else:
        negative_factors.append("Норматив отсутствует или некорректен")
        risk_flags.append("Проверить норматив")

    if amount >= 10000000:
        score += 10
        positive_factors.append("Крупный объем субсидии")
        risk_flags.append("Крупная сумма требует ручной проверки")
    elif amount >= 3000000:
        score += 7
        positive_factors.append("Значимая сумма субсидии")
    elif amount > 0:
        score += 3
        positive_factors.append("Сумма субсидии указана")
    else:
        negative_factors.append("Сумма отсутствует или некорректна")
        risk_flags.append("Проверить сумму")

    if not subsidy_name:
        score -= 10
        negative_factors.append("Нет наименования субсидирования")
        risk_flags.append("Неполные данные")

    if not region:
        score -= 8
        negative_factors.append("Не указан район хозяйства")
        risk_flags.append("Нет района")

    if not direction:
        score -= 5
        negative_factors.append("Не указано направление")
        risk_flags.append("Нет направления")

    if not akimat:
        score -= 4
        negative_factors.append("Не указан акимат")
        risk_flags.append("Нет акимата")

    score = max(0, min(score, 100))

    if score >= 75:
        recommendation = "Recommended"
    elif score >= 60:
        recommendation = "Manual Review"
    else:
        recommendation = "Low Priority"

    if "Крупная сумма требует ручной проверки" in risk_flags:
        risk = "High"
    elif len(risk_flags) >= 2:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "score": round(score, 2),
        "recommendation": recommendation,
        "risk": risk,
        "positive_factors": positive_factors,
        "negative_factors": negative_factors,
        "risk_flags": risk_flags,
    }


def run_scoring(df: pd.DataFrame) -> pd.DataFrame:
    result_rows = []

    for _, row in df.iterrows():
        row_data = row.to_dict()
        scoring_result = calculate_score(row)
        row_data.update(scoring_result)

        row_data["name"] = str(row.get("Наименование субсидирования", "Без названия")).strip()
        row_data["region"] = str(row.get("Район хозяйства", "Не указан")).strip()

        result_rows.append(row_data)

    return pd.DataFrame(result_rows)