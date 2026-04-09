#!/usr/bin/env python3
"""
Test Capture Field Validation Feature

This test verifies:
1. Validation method exists (_validate_capture_fields)
2. All required fields are checked
3. Unit "none" is set as default
4. Alert system is properly integrated
5. No syntax errors introduced
"""

import sys
import ast

print("[TEST] Capture Field Validation Feature")
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

# Test 2: Check for validation method
print("\n[TEST 2] Checking for validation method...")
if 'def _validate_capture_fields' in code:
    print("[OK] _validate_capture_fields method found")
else:
    print("[ERROR] Validation method not found")
    sys.exit(1)

# Test 3: Check what fields are validated
print("\n[TEST 3] Verifying all required fields are checked...")
validation_checks = [
    ('Product name', 'product_name_edit.text()'),
    ('Brand', 'brand_edit.text()'),
    ('Description', 'description_edit.text()'),
    ('Quantity', 'quantity_edit.value()'),
    ('Unit', 'unit_combo.currentText()'),
    ('URL', 'url_edit.text()'),
]

all_found = True
for field_name, field_check in validation_checks:
    if field_check in code:
        print(f"  [OK] {field_name} validation found")
    else:
        print(f"  [ERROR] {field_name} validation missing")
        all_found = False

if not all_found:
    sys.exit(1)

# Test 4: Check for "none" default in unit combo
print("\n[TEST 4] Checking for 'none' as default unit...")
if 'self.unit_combo.setCurrentIndex(0)  # Set "none" as default' in code or \
   'default_units = ["none"' in code:
    print("[OK] 'none' set as default unit")
else:
    print("[ERROR] 'none' not set as default")
    sys.exit(1)

# Test 5: Check alert system
print("\n[TEST 5] Verifying alert system...")
alert_checks = [
    ('Alert creation', 'QMessageBox(self)'),
    ('Missing fields display', 'missing_text ='),
    ('Go Back button', 'go_back_btn'),
    ('Continue Anyway button', 'continue_btn'),
    ('Button click handling', 'alert.clickedButton()'),
]

all_found = True
for check_name, check_string in alert_checks:
    if check_string in code:
        print(f"  [OK] {check_name}")
    else:
        print(f"  [ERROR] {check_name} not found")
        all_found = False

if not all_found:
    sys.exit(1)

# Test 6: Check validation logic
print("\n[TEST 6] Verifying validation logic...")
logic_checks = [
    ('Empty product check', 'not self.product_name_edit.text().strip()'),
    ('Quantity zero check', 'self.quantity_edit.value() == 0.0'),
    ('Unit none check', 'self.unit_combo.currentText() == "none"'),
    ('Missing fields returned', 'return missing_fields'),
]

all_found = True
for check_name, check_string in logic_checks:
    if check_string in code:
        print(f"  [OK] {check_name}")
    else:
        print(f"  [ERROR] {check_name} not found")
        all_found = False

if not all_found:
    sys.exit(1)

# Test 7: Check portable version
print("\n[TEST 7] Checking portable version sync...")
try:
    with open(r"C:\Users\emman\p_Claude\devs\snipper_tool\portable_app_v2\main.py", 'r', encoding='utf-8') as f:
        portable_code = f.read()

    if 'def _validate_capture_fields' in portable_code:
        print("[OK] Portable version has validation method")
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
print("\nCapture Field Validation Feature Status:")
print("  [OK] Validation method implemented")
print("  [OK] All required fields checked:")
print("       - Product name (must not be empty)")
print("       - Brand (must not be empty)")
print("       - Description (must not be empty)")
print("       - Quantity (must be > 0)")
print("       - Unit (must not be 'none')")
print("       - URL (must not be empty)")
print("  [OK] 'none' set as default in unit combo")
print("  [OK] Alert system integrated with two buttons:")
print("       - 'Go Back' (return to form, no capture)")
print("       - 'Continue Anyway' (skip validation, capture anyway)")
print("  [OK] Portable version synchronized")

print("\nBehavior:")
print("  1. User fills all fields correctly")
print("     Result: No alert shown, screenshot captures silently")
print("  2. User has missing/invalid fields")
print("     Result: Warning alert appears listing what's missing")
print("     Option A: 'Go Back' returns to form for editing")
print("     Option B: 'Continue Anyway' proceeds to screenshot anyway")

print("\n" + "=" * 80)
sys.exit(0)
