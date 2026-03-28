import pandas as pd
from fastapi import UploadFile, HTTPException


HEADER_KEYWORDS = [
    "Наименование субсидирования",
    "Статус заявки",
    "Норматив",
    "Причитающаяся сумма",
    "Район хозяйства",
]


def _normalize_cell(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().replace("\n", " ")


def _find_header_row(raw_df: pd.DataFrame) -> int:
    for i in range(min(len(raw_df), 30)):
        row_values = [_normalize_cell(v) for v in raw_df.iloc[i].tolist()]
        row_text = " | ".join(row_values)

        matches = sum(1 for keyword in HEADER_KEYWORDS if keyword.lower() in row_text.lower())
        if matches >= 3:
            return i

    raise HTTPException(
        status_code=400,
        detail="Не удалось автоматически найти строку заголовков в Excel"
    )


def parse_uploaded_file(file: UploadFile) -> pd.DataFrame:
    filename = file.filename.lower()

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(file.file)
            df.columns = [str(col).strip().replace("\n", " ") for col in df.columns]
            return df

        elif filename.endswith(".xlsx"):
            raw_df = pd.read_excel(file.file, header=None)
            header_row = _find_header_row(raw_df)

            # перечитываем файл уже с правильной строкой заголовка
            file.file.seek(0)
            df = pd.read_excel(file.file, header=header_row)

            df.columns = [str(col).strip().replace("\n", " ") for col in df.columns]

            # убираем полностью пустые строки
            df = df.dropna(how="all").reset_index(drop=True)

            return df

        else:
            raise HTTPException(status_code=400, detail="Поддерживаются только CSV и XLSX")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка чтения файла: {str(e)}")