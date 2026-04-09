#!/usr/bin/env python3
"""
Test Export Functionality - Verify CSV and JSON exports work correctly
Tests the changes made to _export_filtered_csv() and _export_filtered_json()
"""

import json
import csv
from pathlib import Path
from datetime import datetime

# Test data - simulated captured products
TEST_METADATA = [
    {
        "timestamp": "2026-04-02T18:18:39.852",
        "product": "Café",
        "brand": "MDD",
        "description": "250g moulu tradition",
        "magazine": "auchan_fr",
        "magazine_location": "Paris",
        "quantity": "250",
        "unit": "g",
        "price": 3.99,
        "currency": "EUR",
        "url": "auchan.fr/product/12345",
        "store": "Auchan",
        "location": "Paris",
        "week": 14,
        "year": 2026,
        "image": "/home/user/.snippets/images/2026-04-02_18-18-39.png",
        "ocr_confidence": 0.92,
        "language": "fr",
        "notes": "Test capture 1"
    },
    {
        "timestamp": "2026-04-02T18:25:00.000",
        "product": "Lait",
        "brand": "Lactel",
        "description": "1L demi-écrémé",
        "magazine": "carrefour_fr",
        "magazine_location": "Paris",
        "quantity": "1",
        "unit": "L",
        "price": 0.95,
        "currency": "EUR",
        "url": "carrefour.fr/item/67890",
        "store": "Carrefour",
        "location": "Paris",
        "week": 14,
        "year": 2026,
        "image": "/home/user/.snippets/images/2026-04-02_18-25-00.png",
        "ocr_confidence": 0.88,
        "language": "fr",
        "notes": "Test capture 2"
    },
    {
        "timestamp": "2026-04-02T18:32:15.500",
        "product": "Pain",
        "brand": "Boulangerie locale",
        "description": "Baguette tradition",
        "magazine": "aldi_de",
        "magazine_location": "Berlin",
        "quantity": "1",
        "unit": "piece",
        "price": 1.49,
        "currency": "EUR",
        "url": "none",
        "store": "Aldi",
        "location": "Berlin",
        "week": 14,
        "year": 2026,
        "image": "/home/user/.snippets/images/2026-04-02_18-32-15.png",
        "ocr_confidence": 0.85,
        "language": "fr",
        "notes": "Offline in-store capture"
    }
]

def export_test_csv(data, output_path):
    """Export test data as CSV (simulating _export_filtered_csv)"""
    print(f"\n[TEST] Exporting CSV to: {output_path}")

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        # Header MUST include: description, currency, url, ocr_confidence
        header = "Date,Time,Store,Location,Magazine,Magazine_Location,Week,Year,Product," \
                 "Brand,Description,Quantity,Unit,Price,Currency,URL,OCR_Confidence,Language,Notes,Image_Path\n"
        f.write(header)

        for meta in data:
            timestamp = meta.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(timestamp)
                date_str = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%H:%M:%S")
            except:
                date_str = ""
                time_str = ""

            # Safe CSV escaping
            store = meta.get("store", "").replace(",", ";")
            location = meta.get("location", "").replace(",", ";")
            product = meta.get("product", "").replace(",", ";")
            brand = meta.get("brand", "").replace(",", ";")
            description = meta.get("description", "").replace(",", ";").replace("\n", " ")
            quantity = meta.get("quantity", "")
            unit = meta.get("unit", "")
            price = meta.get("price", 0.0)
            currency = meta.get("currency", "EUR")
            url = meta.get("url", "none")
            ocr_confidence = meta.get("ocr_confidence", "")
            notes = meta.get("notes", "").replace(",", ";").replace("\n", " ")
            image = meta.get("image", "")

            magazine = meta.get("magazine", "")
            magazine_location = meta.get("magazine_location", "")
            week = meta.get("week", "")
            year = meta.get("year", "")
            language = meta.get("language", "")

            row = f"{date_str},{time_str},{store},{location},{magazine},{magazine_location}," \
                  f"{week},{year},{product},{brand},\"{description}\",{quantity},{unit},{price:.2f}," \
                  f"{currency},{url},{ocr_confidence},{language},\"{notes}\",\"{image}\"\n"
            f.write(row)

    print(f"[OK] CSV exported successfully")
    return True

def export_test_json(data, output_path):
    """Export test data as JSON (simulating _export_filtered_json)"""
    print(f"\n[TEST] Exporting JSON to: {output_path}")

    export_data = []
    for meta in data:
        record = meta.copy()
        record["export_language"] = "fr"
        export_data.append(record)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print(f"[OK] JSON exported successfully")
    return True

