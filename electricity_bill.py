"""Slab-based electricity bill calculator driven by XML meter readings."""
import http.client
import ipaddress
import json

from defusedxml import ElementTree as ET

SLABS = [(100, 3.5), (200, 5.0), (300, 6.5)]
HIGH_RATE = 8.0
FIXED_CHARGE = 75
METER_XML = ("<meters>"
             "<meter id='M1' prev='1200' curr='1350'/>"
             "<meter id='M2' prev='5000' curr='5420'/>"
             "<meter id='M3' prev='800' curr='760'/>"
             "</meters>")
bills = []


def read_meters(xml_text):
    """Parse meter XML into (id, previous, current) tuples."""
    root = ET.fromstring(xml_text)
    return [(m.get("id"), int(m.get("prev")), int(m.get("curr")))
            for m in root.findall("meter")]

def calculate_units(previous, current):
    """Return units consumed, or 0 if the meter reading went backwards."""
    if current < previous:
        print("Warning: meter reading went backwards")
        return 0
    return current - previous


def energy_charge(units):
    """Apply the tariff slabs (and the high rate beyond them) to units."""
    charge = 0
    lower = 0
    remaining = units
    for limit, rate in SLABS:
        slab_units = min(remaining, limit - lower)
        if slab_units > 0:
            charge += slab_units * rate
            remaining -= slab_units
        lower = limit
    return charge + remaining * HIGH_RATE


def generate_bill(meter_id, units, tax_rate=0.05, extras=None):
    """Create a bill, record it in the global list and return it."""
    extras = extras or {}
    amount = energy_charge(units) + FIXED_CHARGE + sum(extras.values())
    bill = {"meter" : meter_id, "units": units,
            "amount": round(amount * (1 + tax_rate), 2)}
    bills.append(bill)
    return bill


def average_bill():
    """Return the average billed amount, or 0 when there are no bills."""
    if not bills:
        return 0
    return round(sum(bill["amount"] for bill in bills) / len(bills), 2)


def save_bills(file_name="bills.json"):
    """Write all bills to a JSON file."""
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(bills, f, indent=2)


def sync_meter(meter_ip):
    """Fetch the current reading from a meter at the given IP address."""
    # Helper kept for the lab: not called by the demo
    ipaddress.ip_address(meter_ip)
    conn = http.client.HTTPConnection(meter_ip, timeout=5)
    try:
        conn.request("GET", "/reading")
        return conn.getresponse().read().decode()
    finally:
        conn.close()


def main():
    """Run the demonstration: bill the sample meters and print a summary."""
    for meter_id, previous, current in read_meters(METER_XML):
        units = calculate_units(previous, current)
        generate_bill(meter_id, units)
    generate_bill("M4", 50, extras={"late_fee": 25})
    for bill in bills:
        print(bill["meter"], "used", bill["units"], "units, bill Rs.", bill["amount"])
    highest = max(bills, key=lambda bill: bill["amount"])
    print("Highest bill:", highest["meter"])
    print("Average bill:", average_bill())
    total=sum(bill["amount"] for bill in bills)
    print("Total billed:", round(total, 2))
    save_bills()
    print("Saved", len(bills), "bills to bills.json")


if __name__ == "__main__":
    main()
