from sheets import find_tariff


def calculate_payment(model, department, operation, value):

    tariff = find_tariff(model, department, operation)

    if tariff is None:
        return None

    rate = tariff["Тариф"]
    ttype = tariff["Тип"]

    total = float(value) * float(rate)

    return {
        "type": ttype,
        "rate": rate,
        "total": total
    }