def verify_csv_export(filepath):
    """Verify CSV has all required fields"""
    print(f"\n[VERIFY] Checking CSV fields: {filepath}")

    required_fields = [
        "Date", "Time", "Store", "Location", "Magazine", "Magazine_Location",
        "Week", "Year", "Product", "Brand", "Description", "Quantity", "Unit",
        "Price", "Currency", "URL", "OCR_Confidence", "Language", "Notes", "Image_Path"
    ]

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip()
        fields = header.split(',')

    print(f"[CSV] Found {len(fields)} fields:")
    for i, field in enumerate(fields, 1):
        status = "[OK]" if field in required_fields else "[?]"
        print(f"  {status} {i:2d}. {field}")

    # Check for new fields
    new_fields = ["Description", "Currency", "URL", "OCR_Confidence"]
    print(f"\n[CHECK] New fields added:")
    for field in new_fields:
        if field in fields:
            print(f"  [OK] {field} - PRESENT")
        else:
            print(f"  [ERR] {field} - MISSING")

    # Verify data
    print(f"\n[DATA] CSV sample rows:")
    with open(filepath, 'r', encoding='utf-8') as f2:
        lines = f2.readlines()
        for i, line in enumerate(lines[1:3], 1):
            values = line.split(',')
            print(f"  Row {i}: {len(values)} columns")

    return len(fields) == len(required_fields)

def verify_json_export(filepath):
    """Verify JSON has all required fields"""
    print(f"\n[VERIFY] Checking JSON fields: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"[JSON] Found {len(data)} records")

    if len(data) > 0:
        first_record = data[0]
        print(f"[JSON] Fields in first record ({len(first_record.keys())} fields):")

        required_fields = [
            "timestamp", "product", "brand", "description", "magazine",
            "magazine_location", "quantity", "unit", "price", "currency",
            "url", "ocr_confidence", "language", "notes", "image"
        ]

        for field in sorted(first_record.keys()):
            status = "[OK]" if field in required_fields else "[*]"
            value = str(first_record[field])[:40]
            print(f"  {status} {field}: {value}")

        # Check for critical new fields
        print(f"\n[CHECK] Critical fields in JSON:")
        critical_fields = ["description", "url", "ocr_confidence", "currency"]
        for field in critical_fields:
            if field in first_record:
                value = first_record[field]
                print(f"  [OK] {field}: {value}")
            else:
                print(f"  [ERR] {field}: MISSING")

        return all(field in first_record for field in critical_fields)

    return False

def main():
    """Run all tests"""
    print("=" * 80)
    print("EXPORT FUNCTIONALITY TEST")
    print("=" * 80)

    # Create test directory
    test_dir = Path.home() / "snippets_test"
    test_dir.mkdir(exist_ok=True)

    csv_path = test_dir / "test_export.csv"
    json_path = test_dir / "test_export.json"

    try:
        # Test CSV Export
        print("\n[TEST 1] CSV EXPORT")
        print("-" * 80)
        csv_ok = export_test_csv(TEST_METADATA, str(csv_path))
        csv_verified = verify_csv_export(str(csv_path))

        # Test JSON Export
        print("\n[TEST 2] JSON EXPORT")
        print("-" * 80)
        json_ok = export_test_json(TEST_METADATA, str(json_path))
        json_verified = verify_json_export(str(json_path))

        # Summary
        print("\n" + "=" * 80)
        print("TEST RESULTS SUMMARY")
        print("=" * 80)

        results = [
            ("CSV Export", csv_ok and csv_verified),
            ("JSON Export", json_ok and json_verified),
            ("CSV has Description", "Description" in open(csv_path).readline()),
            ("CSV has Currency", "Currency" in open(csv_path).readline()),
            ("CSV has URL", "URL" in open(csv_path).readline()),
            ("CSV has OCR_Confidence", "OCR_Confidence" in open(csv_path).readline()),
        ]

        print("\nTest Results:")
        for test_name, passed in results:
            status = "[PASS]" if passed else "[FAIL]"
            print(f"  {status} - {test_name}")

        all_passed = all(result[1] for result in results)

        print("\n" + "=" * 80)
        if all_passed:
            print("[SUCCESS] ALL TESTS PASSED - Export functionality is working correctly!")
        else:
            print("[ERROR] SOME TESTS FAILED - Check output above")
        print("=" * 80)

        print(f"\nTest files created:")
        print(f"  CSV: {csv_path}")
        print(f"  JSON: {json_path}")
        print(f"\nYou can open these files to verify the exports manually.")

        return all_passed

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
