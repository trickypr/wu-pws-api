def celsius_to_farenheight(celsius: float) -> float:
    return round(celsius * 1.8 + 32, 1)

def hpa_to_inhg(pressure: float) -> float:
    # Source: https://www.flightpedia.org/convert-hectopascals-to-inches-of-mercury.html
    return round(pressure * 0.02952998597817832, 3)

def mm_to_inches(mm: float) -> float:
    return round(mm / 25.4, 1)
