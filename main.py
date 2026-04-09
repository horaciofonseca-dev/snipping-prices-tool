import sys
import os
import json
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple

import keyboard
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QCompleter, QInputDialog, QFileDialog,
    QTabWidget, QScrollArea, QCheckBox, QSplitter, QListWidget, QListWidgetItem,
    QSpinBox, QDoubleSpinBox, QTextEdit, QGridLayout, QMessageBox, QDialog, QRadioButton,
    QTableWidget, QTableWidgetItem, QGroupBox
)
from PyQt5.QtCore import Qt, QStringListModel, QSize, QLocale, QTimer
from PyQt5.QtGui import QFont, QPixmap

from snipping_tool import SnippingOverlay

# Debug logging
DEBUG = True
def debug_log(action: str, details: str = ""):
    """Log debug information to console and debug file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    msg = f"[{timestamp}] {action}"
    if details:
        msg += f" | {details}"
    if DEBUG:
        print(msg)
    # Also save to debug log file
    try:
        debug_file = Path.home() / "snippets" / "debug.log"
        with open(debug_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except:
        pass

# Dataset Configuration Manager
class DatasetConfig:
    """Manage dataset path and loading state."""

    def __init__(self):
        self.config_file = "dataset_config.json"
        self.dataset_path = None
        self.is_loaded = False
        self.load_config()

    def load_config(self):
        """Load dataset path from config file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.dataset_path = data.get("dataset_path")
                    self.is_loaded = True
                    debug_log("CONFIG_LOADED", f"Dataset path: {self.dataset_path}")
        except Exception as e:
            debug_log("CONFIG_ERROR", f"Failed to load dataset config: {e}")
            self.is_loaded = False

    def save_config(self, path):
        """Save dataset path to config."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({"dataset_path": path}, f)
                self.dataset_path = path
                self.is_loaded = True
                debug_log("CONFIG_SAVED", f"Dataset path saved: {path}")
        except Exception as e:
            debug_log("CONFIG_SAVE_ERROR", f"Failed to save config: {e}")

# Unit conversion (canonical = metric)
UNIT_CONVERSION_MAP = {
    # Volume (canonical: L)
    "L": 1.0,
    "l": 1.0,
    "ml": 0.001,
    "mL": 0.001,
    "cl": 0.01,
    "cL": 0.01,
    "gal": 3.78541,  # US gallon
    "gallon": 3.78541,
    "fl oz": 0.0295735,
    "floz": 0.0295735,

    # Weight (canonical: kg)
    "kg": 1.0,
    "g": 0.001,
    "mg": 0.000001,
    "oz": 0.0283495,  # Ounces
    "lb": 0.453592,   # Pounds
    "lbs": 0.453592,

    # Count (canonical: piece)
    "piece": 1.0,
    "pieces": 1.0,
}

CANONICAL_UNITS = {
    "L": "volume",
    "ml": "volume",
    "cl": "volume",
    "gal": "volume",
    "fl oz": "volume",
    "kg": "weight",
    "g": "weight",
    "mg": "weight",
    "oz": "weight",
    "lb": "weight",
    "piece": "count",
}

def get_iso_week(d: datetime = None) -> Tuple[int, int]:
    """
    Get ISO week number (Monday-Sunday).

    Args:
        d: datetime object (default: today)

    Returns:
        (year, week_number)
    """
    if d is None:
        d = datetime.now()
    return d.isocalendar()[0:2]

def get_week_date_range(week: int, year: int) -> Tuple[date, date]:
    """
    Get Monday-Sunday date range for ISO week.

    Args:
        week: ISO week number (1-53)
        year: Year

    Returns:
        (monday_date, sunday_date)
    """
    # Jan 4 is always in week 1 (ISO 8601)
    jan4 = date(year, 1, 4)
    # Monday of week 1
    week_one_monday = jan4 - timedelta(days=jan4.weekday())
    # Monday of target week
    monday = week_one_monday + timedelta(weeks=week-1)
    # Sunday of target week
    sunday = monday + timedelta(days=6)
    return (monday, sunday)

def format_week_display(week: int, year: int) -> str:
    """
    Format week display with date range.

    Args:
        week: ISO week number (1-53)
        year: Year

    Returns:
        Formatted string: "Week 13 (Mar 16-22, 2026)"
    """
    monday, sunday = get_week_date_range(week, year)
    monday_str = monday.strftime("%b %d")
    sunday_str = sunday.strftime("%d, %Y")
    return f"Week {week} ({monday_str}-{sunday_str})"

def convert_unit(value: float, from_unit: str, to_unit: str = "canonical") -> float:
    """
    Convert units to canonical metric format.

    Args:
        value: Numeric value
        from_unit: Source unit (L, gal, kg, oz, g, piece, etc.)
        to_unit: Target unit (default: canonical metric)

    Returns:
        Converted value
    """
    if from_unit not in UNIT_CONVERSION_MAP:
        debug_log("UNIT_CONVERSION_WARNING", f"Unknown unit: {from_unit}, returning original value")
        return value

    # Convert to metric (canonical)
    conversion_factor = UNIT_CONVERSION_MAP[from_unit]
    converted_value = value * conversion_factor

    return converted_value

def get_canonical_unit(unit: str) -> str:
    """Get the canonical (metric) unit for a given unit."""
    unit_type = CANONICAL_UNITS.get(unit, "unknown")
    if unit_type == "volume":
        return "L"
    elif unit_type == "weight":
        return "kg"
    elif unit_type == "count":
        return "piece"
    else:
        return unit

# Optional OCR support
try:
    from ocr_handler import detect_price, PriceDetector
    OCR_ENABLED = True
except Exception as e:
    OCR_ENABLED = False
    print(f"OCR disabled: {e}")
    detect_price = lambda x: None

# Get the detector instance for detecting all prices
try:
    from ocr_handler import get_price_detector
    price_detector = get_price_detector()
    if price_detector:
        print(f"[OK] Price detector initialized successfully")
    else:
        print(f"[WARNING] Price detector is None (OCR not available)")
except Exception as e:
    print(f"[ERROR] Failed to initialize price detector: {e}")
    import traceback
    traceback.print_exc()
    price_detector = None


class SnippetApp(QMainWindow):
    """Main application window for product screenshot capture and review."""

    def __init__(self):
        debug_log("APP_INIT", "Starting SnippetApp initialization")
        super().__init__()
        self.base_folder = Path.home() / "snippets"
        self.metadata_file = self.base_folder / "metadata.json"
        self.product_history_file = self.base_folder / "product_history.json"
        self.stores_file = self.base_folder / "stores.json"
        self.config_file = self.base_folder / "config.json"
        self.products_file = Path(__file__).parent / "products.json"
        self.captured_products_file = self.base_folder / "captured_products.json"
        self.magazines_file = Path(__file__).parent / "magazines.json"
        self.product_registry_file = Path(__file__).parent / "product_registry.json"

        # Ensure base folder exists
        self.base_folder.mkdir(exist_ok=True)

        # Initialize dataset configuration manager
        self.dataset_config = DatasetConfig()

        # Load data (metadata must load first for locations)
        self.product_names = self._load_product_history()
        self.stores = self._load_stores()
        self.selected_folder = self._load_selected_folder()
        self._load_config()  # Load locale and unit_system settings
        self.products_db = self._load_products_db()
        self.captured_products = self._load_captured_products()
        self.metadata_list = self._load_metadata()
        self.locations = self._load_locations()  # Must be after metadata_list
        self.brands_list = []  # Initialize brands list for autocomplete
        self.current_basket = "ample"

        # Load new multi-store data structures
        self.magazines = self._load_magazines()
        self.product_registry = self._load_product_registry()

        # Snipping overlay
        self.snipping_overlay = None

        # Location locking
        self.location_locked = False
        self.locked_location = None

        # Magazine/location selection (Phase 1)
        self.selected_magazine = "auchan_fr"
        self.selected_location = "Paris"
        self.selected_week = get_iso_week()[1]
        self.selected_year = get_iso_week()[0]

        # Initialize gallery filters (will be replaced by actual UI controls)
        self.filter_store = None
        self.filter_product = None
        self.filter_gallery_magazine = None
        self.filter_gallery_location = None
        self.filter_gallery_week = None

        # Backup and audit system
        self.backup_folder = self.base_folder / ".backups"
        self.backup_folder.mkdir(exist_ok=True)
        self.audit_log_file = self.base_folder / ".audit.json"
        self.audit_log = self._load_audit_log()
        self.admin_mode_unlocked = False

        self.init_ui()
        self.setup_hotkeys()

    def get_product_name(self, product_id: str) -> str:
        """
        Get product name in the selected language.

        Args:
            product_id: Product identifier (e.g., "lait_1.0_L")

        Returns:
            Product name in selected language (French or English)
        """
        if not self.product_registry or product_id not in self.product_registry:
            return product_id

        product_data = self.product_registry[product_id]

        if self.language == "fr":
            return product_data.get("french_name", product_id)
        else:  # English
            return product_data.get("english_name", product_id)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Snippet Tool - Shrinkflation Basket Analyzer")

        # Set compact default window size - user can resize freely
        self.setGeometry(50, 50, 480, 800)  # Start at 480px width (very compact)

        # Allow window to be resized to any size - NO constraints
        self.setMinimumSize(300, 400)  # Absolute minimum (300px width allows resizing down)
        # No maximum size - user can expand freely

        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main tabs: Capture, Review, Settings & Admin
        main_tabs = QTabWidget()

        # Capture tab
        capture_tab = self._create_capture_tab()
        main_tabs.addTab(capture_tab, "Capture")

        # Review/Gallery tab
        review_tab = self._create_review_tab()
        main_tabs.addTab(review_tab, "Review Gallery")

        # Settings & Admin tab (PHASE 1)
        admin_tab = self._create_settings_admin_tab()
        main_tabs.addTab(admin_tab, "Settings & Admin")

        # Connect tab change event for PHASE B auto-sync (Feature 4 enhancement)
        main_tabs.currentChanged.connect(self._on_tab_changed)
        self.main_tabs = main_tabs  # Save reference for tab tracking

        layout = QVBoxLayout()
        layout.addWidget(main_tabs)
        central_widget.setLayout(layout)

        # Populate brand autocomplete from historical data
        self._update_brand_completer()

        # Apply initial week spinbox styling
        self._update_week_spinbox_styling()

        self.show()

    def _create_capture_tab(self):
        """Create the capture tab with compact controls + image preview stacked vertically."""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Left panel - CONTROLS: Capture controls + image preview (stacked vertically)
        left_panel = self._create_capture_panel()
        layout.addWidget(left_panel, 1)  # Takes proportional space - user controls via window resize

        # Right panel - CATEGORIES: Product categories and product list
        right_panel = self._create_product_panel()
        layout.addWidget(right_panel, 0)  # Minimal - collapses when window is narrow

        widget.setLayout(layout)

        # Load initial basket on startup (with fallback if no data)
        try:
            if self.products_db and "baskets" in self.products_db:
                self.load_basket("Ample")
            else:
                self.load_basket("Minimum")  # Fallback
                debug_log("BASKET_LOAD", "Using fallback basket due to missing data")
        except Exception as e:
            debug_log("BASKET_LOAD_ERROR", f"Failed to load basket: {e}")
            # Create empty basket structure
            self.current_basket = "minimum"
            self._populate_categories()

        return widget

    def _create_review_tab(self):
        """Create the image review/gallery tab."""
        widget = QWidget()
        layout = QHBoxLayout()

        # Left: Image list
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        # PHASE C Task 2: Context indicator showing current session
        self.context_indicator = QLabel()
        self.context_indicator.setStyleSheet("font-weight: bold; color: #333; padding: 5px; background-color: #e8f4f8; border-radius: 3px;")
        self.context_indicator.setAlignment(Qt.AlignLeft)
        left_layout.addWidget(self.context_indicator)

        # Filters (Feature 4: Gallery Organization + original Store filter)
        filter_layout = QGridLayout()

        # Row 1: Magazine, Location, Week
        filter_layout.addWidget(QLabel("Magazine:"), 0, 0)
        self.filter_gallery_magazine = QComboBox()
        self.filter_gallery_magazine.addItem("All")
        magazines_set = sorted(set(m.get("magazine", "") for m in self.metadata_list if m.get("magazine")))
        self.filter_gallery_magazine.addItems(magazines_set)
        self.filter_gallery_magazine.currentTextChanged.connect(self.refresh_image_list)
        filter_layout.addWidget(self.filter_gallery_magazine, 0, 1)

        filter_layout.addWidget(QLabel("Location:"), 0, 2)
        self.filter_gallery_location = QComboBox()
        self.filter_gallery_location.addItem("All")
        locations_set = sorted(set(m.get("magazine_location", "") for m in self.metadata_list if m.get("magazine_location")))
        self.filter_gallery_location.addItems(locations_set)
        self.filter_gallery_location.currentTextChanged.connect(self.refresh_image_list)
        filter_layout.addWidget(self.filter_gallery_location, 0, 3)

        filter_layout.addWidget(QLabel("Week:"), 0, 4)
        self.filter_gallery_week = QComboBox()
        self.filter_gallery_week.addItem("All")
        weeks_set = sorted(set(m.get("week") for m in self.metadata_list if m.get("week")))
        self.filter_gallery_week.addItems([str(w) for w in weeks_set])
        self.filter_gallery_week.currentTextChanged.connect(self.refresh_image_list)
        filter_layout.addWidget(self.filter_gallery_week, 0, 5)

        # Row 2: Legacy Store filter (backward compatibility) + Product filter
        filter_layout.addWidget(QLabel("Store:"), 1, 0)
        self.filter_store = QComboBox()
        self.filter_store.addItem("All")
        self.filter_store.addItems(sorted(set(m.get("store", "") for m in self.metadata_list)))
        self.filter_store.currentTextChanged.connect(self.refresh_image_list)
        filter_layout.addWidget(self.filter_store, 1, 1)

        filter_layout.addWidget(QLabel("Product:"), 1, 2)
        self.filter_product = QComboBox()
        self.filter_product.addItem("All")
        self.filter_product.addItems(sorted(set(m.get("product", "") for m in self.metadata_list)))
        self.filter_product.currentTextChanged.connect(self.refresh_image_list)
        filter_layout.addWidget(self.filter_product, 1, 3)

        # Refresh and Clear buttons
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_image_list)
        filter_layout.addWidget(refresh_btn, 1, 4)

        clear_btn = QPushButton("Clear Filters")
        clear_btn.clicked.connect(self._clear_gallery_filters)
        filter_layout.addWidget(clear_btn, 1, 5)

        # Export button (Feature 5)
        export_btn = QPushButton("Export Data")
        export_btn.clicked.connect(self.export_granular_data)
        export_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        filter_layout.addWidget(export_btn, 1, 6)

        left_layout.addLayout(filter_layout)

        # PHASE C Task 3: Gallery progress indicator
        self.gallery_progress_label = QLabel("Gallery: 0 images")
        self.gallery_progress_label.setStyleSheet("font-size: 10px; color: #666; padding: 3px;")
        left_layout.addWidget(self.gallery_progress_label)

        # Image list
        left_layout.addWidget(QLabel("Captured Images:"))
        self.image_list = QListWidget()
        self.image_list.itemClicked.connect(self.on_image_selected)
        left_layout.addWidget(self.image_list)

        left_panel.setLayout(left_layout)
        layout.addWidget(left_panel, 1)

        # Right: Image preview and metadata
        right_panel = self._create_image_preview_panel()
        layout.addWidget(right_panel, 1)

        widget.setLayout(layout)
        self.refresh_image_list()
        return widget

    def _create_image_preview_panel(self):
        """Create image preview and metadata panel."""
        panel = QWidget()
        layout = QVBoxLayout()

        # Image preview
        self.image_preview = QLabel()
        self.image_preview.setMinimumSize(300, 300)
        self.image_preview.setStyleSheet("border: 1px solid gray;")
        self.image_preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_preview)

        # PHASE C Task 1: Cleaned-up metadata editor - editable fields only
        layout.addWidget(QLabel("Product Details:"))
        metadata_layout = QGridLayout()

        # Product (primary)
        metadata_layout.addWidget(QLabel("Product:"), 0, 0)
        self.meta_product = QLineEdit()
        metadata_layout.addWidget(self.meta_product, 0, 1)

        # Brand
        metadata_layout.addWidget(QLabel("Brand:"), 1, 0)
        self.meta_brand = QLineEdit()
        metadata_layout.addWidget(self.meta_brand, 1, 1)

        # Description
        metadata_layout.addWidget(QLabel("Description:"), 2, 0)
        self.meta_description = QLineEdit()
        metadata_layout.addWidget(self.meta_description, 2, 1)

        # Quantity & Unit (side-by-side)
        metadata_layout.addWidget(QLabel("Quantity:"), 3, 0)
        self.meta_quantity = QLineEdit()
        metadata_layout.addWidget(self.meta_quantity, 3, 1)

        metadata_layout.addWidget(QLabel("Unit:"), 4, 0)
        self.meta_unit = QLineEdit()
        metadata_layout.addWidget(self.meta_unit, 4, 1)

        # Price
        metadata_layout.addWidget(QLabel("Price (€):"), 5, 0)
        self.meta_price = QDoubleSpinBox()
        self.meta_price.setRange(0, 1000)
        self.meta_price.setDecimals(2)
        metadata_layout.addWidget(self.meta_price, 5, 1)

        # URL (NEW - for bot automation and tracking)
        metadata_layout.addWidget(QLabel("URL:"), 6, 0)
        self.meta_url = QLineEdit()
        self.meta_url.setPlaceholderText("e.g., auchan.fr/product/123 or 'none' for offline")
        metadata_layout.addWidget(self.meta_url, 6, 1)

        # Notes
        metadata_layout.addWidget(QLabel("Notes:"), 7, 0)
        self.meta_notes = QTextEdit()
        self.meta_notes.setMaximumHeight(80)
        metadata_layout.addWidget(self.meta_notes, 7, 1)

        layout.addLayout(metadata_layout)

        # PHASE C Task 1: Read-only info section (minimal, optional)
        info_layout = QGridLayout()
        info_layout.addWidget(QLabel("Location:"), 0, 0)
        self.meta_location = QLineEdit()
        self.meta_location.setStyleSheet("background-color: #f0f0f0;")
        info_layout.addWidget(self.meta_location, 0, 1)

        info_layout.addWidget(QLabel("Captured:"), 1, 0)
        self.meta_timestamp = QLineEdit()
        self.meta_timestamp.setReadOnly(True)
        self.meta_timestamp.setStyleSheet("background-color: #f0f0f0; color: gray;")
        self.meta_timestamp.setMaximumHeight(20)
        info_layout.addWidget(self.meta_timestamp, 1, 1)

        # Store reassignment dropdown (NEW)
        info_layout.addWidget(QLabel("Reassign Store:"), 2, 0)
        self.meta_store_reassign = QComboBox()
        self.meta_store_reassign.addItem("Select store...")
        self.meta_store_reassign.setStyleSheet("background-color: #fff3cd;")  # Light yellow to indicate action
        info_layout.addWidget(self.meta_store_reassign, 2, 1)

        layout.addLayout(info_layout)

        layout.addLayout(metadata_layout)

        # Action buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save Changes")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px;")
        save_btn.clicked.connect(self.save_image_annotations)
        button_layout.addWidget(save_btn)

        retake_btn = QPushButton("Retake Image")
        retake_btn.clicked.connect(self.retake_image)
        button_layout.addWidget(retake_btn)

        delete_btn = QPushButton("Delete Image")
        delete_btn.clicked.connect(self.delete_image)
        button_layout.addWidget(delete_btn)

        detect_price_btn = QPushButton("Detect Price")
        detect_price_btn.clicked.connect(self.manual_detect_price)
        button_layout.addWidget(detect_price_btn)

        # NEW: Reassign selected items to store button
        reassign_btn = QPushButton("Reassign Selected to Store")
        reassign_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 5px;")
        reassign_btn.clicked.connect(self.reassign_selected_store)
        button_layout.addWidget(reassign_btn)

        delete_record_btn = QPushButton("Delete Record & Image")
        delete_record_btn.clicked.connect(self.delete_record_and_image)
        delete_record_btn.setStyleSheet("background-color: #ff6b6b; color: white;")
        button_layout.addWidget(delete_record_btn)

        layout.addLayout(button_layout)

        # Export moved to Gallery filters (Feature 5 - PHASE A cleanup: removed old export buttons)

        panel.setLayout(layout)
        return panel

    def refresh_image_list(self):
        """Refresh the image list based on filters (Feature 4: Gallery Organization)."""
        self.image_list.clear()
        self.current_images = []

        # Get all filters (with safe defaults if not initialized yet)
        store_filter = self.filter_store.currentText() if hasattr(self, 'filter_store') else "All"
        product_filter = self.filter_product.currentText() if hasattr(self, 'filter_product') else "All"
        magazine_filter = self.filter_gallery_magazine.currentText() if hasattr(self, 'filter_gallery_magazine') else "All"
        location_filter = self.filter_gallery_location.currentText() if hasattr(self, 'filter_gallery_location') else "All"
        week_filter = self.filter_gallery_week.currentText() if hasattr(self, 'filter_gallery_week') else "All"

        # Collect filtered items
        filtered_items = []

        for idx, meta in enumerate(self.metadata_list):
            # Apply filters (Feature 4)
            if store_filter != "All" and meta.get("store") != store_filter:
                continue
            if product_filter != "All" and meta.get("product") != product_filter:
                continue
            if magazine_filter != "All" and meta.get("magazine") != magazine_filter:
                continue
            if location_filter != "All" and meta.get("magazine_location") != location_filter:
                continue
            if week_filter != "All" and str(meta.get("week", "")) != week_filter:
                continue

            filtered_items.append((idx, meta))

        # Sort by timestamp descending (newest first)
        filtered_items.sort(key=lambda x: x[1].get("timestamp", ""), reverse=True)

        # Add sorted items to gallery
        for idx, meta in filtered_items:
            image_path = meta.get("image", "")
            product = meta.get("product", "Unknown")
            store = meta.get("store", "Unknown")
            timestamp = meta.get("timestamp", "")

            # Extract date from timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                date_str = "Unknown"

            display_text = f"{product} - {store} ({date_str})"

            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, idx)  # Store index for batch operations
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Enable checkbox
            item.setCheckState(Qt.Unchecked)  # Default unchecked
            self.image_list.addItem(item)
            self.current_images.append((idx, meta))

        # PHASE C Task 3: Update gallery progress indicator
        if hasattr(self, 'gallery_progress_label'):
            image_count = len(self.current_images)
            self.gallery_progress_label.setText(f"Gallery: {image_count} image(s)")

        # PHASE C Task 2: Update context indicator
        if hasattr(self, 'context_indicator'):
            self._update_context_indicator()

    def _clear_gallery_filters(self):
        """Clear all gallery filters (Feature 4)."""
        if hasattr(self, 'filter_store'):
            self.filter_store.setCurrentIndex(0)  # "All"
        if hasattr(self, 'filter_product'):
            self.filter_product.setCurrentIndex(0)  # "All"
        if hasattr(self, 'filter_gallery_magazine'):
            self.filter_gallery_magazine.setCurrentIndex(0)  # "All"
        if hasattr(self, 'filter_gallery_location'):
            self.filter_gallery_location.setCurrentIndex(0)  # "All"
        if hasattr(self, 'filter_gallery_week'):
            self.filter_gallery_week.setCurrentIndex(0)  # "All"
        self.refresh_image_list()
        debug_log("GALLERY_FILTERS_CLEARED", "All filters reset to 'All'")

    def on_image_selected(self, item):
        """Handle image selection."""
        idx = item.data(Qt.UserRole)
        if idx < len(self.metadata_list):
            meta = self.metadata_list[idx]
            self.display_image(meta)

    def display_image(self, metadata):
        """Display selected image and its metadata."""
        try:
            image_path = metadata.get("image", "")

            # Load and display image
            if image_path and Path(image_path).exists():
                pixmap = QPixmap(image_path)
                scaled = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
                self.image_preview.setPixmap(scaled)
            else:
                self.image_preview.setText("Image not found")

            # Load metadata
            # Store removed (PHASE A cleanup: shown in gallery list only)
            location_text = metadata.get("location", "")
            self.meta_location.setText(location_text if location_text else "")
            self.meta_product.setText(metadata.get("product", ""))
            self.meta_description.setText(metadata.get("description", ""))
            self.meta_brand.setText(metadata.get("brand", ""))
            self.meta_quantity.setText(str(metadata.get("quantity", "")))
            self.meta_unit.setText(metadata.get("unit", ""))
            self.meta_url.setText(metadata.get("url", "none"))  # NEW: URL field

            # Safely set price value
            price = metadata.get("price", 0.0)
            if price is None:
                price = 0.0
            try:
                self.meta_price.setValue(float(price))
            except (ValueError, TypeError):
                self.meta_price.setValue(0.0)

            self.meta_notes.setPlainText(metadata.get("notes", ""))
            self.meta_timestamp.setText(metadata.get("timestamp", ""))

            # Populate store reassign dropdown with available stores (NEW)
            if hasattr(self, 'meta_store_reassign'):
                self.meta_store_reassign.clear()
                self.meta_store_reassign.addItem("Select store...")
                # Get all unique stores from magazines data
                available_stores = set()
                for mag in self.magazines.get("magazines", {}).values():
                    if "name" in mag:
                        available_stores.add(mag.get("name", ""))
                for store in sorted(available_stores):
                    self.meta_store_reassign.addItem(store)

        except Exception as e:
            print(f"Error displaying image: {e}")
            self.image_preview.setText(f"Error loading image: {e}")

        # Store reference for saving
        self.current_metadata_index = self.metadata_list.index(metadata)

    def _validate_gallery_fields(self) -> list:
        """Validate quantity and unit fields in Review Gallery. Returns list of missing/invalid fields."""
        missing_fields = []

        # Check quantity (must be > 0)
        try:
            qty = float(self.meta_quantity.text())
            if qty == 0.0:
                missing_fields.append("Quantity (must be > 0)")
        except (ValueError, AttributeError):
            missing_fields.append("Quantity (must be a valid number > 0)")

        # Check unit (must not be empty)
        if not self.meta_unit.text().strip():
            missing_fields.append("Unit (must not be empty)")

        return missing_fields

    def save_image_annotations(self):
        """Save annotations for current image with validation."""
        if not hasattr(self, 'current_metadata_index'):
            return

        idx = self.current_metadata_index
        if idx < len(self.metadata_list):
            # Validate quantity and unit (same as capture view)
            missing_fields = self._validate_gallery_fields()

            if missing_fields:
                # Show alert with missing fields
                missing_text = "\n".join([f"  - {field}" for field in missing_fields])
                alert = QMessageBox(self)
                alert.setWindowTitle("Invalid Quantity or Unit")
                alert.setText(f"The following fields are invalid:\n\n{missing_text}\n\nDo you want to fix these fields, or save anyway?")
                alert.setIcon(QMessageBox.Warning)

                # Add buttons
                fix_btn = alert.addButton("Fix Fields", QMessageBox.RejectRole)
                save_btn = alert.addButton("Save Anyway", QMessageBox.AcceptRole)

                alert.exec_()

                # If user clicked "Fix Fields", return without saving
                if alert.clickedButton() == fix_btn:
                    self.status_label.setText("Please fix Quantity and Unit before saving.")
                    self.status_label.setStyleSheet("color: orange;")
                    return
                # If user clicked "Save Anyway", proceed below

            unit_text = self.meta_unit.text()
            quantity_text = self.meta_quantity.text()
            # Recalculate canonical unit if unit changed
            canonical_quantity = convert_unit(float(quantity_text) if quantity_text else 0.0, unit_text)
            canonical_unit = get_canonical_unit(unit_text)

            self.metadata_list[idx].update({
                "location": self.meta_location.text(),
                "product": self.meta_product.text(),
                "description": self.meta_description.text(),
                "brand": self.meta_brand.text(),
                "quantity": quantity_text,
                "unit": unit_text,
                "canonical_quantity": canonical_quantity,
                "canonical_unit": canonical_unit,
                "price": self.meta_price.value(),
                "url": self.meta_url.text() or "none",  # NEW: Save URL field
                "notes": self.meta_notes.toPlainText(),
            })
            self._save_metadata_list()

            # Update brand autocomplete with newly saved brand
            self._update_brand_completer()

            self.status_label.setText("Annotations saved!")
            self.status_label.setStyleSheet("color: green;")

    def delete_image(self):
        """Delete current image."""
        if not hasattr(self, 'current_metadata_index'):
            return

        idx = self.current_metadata_index
        if idx < len(self.metadata_list):
            meta = self.metadata_list[idx]
            image_path = meta.get("image", "")

            # Delete image file
            if image_path and Path(image_path).exists():
                Path(image_path).unlink()

            # Remove from metadata
            del self.metadata_list[idx]
            self._save_metadata_list()

            self.refresh_image_list()
            self.image_preview.setText("Image deleted")

    def retake_image(self):
        """Retake screenshot for current image."""
        if not hasattr(self, 'current_metadata_index'):
            return

        idx = self.current_metadata_index
        if idx >= len(self.metadata_list):
            return

        # Get metadata for the image being retaken
        old_metadata = self.metadata_list[idx]
        product = old_metadata.get("product", "")

        # Store metadata index to update later
        self.retake_metadata_index = self.current_metadata_index

        # Delete old image file
        old_image = old_metadata.get("image", "")
        if old_image and Path(old_image).exists():
            try:
                Path(old_image).unlink()
            except:
                pass

        # Pre-fill product name temporarily and start capture
        original_product = self.product_name_edit.text()
        self.product_name_edit.setText(product)

        # Prevent multiple overlays from being created - clean up properly
        if self.snipping_overlay is not None:
            try:
                self.snipping_overlay.cleanup()
                self.snipping_overlay.deleteLater()
            except Exception as e:
                print(f"Cleanup error: {e}")
            self.snipping_overlay = None

        # Minimize GUI so user can see content behind (same as normal capture)
        debug_log("RETAKE_START", "Minimizing GUI window for retake")
        self.showMinimized()

        # Create new overlay for retake
        try:
            self.snipping_overlay = SnippingOverlay(self)
            self.snipping_overlay.capture_complete.connect(self.on_capture_complete)
            self.snipping_overlay.show_overlay()
        except Exception as e:
            print(f"Error creating overlay: {e}")
            self.product_name_edit.setText(original_product)
            self.status_label.setText("Error creating overlay.")
            self.status_label.setStyleSheet("color: red;")

    def delete_record_and_image(self):
        """Delete selected record and its image file."""
        if not hasattr(self, 'current_metadata_index'):
            self.status_label.setText("No record selected!")
            self.status_label.setStyleSheet("color: red;")
            return

        idx = self.current_metadata_index
        if idx >= len(self.metadata_list):
            return

        metadata = self.metadata_list[idx]
        image_path = metadata.get("image", "")

        # Delete image file
        if image_path:
            try:
                Path(image_path).unlink()
                print(f"DEBUG: Image deleted: {image_path}")
            except Exception as e:
                print(f"ERROR: Failed to delete image: {e}")

        # Delete record from metadata
        del self.metadata_list[idx]
        self._save_metadata_list()

        # Clear display
        self.image_preview.setText("Record deleted")
        self.image_preview.setStyleSheet("color: red;")
        self.refresh_image_list()

        self.status_label.setText("Record and image deleted!")
        self.status_label.setStyleSheet("color: orange;")
        print(f"DEBUG: Record deleted at index {idx}")

    def reassign_selected_store(self):
        """Reassign selected items to a different store (moves files and updates metadata)."""
        # Get the selected store from dropdown
        new_store = self.meta_store_reassign.currentText()
        if new_store == "Select store..." or not new_store:
            self.status_label.setText("Please select a store to reassign to!")
            self.status_label.setStyleSheet("color: orange;")
            return

        # Get all checked items from the gallery list
        checked_indices = []
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            if item.checkState() == Qt.Checked:
                idx = item.data(Qt.UserRole)
                checked_indices.append(idx)

        if not checked_indices:
            self.status_label.setText("Please select items to reassign (check the boxes)!")
            self.status_label.setStyleSheet("color: orange;")
            return

        # Find the magazine code for the new store
        new_magazine = None
        for mag_code, mag_data in self.magazines.get("magazines", {}).items():
            if mag_data.get("name") == new_store:
                new_magazine = mag_code
                break

        if not new_magazine:
            self.status_label.setText(f"Store '{new_store}' not found in magazines!")
            self.status_label.setStyleSheet("color: red;")
            return

        # Confirmation dialog
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirm Store Reassignment")
        msg.setText(f"Reassign {len(checked_indices)} item(s) to '{new_store}'?\n\n"
                   f"This will:\n"
                   f"• Move image files to the {new_store} folder\n"
                   f"• Update metadata with new store assignment\n"
                   f"• Update image file paths")
        msg.setIcon(QMessageBox.Question)

        confirm_btn = msg.addButton("Reassign", QMessageBox.AcceptRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.RejectRole)

        msg.exec_()

        if msg.clickedButton() != confirm_btn:
            self.status_label.setText("Reassignment cancelled")
            return

        # Perform reassignment for each checked item
        moved_count = 0
        failed_count = 0
        errors = []

        for idx in checked_indices:
            if idx >= len(self.metadata_list):
                failed_count += 1
                continue

            metadata = self.metadata_list[idx]
            old_image_path = metadata.get("image", "")
            old_store = metadata.get("store", "")

            if not old_image_path or not Path(old_image_path).exists():
                failed_count += 1
                errors.append(f"Image not found: {old_image_path}")
                continue

            try:
                # Calculate new image path
                old_path = Path(old_image_path)
                # New path: replace old store with new store
                new_path_str = str(old_path).replace(f"/{old_store}/", f"/{new_store}/")
                new_path = Path(new_path_str)

                # Create destination directory if it doesn't exist
                new_path.parent.mkdir(parents=True, exist_ok=True)

                # Move the image file
                old_path.rename(new_path)

                # Update metadata
                metadata["store"] = new_store
                metadata["magazine"] = new_magazine
                metadata["image"] = str(new_path)

                moved_count += 1
                self._add_audit_entry("STORE_REASSIGNED", f"Item {idx}: {old_store} → {new_store}")

            except Exception as e:
                failed_count += 1
                errors.append(f"Error moving {old_image_path}: {e}")
                print(f"ERROR: Failed to reassign item {idx}: {e}")

        # Save updated metadata
        if moved_count > 0:
            self._save_metadata_list()

        # Clear checkboxes
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            item.setCheckState(Qt.Unchecked)

        # Refresh gallery
        self.refresh_image_list()

        # Show result
        result_msg = f"Reassignment complete:\n• Moved: {moved_count}\n• Failed: {failed_count}"
        if errors:
            result_msg += f"\n\nErrors:\n" + "\n".join(errors[:3])  # Show first 3 errors

        self.status_label.setText(result_msg)
        if failed_count == 0:
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setStyleSheet("color: orange;")

        print(f"DEBUG: Store reassignment completed - Moved: {moved_count}, Failed: {failed_count}")

    def manual_detect_price(self):
        """Manually detect price from current image."""
        print("DEBUG: manual_detect_price called")

        if not hasattr(self, 'current_metadata_index'):
            self.status_label.setText("No image selected!")
            self.status_label.setStyleSheet("color: red;")
            print("DEBUG: No current_metadata_index")
            return

        idx = self.current_metadata_index
        print(f"DEBUG: Current index: {idx}, Total images: {len(self.metadata_list)}")

        if idx >= len(self.metadata_list):
            self.status_label.setText("Invalid image index!")
            self.status_label.setStyleSheet("color: red;")
            return

        metadata = self.metadata_list[idx]
        image_path = metadata.get("image", "")
        print(f"DEBUG: Image path: {image_path}")

        if not image_path or not Path(image_path).exists():
            self.status_label.setText(f"Image file not found: {image_path}")
            self.status_label.setStyleSheet("color: red;")
            print(f"DEBUG: Image does not exist: {image_path}")
            return

        # Try to detect price
        self.status_label.setText("Detecting price...")
        self.status_label.setStyleSheet("color: orange;")
        QApplication.processEvents()

        try:
            print(f"DEBUG: Calling detect_price for: {image_path}")
            detected_price = detect_price(str(image_path))
            print(f"DEBUG: Detected price: {detected_price}")

            if detected_price and detected_price > 0:
                # Show price dialog to confirm/edit
                confirmed_price = self._show_price_dialog(detected_price)
                if confirmed_price > 0:
                    self._save_price(confirmed_price, metadata)
                    self.status_label.setText(f"Price detected: €{confirmed_price:.2f}")
                    self.status_label.setStyleSheet("color: green;")
                    print(f"DEBUG: Price saved: {confirmed_price}")
            else:
                # Show dialog to manually enter price
                confirmed_price = self._show_price_dialog(0.0)
                if confirmed_price > 0:
                    self._save_price(confirmed_price, metadata)
                    self.status_label.setText(f"Price entered: €{confirmed_price:.2f}")
                    self.status_label.setStyleSheet("color: green;")
                    print(f"DEBUG: Manual price saved: {confirmed_price}")
                else:
                    self.status_label.setText("No price entered.")
                    self.status_label.setStyleSheet("color: orange;")
        except Exception as e:
            print(f"ERROR detecting price: {e}")
            import traceback
            traceback.print_exc()
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

    def export_metadata(self):
        """Export metadata to JSON file."""
        export_path = QFileDialog.getSaveFileName(
            self, "Export Metadata", str(self.base_folder / "metadata_export.json"), "JSON Files (*.json)"
        )

        if export_path[0]:
            with open(export_path[0], 'w', encoding='utf-8') as f:
                json.dump(self.metadata_list, f, ensure_ascii=False, indent=2)

            self.status_label.setText(f"Exported to {Path(export_path[0]).name}")
            self.status_label.setStyleSheet("color: green;")

    def _create_product_panel(self):
        """Create the product list panel with dropdown categories and editing."""
        panel = QWidget()
        layout = QVBoxLayout()

        # Basket selection
        basket_layout = QHBoxLayout()
        basket_layout.addWidget(QLabel("Select Basket:"))
        self.basket_combo = QComboBox()
        self.basket_combo.addItems(["Minimum", "Medium", "Ample"])
        self.basket_combo.setCurrentIndex(2)  # Default to Ample
        self.basket_combo.currentTextChanged.connect(self.load_basket)
        basket_layout.addWidget(self.basket_combo)
        basket_layout.addStretch()
        layout.addLayout(basket_layout)

        # APPROACH 1: Multi-select category checkboxes (replaces tabs)
        category_header_layout = QHBoxLayout()
        category_header_layout.addWidget(QLabel("Select Categories:"))

        add_category_btn = QPushButton("+ New Category")
        add_category_btn.clicked.connect(self._add_new_category)
        category_header_layout.addWidget(add_category_btn)
        category_header_layout.addStretch()
        layout.addLayout(category_header_layout)

        # Multi-select category list with "All" option
        self.category_list_widget = QListWidget()
        self.category_list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.category_list_widget.setMaximumHeight(100)
        self.category_list_widget.itemSelectionChanged.connect(self._on_categories_selected)
        layout.addWidget(self.category_list_widget)

        # Category management buttons
        category_mgmt_layout = QHBoxLayout()
        rename_cat_btn = QPushButton("Rename Selected")
        rename_cat_btn.clicked.connect(self._rename_selected_category)
        category_mgmt_layout.addWidget(rename_cat_btn)

        del_cat_btn = QPushButton("Delete Selected")
        del_cat_btn.setStyleSheet("background-color: #ff6b6b; color: white;")
        del_cat_btn.clicked.connect(self._delete_selected_category)
        category_mgmt_layout.addWidget(del_cat_btn)
        category_mgmt_layout.addStretch()
        layout.addLayout(category_mgmt_layout)

        # Product list area
        layout.addWidget(QLabel("Products in Selected Categories:"))

        # Scrollable product list with buttons
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.product_list_layout = QVBoxLayout()
        scroll_widget.setLayout(self.product_list_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Add product button
        add_prod_btn = QPushButton("+ Add Product to Category")
        add_prod_btn.clicked.connect(self._add_product_to_category)
        add_prod_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        layout.addWidget(add_prod_btn)

        # Progress info
        progress_layout = QHBoxLayout()
        self.progress_label = QLabel("Captured: 0/0")
        progress_layout.addWidget(self.progress_label)
        layout.addLayout(progress_layout)

        # ============================================================
        # PREVIOUS CAPTURES SECTION (Phase 2 - UI)
        # ============================================================

        # Previous captures header
        prev_header = QLabel("Previous Captures")
        prev_header_font = prev_header.font()
        prev_header_font.setBold(True)
        prev_header.setFont(prev_header_font)
        layout.addWidget(prev_header)

        # Previous captures list (scrollable)
        self.previous_captures_scroll = QScrollArea()
        self.previous_captures_scroll.setWidgetResizable(True)
        self.previous_captures_scroll_widget = QWidget()
        self.previous_captures_layout = QVBoxLayout()
        self.previous_captures_scroll_widget.setLayout(self.previous_captures_layout)
        self.previous_captures_scroll.setWidget(self.previous_captures_scroll_widget)
        self.previous_captures_scroll.setMaximumHeight(200)  # Set reasonable height
        layout.addWidget(self.previous_captures_scroll)

        # Store previous captures for checkbox management
        self.previous_captures_checkboxes = {}  # Map checkbox -> capture data

        # Store selected category keys
        self.selected_category_keys = []
        self.current_category_widgets = {}  # Store widget references for products
        self.category_items = {}  # Map category key to QListWidgetItem

        panel.setLayout(layout)
        return panel

    def get_captured_products_for_selection(self) -> Dict[str, List[Dict]]:
        """
        Get actual captured products for selected magazine/location/week (Feature 3).

        Returns:
            Dict organized by category: {category: [products]}
        """
        captured_by_product = {}

        # Scan metadata for matching captures
        for item in self.metadata_list:
            if (item.get("magazine") == self.selected_magazine and
                item.get("magazine_location") == self.selected_location and
                item.get("week") == self.selected_week and
                item.get("year") == self.selected_year):

                # Build product ID
                product = item.get("product", "").strip()
                quantity = item.get("quantity", "")
                unit = item.get("unit", "")

                if product:
                    # Create canonical product ID
                    product_id = f"{product}_{quantity}_{unit}".replace(" ", "_")

                    # Get product info from registry
                    if product_id in self.product_registry:
                        product_data = self.product_registry[product_id]

                        # Track capture
                        if product_id not in captured_by_product:
                            captured_by_product[product_id] = {
                                "product_id": product_id,
                                "french_name": product_data.get("french_name", product),
                                "english_name": product_data.get("english_name", product),
                                "quantity": quantity,
                                "unit": unit,
                                "brand": item.get("brand", ""),
                                "price": item.get("price"),
                                "category": product_data.get("category", "Other"),
                                "count": 0,
                            }
                        captured_by_product[product_id]["count"] += 1

        # Organize by category (Feature 3)
        products_by_category = {}

        for product_id, product_info in captured_by_product.items():
            category = product_info["category"]
            if category not in products_by_category:
                products_by_category[category] = []
            products_by_category[category].append(product_info)

        return products_by_category

    def _populate_categories(self):
        """Populate category list widget with basket categories (multi-select)."""
        # Use basket template as the guide
        basket_key = self.current_basket.lower()
        if basket_key not in self.products_db["baskets"]:
            return

        basket_data = self.products_db["baskets"][basket_key]
        self.current_basket_categories = basket_data["products"]
        self.current_basket_category_names = self.products_db["categories"]

        # Populate list widget with "All" first
        self.category_list_widget.blockSignals(True)
        self.category_list_widget.clear()
        self.category_items = {}

        # Add "All" option first
        all_item = QListWidgetItem("All Categories")
        all_item.setData(Qt.UserRole, "__all__")
        self.category_list_widget.addItem(all_item)
        self.category_items["__all__"] = all_item

        # Add individual categories
        for category_key in sorted(self.current_basket_categories.keys()):
            category_name = self.current_basket_category_names.get(category_key, category_key)
            item = QListWidgetItem(category_name)
            item.setData(Qt.UserRole, category_key)
            self.category_list_widget.addItem(item)
            self.category_items[category_key] = item

        self.category_list_widget.blockSignals(False)

        # Select "All" by default
        if len(self.category_items) > 0:
            self.category_list_widget.setCurrentItem(self.category_items.get("__all__"))
            self._on_categories_selected()

    def _on_product_name_changed(self, text: str) -> None:
        """
        Handle product name field changes (Phase 2 - UI Trigger).

        Called when user enters or selects a product name. Triggers the display of
        previous captures for that product in the right panel.

        Args:
            text: Current text in product_name_edit field
        """
        if text.strip():
            # Only refresh if we have a magazine selected
            if self.selected_magazine:
                self._refresh_previous_captures_display(text.strip())
        else:
            # Clear previous captures if product name is empty
            while self.previous_captures_layout.count():
                child = self.previous_captures_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            self.previous_captures_checkboxes = {}

    def _on_previous_capture_checked(self, checkbox: QCheckBox, capture_data: Dict) -> None:
        """
        Handle checkbox click for previous capture (Phase 3 - Auto-Fill).

        When user checks a previous capture, auto-fill brand, description, quantity, unit, and URL fields.
        Fields remain fully editable for substitutes.

        Args:
            checkbox: The checkbox that was clicked
            capture_data: Dict with {brand, description, quantity, unit, url, price, ...} from previous capture
        """
        try:
            if checkbox.isChecked():
                # Auto-fill brand, description, quantity, unit, and URL from previous capture
                brand = capture_data.get("brand", "").strip()
                description = capture_data.get("description", "").strip()
                quantity = capture_data.get("quantity", "")
                unit = capture_data.get("unit", "").strip()
                url = capture_data.get("url", "none").strip()

                self.brand_edit.setText(brand)
                self.description_edit.setText(description)

                # Auto-fill quantity (as float in the spinner)
                if quantity:
                    try:
                        qty_float = float(quantity)
                        self.quantity_edit.setValue(qty_float)
                    except (ValueError, TypeError):
                        pass  # Keep existing value if conversion fails

                # Auto-fill unit
                if unit:
                    # Find unit in combo box
                    unit_index = self.unit_combo.findText(unit)
                    if unit_index >= 0:
                        self.unit_combo.setCurrentIndex(unit_index)

                # Auto-fill URL (Phase 1)
                if url and url != "none":
                    self.url_edit.setText(url)
                else:
                    self.url_edit.setText("none")

                debug_log("AUTO_FILL", f"Filled: Brand={brand}, Desc={description}, Qty={quantity}{unit}, URL={url}")

        except Exception as e:
            debug_log("AUTO_FILL_ERROR", f"Failed to auto-fill from previous capture: {str(e)}")

    def _on_previous_capture_unchecked(self) -> None:
        """
        Handle unchecking a previous capture (Phase 3 - Clear Fields).

        When user unchecks a previous capture, clear the auto-filled fields
        (brand, description, quantity, unit, URL).

        Args:
            None
        """
        try:
            # Clear all auto-filled fields
            self.brand_edit.setText("")
            self.description_edit.setText("")
            self.quantity_edit.setValue(0)
            self.unit_combo.setCurrentIndex(0)  # Reset to first unit option
            self.url_edit.setText("none")  # Reset to default (Phase 1)

            debug_log("CLEAR_FIELDS", "Cleared brand, description, quantity, unit, and URL fields")

        except Exception as e:
            debug_log("CLEAR_FIELDS_ERROR", f"Failed to clear fields: {str(e)}")

    def _on_categories_selected(self):
        """Handle multi-category selection from list widget."""
        # Get selected items
        selected_items = self.category_list_widget.selectedItems()
        self.selected_category_keys = []

        # Check if "All" is selected
        if selected_items and selected_items[0].data(Qt.UserRole) == "__all__":
            # Show all categories
            self.selected_category_keys = list(self.current_basket_categories.keys())
        else:
            # Show selected categories only
            for item in selected_items:
                key = item.data(Qt.UserRole)
                if key != "__all__":
                    self.selected_category_keys.append(key)

        # Clear and rebuild product list for all selected categories
        while self.product_list_layout.count():
            item = self.product_list_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        self.current_category_widgets = {}
        self.product_items = {}

        # Add products from selected categories
        for category_key in sorted(self.selected_category_keys):
            if category_key in self.current_basket_categories:
                products = self.current_basket_categories[category_key]
                category_name = self.current_basket_category_names.get(category_key, category_key)

                # Add category header
                if len(self.selected_category_keys) > 1:
                    header = QLabel(f"[{category_name}]")
                    header.setStyleSheet("font-weight: bold; color: #333; margin-top: 10px;")
                    self.product_list_layout.addWidget(header)

                self.product_items[category_key] = {}

                for product in sorted(products, key=lambda p: p["name"]):
                    product_key = f"{category_key}_{product['name']}"
                    is_captured = product_key in self.captured_products

                    # Create product row with checkbox and buttons
                    product_row = QHBoxLayout()

                    checkbox = QCheckBox(f"{product['name']} ({product.get('size', '')})")
                    checkbox.setChecked(is_captured)
                    checkbox.stateChanged.connect(lambda state, pk=product_key: self._on_product_toggled(pk, state))
                    checkbox.setMinimumWidth(250)
                    product_row.addWidget(checkbox)

                    # Edit button
                    edit_btn = QPushButton("Edit")
                    edit_btn.setMaximumWidth(60)
                    edit_btn.clicked.connect(lambda checked, pk=product_key, p=product, ck=category_key: self._edit_product(pk, p, ck))
                    product_row.addWidget(edit_btn)

                    # Remove button
                    remove_btn = QPushButton("Remove")
                    remove_btn.setMaximumWidth(70)
                    remove_btn.setStyleSheet("background-color: #ffcc00; color: black;")
                    remove_btn.clicked.connect(lambda checked, pk=product_key, ck=category_key: self._remove_product(pk, ck))
                    product_row.addWidget(remove_btn)

                    # Move button (dropdown to select target category)
                    move_combo = QComboBox()
                    move_combo.addItem("Move to...")
                    for other_key, other_name in self.current_basket_category_names.items():
                        if other_key != category_key:
                            move_combo.addItem(other_name, other_key)
                    move_combo.currentIndexChanged.connect(
                        lambda idx, pk=product_key, ck=category_key, mc=move_combo:
                        self._move_product_if_selected(pk, ck, mc)
                    )
                    move_combo.setMaximumWidth(120)
                    product_row.addWidget(move_combo)

                    product_row.addStretch()

                    # Add to layout
                    container = QWidget()
                    container.setLayout(product_row)
                    self.product_list_layout.addWidget(container)

                    self.product_items[category_key][product_key] = checkbox
                    self.current_category_widgets[product_key] = (checkbox, edit_btn, remove_btn, category_key)

        self.product_list_layout.addStretch()
        self._update_progress()

    def _create_category_tab(self, category_key, category_name, product_list):
        """Create a tab for a category with checkboxes."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widget = QWidget()
        layout = QVBoxLayout()

        self.product_items[category_key] = {}

        for product in sorted(product_list, key=lambda p: p["name"]):
            product_key = f"{category_key}_{product['name']}"
            is_captured = product_key in self.captured_products

            checkbox = QCheckBox(f"{product['name']} ({product['size']})")
            checkbox.setChecked(is_captured)
            checkbox.stateChanged.connect(lambda state, pk=product_key: self._on_product_toggled(pk, state))

            self.product_items[category_key][product_key] = checkbox
            layout.addWidget(checkbox)

        layout.addStretch()
        widget.setLayout(layout)
        scroll.setWidget(widget)
        return scroll

    def _on_product_toggled(self, product_key, state):
        """Handle product checkbox toggle."""
        if state == Qt.Checked:
            if product_key not in self.captured_products:
                self.captured_products[product_key] = {
                    "timestamp": datetime.now().isoformat(),
                    "captured": True
                }
        else:
            if product_key in self.captured_products:
                del self.captured_products[product_key]

        self._save_captured_products()
        self._update_progress()

    def _rename_selected_category(self):
        """Rename selected category (multi-select aware) - WITH AUTO-BACKUP."""
        selected_items = self.category_list_widget.selectedItems()
        if not selected_items or selected_items[0].data(Qt.UserRole) == "__all__":
            QMessageBox.warning(self, "Invalid", "Please select a specific category to rename")
            return

        category_key = selected_items[0].data(Qt.UserRole)
        old_name = self.current_basket_category_names.get(category_key, category_key)

        new_name, ok = QInputDialog.getText(self, "Rename Category", "New category name:", text=old_name)
        if not ok or not new_name.strip():
            return

        new_name = new_name.strip()
        if new_name == old_name:
            return

        # Auto-backup before rename
        backup_path = self._create_auto_backup(f"rename category '{old_name}' to '{new_name}'")

        try:
            # Update in memory
            self.current_basket_category_names[category_key] = new_name

            # Update products.json
            self.products_db["categories"][category_key] = new_name
            self._save_products_db()

            self.status_label.setText(f"Category renamed: {old_name} -> {new_name}")
            self.status_label.setStyleSheet("color: green;")

            # Refresh UI
            self._populate_categories()
            self._add_audit_entry("CATEGORY_RENAMED", f"'{old_name}' -> '{new_name}'")
            debug_log("CATEGORY_RENAMED", f"{old_name} -> {new_name}")
        except Exception as e:
            self.status_label.setText(f"Rename failed: {e}")
            self.status_label.setStyleSheet("color: red;")
            self._add_audit_entry("CATEGORY_RENAME_FAILED", f"'{old_name}': {e}", "failed")

    def _delete_selected_category(self):
        """Delete selected category (multi-select aware) - WITH AUTO-BACKUP & DOUBLE-CONFIRM."""
        selected_items = self.category_list_widget.selectedItems()
        if not selected_items or selected_items[0].data(Qt.UserRole) == "__all__":
            QMessageBox.warning(self, "Invalid", "Please select a specific category to delete")
            return

        category_key = selected_items[0].data(Qt.UserRole)
        category_name = self.current_basket_category_names.get(category_key)

        # Count products that will be moved
        product_count = len(self.current_basket_categories.get(category_key, []))

        # Double-confirm dialog
        if not self._double_confirm_dialog(
            "Delete Category",
            f"Delete category '{category_name}'?\n\nThis will move {product_count} products to 'Other'.\nThis cannot be undone.",
            "DELETE"
        ):
            return

        # Auto-backup before deletion
        backup_path = self._create_auto_backup(f"delete category '{category_name}'")

        try:
            # Move products to "Other"
            other_key = "other"
            if category_key != other_key and other_key in self.current_basket_categories:
                products_to_move = self.current_basket_categories[category_key]
                self.current_basket_categories[other_key].extend(products_to_move)

            # Delete category
            del self.current_basket_categories[category_key]
            del self.current_basket_category_names[category_key]

            # Update products.json
            basket_key = self.current_basket.lower()
            self.products_db["baskets"][basket_key]["products"] = self.current_basket_categories
            if category_key in self.products_db["categories"]:
                del self.products_db["categories"][category_key]
            self._save_products_db()

            self.status_label.setText(f"Category deleted: {category_name} (backup available)")
            self.status_label.setStyleSheet("color: green;")
            self._add_audit_entry("CATEGORY_DELETED", f"'{category_name}' ({product_count} products moved)")

        except Exception as e:
            self.status_label.setText(f"Delete failed: {e}")
            self.status_label.setStyleSheet("color: red;")
            self._add_audit_entry("CATEGORY_DELETE_FAILED", f"'{category_name}': {e}", "failed")

        # Refresh UI
        self._populate_categories()

    def _add_new_category(self):
        """Add a new category (APPROACH 1) - WITH AUDIT LOGGING."""
        text, ok = QInputDialog.getText(self, "New Category", "Enter category name:")
        if not ok or not text.strip():
            return

        category_name = text.strip()

        # Generate key from name
        category_key = category_name.lower().replace(" ", "_").replace("&", "and")

        if category_key in self.current_basket_category_names:
            QMessageBox.warning(self, "Duplicate", "Category already exists")
            return

        try:
            # Add to data
            self.current_basket_category_names[category_key] = category_name
            self.current_basket_categories[category_key] = []

            # Update products.json
            self.products_db["categories"][category_key] = category_name
            basket_key = self.current_basket.lower()
            self.products_db["baskets"][basket_key]["products"][category_key] = []
            self._save_products_db()

            self.status_label.setText(f"Category added: {category_name}")
            self.status_label.setStyleSheet("color: green;")
            self._add_audit_entry("CATEGORY_ADDED", f"New category '{category_name}' (key: {category_key})")
        except Exception as e:
            self.status_label.setText(f"Add category failed: {e}")
            self.status_label.setStyleSheet("color: red;")
            self._add_audit_entry("CATEGORY_ADD_FAILED", f"'{category_name}': {e}", "failed")
        self.status_label.setStyleSheet("color: green;")

        # Refresh UI
        self._populate_categories()
        debug_log("CATEGORY_ADDED", category_name)

    def _add_product_to_category(self):
        """Add a product to selected categories (APPROACH 1)."""
        if not self.selected_category_keys:
            QMessageBox.warning(self, "Invalid", "Please select a category first")
            return

        # Dialog for product details
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Product")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Product Name:"))
        name_edit = QLineEdit()
        layout.addWidget(name_edit)

        layout.addWidget(QLabel("Size (e.g., 500g, 1L):"))
        size_edit = QLineEdit()
        layout.addWidget(size_edit)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Add")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        def add_product():
            product_name = name_edit.text().strip()
            product_size = size_edit.text().strip()

            if not product_name:
                QMessageBox.warning(dialog, "Invalid", "Product name required")
                return

            # Add product to selected category (use first selected)
            category_key = self.selected_category_keys[0]
            new_product = {"name": product_name, "size": product_size or "1 unit"}
            self.current_basket_categories[category_key].append(new_product)

            # Update products.json
            basket_key = self.current_basket.lower()
            self.products_db["baskets"][basket_key]["products"][category_key].append(new_product)
            self._save_products_db()

            self.status_label.setText(f"Product added: {product_name}")
            self.status_label.setStyleSheet("color: green;")

            dialog.accept()
            self._on_categories_selected()

        ok_btn.clicked.connect(add_product)
        cancel_btn.clicked.connect(dialog.reject)

        dialog.exec_()

    def _edit_product(self, product_key, product, category_key):
        """Edit product name/size (APPROACH 1)."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Product")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Product Name:"))
        name_edit = QLineEdit()
        name_edit.setText(product["name"])
        layout.addWidget(name_edit)

        layout.addWidget(QLabel("Size:"))
        size_edit = QLineEdit()
        size_edit.setText(product.get("size", ""))
        layout.addWidget(size_edit)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        def save_changes():
            new_name = name_edit.text().strip()
            new_size = size_edit.text().strip()

            if not new_name:
                QMessageBox.warning(dialog, "Invalid", "Product name required")
                return

            # Update product
            product["name"] = new_name
            product["size"] = new_size or "1 unit"

            # Update products.json
            basket_key = self.current_basket.lower()
            self._save_products_db()

            self.status_label.setText(f"Product updated: {new_name}")
            self.status_label.setStyleSheet("color: green;")

            dialog.accept()
            self._on_categories_selected()

        ok_btn.clicked.connect(save_changes)
        cancel_btn.clicked.connect(dialog.reject)

        dialog.exec_()

    def _remove_product(self, product_key, category_key):
        """Remove product from category (APPROACH 1) - WITH AUTO-BACKUP & DOUBLE-CONFIRM."""
        product_name = product_key.split("_", 1)[1] if "_" in product_key else product_key

        # Double-confirm dialog
        if not self._double_confirm_dialog(
            "Remove Product",
            f"Remove '{product_name}' from '{category_key}'?\n\nThis cannot be undone.",
            "REMOVE"
        ):
            return

        # Auto-backup before removal
        backup_path = self._create_auto_backup(f"remove product '{product_name}'")

        try:
            # Find and remove product
            if category_key in self.current_basket_categories:
                self.current_basket_categories[category_key] = [
                    p for p in self.current_basket_categories[category_key]
                    if p["name"] != product_name
                ]

            # Update products.json
            basket_key = self.current_basket.lower()
            self.products_db["baskets"][basket_key]["products"] = self.current_basket_categories
            self._save_products_db()

            self.status_label.setText(f"Product removed: {product_name} (backup available)")
            self.status_label.setStyleSheet("color: green;")
            self._add_audit_entry("PRODUCT_REMOVED", f"'{product_name}' from '{category_key}'")

            self._on_categories_selected()
        except Exception as e:
            self.status_label.setText(f"Remove failed: {e}")
            self.status_label.setStyleSheet("color: red;")
            self._add_audit_entry("PRODUCT_REMOVE_FAILED", f"'{product_name}': {e}", "failed")

    def _move_product_if_selected(self, product_key, from_category, move_combo):
        """Move product to different category if user selects one (APPROACH 1)."""
        if move_combo.currentIndex() == 0:  # "Move to..." is selected
            return

        target_category = move_combo.currentData()
        if not target_category:
            return

        product_name = product_key.split("_", 1)[1] if "_" in product_key else product_key

        # Find product
        product_to_move = None
        if from_category in self.current_basket_categories:
            for p in self.current_basket_categories[from_category]:
                if p["name"] == product_name:
                    product_to_move = p
                    break

        if not product_to_move:
            move_combo.setCurrentIndex(0)
            return

        # Move product
        self.current_basket_categories[from_category].remove(product_to_move)
        if target_category not in self.current_basket_categories:
            self.current_basket_categories[target_category] = []
        self.current_basket_categories[target_category].append(product_to_move)

        # Update products.json
        basket_key = self.current_basket.lower()
        self.products_db["baskets"][basket_key]["products"] = self.current_basket_categories
        self._save_products_db()

        target_name = self.current_basket_category_names.get(target_category, target_category)
        self.status_label.setText(f"Moved '{product_name}' to {target_name}")
        self.status_label.setStyleSheet("color: green;")

        # Reset UI
        move_combo.blockSignals(True)
        move_combo.setCurrentIndex(0)
        move_combo.blockSignals(False)

        self._on_categories_selected()

    def _save_products_db(self):
        """Save products database to file."""
        with open(self.products_file, 'w', encoding='utf-8') as f:
            json.dump(self.products_db, f, ensure_ascii=False, indent=2)
        debug_log("PRODUCTS_DB_SAVED", "products.json updated")

    def load_dataset_from_path(self, path):
        """Load dataset from user-selected path."""
        try:
            products_path = os.path.join(path, "products.json")
            magazines_path = os.path.join(path, "magazines.json")

            if not os.path.exists(products_path):
                QMessageBox.warning(self, "Error", "products.json not found in selected folder")
                debug_log("DATASET_LOAD_ERROR", f"products.json not found in {path}")
                return False

            with open(products_path, 'r', encoding='utf-8') as f:
                self.products_db = json.load(f)

            # Save config
            self.dataset_config.save_config(path)

            # Reload UI
            self._refresh_dataset_display()

            debug_log("DATASET_LOADED", f"Dataset loaded from {path}")
            QMessageBox.information(self, "Success", f"Dataset loaded from {path}")
            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load dataset: {str(e)}")
            debug_log("LOAD_ERROR", str(e))
            return False

    def _refresh_dataset_display(self):
        """Refresh all UI elements after dataset change."""
        try:
            self.product_names = list(set([m.get("product", "") for m in self.metadata_list if m]))
            self._update_brand_completer()
            if hasattr(self, 'progress_label'):
                self._update_progress()
            debug_log("DATASET_REFRESHED", "UI elements refreshed")
        except Exception as e:
            debug_log("REFRESH_ERROR", str(e))

    def browse_dataset(self):
        """Open folder dialog to select dataset location."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Dataset Folder",
            os.path.expanduser("~")
        )
        if folder:
            if self.load_dataset_from_path(folder):
                if hasattr(self, 'dataset_path_label'):
                    self.dataset_path_label.setText(f"Loaded: {folder}")

    def reload_dataset(self):
        """Reload dataset from current path."""
        if self.dataset_config.dataset_path:
            self.load_dataset_from_path(self.dataset_config.dataset_path)
        else:
            QMessageBox.warning(self, "No Path", "No dataset path configured yet. Use Browse to select one.")
            debug_log("RELOAD_WARNING", "No dataset path configured")

    def _update_progress(self):
        """Update progress label - safe version."""
        try:
            if not self.products_db or "baskets" not in self.products_db:
                if hasattr(self, 'progress_label'):
                    self.progress_label.setText("No dataset loaded")
                return

            basket_key = self.current_basket.lower()

            if basket_key not in self.products_db["baskets"]:
                debug_log("PROGRESS", f"Basket '{basket_key}' not found in db")
                if hasattr(self, 'progress_label'):
                    self.progress_label.setText("Dataset unavailable")
                return

            basket_data = self.products_db["baskets"][basket_key]
            products = basket_data.get("products", {})

            total = sum(len(cat) for cat in products.values())
            captured = sum(
                1 for cat_key in products.keys()
                for product in products[cat_key]
                if f"{cat_key}_{product['name']}" in self.captured_products
            )

            if hasattr(self, 'progress_label'):
                self.progress_label.setText(f"Captured: {captured}/{total}")

        except Exception as e:
            debug_log("PROGRESS_ERROR", str(e))
            if hasattr(self, 'progress_label'):
                self.progress_label.setText("Error calculating progress")

    def _create_settings_admin_tab(self):
        """Create the Settings & Admin tab (PHASE 1 - Protected Operations)."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Dataset Management Section
        dataset_section = QGroupBox("Dataset Management")
        dataset_layout = QVBoxLayout()

        # Current path display
        self.dataset_path_label = QLabel("No dataset loaded")
        self.dataset_path_label.setWordWrap(True)
        self.dataset_path_label.setStyleSheet("color: #666; padding: 10px;")
        dataset_layout.addWidget(QLabel("Current Dataset:"))
        dataset_layout.addWidget(self.dataset_path_label)

        # Load button
        load_dataset_btn = QPushButton("Browse & Load Dataset Folder")
        load_dataset_btn.clicked.connect(self.browse_dataset)
        dataset_layout.addWidget(load_dataset_btn)

        # Reload button
        reload_dataset_btn = QPushButton("Reload Current Dataset")
        reload_dataset_btn.clicked.connect(self.reload_dataset)
        dataset_layout.addWidget(reload_dataset_btn)

        dataset_section.setLayout(dataset_layout)
        layout.addWidget(dataset_section)

        # Admin mode unlock banner
        admin_banner = QHBoxLayout()
        admin_banner.addWidget(QLabel("Admin Mode:"))
        self.admin_unlock_btn = QPushButton("🔓 UNLOCK")
        self.admin_unlock_btn.setMaximumWidth(150)
        self.admin_unlock_btn.setStyleSheet("background-color: #90EE90; color: black; padding: 8px; font-weight: bold;")
        self.admin_unlock_btn.clicked.connect(self._toggle_admin_mode)
        admin_banner.addWidget(self.admin_unlock_btn)

        self.admin_status_label = QLabel("Status: LOCKED - Click UNLOCK to access admin operations")
        self.admin_status_label.setStyleSheet("color: red; font-weight: bold;")
        admin_banner.addWidget(self.admin_status_label)
        admin_banner.addStretch()
        layout.addLayout(admin_banner)

        # Main content - split panel
        content_layout = QHBoxLayout()

        # Left: Admin menu
        menu_panel = QWidget()
        menu_layout = QVBoxLayout()
        menu_layout.addWidget(QLabel("ADMIN OPERATIONS:"))
        menu_layout.addSpacing(10)

        # Menu buttons
        self.admin_category_btn = QPushButton("📦 Baskets & Categories")
        self.admin_category_btn.setEnabled(False)
        self.admin_category_btn.clicked.connect(self._show_category_admin)
        menu_layout.addWidget(self.admin_category_btn)

        self.admin_stores_btn = QPushButton("🏪 Stores & Locations")
        self.admin_stores_btn.setEnabled(False)
        self.admin_stores_btn.clicked.connect(self._show_stores_admin)
        menu_layout.addWidget(self.admin_stores_btn)

        self.admin_data_mgmt_btn = QPushButton("🏷️ Products & Brands Management")
        self.admin_data_mgmt_btn.setEnabled(False)
        self.admin_data_mgmt_btn.clicked.connect(self._show_data_management)
        menu_layout.addWidget(self.admin_data_mgmt_btn)

        self.admin_backup_btn = QPushButton("💾 Data Backup & Recovery")
        self.admin_backup_btn.setEnabled(False)
        self.admin_backup_btn.clicked.connect(self._show_backup_admin)
        menu_layout.addWidget(self.admin_backup_btn)

        self.admin_audit_btn = QPushButton("📋 Audit Log")
        self.admin_audit_btn.setEnabled(False)
        self.admin_audit_btn.clicked.connect(self._show_audit_admin)
        menu_layout.addWidget(self.admin_audit_btn)

        self.admin_stats_btn = QPushButton("📊 Statistics")
        self.admin_stats_btn.setEnabled(False)
        self.admin_stats_btn.clicked.connect(self._show_stats_admin)
        menu_layout.addWidget(self.admin_stats_btn)

        self.admin_help_btn = QPushButton("❓ How to Use This App")
        self.admin_help_btn.clicked.connect(self._show_gui_instructions)
        menu_layout.addWidget(self.admin_help_btn)

        menu_layout.addSpacing(20)
        menu_layout.addWidget(QLabel("Recent Changes:"))

        self.admin_changelog = QTextEdit()
        self.admin_changelog.setReadOnly(True)
        self.admin_changelog.setMaximumHeight(200)
        self.admin_changelog.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd;")
        menu_layout.addWidget(self.admin_changelog)

        menu_layout.addStretch()
        menu_panel.setLayout(menu_layout)
        content_layout.addWidget(menu_panel, 0)

        # Right: Operation panel
        self.admin_operation_panel = QTextEdit()
        self.admin_operation_panel.setReadOnly(True)
        self.admin_operation_panel.setStyleSheet("background-color: white; border: 1px solid #ccc; padding: 10px;")
        self.admin_operation_panel.setText(
            "Admin Operations Interface\n"
            "====================\n\n"
            "Click UNLOCK above to enable admin mode, then select an operation from the menu.\n\n"
            "WARNING: All operations here directly modify your database.\n"
            "- Auto-backups are created before each operation\n"
            "- All changes are logged in the Audit Log\n"
            "- You can restore from backups if needed\n\n"
            "See USER_GUIDE.md for detailed instructions."
        )
        content_layout.addWidget(self.admin_operation_panel, 1)

        layout.addLayout(content_layout, 1)
        widget.setLayout(layout)
        return widget

    def _toggle_admin_mode(self):
        """Toggle admin mode lock."""
        if self.admin_mode_unlocked:
            # Lock
            self.admin_mode_unlocked = False
            self.admin_unlock_btn.setText("🔓 UNLOCK")
            self.admin_unlock_btn.setStyleSheet("background-color: #90EE90; color: black; padding: 8px; font-weight: bold;")
            self.admin_status_label.setText("Status: LOCKED - Click UNLOCK to access admin operations")
            self.admin_status_label.setStyleSheet("color: red; font-weight: bold;")

            # Disable all operation buttons
            self.admin_category_btn.setEnabled(False)
            self.admin_stores_btn.setEnabled(False)
            self.admin_data_mgmt_btn.setEnabled(False)
            self.admin_backup_btn.setEnabled(False)
            self.admin_audit_btn.setEnabled(False)
            self.admin_stats_btn.setEnabled(False)

            self.admin_operation_panel.setText("Admin Mode: LOCKED\n\nClick UNLOCK to access operations.")
        else:
            # Unlock
            self.admin_mode_unlocked = True
            self.admin_unlock_btn.setText("🔒 LOCK")
            self.admin_unlock_btn.setStyleSheet("background-color: #FF6B6B; color: white; padding: 8px; font-weight: bold;")
            self.admin_status_label.setText("Status: UNLOCKED - Admin mode active. Be careful!")
            self.admin_status_label.setStyleSheet("color: green; font-weight: bold;")

            # Enable all operation buttons
            self.admin_category_btn.setEnabled(True)
            self.admin_stores_btn.setEnabled(True)
            self.admin_data_mgmt_btn.setEnabled(True)
            self.admin_backup_btn.setEnabled(True)
            self.admin_audit_btn.setEnabled(True)
            self.admin_stats_btn.setEnabled(True)

            self._add_audit_entry("ADMIN_MODE_UNLOCKED", "Admin mode enabled")

    def _show_category_admin(self):
        """Show category administration interface."""
        self.admin_operation_panel.setText(
            "📦 BASKETS & CATEGORIES MANAGEMENT\n"
            "==================================\n\n"
            "Available operations:\n\n"
            "1. Rename Category\n"
            "   - Select category from Capture view\n"
            "   - Click 'Rename Selected' button\n"
            "   - Double-confirm the change\n"
            "   - Auto-backup created\n\n"
            "2. Delete Category\n"
            "   - Select category from Capture view\n"
            "   - Click 'Delete Selected' button\n"
            "   - Products moved to 'Other'\n"
            "   - Double-confirm required\n"
            "   - Auto-backup created\n\n"
            "3. Add New Category\n"
            "   - Click '+ New Category' in Capture view\n"
            "   - Enter category name\n"
            "   - Added to all baskets\n"
            "   - Auto-backup created\n\n"
            "Note: All critical operations are protected with double-confirmation.\n"
            "See USER_GUIDE.md for detailed instructions."
        )
        self._update_changelog()

    def _show_stores_admin(self):
        """Show store management interface."""
        self.admin_operation_panel.setText(
            "🏪 STORE & LOCATION MANAGEMENT\n"
            "================================\n\n"
            "Available operations:\n\n"
            "1. Add New Magazine (Store)\n"
            "   - Click '+ Magazine' in Capture view\n"
            "   - Enter magazine code (e.g., carrefour_es)\n"
            "   - Enter magazine name (e.g., Carrefour Spain)\n"
            "   - Duplicate check prevents conflicts\n"
            "   - Auto-backup created\n\n"
            "2. Add New Location\n"
            "   - Select magazine in Capture view\n"
            "   - Click '+ Location'\n"
            "   - Enter location name\n"
            "   - Duplicate check per magazine\n"
            "   - Auto-backup created\n\n"
            f"Current magazines: {len(self.magazines.get('magazines', {}))}\n\n"
            "Note: Store management operations are automatically backed up.\n"
            "See USER_GUIDE.md for detailed instructions."
        )
        self._update_changelog()

    def _show_data_management(self):
        """Show product and brand data management interface."""
        products_count = len(self.product_names)
        brands_count = len(self.brands_list)

        self.admin_operation_panel.setText(
            "🏷️ PRODUCTS & BRANDS MANAGEMENT\n"
            "================================\n\n"
            "Available operations:\n\n"
            "1. Manage Products\n"
            "   - View all captured product names\n"
            "   - See how many times each product was captured\n"
            "   - Rename products (updates all captures with old name)\n"
            "   - Delete products from autocomplete\n"
            "   - Reorder by frequency or alphabetically\n\n"
            "2. Manage Brands\n"
            "   - View all captured brand names\n"
            "   - See how many times each brand was captured\n"
            "   - Rename brands (updates all captures with old name)\n"
            "   - Delete brands from autocomplete\n"
            "   - Reorder by frequency or alphabetically\n\n"
            f"Current Status:\n"
            f"- Products in autocomplete: {products_count}\n"
            f"- Brands in autocomplete: {brands_count}\n"
            f"- Total captures: {len(self.metadata_list)}\n\n"
            "IMPORTANT: Renaming will retroactively update ALL captures with the old name.\n"
            "Example: Rename 'nescafe' > 'Nescafé' updates all {n} existing captures.\n\n"
            "[Click 'Open Management Dialog' below to start editing]\n"
        )

        # Replace text with a button that opens the interactive dialog
        self.admin_operation_panel.setReadOnly(False)
        self.admin_operation_panel.clear()

        # Create panel with button
        panel_widget = QWidget()
        panel_layout = QVBoxLayout()

        # Info text
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText(
            "🏷️ PRODUCTS & BRANDS MANAGEMENT\n"
            "================================\n\n"
            "Manage your product and brand autocomplete lists.\n\n"
            f"Current Status:\n"
            f"- Products: {products_count}\n"
            f"- Brands: {brands_count}\n"
            f"- Total captures: {len(self.metadata_list)}\n\n"
            "Operations:\n"
            "- Rename: Updates all existing captures with old name\n"
            "- Delete: Removes from autocomplete (doesn't affect old data)\n"
            "- Reorder: Sort by frequency or alphabetically\n\n"
            "WARNING: Rename operations are permanent and retroactive!\n"
        )
        panel_layout.addWidget(info_text)

        # Buttons
        btn_layout = QHBoxLayout()

        products_btn = QPushButton("Manage Products")
        products_btn.clicked.connect(self._open_products_dialog)
        btn_layout.addWidget(products_btn)

        brands_btn = QPushButton("Manage Brands")
        brands_btn.clicked.connect(self._open_brands_dialog)
        btn_layout.addWidget(brands_btn)

        btn_layout.addStretch()
        panel_layout.addLayout(btn_layout)

        # Replace the text edit with our widget (we need to work with the existing panel)
        # For now, just add the button info to the text
        self.admin_operation_panel.setReadOnly(True)
        self.admin_operation_panel.setText(
            "🏷️ PRODUCTS & BRANDS MANAGEMENT\n"
            "================================\n\n"
            "Manage your product and brand autocomplete lists.\n\n"
            f"Current Status:\n"
            f"- Products: {products_count}\n"
            f"- Brands: {brands_count}\n"
            f"- Total captures: {len(self.metadata_list)}\n\n"
            "Click on one of these buttons to manage:\n"
            "1. Click 'Settings & Admin' > 'Products & Brands Management'\n"
            "2. A dialog will open with full editing capabilities\n\n"
            "Operations:\n"
            "- Rename: Updates all existing captures with old name\n"
            "- Delete: Removes from autocomplete (doesn't affect old data)\n"
            "- Reorder: Sort by frequency or alphabetically\n\n"
            "WARNING: Rename operations are permanent and retroactive!\n"
            "All changes are logged in the Audit Log.\n"
        )

        # Add buttons that open dialogs
        self._update_changelog()

        # Open dialog immediately when clicked
        QTimer.singleShot(500, self._open_data_management_dialog)

    def _open_data_management_dialog(self):
        """Open interactive product/brand management dialog."""
        dialog = DataManagementDialog(self)
        dialog.exec_()

    def _open_products_dialog(self):
        """Open products management dialog."""
        dialog = ProductsBrandDialog(self, "Products", self.product_names, "product")
        dialog.exec_()

    def _open_brands_dialog(self):
        """Open brands management dialog."""
        dialog = ProductsBrandDialog(self, "Brands", self.brands_list, "brand")
        dialog.exec_()

    def _show_backup_admin(self):
        """Show backup & recovery interface."""
        backup_path = self.backup_folder
        backups = sorted(backup_path.iterdir()) if backup_path.exists() else []

        backup_info = f"💾 DATA BACKUP & RECOVERY\n" \
                     f"========================\n\n" \
                     f"Backup Status:\n" \
                     f"- Backup folder: {backup_path}\n" \
                     f"- Available backups: {len(backups)}\n" \
                     f"- Auto-backup on critical operations: YES\n\n" \
                     f"Latest Backups:\n"

        for backup in sorted(backups, reverse=True)[:5]:
            backup_info += f"  - {backup.name}\n"

        backup_info += f"\n" \
                      f"Available operations:\n\n" \
                      f"1. Manual Backup\n" \
                      f"   - Create backup now\n" \
                      f"   - Keeps last 5 manual backups\n\n" \
                      f"2. Restore from Backup\n" \
                      f"   - Select backup version\n" \
                      f"   - Requires double-confirm\n" \
                      f"   - Overwrites current data\n\n" \
                      f"3. Auto-Backup Status\n" \
                      f"   - Created before each critical operation\n" \
                      f"   - Keeps last 10 versions\n" \
                      f"   - Timestamped for easy identification\n\n" \
                      f"See USER_GUIDE.md for detailed instructions."

        self.admin_operation_panel.setText(backup_info)
        self._update_changelog()

    def _show_audit_admin(self):
        """Show audit log."""
        audit_info = "📋 AUDIT LOG\n" \
                    f"============\n\n" \
                    f"Total operations logged: {len(self.audit_log)}\n\n"

        audit_info += "Recent operations (last 20):\n" \
                     f"{'-' * 50}\n"

        for entry in self.audit_log[-20:]:
            timestamp = entry.get('timestamp', 'N/A')
            operation = entry.get('operation', 'UNKNOWN')
            details = entry.get('details', '')
            status = entry.get('status', 'unknown')

            status_emoji = "✓" if status == "success" else "✗"
            audit_info += f"{status_emoji} [{timestamp}] {operation}: {details}\n"

        audit_info += f"\n" \
                     f"All operations are logged with timestamp.\n" \
                     f"This log cannot be deleted (audit integrity).\n" \
                     f"See USER_GUIDE.md for detailed information."

        self.admin_operation_panel.setText(audit_info)
        self._update_changelog()

    def _show_stats_admin(self):
        """Show database statistics."""
        stats_info = "📊 DATABASE STATISTICS\n" \
                    f"====================\n\n"

        # Products.json stats
        if self.products_file.exists():
            size = self.products_file.stat().st_size
            baskets = self.products_db.get('baskets', {})
            categories = self.products_db.get('categories', {})

            total_products = 0
            for basket in baskets.values():
                for products_list in basket.get('products', {}).values():
                    total_products += len(products_list)

            stats_info += f"products.json:\n" \
                         f"  - File size: {size:,} bytes\n" \
                         f"  - Baskets: {len(baskets)}\n" \
                         f"  - Categories: {len(categories)}\n" \
                         f"  - Total products: {total_products}\n\n"

        # Magazines.json stats
        if self.magazines_file.exists():
            size = self.magazines_file.stat().st_size
            magazines = self.magazines.get('magazines', {})
            total_locations = sum(len(m.get('locations', [])) for m in magazines.values())

            stats_info += f"magazines.json:\n" \
                         f"  - File size: {size:,} bytes\n" \
                         f"  - Magazines (stores): {len(magazines)}\n" \
                         f"  - Total locations: {total_locations}\n\n"

        # Metadata stats
        stats_info += f"metadata.json:\n" \
                     f"  - Captured records: {len(self.metadata_list)}\n" \
                     f"  - Audit log entries: {len(self.audit_log)}\n\n" \
                     f"Backup Statistics:\n" \
                     f"  - Backups directory: {self.backup_folder}\n" \
                     f"  - Available backups: {len(list(self.backup_folder.iterdir())) if self.backup_folder.exists() else 0}\n"

        self.admin_operation_panel.setText(stats_info)
        self._update_changelog()

    def _show_gui_instructions(self):
        """Show GUI instructions and how to use the application."""
        instructions = """❓ HOW TO USE THIS APPLICATION
