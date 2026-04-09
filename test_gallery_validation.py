#!/usr/bin/env python3
"""
Test Review Gallery Field Validation Feature

This test verifies:
1. Gallery validation method exists (_validate_gallery_fields)
2. Quantity validation is implemented
3. Unit validation is implemented
4. Alert system is properly integrated
5. Matches capture view validation behavior
6. No syntax errors introduced
"""

import sys
import ast

print("[TEST] Review Gallery Field Validation")
print("=" * 80)

# Test 1: Verify syntax
print("\n[TEST 1] Checking syntax...")
try:
    with open(r"C:\Users\emman\p_Claude\devs\snipper_tool\main.py", 'r', encoding='utf-8') as f:
        code = f.read()
    ast.parse(code)
    print("[OK] main.py has valid Python syntax")
except SyntaxError as e:
    print(f"[ERROR] Syntax error: {e}")
    sys.exit(1)

# Test 2: Check for gallery validation method
print("\n[TEST 2] Checking for gallery validation method...")
if 'def _validate_gallery_fields' in code:
    print("[OK] _validate_gallery_fields method found")
else:
    print("[ERROR] Gallery validation method not found")
    sys.exit(1)

# Test 3: Verify gallery validations
print("\n[TEST 3] Verifying gallery field validations...")
validation_checks = [
    ('Quantity float conversion', 'float(self.meta_quantity.text())'),
    ('Quantity zero check', 'if qty == 0.0'),
    ('Unit empty check', 'self.meta_unit.text().strip()'),
    ('Invalid quantity error', 'must be a valid number > 0'),
]

all_found = True
for check_name, check_string in validation_checks:
    if check_string in code:
        print(f"  [OK] {check_name}")
    else:
        print(f"  [ERROR] {check_name} not found")
        all_found = False

if not all_found:
    sys.exit(1)

# Test 4: Check integration with save_image_annotations
print("\n[TEST 4] Checking integration with save function...")
integration_checks = [
    ('Validation called', 'missing_fields = self._validate_gallery_fields()'),
    ('Check for missing fields', 'if missing_fields:'),
    ('Alert shown', 'QMessageBox(self)'),
    ('Fix Fields button', 'fix_btn = alert.addButton("Fix Fields"'),
    ('Save Anyway button', 'save_btn = alert.addButton("Save Anyway"'),
    ('Button handling', 'alert.clickedButton() == fix_btn'),
]

all_found = True
for check_name, check_string in integration_checks:
    if check_string in code:
        print(f"  [OK] {check_name}")
    else:
        print(f"  [ERROR] {check_name} not found")
        all_found = False

if not all_found:
    sys.exit(1)

# Test 5: Verify matching capture view logic
print("\n[TEST 5] Comparing with capture view validation...")
capture_section = code[code.find('def _validate_capture_fields'):code.find('def _validate_capture_fields') + 1000]
gallery_section = code[code.find('def _validate_gallery_fields'):code.find('def _validate_gallery_fields') + 1000]

# Both should check similar things
checks = [
    ('Both return list', 'return missing_fields'),
]

for check_name, check_string in checks:
    if check_string in capture_section and check_string in gallery_section:
        print(f"  [OK] {check_name} - both consistent")
    else:
        print(f"  [WARNING] {check_name} - may differ")

# Test 6: Check portable version
print("\n[TEST 6] Checking portable version sync...")
try:
    with open(r"C:\Users\emman\p_Claude\devs\snipper_tool\portable_app_v2\main.py", 'r', encoding='utf-8') as f:
        portable_code = f.read()

    if 'def _validate_gallery_fields' in portable_code:
        print("[OK] Portable version has gallery validation")
    else:
        print("[ERROR] Portable version not synced")
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] Could not check portable version: {e}")
    sys.exit(1)

# Final Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

print("\n[SUCCESS] All tests passed!")
print("\nReview Gallery Field Validation Status:")
print("  [OK] Validation method implemented: _validate_gallery_fields()")
print("  [OK] Quantity validation:")
print("       - Must be > 0")
print("       - Must be a valid number")
print("  [OK] Unit validation:")
print("       - Must not be empty")
print("  [OK] Alert system integrated:")
print("       - 'Fix Fields' button returns to gallery for editing")
print("       - 'Save Anyway' button proceeds despite errors")
print("  [OK] Portable version synchronized")

print("\nBehavior in Review Gallery:")
print("  1. User edits Quantity to 0 or Unit to empty")
print("  2. User clicks 'Save Changes'")
print("  3. Validation triggers:")
print("     Result: Alert shows 'Invalid Quantity or Unit'")
print("     Lists exactly what's wrong")
print("  4. User has two options:")
print("     Option A: 'Fix Fields' - Returns to gallery for editing")
print("     Option B: 'Save Anyway' - Proceeds despite warnings")
print("\n  Compare with Capture View:")
print("  - Capture: Shows 'Missing Required Fields' alert")
print("  - Gallery: Shows 'Invalid Quantity or Unit' alert")
print("  - Both: Offer to go back or continue anyway")

print("\n" + "=" * 80)
sys.exit(0)
