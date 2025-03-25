from datetime import datetime

translated_months = {
    1: 'Enero',
    2: 'Febrero',
    3: 'Marzo',
    4: 'Abril',
    5: 'Mayo',
    6: 'Junio',
    7: 'Julio',
    8: 'Agosto',
    9: 'Septiembre',
    10: 'Octubre',
    11: 'Noviembre',
    12: 'Diciembre'
}

def get_today_spanish_format() -> str:
    today = datetime.today()
    return f"{today.day} de {translated_months[today.month]} de {today.year}"