================================

OVERVIEW:
This is a Shrinkflation Basket Analyzer - track grocery product prices
across different stores and time periods to detect price/quantity changes.

GUI LAYOUT - 2 PANELS:

LEFT PANEL (Narrow Controls Column):
  ► Store & Location selector (with [+] buttons to add new)
  ► Week & Year selection
  ► Lock button (prevents accidental context changes)
  ► Market, Language, Unit system settings
  ► Folder selection for saved data
  ► Product entry fields:
    - Product name (auto-complete available)
    - Brand (auto-fills from database)
    - Description (optional: flavor, size, etc)
    - Quantity & Unit selector
  ► Capture button (F2) - starts screenshot tool
  ► Add to List button
  ► Image preview (shows just-captured products)

RIGHT PANEL (Categories & Products):
  ► Basket selector (Minimum/Medium/Ample)
  ► Category multi-select list (All, Beverages, Dairy, etc)
  ► Products in selected categories (with edit/remove buttons)
  ► Progress counter (Captured: X/Y)

CAPTURE WORKFLOW:

1. SELECT CONTEXT (Left panel - top):
   - Choose Store (Magazine) and Location
   - Set Week and Year for tracking period
   - Click Lock button to prevent accidental changes

2. SELECT BASKET (Right panel):
   - Minimum (15-20 items) - quick capture
   - Medium (30-40 items) - standard
   - Ample (50-70 items) - comprehensive

