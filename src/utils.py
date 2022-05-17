def celsius_to_farenheight(celsius: float) -> float:
    return celsius * 1.8 + 32

def hpa_to_inhg(pressure: float) -> float:
    # Source: https://www.flightpedia.org/convert-hectopascals-to-inches-of-mercury.html
    return pressure * 0.02952998597817832

def mm_to_inches(mm: float) -> float:
    return mm / 25.4