3. FILTER CATEGORIES (Right panel):
   - By default "All Categories" selected
   - Click category names to show only those products
   - Helps organize your capture workflow

4. ENTER PRODUCT INFO (Left panel):
   - Product name (type or select from dropdown)
   - Brand (auto-fills if in database)
   - Description (optional)
   - Quantity & Unit (e.g., 1.00 L)

5. CAPTURE SCREENSHOT:
   - Click CAPTURE (F2) button
   - Screenshot tool appears
   - Click and drag to select product/price area
   - Release to capture (auto-saved)

6. REVIEW & CONTINUE:
   - Image preview shows below Capture button
   - Progress bar shows Captured: X/Y
   - Select next product and repeat

IMPORTANT FEATURES:

📌 LOCK CONTEXT:
   - Click green "Unlock" button to toggle lock state
   - While locked, can't accidentally change Store/Location/Week
   - Critical when capturing many products in one session

📌 AUTO-COMPLETE:
   - Product names auto-complete as you type
   - Brand auto-fills from database when product selected
   - Speed up data entry significantly

📌 MARKET & LANGUAGE:
   - Market: Sets currency (FR €, EN $, ES $)
   - Language: Product name language (FR, EN, ES)
   - Unit System: SI (metric) or Imp (imperial)

📌 BACKUP & AUDIT:
   - All operations auto-backed up before changes
   - Complete audit trail in Settings & Admin
   - Can restore from backup if needed

SETTINGS & ADMIN TAB (3rd tab):

- UNLOCK button: Enables admin operations (be careful!)
- 📦 Baskets & Categories: Rename/delete categories
- 🏪 Stores & Locations: Add new stores and locations
- 💾 Data Backup & Recovery: View and restore backups
- 📋 Audit Log: View all changes made to database
- 📊 Statistics: Database size and capture counts
- ❓ How to Use This App: This help text

REVIEW GALLERY TAB (2nd tab):

- View all captured images
- Filter by Magazine, Location, Week, Product
- Edit metadata for captured images
- Export data as CSV or JSON
- Retake images if needed

KEYBOARD SHORTCUTS:

- F2: Start capture from Capture tab

TIPS FOR EFFICIENT USE:

1. Start with "Ample" basket for comprehensive data
2. Lock context at start of session to prevent mistakes
3. Use categories to group similar products
4. Capture in store order (all Beverages, then Dairy, etc)
5. Regular backups happen automatically
6. Check audit log periodically to verify changes

For more details, see USER_GUIDE.md in the application folder.
"""
        self.admin_operation_panel.setText(instructions)

    def _update_changelog(self):
        """Update changelog display with recent changes."""
        changelog = "Recent Changes:\n"
        changelog += "================\n\n"

        for entry in self.audit_log[-10:]:
            timestamp = entry.get('timestamp', 'N/A')[:16]  # YYYY-MM-DD HH:MM
            operation = entry.get('operation', 'UNKNOWN')
            details = entry.get('details', '')

            changelog += f"[{timestamp}] {operation}\n"
            if details:
                changelog += f"  {details}\n"

        self.admin_changelog.setText(changelog)

    def _create_capture_panel(self):
        """Create the capture controls panel - VERTICAL COMPACT LAYOUT (70% width)."""
        panel = QWidget()
        # Width is now controlled by layout fractions (70% left, 30% right)
        layout = QVBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(2)

        # Use QGridLayout for efficient 2-column label:value pairs
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(2)
        grid.setColumnStretch(0, 0)  # Labels: minimal
        grid.setColumnStretch(1, 1)  # Values: expand

        row = 0

        # Store + Add button
        grid.addWidget(QLabel("Store:"), row, 0)
        store_layout = QHBoxLayout()
        self.magazine_combo = QComboBox()
        self.magazine_combo.setMinimumWidth(120)
        magazines_list = [(code, mag.get("name")) for code, mag in self.magazines.get("magazines", {}).items()]
        magazines_list.sort(key=lambda x: x[1])
        for code, name in magazines_list:
            self.magazine_combo.addItem(f"{name}", code)
        self.magazine_combo.currentIndexChanged.connect(self._on_magazine_changed)
        store_layout.addWidget(self.magazine_combo, 1)
        add_magazine_btn = QPushButton("+")
        add_magazine_btn.setMaximumWidth(30)
        add_magazine_btn.clicked.connect(self._add_new_magazine)
        store_layout.addWidget(add_magazine_btn, 0)
        grid.addLayout(store_layout, row, 1)
        row += 1

        # Location + Add button
        grid.addWidget(QLabel("Location:"), row, 0)
        loc_layout = QHBoxLayout()
        self.magazine_location_combo = QComboBox()
        self.magazine_location_combo.setMinimumWidth(100)
        self._update_magazine_locations()
        self.magazine_location_combo.currentTextChanged.connect(self._on_magazine_location_changed)
        loc_layout.addWidget(self.magazine_location_combo, 1)
        add_location_btn = QPushButton("+")
        add_location_btn.setMaximumWidth(30)
        add_location_btn.clicked.connect(self._add_new_location)
        loc_layout.addWidget(add_location_btn, 0)
        grid.addLayout(loc_layout, row, 1)
        row += 1

        # Week
        grid.addWidget(QLabel("Week:"), row, 0)
        self.week_spinbox = QSpinBox()
        self.week_spinbox.setMinimum(1)
        self.week_spinbox.setMaximum(53)
        self.week_spinbox.setValue(self.selected_week)
        self.week_spinbox.setMaximumWidth(60)
        self.week_spinbox.valueChanged.connect(self._on_week_changed)
        grid.addWidget(self.week_spinbox, row, 1)
        row += 1

        # Year
        grid.addWidget(QLabel("Year:"), row, 0)
        self.year_spinbox = QSpinBox()
        self.year_spinbox.setMinimum(2020)
        self.year_spinbox.setMaximum(2050)
        self.year_spinbox.setValue(self.selected_year)
        self.year_spinbox.setMaximumWidth(80)
        self.year_spinbox.valueChanged.connect(self._on_year_changed)
        grid.addWidget(self.year_spinbox, row, 1)
        row += 1

        # Week date display (spanning both columns)
        self.week_date_label = QLabel(format_week_display(self.selected_week, self.selected_year))
        self.week_date_label.setStyleSheet("color: gray; font-size: 8px;")
        grid.addWidget(self.week_date_label, row, 0, 1, 2)
        row += 1

        # Lock button + Reset week button (spanning both columns)
        button_layout = QHBoxLayout()
        self.lock_button = QPushButton("🔓 Unlock")
        self.lock_button.setMaximumWidth(100)
        self.lock_button.setStyleSheet("background-color: #90EE90; color: black; padding: 3px; font-size: 9px;")
        self.lock_button.clicked.connect(self._toggle_context_lock)
        self.lock_button.setToolTip("Lock Magazine/Location/Week during capture")
        button_layout.addWidget(self.lock_button)

        # NEW: Reset to current week button
        self.reset_week_button = QPushButton("Reset Week")
        self.reset_week_button.setMaximumWidth(100)
        self.reset_week_button.setStyleSheet("background-color: #FFB6C1; color: black; padding: 3px; font-size: 9px;")
        self.reset_week_button.clicked.connect(self._reset_to_current_week)
        self.reset_week_button.setToolTip("Reset to current ISO week")
        button_layout.addWidget(self.reset_week_button)
        button_layout.addStretch()

        grid.addLayout(button_layout, row, 0, 1, 2)
        row += 1

        # Market
        grid.addWidget(QLabel("Market:"), row, 0)
        self.market_combo = QComboBox()
        self.market_combo.setMinimumWidth(80)
        self.market_combo.addItems(["FR €", "EN $", "ES $"])
        market_index = 0 if self.locale == "fr" else (1 if self.locale == "en" else 2)
        self.market_combo.setCurrentIndex(market_index)
        self.market_combo.currentIndexChanged.connect(self._on_market_changed)
        grid.addWidget(self.market_combo, row, 1)
        row += 1

        # Language
        grid.addWidget(QLabel("Lng:"), row, 0)
        self.language_combo = QComboBox()
        self.language_combo.setMinimumWidth(80)
        self.language_combo.addItems(["FR", "EN"])
        language_index = 0 if self.language == "fr" else 1
        self.language_combo.setCurrentIndex(language_index)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        grid.addWidget(self.language_combo, row, 1)
        row += 1

        # Unit system
        grid.addWidget(QLabel("Unit:"), row, 0)
        self.unit_system_combo = QComboBox()
        self.unit_system_combo.setMinimumWidth(80)
        self.unit_system_combo.addItems(["SI", "Imp"])
        unit_system_index = 0 if self.unit_system == "SI" else 1
        self.unit_system_combo.setCurrentIndex(unit_system_index)
        self.unit_system_combo.currentIndexChanged.connect(self._on_unit_system_changed)
        grid.addWidget(self.unit_system_combo, row, 1)
        row += 1

        # Folder (spanning both columns with button)
        grid.addWidget(QLabel("Folder:"), row, 0)
        folder_layout = QHBoxLayout()
        self.folder_path_display = QLineEdit()
        self.folder_path_display.setText(str(self.selected_folder))
        self.folder_path_display.setReadOnly(True)
        self.folder_path_display.setMaximumHeight(24)
        folder_layout.addWidget(self.folder_path_display, 1)
        browse_btn = QPushButton("...")
        browse_btn.setMaximumWidth(30)
        browse_btn.clicked.connect(self.select_folder)
        folder_layout.addWidget(browse_btn, 0)
        grid.addLayout(folder_layout, row, 1)
        row += 1

        layout.addLayout(grid)
        layout.addSpacing(3)

        # Initialize lock state
        self.context_locked = False
        self.locked_magazine = None
        self.locked_location = None
        self.locked_week = None

        # ===== Product Entry Section (compact vertical)
        layout.addWidget(QLabel("Product Entry:"))

        # Product name
        grid2 = QGridLayout()
        grid2.setContentsMargins(0, 0, 0, 0)
        grid2.setSpacing(2)
        grid2.setColumnStretch(0, 0)
        grid2.setColumnStretch(1, 1)

        grid2.addWidget(QLabel("Product:"), 0, 0)
        self.product_name_edit = QLineEdit()
        self.product_name_edit.setFocusPolicy(Qt.StrongFocus)
        self.product_completer = QCompleter(self.product_names)
        self.product_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.product_name_edit.setCompleter(self.product_completer)
        self.product_name_edit.setMaximumHeight(24)
        # Wire up previous captures display when product name changes (Phase 2)
        self.product_name_edit.textChanged.connect(self._on_product_name_changed)
        grid2.addWidget(self.product_name_edit, 0, 1)

        grid2.addWidget(QLabel("Brand:"), 1, 0)
        self.brand_edit = QLineEdit()
        self.brand_edit.setFocusPolicy(Qt.StrongFocus)
        self.brand_completer = QCompleter([])
        self.brand_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.brand_edit.setCompleter(self.brand_completer)
        self.brand_edit.setMaximumHeight(24)
        grid2.addWidget(self.brand_edit, 1, 1)

        grid2.addWidget(QLabel("Description:"), 2, 0)
        self.description_edit = QLineEdit()
        self.description_edit.setFocusPolicy(Qt.StrongFocus)
        self.description_edit.setPlaceholderText("flavor, size, etc")
        self.description_edit.setMaximumHeight(24)
        grid2.addWidget(self.description_edit, 2, 1)

        # URL field (Phase 1: Store product URL for future bot automation)
        grid2.addWidget(QLabel("URL:"), 3, 0)
        self.url_edit = QLineEdit()
        self.url_edit.setFocusPolicy(Qt.StrongFocus)
        self.url_edit.setPlaceholderText("e.g., auchan.fr/product/... or 'none'")
        self.url_edit.setText("none")  # Default to "none" for offline pricing
        self.url_edit.setMaximumHeight(24)
        grid2.addWidget(self.url_edit, 3, 1)

        # Quantity and Unit on same row
        qty_unit_layout = QHBoxLayout()
        qty_unit_layout.setSpacing(2)
        qty_unit_layout.addWidget(QLabel("Qty:"), 0)
        self.quantity_edit = QDoubleSpinBox()
        self.quantity_edit.setRange(0, 9999.99)
        self.quantity_edit.setSingleStep(1.0)
        self.quantity_edit.setDecimals(2)
        self.quantity_edit.setValue(0)
        self.quantity_edit.setLocale(QLocale.c())
        self.quantity_edit.setMaximumWidth(60)
        self.quantity_edit.setMaximumHeight(24)
        qty_unit_layout.addWidget(self.quantity_edit, 0)
        qty_unit_layout.addWidget(QLabel("Unit:"), 0)
        self.unit_combo = QComboBox()
        default_units = ["none", "g", "kg", "mL", "cl", "L", "mm", "cm", "m", "piece"] if self.unit_system == "SI" else ["none", "oz", "lb", "fl oz", "pt", "qt", "gal", "in", "ft", "piece"]
        self.unit_combo.addItems(default_units)
        self.unit_combo.setCurrentIndex(0)  # Set "none" as default
        self.unit_combo.setMaximumWidth(70)
        self.unit_combo.setMaximumHeight(24)
        qty_unit_layout.addWidget(self.unit_combo, 0)
        qty_unit_layout.addStretch()
        grid2.addLayout(qty_unit_layout, 4, 0, 1, 2)

        layout.addLayout(grid2)

        # Status info (compact)
        self.folder_preview = QLabel("Save to: (set product)")
        self.folder_preview.setStyleSheet("color: gray; font-size: 7px;")
        self.folder_preview.setWordWrap(True)
        layout.addWidget(self.folder_preview)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: blue; font-size: 8px;")
        layout.addWidget(self.status_label)

        layout.addSpacing(3)

        # Capture button (full width)
        self.capture_btn = QPushButton("CAPTURE (F2)")
        self.capture_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.capture_btn.setMinimumHeight(40)
        self.capture_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.capture_btn.clicked.connect(self.start_capture)
        layout.addWidget(self.capture_btn)

        # Add product button
        add_product_btn = QPushButton("+ Add to List")
        add_product_btn.setMaximumHeight(28)
        add_product_btn.clicked.connect(self.add_product_to_list)
        layout.addWidget(add_product_btn)

        # ===== IMAGE PREVIEW SECTION (at bottom)
        layout.addSpacing(5)
        layout.addWidget(QLabel("Capture Preview:"))

        # Image display area
        self.capture_preview = QLabel()
        self.capture_preview.setMinimumHeight(150)
        self.capture_preview.setMaximumHeight(250)
        self.capture_preview.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.capture_preview.setAlignment(Qt.AlignCenter)
        self.capture_preview.setText("No image captured yet")
        self.capture_preview.setScaledContents(False)
        layout.addWidget(self.capture_preview)

        # Capture info
        self.capture_info_label = QLabel("Ready to capture...")
        self.capture_info_label.setStyleSheet("color: #666; font-size: 8px;")
        self.capture_info_label.setWordWrap(True)
        layout.addWidget(self.capture_info_label)

        # Connect signals
        self.product_name_edit.textChanged.connect(self._sanitize_product_name)
        self.product_name_edit.textChanged.connect(self.update_folder_preview)
        self.product_name_edit.textChanged.connect(self.auto_fill_brand)
        self.brand_edit.textChanged.connect(self._sanitize_brand)
        self.quantity_edit.valueChanged.connect(self.update_folder_preview)
        self.unit_combo.currentTextChanged.connect(self.update_folder_preview)

        panel.setLayout(layout)
        return panel

    def load_basket(self, basket_name):
        """Load selected basket."""
        basket_map = {"Minimum": "minimum", "Medium": "medium", "Ample": "ample"}
        self.current_basket = basket_map.get(basket_name, "minimum")
        self._populate_categories()
        self._update_progress()

    def auto_fill_brand(self):
        """Auto-fill brand from products database when product name is selected."""
        product = self.product_name_edit.text().strip()
        if not product:
            self.brand_edit.clear()
            return

        # Look up product in database
        if self.products_db and product in self.products_db:
            product_data = self.products_db[product]
            brand = product_data.get("brand", "")
            if brand:
                self.brand_edit.setText(brand)

    def update_folder_preview(self):
        """Update the folder preview based on current inputs."""
        product = self.product_name_edit.text().strip()
        # Quantity is numeric - get value and format as string if > 0
        quantity_value = self.quantity_edit.value()
        quantity = f"{quantity_value:.2f}" if quantity_value > 0 else ""
        unit = self.unit_combo.currentText()

        if product:
            size_part = f"{quantity}{unit}" if quantity else ""
            folder_name = f"{product}_{size_part}" if size_part else product
            # Use Magazine as context for folder organization
            magazine_name = self.magazines.get("magazines", {}).get(self.selected_magazine, {}).get("name", "Store")
            folder_path = Path(self.selected_folder) / magazine_name / folder_name
            self.folder_preview.setText(f"Save to: {folder_path}")
        else:
            self.folder_preview.setText("Save to: (set product name)")

    def _validate_capture_fields(self) -> list:
        """Validate all required capture fields. Returns list of missing/invalid fields."""
        missing_fields = []

        # Check product name
        if not self.product_name_edit.text().strip():
            missing_fields.append("Product name")

        # Check brand
        if not self.brand_edit.text().strip():
            missing_fields.append("Brand")

        # Check description
        if not self.description_edit.text().strip():
            missing_fields.append("Description")

        # Check quantity (must be > 0)
        if self.quantity_edit.value() == 0.0:
            missing_fields.append("Quantity (must be > 0)")

        # Check unit (must not be "none")
        if self.unit_combo.currentText() == "none":
            missing_fields.append("Unit (must select a unit, not 'none')")

        # Check URL
        if not self.url_edit.text().strip():
            missing_fields.append("URL")

        return missing_fields

    def start_capture(self):
        """Start the snipping overlay with field validation."""
        # Validate all required fields
        missing_fields = self._validate_capture_fields()

        if missing_fields:
            # Show alert with missing fields
            missing_text = "\n".join([f"  - {field}" for field in missing_fields])
            alert = QMessageBox(self)
            alert.setWindowTitle("Missing Required Fields")
            alert.setText(f"The following fields are missing or invalid:\n\n{missing_text}\n\nDo you want to return and fill these fields, or continue anyway?")
            alert.setIcon(QMessageBox.Warning)

            # Add buttons
            go_back_btn = alert.addButton("Go Back", QMessageBox.RejectRole)
            continue_btn = alert.addButton("Continue Anyway", QMessageBox.AcceptRole)

            alert.exec_()

            # If user clicked "Go Back", return without capturing
            if alert.clickedButton() == go_back_btn:
                self.status_label.setText("Please fill all required fields before capturing.")
                self.status_label.setStyleSheet("color: orange;")
                return
            # If user clicked "Continue Anyway", proceed below

        # All fields valid (or user chose to continue anyway) - proceed to screenshot
        product = self.product_name_edit.text().strip()

        # Prevent multiple overlays from being created - clean up properly
        if self.snipping_overlay is not None:
            try:
                self.snipping_overlay.rubberBand.hide()
                self.snipping_overlay.close()
                self.snipping_overlay.deleteLater()
            except Exception as e:
                print(f"Cleanup error: {e}")
            self.snipping_overlay = None

        # Minimize GUI so user can see content behind
        debug_log("CAPTURE_START", "Minimizing GUI window")
        self.showMinimized()

        # Create overlay immediately for capture
        try:
            self.snipping_overlay = SnippingOverlay(self)
            self.snipping_overlay.capture_complete.connect(self.on_capture_complete)
            self.snipping_overlay.show_overlay()
        except Exception as e:
            print(f"Error creating overlay: {e}")
            self.status_label.setText("Error creating overlay. Please try again.")
            self.status_label.setStyleSheet("color: red;")
            # Restore window on error
            self.showNormal()

    def on_capture_complete(self, image_path):
        """Handle captured screenshot."""
        print(f"DEBUG: on_capture_complete called with: {image_path}")

        # Restore GUI window
        debug_log("CAPTURE_COMPLETE", "Restoring GUI window")
        self.showNormal()
        self.raise_()
        self.activateWindow()

        # Don't close overlay - keep it open for more captures
        # Just process the image

        # Handle capture failures
        if not image_path or not Path(image_path).exists():
            self.status_label.setText("Capture failed. Please try again.")
            self.status_label.setStyleSheet("color: red;")
            return

        # Use Magazine and selected_location (PHASE A: removed store_combo and location_combo)
        magazine_info = self.magazines.get("magazines", {}).get(self.selected_magazine, {})
        store = magazine_info.get("name", "Store")  # Get readable name from magazine
        location = self.selected_location  # Use selected_location from magazine selector

        # Sanitize text inputs: lowercase, strip spaces, limit to 22 chars
        product, _ = self._sanitize_input(self.product_name_edit.text(), 22)
        description, _ = self._sanitize_input(self.description_edit.text(), 50)  # Description: up to 50 chars
        brand, _ = self._sanitize_input(self.brand_edit.text(), 22)
        # URL: keep as-is but strip spaces (Phase 1)
        url = self.url_edit.text().strip() if self.url_edit.text().strip() else "none"
        # Quantity is numeric: get value (0-1000, with 0.5 increments)
        quantity_value = self.quantity_edit.value()
        quantity = f"{quantity_value:.2f}" if quantity_value > 0 else ""  # Empty string if 0 (optional)
        unit = self.unit_combo.currentText()

        # Move image to selected folder
        quantity_unit = f"{quantity}{unit}" if quantity else ""
        folder_name = f"{product}_{quantity_unit}" if quantity_unit else product
        save_folder = Path(self.selected_folder) / store / folder_name
        save_folder.mkdir(parents=True, exist_ok=True)

        new_image_path = save_folder / Path(image_path).name
        try:
            Path(image_path).rename(new_image_path)
            print(f"DEBUG: Image saved to: {new_image_path}")
        except Exception as e:
            print(f"ERROR: Failed to save image: {e}")
            self.status_label.setText(f"Error saving image: {e}")
            self.status_label.setStyleSheet("color: red;")
            return

        # Detect price using OCR
        detected_price = 0.0
        self.status_label.setText("Detecting price from image...")
        self.status_label.setStyleSheet("color: orange;")
        QApplication.processEvents()  # Update UI

        try:
            debug_log("OCR", f"Starting price detection with locale={self.locale}")
            # Get all detected prices with current locale
            if price_detector:
                debug_log("OCR", f"Calling detect_all_prices for: {new_image_path}")
                all_prices = price_detector.detect_all_prices(str(new_image_path), self.locale)
                debug_log("OCR", f"detect_all_prices returned: {all_prices}")
            else:
                debug_log("OCR", "price_detector is None!")
                all_prices = []

            # Show smart dialog with all options
            if all_prices:
                debug_log("DIALOG", f"Showing smart price dialog with {len(all_prices)} prices: {all_prices}")
                detected_price = self._show_smart_price_dialog(all_prices)
            else:
                # No prices detected - show manual entry dialog
                debug_log("DIALOG", "No prices detected, showing manual entry dialog")
                detected_price = self._show_smart_price_dialog([])
            debug_log("DIALOG", f"User selected price: {detected_price}")
        except Exception as e:
            print(f"DEBUG: EXCEPTION in price detection: {e}")
            import traceback
            traceback.print_exc()
            self.status_label.setText(f"OCR error: {e}. Proceed without price detection.")
            self.status_label.setStyleSheet("color: orange;")

        # Save metadata (with location, magazine, week, and canonical unit)
        # Convert unit to canonical metric format
        canonical_quantity = convert_unit(float(quantity) if quantity else 0.0, unit)
        canonical_unit = get_canonical_unit(unit)

        metadata = {
            "timestamp": datetime.now().isoformat(),
            "store": store,
            "location": location,
            "product": product,
            "description": description,
            "brand": brand,
            "quantity": quantity,
            "unit": unit,
            "canonical_quantity": canonical_quantity,
            "canonical_unit": canonical_unit,
            "price": detected_price,
            "url": url,  # Phase 1: Store product URL (default: "none")
            "notes": "",
            "image": str(new_image_path),
            # Phase 1 additions
            "magazine": self.selected_magazine,
            "magazine_location": self.selected_location,
            "week": self.selected_week,
            "year": self.selected_year,
        }

        # Handle retake: update existing entry instead of appending
        if hasattr(self, 'retake_metadata_index') and self.retake_metadata_index < len(self.metadata_list):
            # Keep original notes, timestamp, and description if retaking
            original = self.metadata_list[self.retake_metadata_index]
            metadata["notes"] = original.get("notes", "")
            metadata["description"] = original.get("description", "")
            metadata["timestamp"] = original.get("timestamp", metadata["timestamp"])
            self.metadata_list[self.retake_metadata_index] = metadata
            self.status_label.setText("Image retaken and saved!")
            del self.retake_metadata_index
        else:
            self.metadata_list.append(metadata)
            self.status_label.setText("Image captured and saved!")

        self._save_metadata_list()

        # Display captured image in preview panel
        try:
            pixmap = QPixmap(str(new_image_path))
            if not pixmap.isNull():
                # Scale to fit preview area while maintaining aspect ratio
                scaled_pixmap = pixmap.scaledToHeight(300, Qt.SmoothTransformation)
                self.capture_preview.setPixmap(scaled_pixmap)
                self.capture_info_label.setText(f"Captured: {product} | Price: {detected_price}")
        except Exception as e:
            print(f"DEBUG: Failed to display image preview: {e}")

        # Smart overlap: Mark as captured in all matching baskets
        matching_baskets = self._get_matching_baskets(product, brand, quantity, unit)
        for basket in matching_baskets:
            # Create a product key for tracking
            product_key = f"{basket}_{product}_{brand}_{quantity}{unit}" if quantity else f"{basket}_{product}_{brand}"
            if product_key not in self.captured_products:
                self.captured_products[product_key] = {
                    "timestamp": datetime.now().isoformat(),
                    "captured": True,
                    "baskets": matching_baskets
                }
        self._save_captured_products()

        # Add product name to history
        if product not in self.product_names:
            self.product_names.append(product)
            self._save_product_history()
            model = QStringListModel(self.product_names)
            self.product_completer.setModel(model)

        # Update brand autocomplete with newly captured brand
        if brand:
            self._update_brand_completer()

        # Add location to list
        if location and location not in self.locations:
            self.locations.append(location)

        # Update status
        filename = Path(new_image_path).name
        price_str = f" - €{detected_price:.2f}" if detected_price and detected_price > 0 else ""
        baskets_str = f" ({', '.join(matching_baskets)})" if matching_baskets else ""

        is_retake = hasattr(self, 'retake_metadata_index')
        if not is_retake:
            self.status_label.setText(f"Captured: {filename}{price_str}{baskets_str}")
            # Clear product fields and focus on product name for next capture
            self.product_name_edit.clear()
            self.description_edit.clear()  # Clear description too
            self.brand_edit.clear()
            self.quantity_edit.setValue(0)  # Reset to 0 (optional field)
            self.unit_combo.setCurrentIndex(0)
            self.url_edit.setText("none")  # Clear URL field and reset to default (Phase 1)

            # Set focus to product name field for next capture
            self.product_name_edit.setFocus()
            self.product_name_edit.setFocusPolicy(Qt.StrongFocus)  # Ensure strong focus policy

            # Delayed focus to ensure it takes effect after dialog closes
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, lambda: self.product_name_edit.setFocus())

            self.update_folder_preview()
        else:
            self.status_label.setText(f"Retaken: {filename}{price_str}{baskets_str}")
            # Refresh gallery to show updated image
            self.refresh_image_list()

            # NEW: Auto-display the retaken image with detected price in metadata panel
            if hasattr(self, 'retake_metadata_index') and self.retake_metadata_index < len(self.metadata_list):
                retaken_metadata = self.metadata_list[self.retake_metadata_index]
                self.display_image(retaken_metadata)
                # Mark this item as selected in the gallery list (visual feedback)
                for i in range(self.image_list.count()):
                    item = self.image_list.item(i)
                    if item.data(Qt.UserRole) == self.retake_metadata_index:
                        self.image_list.setCurrentItem(item)
                        break
                del self.retake_metadata_index

        self.status_label.setStyleSheet("color: green;")

        # Auto-refresh gallery for new captures (non-retake)
        if not is_retake:
            self.refresh_image_list()
            # Update filter dropdowns with new stores/products
            if store not in [self.filter_store.itemText(i) for i in range(self.filter_store.count())]:
                self.filter_store.addItem(store)
            if product not in [self.filter_product.itemText(i) for i in range(self.filter_product.count())]:
                self.filter_product.addItem(product)

    def _save_price(self, price: float, metadata: dict):
        """Save price to metadata and update display."""
        print(f"DEBUG: _save_price called with: {price}")
        metadata["price"] = price
        self.meta_price.setValue(price)  # QDoubleSpinBox uses setValue, not setText
        self._save_metadata_list()
        print(f"DEBUG: Price saved to metadata and file")

    def _sanitize_input(self, text: str, max_length: int = 22) -> tuple[str, bool]:
        """
        Sanitize input text: lowercase, strip spaces, limit length.
        Returns (sanitized_text, was_truncated).
        """
        sanitized = text.strip().lower()
        was_truncated = len(sanitized) > max_length
        sanitized = sanitized[:max_length]
        return sanitized, was_truncated

    def _sanitize_product_name(self):
        """Sanitize product name: lowercase, trim, limit to 22 chars."""
        current = self.product_name_edit.text()
        sanitized, was_truncated = self._sanitize_input(current, 22)
        if current != sanitized:
            # Block signals to avoid recursion
            self.product_name_edit.blockSignals(True)
            self.product_name_edit.setText(sanitized)
            self.product_name_edit.blockSignals(False)
            if was_truncated:
                self.status_label.setText("Product name truncated to 22 characters")
                self.status_label.setStyleSheet("color: orange;")

    def _sanitize_brand(self):
        """Sanitize brand: lowercase, trim, limit to 22 chars."""
        current = self.brand_edit.text()
        sanitized, was_truncated = self._sanitize_input(current, 22)
        if current != sanitized:
            self.brand_edit.blockSignals(True)
            self.brand_edit.setText(sanitized)
            self.brand_edit.blockSignals(False)
            if was_truncated:
                self.status_label.setText("Brand truncated to 22 characters")
                self.status_label.setStyleSheet("color: orange;")

    def _format_price_display(self, price: float, locale: str = "fr") -> str:
        """
        Format price for display based on locale.
        France: 3,99€ | English: $3.99 | Spanish: $3.99
        """
        if locale == "en":
            return f"${price:.2f}"
        elif locale == "es":
            return f"${price:.2f}"
        else:  # fr (default)
            return f"{price:.2f}€".replace(".", ",")

    def _show_smart_price_dialog(self, prices_list: List[float]) -> float:
        """
        Show smart price dialog with multiple detected price options.
        Shows up to 3 price options as radio buttons + manual entry.
        Returns the selected/entered price or 0.0 if skipped.
        """
        debug_log("DIALOG_OPEN", f"Opening smart price dialog with {len(prices_list)} options: {prices_list}")
        dialog = QDialog(self)
        dialog.setWindowTitle("Confirm Price - Multiple Options")
        dialog.setGeometry(400, 250, 400, 300)
        dialog.setWindowModality(Qt.ApplicationModal)  # Make dialog modal (blocks parent)
        dialog.setFocus()  # Ensure dialog has focus

        layout = QVBoxLayout()

        # Title
        layout.addWidget(QLabel("Select or enter the product price:"))

        # Price options as radio buttons
        selected_price = [None]  # Use list to allow modification in nested function
        price_group = None

        if prices_list and len(prices_list) > 0:
            layout.addWidget(QLabel("Detected prices:"))
            price_group = []

            for idx, price in enumerate(prices_list[:3]):  # Max 3 options
                price_display = self._format_price_display(price, self.locale)
                radio = QRadioButton(f"Option {idx + 1}: {price_display}")
                radio.setChecked(idx == 0)  # Default to first option
                price_group.append((radio, price))
                layout.addWidget(radio)

            layout.addSpacing(10)

        # Manual entry
        layout.addWidget(QLabel("Or enter price manually (type to replace):"))
        manual_input = QLineEdit()
        manual_input.setPlaceholderText("e.g., 1.50 or 1,50")

        # Set initial value: use detected price if available, otherwise empty
        if prices_list:
            manual_input.setText(f"{prices_list[0]:.2f}")
        else:
            manual_input.setText("")  # Empty for manual entry

        # Configure for keyboard input
        manual_input.setReadOnly(False)  # Ensure not read-only
        manual_input.setEnabled(True)    # Ensure enabled
        manual_input.setFocusPolicy(Qt.StrongFocus)  # Strong focus policy
        manual_input.setStyleSheet("QLineEdit { background-color: #FFFFCC; border: 2px solid blue; padding: 5px; }")  # Visual cue
        layout.addWidget(manual_input)
        debug_log("DIALOG_INPUT", "Manual input field ready for keyboard input (yellow highlight)")

        # Buttons
        button_layout = QHBoxLayout()

        ok_btn = QPushButton("✓ OK")
        def on_ok():
            debug_log("DIALOG_OK_CLICK", "OK button clicked")
            if price_group:
                for radio, price in price_group:
                    if radio.isChecked():
                        selected_price[0] = price
                        debug_log("DIALOG_PRICE", f"Selected radio option: {price}")
                        dialog.accept()
                        return
            # Parse manual input - accept both comma and period as decimal
            try:
                price_text = manual_input.text().strip()
                debug_log("DIALOG_MANUAL_INPUT", f"Manual input text: '{price_text}'")
                if price_text:
                    # Convert comma to period for float parsing
                    price_value = float(price_text.replace(',', '.'))
                    debug_log("DIALOG_PRICE_VALUE", f"Parsed price: {price_value}")
                    if 0 <= price_value < 10000:
                        selected_price[0] = price_value
                        debug_log("DIALOG_ACCEPT", f"Price accepted: {price_value}")
                    else:
                        debug_log("DIALOG_ERROR", f"Price out of range: {price_value}")
                        QMessageBox.warning(dialog, "Invalid Price", "Price must be between 0 and 10000")
                        return
                else:
                    selected_price[0] = 0.0
                    debug_log("DIALOG_EMPTY", "Empty price input, using 0.0")
            except ValueError as e:
                debug_log("DIALOG_PARSE_ERROR", f"Failed to parse price: {e}")
                QMessageBox.warning(dialog, "Invalid Price", "Please enter a valid number (e.g., 3.99 or 3,99)")
                return
            dialog.accept()

        ok_btn.clicked.connect(on_ok)
        button_layout.addWidget(ok_btn)

        skip_btn = QPushButton("Skip (No Price)")
        skip_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(skip_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        # Configure focus handling for maximum keyboard input reliability
        from PyQt5.QtCore import QTimer
        def set_input_focus():
            """Ensure manual input field receives focus and is ready for typing."""
            debug_log("DIALOG_FOCUS", "Setting keyboard focus to price input field")
            # Select all text so user can type to replace it
            manual_input.selectAll()
            manual_input.setFocus(Qt.ActiveWindowFocusReason)
            # Ensure the text field is active
            QApplication.processEvents()

        debug_log("DIALOG_SHOW", "About to show smart price dialog")
        # Bring window to front and ensure it's visible
        dialog.raise_()
        dialog.activateWindow()

        # Set focus after a brief delay to ensure dialog is fully rendered
        QTimer.singleShot(100, set_input_focus)

        result = dialog.exec_()
        debug_log("DIALOG_RESULT", f"Dialog returned: {result}, selected_price: {selected_price[0]}")

        if result:
            return selected_price[0] if selected_price[0] is not None else 0.0
        return 0.0

    def _show_price_dialog(self, detected_price: float) -> float:
        """
        Show dialog to confirm/edit detected price.
        Returns the confirmed price or 0.0 if cancelled.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Confirm Price")
        dialog.setGeometry(400, 300, 300, 200)

        layout = QVBoxLayout()

        # Message
        price_display = self._format_price_display(detected_price, self.locale)
        layout.addWidget(QLabel(f"Detected price: {price_display}"))
        layout.addWidget(QLabel("Edit if needed:"))

        # Price input (QLineEdit allows direct text input, not just spinner arrows)
        price_input = QLineEdit()
        price_input.setText(f"{detected_price:.2f}")
        price_input.setPlaceholderText("e.g., 3.99 or 3,99")
        price_input.setReadOnly(False)  # Ensure not read-only
        price_input.setEnabled(True)    # Ensure enabled
        price_input.setFocusPolicy(Qt.StrongFocus)  # Strong focus for keyboard input
        layout.addWidget(price_input)
        price_input.setFocus(Qt.TabFocusReason)
        price_input.selectAll()

        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")

        def on_ok_click():
            try:
                price_text = price_input.text().strip()
                if price_text:
                    price_value = float(price_text.replace(',', '.'))
                    if 0 <= price_value < 10000:
                        dialog.accept()
                    else:
                        QMessageBox.warning(dialog, "Invalid Price", "Price must be between 0 and 10000")
                else:
                    dialog.reject()
            except ValueError:
                QMessageBox.warning(dialog, "Invalid Price", "Please enter a valid number (e.g., 3.99 or 3,99)")

        ok_btn.clicked.connect(on_ok_click)
        button_layout.addWidget(ok_btn)

        skip_btn = QPushButton("Skip (No Price)")
        skip_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(skip_btn)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        if dialog.exec_():
            try:
                price_text = price_input.text().strip()
                if price_text:
                    return float(price_text.replace(',', '.'))
            except ValueError:
                pass
        return 0.0

    def setup_hotkeys(self):
        """Setup global hotkeys."""
        try:
            keyboard.add_hotkey("F2", self.start_capture)
            self.status_label.setText("Ready. Press F2 to capture or click the button.")
            self.status_label.setStyleSheet("color: blue;")
        except Exception as e:
            self.status_label.setText(f"Hotkey setup failed: {e}. Use the button instead.")
            self.status_label.setStyleSheet("color: orange;")

    # PHASE A Cleanup: Removed add_store(), _toggle_location_lock(), _on_location_changed(), add_location()
    # These functions were only called by legacy Store/Location dropdown UI elements that have been removed

    def _on_market_changed(self):
        """Handle market (currency/locale) change (PHASE B Task 3: clarified)."""
        index = self.market_combo.currentIndex()
        self.locale = ["fr", "en", "es"][index]
        self._save_config()
        debug_log("MARKET_CHANGED", f"Changed to: {self.locale} (affects currency format and OCR locale)")

    def _on_unit_system_changed(self):
        """Handle unit system change and update unit combo."""
        index = self.unit_system_combo.currentIndex()
        self.unit_system = ["SI", "Imperial"][index]
        self._save_config()

        # Update unit_combo with appropriate units
        current_unit = self.unit_combo.currentText() if self.unit_combo.count() > 0 else ""

        if self.unit_system == "SI":
            units = ["g", "kg", "mL", "cl", "L", "mm", "cm", "m", "piece"]
        else:  # Imperial
            units = ["oz", "lb", "fl oz", "pt", "qt", "gal", "in", "ft", "piece"]

        self.unit_combo.clear()
        self.unit_combo.addItems(units)
        debug_log("UNIT_SYSTEM_CHANGED", f"Changed to: {self.unit_system}, units: {units}")

    def _on_language_changed(self):
        """Handle language change and refresh product displays."""
        index = self.language_combo.currentIndex()
        self.language = ["fr", "en"][index]
        self._save_config()
        self._refresh_product_displays()
        debug_log("LANGUAGE_CHANGED", f"Changed to: {self.language}")

    def _refresh_product_displays(self):
        """Refresh all product displays with current language."""
        # Repopulate categories (which uses get_product_name internally for display)
        self._populate_categories()
        self._update_progress()

    def _update_magazine_locations(self):
        """Update location dropdown based on selected magazine."""
        self.magazine_location_combo.clear()
        magazine_code = self.magazine_combo.currentData()
        if magazine_code:
            magazine_info = self.magazines.get("magazines", {}).get(magazine_code, {})
            locations = magazine_info.get("locations", [])
            self.magazine_location_combo.addItems(locations)
            debug_log("MAGAZINE_LOCATIONS_UPDATED", f"Magazine: {magazine_code}, locations: {locations}")

    def _on_magazine_changed(self):
        """Handle magazine change and refresh baskets (Feature 3)."""
        self.selected_magazine = self.magazine_combo.currentData()
        self._update_magazine_locations()
        self._populate_categories()  # Refresh basket display
        debug_log("MAGAZINE_CHANGED", f"Changed to: {self.selected_magazine}")

    def _on_magazine_location_changed(self):
        """Handle magazine location change and refresh baskets (Feature 3)."""
        self.selected_location = self.magazine_location_combo.currentText()
        self._populate_categories()  # Refresh basket display
        debug_log("MAGAZINE_LOCATION_CHANGED", f"Changed to: {self.selected_location}")

    def _on_week_changed(self):
        """Handle week spinbox change with confirmation dialog if changing from current week."""
        new_week = self.week_spinbox.value()
        new_year = self.year_spinbox.value()
        current_year, current_week = get_iso_week()

        # Only show warning if changing to a different week than current
        if new_week != current_week or new_year != current_year:
            current_display = format_week_display(current_week, current_year)
            new_display = format_week_display(new_week, new_year)

            msg = QMessageBox(self)
            msg.setWindowTitle("Week Change Confirmation")
            msg.setText(f"Current week: {current_display}\n\n"
                       f"You selected: {new_display}\n\n"
                       f"Future captures will be logged to Week {new_week}.\n"
                       f"Are you sure?")
            msg.setIcon(QMessageBox.Warning)
            confirm_btn = msg.addButton("Confirm Change", QMessageBox.AcceptRole)
            reset_btn = msg.addButton("Reset to Current Week", QMessageBox.RejectRole)
            msg.setDefaultButton(reset_btn)

            result = msg.exec_()

            if msg.clickedButton() == reset_btn:
                # Reset spinboxes to current week
                self.week_spinbox.blockSignals(True)
                self.year_spinbox.blockSignals(True)
                self.week_spinbox.setValue(current_week)
                self.year_spinbox.setValue(current_year)
                self.week_spinbox.blockSignals(False)
                self.year_spinbox.blockSignals(False)
                new_week = current_week
                new_year = current_year

        self.selected_week = new_week
        self.selected_year = new_year
        self._update_week_date_display()
        self._update_week_spinbox_styling()
        self._populate_categories()  # Refresh basket display
        debug_log("WEEK_CHANGED", f"Changed to: Week {self.selected_week}, Year {self.selected_year}")

    def _on_year_changed(self):
        """Handle year spinbox change and update date range display (Feature 2) and baskets (Feature 3)."""
        new_year = self.year_spinbox.value()
        current_year, current_week = get_iso_week()

        # Only show warning if changing to a different year than current
        if new_year != current_year:
            msg = QMessageBox(self)
            msg.setWindowTitle("Year Change Confirmation")
            msg.setText(f"Current year: {current_year}\n\n"
                       f"You selected: {new_year}\n\n"
                       f"Future captures will be logged to Year {new_year}.\n"
                       f"Are you sure?")
            msg.setIcon(QMessageBox.Warning)
            confirm_btn = msg.addButton("Confirm Change", QMessageBox.AcceptRole)
            reset_btn = msg.addButton("Reset to Current Year", QMessageBox.RejectRole)
            msg.setDefaultButton(reset_btn)

            if msg.exec_() == QMessageBox.Rejected or msg.clickedButton() == reset_btn:
                self.year_spinbox.blockSignals(True)
                self.year_spinbox.setValue(current_year)
                self.year_spinbox.blockSignals(False)
                new_year = current_year

        self.selected_year = new_year
        self._update_week_date_display()
        self._update_week_spinbox_styling()
        self._populate_categories()  # Refresh basket display
        debug_log("YEAR_CHANGED", f"Changed to: {self.selected_year}")

    def _reset_to_current_week(self):
        """Reset week and year to current ISO week (one-click recovery)."""
        current_year, current_week = get_iso_week()
        self.week_spinbox.blockSignals(True)
        self.year_spinbox.blockSignals(True)
        self.week_spinbox.setValue(current_week)
        self.year_spinbox.setValue(current_year)
        self.week_spinbox.blockSignals(False)
        self.year_spinbox.blockSignals(False)

        self.selected_week = current_week
        self.selected_year = current_year
        self._update_week_date_display()
        self._update_week_spinbox_styling()
        self._populate_categories()

        self.status_label.setText(f"Week reset to current: {format_week_display(current_week, current_year)}")
        self.status_label.setStyleSheet("color: green;")
        debug_log("WEEK_RESET", f"Reset to current week {current_week}, {current_year}")

    def _update_week_spinbox_styling(self):
        """Highlight week/year spinbox if not on current week (visual indicator)."""
        current_year, current_week = get_iso_week()

        # Highlight spinboxes with background color if not on current week
        if self.selected_week != current_week or self.selected_year != current_year:
            # Yellow background: "you are viewing a different week"
            self.week_spinbox.setStyleSheet("background-color: #FFFF99; color: black; font-weight: bold;")
            self.year_spinbox.setStyleSheet("background-color: #FFFF99; color: black; font-weight: bold;")
            self.reset_week_button.setEnabled(True)
            self.reset_week_button.setStyleSheet("background-color: #FF6B6B; color: white; padding: 3px; font-size: 9px; font-weight: bold;")
        else:
            # Normal: on current week
            self.week_spinbox.setStyleSheet("")
            self.year_spinbox.setStyleSheet("")
            self.reset_week_button.setEnabled(False)
            self.reset_week_button.setStyleSheet("background-color: #FFB6C1; color: gray; padding: 3px; font-size: 9px;")

    def _update_week_date_display(self):
        """Update the week date range label (Feature 2)."""
        if hasattr(self, 'week_date_label'):
            date_text = format_week_display(self.selected_week, self.selected_year)
            self.week_date_label.setText(date_text)

    def _add_new_magazine(self):
        """Add a new magazine (store) to the system - WITH AUDIT LOGGING & AUTO-BACKUP."""
        text, ok = QInputDialog.getText(self, "Add Magazine", "Magazine code (e.g., auchan_fr, carrefour_fr):")
        if not ok or not text.strip():
            return

        magazine_code = text.strip().lower()
        if magazine_code in self.magazines.get("magazines", {}):
            QMessageBox.warning(self, "Duplicate", "Magazine already exists")
            return

        # Dialog for magazine details
        name, ok2 = QInputDialog.getText(self, "Add Magazine", "Magazine name (e.g., Auchan France):")
        if not ok2 or not name.strip():
            return

        # Auto-backup before adding
        backup_path = self._create_auto_backup(f"add magazine '{magazine_code}'")

        try:
            # Add to magazines data
            self.magazines["magazines"][magazine_code] = {
                "name": name.strip(),
                "country": "",
                "locations": []
            }

            # Update magazines.json
            with open(self.magazines_file, 'w', encoding='utf-8') as f:
                json.dump(self.magazines, f, ensure_ascii=False, indent=2)

            # Refresh UI
            self.magazine_combo.blockSignals(True)
            self.magazine_combo.clear()
            magazines_list = [(code, mag.get("name")) for code, mag in self.magazines.get("magazines", {}).items()]
            magazines_list.sort(key=lambda x: x[1])
            for code, mag_name in magazines_list:
                self.magazine_combo.addItem(f"{mag_name}", code)
            self.magazine_combo.blockSignals(False)

            self.status_label.setText(f"Magazine added: {name}")
            self.status_label.setStyleSheet("color: green;")
            self._add_audit_entry("MAGAZINE_ADDED", f"Code: {magazine_code}, Name: {name}")
            debug_log("MAGAZINE_ADDED", f"Code: {magazine_code}, Name: {name}")
        except Exception as e:
            self.status_label.setText(f"Add magazine failed: {e}")
            self.status_label.setStyleSheet("color: red;")
            self._add_audit_entry("MAGAZINE_ADD_FAILED", f"'{magazine_code}': {e}", "failed")

    def _add_new_location(self):
        """Add a new location to selected magazine - WITH AUDIT LOGGING & AUTO-BACKUP."""
        magazine_code = self.magazine_combo.currentData()
        if not magazine_code:
            QMessageBox.warning(self, "Error", "Please select a magazine first")
            return

        magazine_name = self.magazine_combo.currentText()
        location, ok = QInputDialog.getText(self, "Add Location", f"Location for {magazine_name} (e.g., Paris, Lyon):")
        if not ok or not location.strip():
            return

        location = location.strip()
        magazine_info = self.magazines.get("magazines", {}).get(magazine_code, {})
        if location in magazine_info.get("locations", []):
            QMessageBox.warning(self, "Duplicate", "Location already exists for this magazine")
            return

        # Auto-backup before adding
        backup_path = self._create_auto_backup(f"add location '{location}' to '{magazine_code}'")

        try:
            # Add location
            if "locations" not in magazine_info:
                magazine_info["locations"] = []
            magazine_info["locations"].append(location)

            # Save to magazines.json
            with open(self.magazines_file, 'w', encoding='utf-8') as f:
                json.dump(self.magazines, f, ensure_ascii=False, indent=2)

            # Refresh location dropdown
            self._update_magazine_locations()
            self.magazine_location_combo.setCurrentText(location)

            self.status_label.setText(f"Location added: {location} for {magazine_name}")
            self.status_label.setStyleSheet("color: green;")
            self._add_audit_entry("LOCATION_ADDED", f"Magazine: {magazine_code}, Location: {location}")
            debug_log("LOCATION_ADDED", f"Magazine: {magazine_code}, Location: {location}")
        except Exception as e:
            self.status_label.setText(f"Add location failed: {e}")
            self.status_label.setStyleSheet("color: red;")
            self._add_audit_entry("LOCATION_ADD_FAILED", f"'{location}': {e}", "failed")

    def _toggle_context_lock(self):
        """Toggle lock on Magazine/Location/Week context to prevent data entry errors (Capture View - Data Integrity)."""
        if self.context_locked:
            # Unlock context
            self.context_locked = False
            self.locked_magazine = None
            self.locked_location = None
            self.locked_week = None

            # Update UI
            self.magazine_combo.setEnabled(True)
            self.magazine_location_combo.setEnabled(True)
            self.week_spinbox.setEnabled(True)
            self.year_spinbox.setEnabled(True)

            self.lock_button.setText("🔓 Lock Context")
            self.lock_button.setStyleSheet("background-color: #90EE90; color: black; padding: 5px;")

            self.status_label.setText("Context unlocked - Ready to change Magazine/Location/Week")
            self.status_label.setStyleSheet("color: blue;")
            debug_log("CONTEXT_UNLOCKED", "Magazine/Location/Week can be changed")

        else:
            # Lock context
            self.context_locked = True
            self.locked_magazine = self.magazine_combo.currentData()
            self.locked_location = self.magazine_location_combo.currentText()
            self.locked_week = self.week_spinbox.value()

            # Update UI
            self.magazine_combo.setEnabled(False)
            self.magazine_location_combo.setEnabled(False)
            self.week_spinbox.setEnabled(False)
            self.year_spinbox.setEnabled(False)

            self.lock_button.setText("🔒 Context Locked")
            self.lock_button.setStyleSheet("background-color: #FF6B6B; color: white; padding: 5px;")

            magazine_name = self.magazine_combo.currentText()

            self.status_label.setText(f"Context locked - Cannot change Magazine/Location/Week until unlocked")
            self.status_label.setStyleSheet("color: red;")
            debug_log("CONTEXT_LOCKED", f"Locked to: {magazine_name} / {self.locked_location} / Week {self.locked_week}")

    def _on_tab_changed(self, tab_index):
        """Handle tab change event (PHASE B: auto-sync Review filters)."""
        if tab_index == 1:  # Review Gallery tab is at index 1
            self._sync_review_filters_to_capture()

    def _sync_review_filters_to_capture(self):
        """
        Auto-sync Review gallery filters to Capture context (PHASE B Task 2).
        When user switches to Review tab, set filters to match current Capture selections.
        """
        # Sync Magazine filter
        magazine_text = self.magazine_combo.currentText()
        index = self.filter_gallery_magazine.findText(magazine_text)
        if index >= 0:
            self.filter_gallery_magazine.blockSignals(True)
            self.filter_gallery_magazine.setCurrentIndex(index)
            self.filter_gallery_magazine.blockSignals(False)
            debug_log("SYNC_FILTERS", f"Magazine synced to: {magazine_text}")

        # Sync Location filter
        location_text = self.magazine_location_combo.currentText()
        index = self.filter_gallery_location.findText(location_text)
        if index >= 0:
            self.filter_gallery_location.blockSignals(True)
            self.filter_gallery_location.setCurrentIndex(index)
            self.filter_gallery_location.blockSignals(False)
            debug_log("SYNC_FILTERS", f"Location synced to: {location_text}")

        # Sync Week filter
        week_text = str(self.week_spinbox.value())
        index = self.filter_gallery_week.findText(week_text)
        if index >= 0:
            self.filter_gallery_week.blockSignals(True)
            self.filter_gallery_week.setCurrentIndex(index)
            self.filter_gallery_week.blockSignals(False)
            debug_log("SYNC_FILTERS", f"Week synced to: {week_text}")

        # Update context indicator (PHASE C Task 2)
        self._update_context_indicator()

        # Refresh the gallery with synced filters
        self.refresh_image_list()

    def _update_context_indicator(self):
        """
        Update the context indicator showing current review scope (PHASE C Task 2).
        Display: "Viewing: [Magazine] [Location] Week [Week] (Year)"
        """
        if not hasattr(self, 'context_indicator'):
            return

        magazine = self.filter_gallery_magazine.currentText()
        location = self.filter_gallery_location.currentText()
        week = self.filter_gallery_week.currentText()
        year = self.selected_year

        # Build context string
        if magazine == "All" and location == "All" and week == "All":
            context_text = "Viewing: All captures"
        else:
            parts = []
            if magazine != "All":
                parts.append(magazine)
            if location != "All":
                parts.append(location)
            if week != "All":
                parts.append(f"Week {week}")
            context_text = f"Viewing: {' | '.join(parts)} ({year})"

        self.context_indicator.setText(context_text)
        debug_log("CONTEXT", f"Updated: {context_text}")

    def add_product_to_list(self):
        """Add current product to quick list."""
        product = self.product_name_edit.text().strip()
        if not product:
            self.status_label.setText("Enter a product name first!")
            self.status_label.setStyleSheet("color: red;")
            return

        if product not in self.product_names:
            self.product_names.append(product)
            self._save_product_history()
            model = QStringListModel(self.product_names)
            self.product_completer.setModel(model)

        self.status_label.setText(f"Added to quick list: {product}")
        self.status_label.setStyleSheet("color: blue;")

    def select_folder(self):
        """Open folder browser to select save location."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Save Folder", str(self.selected_folder)
        )
        if folder:
            self.selected_folder = folder
            self.folder_path_display.setText(folder)
            self._save_selected_folder()
            self.update_folder_preview()

    # Data persistence methods
    def _load_product_history(self) -> List[str]:
        """Load previously entered product names."""
        if self.product_history_file.exists():
            with open(self.product_history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_product_history(self):
        """Save product history to file."""
        with open(self.product_history_file, 'w', encoding='utf-8') as f:
            json.dump(self.product_names, f, ensure_ascii=False, indent=2)

    def _update_brand_completer(self):
        """Extract unique brands from metadata and populate brand autocomplete."""
        # Get all unique brands from existing captures
        unique_brands = set()
        for meta in self.metadata_list:
            brand = meta.get("brand", "").strip()
            if brand:
                unique_brands.add(brand)

        # Sort and update brands list
        self.brands_list = sorted(list(unique_brands))

        # Update the brand completer if it exists
        if hasattr(self, 'brand_completer'):
            model = QStringListModel(self.brands_list)
            self.brand_completer.setModel(model)

    def _load_stores(self) -> List[str]:
        """Load store list from file or return defaults."""
        if self.stores_file.exists():
            with open(self.stores_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return ["Auchan", "Franprix", "Monoprix", "Carrefour"]

    def _save_stores(self):
        """Save store list to file."""
        with open(self.stores_file, 'w', encoding='utf-8') as f:
            json.dump(self.stores, f, ensure_ascii=False, indent=2)

    def _load_selected_folder(self) -> str:
        """Load last selected folder from config."""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("selected_folder", str(self.base_folder))
        return str(self.base_folder)

    def _load_config(self):
        """Load all config settings (folder, locale, unit_system, language)."""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.locale = config.get("locale", "fr")
                self.unit_system = config.get("unit_system", "SI")
                self.language = config.get("language", "fr")
        else:
            self.locale = "fr"
            self.unit_system = "SI"
            self.language = "fr"

    def _save_config(self):
        """Save all config settings to file."""
        config = {
            "selected_folder": self.selected_folder,
            "locale": self.locale,
            "unit_system": self.unit_system,
            "language": self.language
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def _save_selected_folder(self):
        """Save selected folder to config (also saves locale and unit_system)."""
        self._save_config()

    def _load_metadata(self) -> List[Dict]:
        """Load metadata list."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_metadata_list(self):
        """Save metadata list."""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata_list, f, ensure_ascii=False, indent=2)

    def _rename_product(self, old_name: str, new_name: str) -> int:
        """Rename product in metadata retroactively. Returns count of updated items."""
        count = 0
        for meta in self.metadata_list:
            if meta.get("product") == old_name:
                meta["product"] = new_name
                count += 1

        if count > 0:
            self._save_metadata_list()
            # Update product list
            if old_name in self.product_names:
                idx = self.product_names.index(old_name)
                self.product_names[idx] = new_name
                self._save_product_history()
                model = QStringListModel(self.product_names)
                self.product_completer.setModel(model)
            self._add_audit_entry("PRODUCT_RENAMED", f"'{old_name}' -> '{new_name}' ({count} items)")
        return count

    def _rename_brand(self, old_name: str, new_name: str) -> int:
        """Rename brand in metadata retroactively. Returns count of updated items."""
        count = 0
        for meta in self.metadata_list:
            if meta.get("brand") == old_name:
                meta["brand"] = new_name
                count += 1

        if count > 0:
            self._save_metadata_list()
            # Update brands list
            self._update_brand_completer()
            self._add_audit_entry("BRAND_RENAMED", f"'{old_name}' -> '{new_name}' ({count} items)")
        return count

    def _delete_product(self, product_name: str) -> int:
        """Delete product from autocomplete. Returns count of captures still using it."""
        count = 0
        for meta in self.metadata_list:
            if meta.get("product") == product_name:
                count += 1

        if product_name in self.product_names:
            self.product_names.remove(product_name)
            self._save_product_history()
            model = QStringListModel(self.product_names)
            self.product_completer.setModel(model)
            self._add_audit_entry("PRODUCT_DELETED", f"'{product_name}' removed from autocomplete ({count} existing items)")

        return count

    def _delete_brand(self, brand_name: str) -> int:
        """Delete brand from autocomplete. Returns count of captures still using it."""
        count = 0
        for meta in self.metadata_list:
            if meta.get("brand") == brand_name:
                count += 1

        self._update_brand_completer()
        self._add_audit_entry("BRAND_DELETED", f"'{brand_name}' removed from autocomplete ({count} existing items)")

        return count

    def _get_product_counts(self) -> Dict[str, int]:
        """Get usage count for each product."""
        counts = {}
        for meta in self.metadata_list:
            product = meta.get("product", "").strip()
            if product:
                counts[product] = counts.get(product, 0) + 1
        return counts

    def _get_brand_counts(self) -> Dict[str, int]:
        """Get usage count for each brand."""
        counts = {}
        for meta in self.metadata_list:
            brand = meta.get("brand", "").strip()
            if brand:
                counts[brand] = counts.get(brand, 0) + 1
        return counts

    def _load_products_db(self) -> Dict:
        """Load products database with graceful fallback."""
        try:
            if not self.products_file.exists():
                debug_log("PRODUCTS_DB", "products.json not found - starting with empty db")
                return self._empty_products_db()

            with open(self.products_file, 'r', encoding='utf-8') as f:
                db = json.load(f)
                debug_log("PRODUCTS_DB", "Products database loaded successfully")
                return db

        except Exception as e:
            debug_log("PRODUCTS_DB_ERROR", f"Failed to load products.json: {e}")
            return self._empty_products_db()

    def _empty_products_db(self) -> Dict:
        """Return empty product database structure."""
        return {
            "baskets": {
                "minimum": {"products": {}},
                "medium": {"products": {}},
                "ample": {"products": {}}
            },
            "categories": {
                "beverages": "Beverages",
                "bread_pasta": "Bread & Pasta",
                "dairy": "Dairy",
                "household": "Household",
                "meat_protein": "Meat & Protein",
                "other": "Other",
                "pantry": "Pantry",
                "personal_baby": "Personal & Baby",
                "snacks": "Snacks",
                "spices_seasonings": "Spices & Seasonings",
                "vegetables": "Vegetables"
            }
        }

    def _load_captured_products(self) -> Dict:
        """Load captured products."""
        if self.captured_products_file.exists():
            with open(self.captured_products_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_magazines(self) -> Dict:
        """Load magazine (store) definitions."""
        if self.magazines_file.exists():
            with open(self.magazines_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                debug_log("MAGAZINES_LOADED", f"{len(data.get('magazines', {}))} magazines loaded")
                return data
        debug_log("MAGAZINES_WARNING", "magazines.json not found, using empty dict")
        return {"magazines": {}, "countries": {}}

    def _load_product_registry(self) -> Dict:
        """Load product registry (auto-generated from datasets)."""
        if self.product_registry_file.exists():
            with open(self.product_registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                debug_log("PRODUCT_REGISTRY_LOADED", f"{len(data.get('products', {}))} products loaded")
                return data
        debug_log("PRODUCT_REGISTRY_WARNING", "product_registry.json not found, using empty dict")
        return {"products": {}, "categories": {}, "french_to_english": {}}

    def _save_captured_products(self):
        """Save captured products."""
        with open(self.captured_products_file, 'w', encoding='utf-8') as f:
            json.dump(self.captured_products, f, ensure_ascii=False, indent=2)

    def _load_locations(self) -> List[str]:
        """Load locations - default French cities plus any from metadata."""
        # Default French locations
        default_locations = [
            "Paris",      # by far the largest
            "Lyon",
            "Marseille",
            "Lille",
            "Toulouse",
            "Bordeaux",
            "Nantes",
            "Strasbourg",
            "Montpellier",
            "Rennes"
        ]

        # Add any from metadata that aren't already in defaults
        locations = set(default_locations)
        for meta in self.metadata_list:
            if "location" in meta and meta["location"]:
                locations.add(meta["location"])

        return sorted(list(locations))

    # ============================================================
    # PRODUCT HISTORY QUERY METHODS (Phase 1 - Backend)
    # ============================================================

    def _query_previous_captures(self, product_name: str, magazine_code: str) -> List[Dict]:
        """
        Query metadata for all previous captures of a product in a magazine.

        Args:
            product_name: Product name (string, e.g., "Coffee")
            magazine_code: Magazine code (string, e.g., "auchan_fr")

        Returns:
            List of dicts with {product, brand, description, price, timestamp, week, year}
            Sorted by timestamp (newest first)
            Returns empty list if no matches found (graceful "none-yet" handling)
        """
        try:
            # Reload metadata to ensure we have latest data
            self.metadata_list = self._load_metadata()

            # Filter: product name + magazine code match (case-insensitive)
            matches = [
                m for m in self.metadata_list
                if m.get("product", "").lower() == product_name.lower()
                and m.get("magazine", "") == magazine_code
            ]

            # Sort by timestamp (newest first)
            matches.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            debug_log("QUERY_PREVIOUS_CAPTURES",
                      f"Found {len(matches)} captures for '{product_name}' in '{magazine_code}'")

            return matches

        except Exception as e:
            debug_log("QUERY_ERROR", f"Failed to query previous captures: {str(e)}")
            return []

    def _get_last_capture_for_product(self, product_name: str, magazine_code: str) -> Optional[Dict]:
        """
        Get the most recent capture of a product in a magazine.

        Args:
            product_name: Product name
            magazine_code: Magazine code

        Returns:
            Dict with most recent capture, or None if not found
        """
        try:
            captures = self._query_previous_captures(product_name, magazine_code)

            if captures:
                return captures[0]  # First item is newest (sorted reverse)

            return None

        except Exception as e:
            debug_log("QUERY_ERROR", f"Failed to get last capture: {str(e)}")
            return None

    def _get_default_reference_products(self) -> List[Dict]:
        """
        Get all unique products captured in Auchan (for first-time setup reference).

        Used when a store is being set up for the first time - shows Auchan as a reference
        guide of what products to track.

        Returns:
            List of dicts with {product, brand, description, price}
            Unique products from Auchan only
            Sorted by product name
        """
        try:
            self.metadata_list = self._load_metadata()

            # Get Auchan captures only
            auchan_captures = [
                m for m in self.metadata_list
                if m.get("magazine", "").startswith("auchan")  # auchan_fr, auchan_de, etc.
            ]

            # Get unique products (newest capture for each product)
            unique_products = {}
            for capture in auchan_captures:
                product_name = capture.get("product", "").lower()
                if product_name:
                    # Keep the newest capture for each product
                    if product_name not in unique_products:
                        unique_products[product_name] = capture
                    else:
                        # Compare timestamps and keep newest
                        existing_ts = unique_products[product_name].get("timestamp", "")
                        new_ts = capture.get("timestamp", "")
                        if new_ts > existing_ts:
                            unique_products[product_name] = capture

            # Convert to list and sort by product name
            result = list(unique_products.values())
            result.sort(key=lambda x: x.get("product", "").lower())

            debug_log("DEFAULT_REFERENCE", f"Found {len(result)} unique Auchan products for reference")

            return result

        except Exception as e:
            debug_log("QUERY_ERROR", f"Failed to get default reference products: {str(e)}")
            return []

    def _refresh_previous_captures_display(self, product_name: str) -> None:
        """
        Refresh the previous captures display in the right panel.

        Called when a product is selected. Queries previous captures for the selected
        product in the current magazine and displays them in the right panel.

        Args:
            product_name: Name of selected product
        """
        try:
            # Clear existing previous captures display
            while self.previous_captures_layout.count():
                child = self.previous_captures_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            self.previous_captures_checkboxes = {}

            # Query previous captures for current magazine
            previous_captures = self._query_previous_captures(product_name, self.selected_magazine)

            if not previous_captures:
                # "None-yet" message for products with no history
                none_yet_label = QLabel(
                    f"No previous captures yet for '{product_name}'\n\n"
                    f"You're the first to track this product! "
                    f"Enter brand and description below.\n\n"
                    f"After this capture, future prices will have reference data."
                )
                none_yet_label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
                none_yet_label.setWordWrap(True)
                self.previous_captures_layout.addWidget(none_yet_label)
                debug_log("PREVIOUS_CAPTURES", f"No previous captures for '{product_name}' in '{self.selected_magazine}'")
                return

            # Display previous captures (newest first)
            for capture in previous_captures:
                # Create container for this capture
                capture_frame = QWidget()
                capture_layout = QHBoxLayout(capture_frame)
                capture_layout.setContentsMargins(5, 5, 5, 5)
                capture_layout.setSpacing(10)

                # Checkbox (Phase 3: Wire up auto-fill signals)
                checkbox = QCheckBox()
                checkbox.setMaximumWidth(30)
                capture_layout.addWidget(checkbox)

                # Capture info: Brand | Description | Qty+Unit | Price | URL (Phase 1)
                brand = capture.get("brand", "").strip()
                description = capture.get("description", "").strip()
                quantity = capture.get("quantity", "")
                unit = capture.get("unit", "").strip()
                price = capture.get("price", 0)
                url = capture.get("url", "none").strip()

                # Format: Brand | Description | Qty Unit | Prev: €X.XX | URL
                qty_unit_str = ""
                if quantity:
                    qty_unit_str = f" {quantity}{unit}" if unit else f" {quantity}"

                # Build info text
                info_text = f"{brand} | {description}{qty_unit_str}"
                if price and price > 0:
                    info_text += f" | €{price:.2f}"
                if url and url != "none":
                    # Truncate URL for display (show first 30 chars)
                    display_url = url if len(url) <= 30 else url[:27] + "..."
                    info_text += f" | {display_url}"

                info_label = QLabel(info_text)
                info_label.setWordWrap(False)
                capture_layout.addWidget(info_label, 1)

                # Style the frame
                capture_frame.setStyleSheet(
                    "border: 1px solid #ddd; border-radius: 4px; background-color: #f9f9f9;"
                )
                self.previous_captures_layout.addWidget(capture_frame)

                # Store checkbox -> capture mapping for Phase 3
                self.previous_captures_checkboxes[checkbox] = capture

                # Wire up checkbox signals for auto-fill (Phase 3)
                checkbox.stateChanged.connect(
                    lambda state, cb=checkbox, data=capture:
                    self._on_previous_capture_checked(cb, data) if state == Qt.Checked
                    else self._on_previous_capture_unchecked()
                )

            # Add spacer to push captures to top
            self.previous_captures_layout.addStretch()

            debug_log("PREVIOUS_CAPTURES", f"Displayed {len(previous_captures)} captures for '{product_name}'")

        except Exception as e:
            debug_log("DISPLAY_ERROR", f"Failed to refresh previous captures: {str(e)}")
            error_label = QLabel(f"Error loading previous captures: {str(e)}")
            error_label.setStyleSheet("color: #ff0000;")
            self.previous_captures_layout.addWidget(error_label)

    def _get_matching_baskets(self, product: str, brand: str, quantity: str, unit: str) -> List[str]:
        """Find which baskets this product matches (smart overlap)."""
        matching_baskets = []

        product_key = f"{product}_{quantity}{unit}" if quantity else product

        for basket_key in ["minimum", "medium", "ample"]:
            if basket_key not in self.products_db["baskets"]:
                continue

            basket_data = self.products_db["baskets"][basket_key]
            products = basket_data["products"]

            # Check all categories for matching product
            for category_products in products.values():
                for prod in category_products:
                    prod_name = prod["name"]
                    # Check if product name matches (flexible matching)
                    if product.lower() in prod_name.lower() or prod_name.lower() in product.lower():
                        # Check size if provided
                        if quantity:
                            if f"{quantity}{unit}" in prod_name or prod_name.split("(")[-1].strip(")") == f"{quantity}{unit}":
                                matching_baskets.append(basket_key)
                                break
                        else:
                            # No quantity specified, match by product name alone
                            if "Store Brand" in prod_name or "Generic" in prod_name:
                                matching_baskets.append(basket_key)
                                break

        return list(set(matching_baskets))  # Remove duplicates

    def export_unified_csv(self):
        """Export unified dataset as CSV."""
        export_path = QFileDialog.getSaveFileName(
            self, "Export Data (CSV)", str(self.base_folder / "shrinkflation_data.csv"), "CSV Files (*.csv)"
        )

        if not export_path[0]:
            return

        try:
            with open(export_path[0], 'w', encoding='utf-8', newline='') as f:
                # Write header
                header = "Date,Time,Store,Location,Product,Brand,Quantity,Unit,Price,Baskets_Fulfilled,Image_Path,Notes\n"
                f.write(header)

                # Write data
                for meta in self.metadata_list:
                    timestamp = meta.get("timestamp", "")
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        date_str = dt.strftime("%Y-%m-%d")
                        time_str = dt.strftime("%H:%M:%S")
                    except:
                        date_str = ""
                        time_str = ""

                    store = meta.get("store", "").replace(",", ";")
                    location = meta.get("location", "").replace(",", ";")
                    product = meta.get("product", "").replace(",", ";")
                    brand = meta.get("brand", "").replace(",", ";")
                    quantity = meta.get("quantity", "")
                    unit = meta.get("unit", "")
                    price = meta.get("price", 0.0)
                    image = meta.get("image", "")
                    notes = meta.get("notes", "").replace(",", ";").replace("\n", " ")

                    # Get baskets this product fulfills
                    baskets = self._get_matching_baskets(product, brand, quantity, unit)
                    baskets_str = ";".join(baskets) if baskets else ""

                    row = f'{date_str},{time_str},{store},{location},{product},{brand},{quantity},{unit},{price:.2f},{baskets_str},"{image}",{notes}\n'
                    f.write(row)

            self.status_label.setText(f"Exported to {Path(export_path[0]).name}")
            self.status_label.setStyleSheet("color: green;")
        except Exception as e:
            self.status_label.setText(f"Export failed: {e}")
            self.status_label.setStyleSheet("color: red;")

    def export_unified_json(self):
        """Export unified dataset as JSON."""
        export_path = QFileDialog.getSaveFileName(
            self, "Export Data (JSON)", str(self.base_folder / "shrinkflation_data.json"), "JSON Files (*.json)"
        )

        if not export_path[0]:
            return

        try:
            export_data = []
            for meta in self.metadata_list:
                baskets = self._get_matching_baskets(
                    meta.get("product", ""),
                    meta.get("brand", ""),
                    meta.get("quantity", ""),
                    meta.get("unit", "")
                )
                meta["baskets_fulfilled"] = baskets
                export_data.append(meta)

            with open(export_path[0], 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            self.status_label.setText(f"Exported to {Path(export_path[0]).name}")
            self.status_label.setStyleSheet("color: green;")
        except Exception as e:
            self.status_label.setText(f"Export failed: {e}")
            self.status_label.setStyleSheet("color: red;")

    def export_granular_data(self):
        """Export filtered gallery data (Feature 5: Granular Data Export)."""
        # Get filters from gallery tab (with safe defaults)
        magazine_filter = self.filter_gallery_magazine.currentText() if hasattr(self, 'filter_gallery_magazine') else "All"
        location_filter = self.filter_gallery_location.currentText() if hasattr(self, 'filter_gallery_location') else "All"
        week_filter = self.filter_gallery_week.currentText() if hasattr(self, 'filter_gallery_week') else "All"
        product_filter = self.filter_product.currentText() if hasattr(self, 'filter_product') else "All"

        # Filter metadata based on gallery filters
        filtered_data = []

        for meta in self.metadata_list:
            # Apply all filters
            if magazine_filter != "All" and meta.get("magazine") != magazine_filter:
                continue
            if location_filter != "All" and meta.get("magazine_location") != location_filter:
                continue
            if week_filter != "All" and str(meta.get("week", "")) != week_filter:
                continue
            if product_filter != "All" and meta.get("product") != product_filter:
                continue

            filtered_data.append(meta)

        if not filtered_data:
            self.status_label.setText("No data matching filters to export")
            self.status_label.setStyleSheet("color: orange;")
            return

        # Create filter description for filename
        filter_parts = []
        if magazine_filter != "All":
            filter_parts.append(magazine_filter)
        if location_filter != "All":
            filter_parts.append(location_filter)
        if week_filter != "All":
            filter_parts.append(f"week{week_filter}")
        if product_filter != "All":
            filter_parts.append(product_filter)

        filter_desc = "_".join(filter_parts) if filter_parts else "all"
        default_filename = f"shrinkflation_export_{filter_desc}.csv"

        # Ask user for file format and location
        export_path = QFileDialog.getSaveFileName(
            self, "Export Filtered Data", str(self.base_folder / default_filename),
            "CSV Files (*.csv);;JSON Files (*.json)"
        )

        if not export_path[0]:
            return

        try:
            file_ext = Path(export_path[0]).suffix.lower()

            if file_ext == ".csv":
                self._export_filtered_csv(filtered_data, export_path[0])
            else:  # JSON
                self._export_filtered_json(filtered_data, export_path[0])

            self.status_label.setText(
                f"Exported {len(filtered_data)} records to {Path(export_path[0]).name}"
            )
            self.status_label.setStyleSheet("color: green;")
        except Exception as e:
            self.status_label.setText(f"Export failed: {e}")
            self.status_label.setStyleSheet("color: red;")

    def _export_filtered_csv(self, filtered_data: List[Dict], filepath: str):
        """Export filtered data as CSV (Feature 5 helper)."""
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            # Enhanced header with all fields including description, url, ocr_confidence, currency
            header = "Date,Time,Store,Location,Magazine,Magazine_Location,Week,Year,Product," \
                     "Brand,Description,Quantity,Unit,Price,Currency,URL,OCR_Confidence,Language,Notes,Image_Path\n"
            f.write(header)

            for meta in filtered_data:
                timestamp = meta.get("timestamp", "")
                try:
                    dt = datetime.fromisoformat(timestamp)
                    date_str = dt.strftime("%Y-%m-%d")
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    date_str = ""
                    time_str = ""

                # Safe CSV escaping (replace commas with semicolons)
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

                # Phase 1 fields
                magazine = meta.get("magazine", "")
                magazine_location = meta.get("magazine_location", "")
                week = meta.get("week", "")
                year = meta.get("year", "")

                row = f"{date_str},{time_str},{store},{location},{magazine},{magazine_location}," \
                      f"{week},{year},{product},{brand},\"{description}\",{quantity},{unit},{price:.2f}," \
                      f"{currency},{url},{ocr_confidence},{self.language},\"{notes}\",\"{image}\"\n"
                f.write(row)

    def _export_filtered_json(self, filtered_data: List[Dict], filepath: str):
        """Export filtered data as JSON (Feature 5 helper)."""
        export_data = []

        for meta in filtered_data:
            record = meta.copy()
            # Add language field
            record["export_language"] = self.language
            export_data.append(record)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

    # ==================== BACKUP & AUDIT SYSTEM (PHASE 1) ====================

    def _load_audit_log(self) -> List[Dict]:
        """Load audit log from file."""
        if self.audit_log_file.exists():
            try:
                with open(self.audit_log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_audit_log(self):
        """Save audit log to file."""
        try:
            with open(self.audit_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.audit_log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            debug_log("AUDIT_LOG_ERROR", f"Failed to save audit log: {e}")

    def _add_audit_entry(self, operation: str, details: str, status: str = "success"):
        """Add entry to audit log."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details,
            "status": status
        }
        self.audit_log.append(entry)
        self._save_audit_log()
        debug_log("AUDIT_ENTRY", f"{operation}: {details}")

    def _create_auto_backup(self, reason: str) -> str:
        """Create automatic backup before critical operation."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_folder / f"auto_{timestamp}"
            backup_path.mkdir(exist_ok=True)

            # Backup critical files
            import shutil
            shutil.copy(self.products_file, backup_path / "products.json")
            shutil.copy(self.magazines_file, backup_path / "magazines.json")
            if self.metadata_file.exists():
                shutil.copy(self.metadata_file, backup_path / "metadata.json")

            self._add_audit_entry("AUTO_BACKUP", f"Created before {reason}")
            debug_log("AUTO_BACKUP_CREATED", f"Backup: {backup_path}")
            return str(backup_path)
        except Exception as e:
            debug_log("AUTO_BACKUP_ERROR", f"Failed: {e}")
            return None

    def _restore_from_backup(self, backup_path: str) -> bool:
        """Restore data from backup."""
        try:
            backup_path = Path(backup_path)
            import shutil

            # Restore critical files
            if (backup_path / "products.json").exists():
                shutil.copy(backup_path / "products.json", self.products_file)
            if (backup_path / "magazines.json").exists():
                shutil.copy(backup_path / "magazines.json", self.magazines_file)
            if (backup_path / "metadata.json").exists():
                shutil.copy(backup_path / "metadata.json", self.metadata_file)

            # Reload data
            self.products_db = self._load_products_db()
            self.magazines = self._load_magazines()
            self.metadata_list = self._load_metadata()

            self._add_audit_entry("RESTORE", f"Restored from {backup_path.name}")
            debug_log("BACKUP_RESTORED", f"From: {backup_path}")
            return True
        except Exception as e:
            debug_log("RESTORE_ERROR", f"Failed: {e}")
            return False

    def _double_confirm_dialog(self, title: str, message: str, action_verb: str = "CONFIRM") -> bool:
        """Show double-confirmation dialog for critical operations."""
        # First dialog
        reply = QMessageBox.warning(
            self, title, message,
            QMessageBox.Yes | QMessageBox.Cancel
        )

        if reply != QMessageBox.Yes:
            return False

        # Second dialog - require typing action verb
        confirm_text, ok = QInputDialog.getText(
            self, f"{title} - Confirm",
            f"This cannot be undone. Type '{action_verb}' to confirm:"
        )

        if ok and confirm_text.strip().upper() == action_verb:
            return True
        return False

    # ==================== PHASE 2: Delete Magazine & Location & Enhanced Recovery ====================

    def _delete_magazine(self, magazine_code: str):
        """Delete magazine with triple-confirm (PHASE 2)."""
        magazine_info = self.magazines.get("magazines", {}).get(magazine_code, {})
        magazine_name = magazine_info.get("name", magazine_code)
        location_count = len(magazine_info.get("locations", []))

        # Count affected captures
        affected_captures = sum(1 for meta in self.metadata_list if meta.get("magazine") == magazine_code)

        # Triple-confirm dialog
        if not self._double_confirm_dialog(
            "Delete Magazine",
            f"Delete magazine '{magazine_name}'?\n\nThis will affect:\n"
            f"  - {location_count} locations\n"
            f"  - {affected_captures} captured records\n\n"
            f"This cannot be undone.",
            "DELETE"
        ):
            return

        # Auto-backup before deletion
        backup_path = self._create_auto_backup(f"delete magazine '{magazine_name}'")

        try:
            # Delete magazine
            del self.magazines["magazines"][magazine_code]

            # Save to magazines.json
            with open(self.magazines_file, 'w', encoding='utf-8') as f:
                json.dump(self.magazines, f, ensure_ascii=False, indent=2)

            # Refresh UI
            self.magazine_combo.blockSignals(True)
            self.magazine_combo.clear()
            magazines_list = [(code, mag.get("name")) for code, mag in self.magazines.get("magazines", {}).items()]
            magazines_list.sort(key=lambda x: x[1])
            for code, mag_name in magazines_list:
                self.magazine_combo.addItem(f"{mag_name}", code)
            self.magazine_combo.blockSignals(False)

            self.status_label.setText(f"Magazine deleted: {magazine_name} (backup available)")
            self.status_label.setStyleSheet("color: green;")
            self._add_audit_entry("MAGAZINE_DELETED", f"'{magazine_name}' ({location_count} locations, {affected_captures} captures)")
        except Exception as e:
            self.status_label.setText(f"Delete magazine failed: {e}")
            self.status_label.setStyleSheet("color: red;")
            self._add_audit_entry("MAGAZINE_DELETE_FAILED", f"'{magazine_name}': {e}", "failed")

    def _delete_location(self, magazine_code: str, location_name: str):
        """Delete location with double-confirm (PHASE 2)."""
        magazine_info = self.magazines.get("magazines", {}).get(magazine_code, {})
        magazine_name = magazine_info.get("name", magazine_code)

        # Count affected captures
        affected_captures = sum(1 for meta in self.metadata_list
                               if meta.get("magazine") == magazine_code and meta.get("magazine_location") == location_name)

        # Double-confirm dialog
        if not self._double_confirm_dialog(
            "Delete Location",
            f"Delete location '{location_name}' from '{magazine_name}'?\n\n"
            f"This will affect {affected_captures} captured records.\n"
            f"This cannot be undone.",
            "DELETE"
        ):
            return

        # Auto-backup before deletion
        backup_path = self._create_auto_backup(f"delete location '{location_name}' from '{magazine_code}'")

        try:
            # Delete location
            locations = magazine_info.get("locations", [])
            if location_name in locations:
                locations.remove(location_name)

            # Save to magazines.json
            with open(self.magazines_file, 'w', encoding='utf-8') as f:
                json.dump(self.magazines, f, ensure_ascii=False, indent=2)

            # Refresh location dropdown
            self._update_magazine_locations()

            self.status_label.setText(f"Location deleted: {location_name} (backup available)")
            self.status_label.setStyleSheet("color: green;")
            self._add_audit_entry("LOCATION_DELETED", f"'{location_name}' from '{magazine_code}' ({affected_captures} captures)")
        except Exception as e:
            self.status_label.setText(f"Delete location failed: {e}")
            self.status_label.setStyleSheet("color: red;")
            self._add_audit_entry("LOCATION_DELETE_FAILED", f"'{location_name}': {e}", "failed")

    def _edit_magazine_details(self, magazine_code: str, new_name: str, new_country: str = ""):
        """Edit magazine details (PHASE 2)."""
        magazine_info = self.magazines.get("magazines", {}).get(magazine_code, {})
        old_name = magazine_info.get("name", "")

        # Auto-backup before edit
        backup_path = self._create_auto_backup(f"edit magazine '{magazine_code}'")

        try:
            magazine_info["name"] = new_name
            if new_country:
                magazine_info["country"] = new_country

            # Save to magazines.json
            with open(self.magazines_file, 'w', encoding='utf-8') as f:
                json.dump(self.magazines, f, ensure_ascii=False, indent=2)

            # Refresh UI
            self.magazine_combo.blockSignals(True)
            current_index = self.magazine_combo.currentIndex()
            self.magazine_combo.setItemText(current_index, new_name)
            self.magazine_combo.blockSignals(False)

            self.status_label.setText(f"Magazine updated: {old_name} -> {new_name}")
            self.status_label.setStyleSheet("color: green;")
            self._add_audit_entry("MAGAZINE_EDITED", f"'{old_name}' -> '{new_name}'")
        except Exception as e:
            self.status_label.setText(f"Edit magazine failed: {e}")
            self.status_label.setStyleSheet("color: red;")
            self._add_audit_entry("MAGAZINE_EDIT_FAILED", f"'{magazine_code}': {e}", "failed")

    def _restore_deleted_record(self, record_backup_path: str):
        """Restore deleted record from 24h recovery window (PHASE 2)."""
        try:
            # Find and restore record from backup
            backup_file = Path(record_backup_path) / "metadata.json"
            if backup_file.exists():
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_metadata = json.load(f)

                # Restore to current metadata
                self.metadata_list.extend(backup_metadata)
                self._save_metadata_list()

                self.status_label.setText("Record(s) restored from backup")
                self.status_label.setStyleSheet("color: green;")
                self._add_audit_entry("RECORD_RESTORED", f"From backup: {Path(record_backup_path).name}")
            else:
                self.status_label.setText("Backup file not found")
                self.status_label.setStyleSheet("color: orange;")
        except Exception as e:
            self.status_label.setText(f"Restore failed: {e}")
            self.status_label.setStyleSheet("color: red;")
            self._add_audit_entry("RECORD_RESTORE_FAILED", f"Error: {e}", "failed")

    # ==================== PHASE 3: Enhanced Audit & Statistics ====================

    def _export_audit_log_csv(self):
        """Export audit log as CSV (PHASE 3)."""
        export_path = QFileDialog.getSaveFileName(
            self, "Export Audit Log", str(self.base_folder / "audit_log.csv"), "CSV Files (*.csv)"
        )

        if not export_path[0]:
            return

        try:
            import csv
            with open(export_path[0], 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Operation", "Details", "Status"])

                for entry in self.audit_log:
                    writer.writerow([
                        entry.get("timestamp", ""),
                        entry.get("operation", ""),
                        entry.get("details", ""),
                        entry.get("status", "")
                    ])

            self.status_label.setText(f"Audit log exported: {Path(export_path[0]).name}")
            self.status_label.setStyleSheet("color: green;")
        except Exception as e:
            self.status_label.setText(f"Export failed: {e}")
            self.status_label.setStyleSheet("color: red;")

    def _filter_audit_log(self, operation_filter: str = "", date_filter: str = ""):
        """Filter and search audit log (PHASE 3)."""
        filtered = self.audit_log

        if operation_filter:
            filtered = [e for e in filtered if operation_filter.lower() in e.get("operation", "").lower()]

        if date_filter:
            filtered = [e for e in filtered if date_filter in e.get("timestamp", "")]

        return filtered

    def _check_database_integrity(self) -> Dict:
        """Check database integrity and report issues (PHASE 3)."""
        issues = {
            "warnings": [],
            "errors": [],
            "info": []
        }

        # Check for orphaned captures (captures without products)
        for meta in self.metadata_list:
            product = meta.get("product", "")
            if not product:
                issues["warnings"].append("Capture without product name")

        # Check baskets consistency
        for basket_key in self.products_db.get("baskets", {}):
            basket = self.products_db["baskets"][basket_key]
            for cat_key in basket.get("products", {}):
                if cat_key not in self.products_db.get("categories", {}):
                    issues["warnings"].append(f"Category '{cat_key}' in basket but not in categories")

        # Check magazine consistency
        for mag_code in self.magazines.get("magazines", {}):
            if not mag_code:
                issues["errors"].append("Magazine with empty code")

        # Info: Database size
        issues["info"].append(f"Total captures: {len(self.metadata_list)}")
        issues["info"].append(f"Total backups: {len(list(self.backup_folder.iterdir())) if self.backup_folder.exists() else 0}")
        issues["info"].append(f"Audit entries: {len(self.audit_log)}")

        return issues

    def _show_database_health_report(self):
        """Show database health and integrity report (PHASE 3)."""
        integrity = self._check_database_integrity()

        report = "DATABASE HEALTH REPORT\n" \
                "======================\n\n"

        if integrity["errors"]:
            report += f"ERRORS ({len(integrity['errors'])}):\n"
            for error in integrity["errors"]:
                report += f"  X {error}\n"
            report += "\n"

        if integrity["warnings"]:
            report += f"WARNINGS ({len(integrity['warnings'])}):\n"
            for warning in integrity["warnings"][:10]:  # Show first 10
                report += f"  ! {warning}\n"
            if len(integrity["warnings"]) > 10:
                report += f"  ... and {len(integrity['warnings']) - 10} more\n"
            report += "\n"

        if integrity["info"]:
            report += "DATABASE INFO:\n"
            for info in integrity["info"]:
                report += f"  • {info}\n"

        QMessageBox.information(self, "Database Health", report)

    def _setup_integrity_alerts(self):
        """Setup automatic integrity checks and alerts (PHASE 3)."""
        # Check on startup
        integrity = self._check_database_integrity()
        if integrity["errors"]:
            debug_log("INTEGRITY_ERROR", f"{len(integrity['errors'])} errors found")
        if integrity["warnings"]:
            debug_log("INTEGRITY_WARNING", f"{len(integrity['warnings'])} warnings found")


# ============================================================================
# DIALOG CLASSES FOR DATA MANAGEMENT
# ============================================================================

class ProductsBrandDialog(QDialog):
    """Dialog for managing products or brands with rename/delete/reorder."""

    def __init__(self, parent, title: str, items_list: list, item_type: str):
        super().__init__(parent)
        self.parent_app = parent
        self.title = title
        self.items_list = items_list.copy()  # Copy to avoid modifying original
        self.item_type = item_type  # "product" or "brand"
        self.original_items = items_list.copy()

        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle(f"Manage {self.title}")
        self.setGeometry(100, 100, 700, 500)

        layout = QVBoxLayout()

        # Get usage counts
        if self.item_type == "product":
            self.counts = self.parent_app._get_product_counts()
        else:
            self.counts = self.parent_app._get_brand_counts()

        # Info label
        info_label = QLabel(f"Manage {self.title} - Rename or Delete Entries")
        info_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(info_label)

        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Usage Count", "Rename", "Delete"])
        self.table.setColumnWidth(0, 350)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 80)

        # Populate table
        self.table.setRowCount(len(self.items_list))
        for row, item in enumerate(sorted(self.items_list)):
            count = self.counts.get(item, 0)

            # Name column
            name_item = QTableWidgetItem(item)
            self.table.setItem(row, 0, name_item)

            # Count column
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, count_item)

            # Rename button
            rename_btn = QPushButton("Edit")
            rename_btn.clicked.connect(lambda checked, r=row: self.rename_item(r))
            self.table.setCellWidget(row, 2, rename_btn)

            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("background-color: #ffcccc;")
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_item(r))
            self.table.setCellWidget(row, 3, delete_btn)

        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def rename_item(self, row: int):
        """Rename an item."""
        old_name = self.table.item(row, 0).text()

        new_name, ok = QInputDialog.getText(
            self,
            "Rename Item",
            f"Rename '{old_name}' to:",
            text=old_name
        )

        if ok and new_name and new_name != old_name:
            # Confirm retroactive update
            count = self.counts.get(old_name, 0)
            msg = f"This will update {count} existing captures.\n\nConfirm rename '{old_name}' > '{new_name}'?"
            reply = QMessageBox.question(self, "Confirm Retroactive Update", msg)

            if reply == QMessageBox.Yes:
                # Perform rename
                if self.item_type == "product":
                    updated = self.parent_app._rename_product(old_name, new_name)
                else:
                    updated = self.parent_app._rename_brand(old_name, new_name)

                QMessageBox.information(self, "Success", f"Updated {updated} items with new name.")

                # Refresh table
                self.items_list = self.original_items.copy()
                if self.item_type == "product":
                    self.items_list = self.parent_app.product_names.copy()
                    self.counts = self.parent_app._get_product_counts()
                else:
                    self.items_list = self.parent_app.brands_list.copy()
                    self.counts = self.parent_app._get_brand_counts()

                self.refresh_table()

    def delete_item(self, row: int):
        """Delete an item."""
        item_name = self.table.item(row, 0).text()
        count = self.counts.get(item_name, 0)

        msg = f"Delete '{item_name}' from autocomplete?\n\n{count} existing captures still use this name.\n" \
              f"(Existing data will NOT be changed, only removed from suggestions)"
        reply = QMessageBox.question(self, "Confirm Delete", msg)

        if reply == QMessageBox.Yes:
            # Perform delete
            if self.item_type == "product":
                self.parent_app._delete_product(item_name)
            else:
                self.parent_app._delete_brand(item_name)

            QMessageBox.information(self, "Success", f"'{item_name}' removed from autocomplete.")

            # Refresh
            if self.item_type == "product":
                self.items_list = self.parent_app.product_names.copy()
                self.counts = self.parent_app._get_product_counts()
            else:
                self.items_list = self.parent_app.brands_list.copy()
                self.counts = self.parent_app._get_brand_counts()

            self.refresh_table()

    def refresh_table(self):
        """Refresh table content."""
        self.table.setRowCount(len(self.items_list))
        for row, item in enumerate(sorted(self.items_list)):
            count = self.counts.get(item, 0)

            name_item = QTableWidgetItem(item)
            self.table.setItem(row, 0, name_item)

            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, count_item)

            rename_btn = QPushButton("Edit")
            rename_btn.clicked.connect(lambda checked, r=row: self.rename_item(r))
            self.table.setCellWidget(row, 2, rename_btn)

            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("background-color: #ffcccc;")
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_item(r))
            self.table.setCellWidget(row, 3, delete_btn)


class DataManagementDialog(QDialog):
    """Main dialog with tabs for Products and Brands management."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent_app = parent

        self.setWindowTitle("Products & Brands Management")
        self.setGeometry(50, 50, 900, 600)

        layout = QVBoxLayout()

        # Tabs
        tabs = QTabWidget()

        # Products tab
        products_dialog = ProductsBrandDialog(parent, "Products", parent.product_names, "product")
        tabs.addTab(products_dialog.table.parent() if hasattr(products_dialog.table, 'parent') else products_dialog,
                   "Products")

        # Brands tab
        brands_dialog = ProductsBrandDialog(parent, "Brands", parent.brands_list, "brand")
        tabs.addTab(brands_dialog, "Brands")

        layout.addWidget(tabs)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    window = SnippetApp()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
