
NEON_PALETTE = {
    "background": "#0a0b0d",
    "surface": "rgba(30, 32, 38, 0.7)",
    "border": "rgba(255, 255, 255, 0.1)",
    "primary": "#3498db",  # Keep blue for primary actions
    "success": "#10b981",  # Electric Mint
    "danger": "#ef4444",   # Crimson Glow
    "text_primary": "#ffffff",
    "text_secondary": "#94a3b8",
    "sidebar_bg": "#0f1115",
    "sidebar_hover": "#1e2126",
    "sidebar_active": "#1a1d24",
    "table_header": "#1a1d24",
    "table_row_hover": "#1e2126",
    "scroll_handle": "#2c3e50"
}

GLOBAL_STYLESHEET = f"""
/* Global Reset */
QWidget {{
    background-color: {NEON_PALETTE["background"]};
    color: {NEON_PALETTE["text_primary"]};
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 14px;
}}

/* Main Window */
QMainWindow {{
    background-color: {NEON_PALETTE["background"]};
}}

/* Scrollbars */
QScrollBar:vertical {{
    border: none;
    background: {NEON_PALETTE["background"]};
    width: 10px;
    margin: 0px 0px 0px 0px;
}}
QScrollBar::handle:vertical {{
    background: {NEON_PALETTE["scroll_handle"]};
    min-height: 20px;
    border-radius: 5px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* Group Boxes (Cards) */
QGroupBox {{
    background-color: {NEON_PALETTE["surface"]};
    border: 1px solid {NEON_PALETTE["border"]};
    border-radius: 12px;
    margin-top: 24px;
    padding-top: 10px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: {NEON_PALETTE["text_secondary"]};
    background-color: transparent;
}}

/* Inputs & Combos */
QLineEdit, QComboBox, QDoubleSpinBox {{
    background-color: {NEON_PALETTE["sidebar_bg"]};
    border: 1px solid {NEON_PALETTE["border"]};
    border-radius: 6px;
    padding: 8px;
    color: {NEON_PALETTE["text_primary"]};
    selection-background-color: {NEON_PALETTE["primary"]};
}}
QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {NEON_PALETTE["primary"]};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

/* Buttons */
QPushButton {{
    background-color: {NEON_PALETTE["surface"]};
    border: 1px solid {NEON_PALETTE["border"]};
    border-radius: 8px;
    padding: 8px 16px;
    color: {NEON_PALETTE["text_primary"]};
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {NEON_PALETTE["sidebar_hover"]};
    border: 1px solid {NEON_PALETTE["text_secondary"]};
}}
QPushButton:pressed {{
    background-color: {NEON_PALETTE["sidebar_active"]};
}}
QPushButton:disabled {{
    background-color: {NEON_PALETTE["sidebar_bg"]};
    color: {NEON_PALETTE["text_secondary"]};
    border: 1px solid transparent;
}}

/* Primary Action Buttons (Success/Danger overrides can be done inline or with object names) */

/* Tables */
QTableWidget {{
    background-color: {NEON_PALETTE["surface"]};
    border: 1px solid {NEON_PALETTE["border"]};
    gridline-color: {NEON_PALETTE["border"]};
    border-radius: 8px;
    outline: none;
}}
QHeaderView::section {{
    background-color: {NEON_PALETTE["table_header"]};
    color: {NEON_PALETTE["text_secondary"]};
    padding: 8px;
    border: none;
    border-bottom: 1px solid {NEON_PALETTE["border"]};
    font-weight: 600;
    text-transform: uppercase;
    font-size: 12px;
}}
QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}}
QTableWidget::item:selected {{
    background-color: {NEON_PALETTE["sidebar_active"]};
    color: {NEON_PALETTE["text_primary"]};
}}
/* Row Hover Effect */
QTableWidget::item:hover {{
    background-color: {NEON_PALETTE["table_row_hover"]};
}}

/* Sidebar Specifics */
QWidget#sidebar {{
    background-color: {NEON_PALETTE["sidebar_bg"]};
    border-right: 1px solid {NEON_PALETTE["border"]};
}}
QPushButton#sidebar_btn {{
    text-align: left;
    padding: 12px 20px;
    border: none;
    border-radius: 0px;
    background-color: transparent;
    color: {NEON_PALETTE["text_secondary"]};
    font-size: 15px;
    margin: 2px 10px;
    border-radius: 8px;
}}
QPushButton#sidebar_btn:hover {{
    background-color: {NEON_PALETTE["sidebar_hover"]};
    color: {NEON_PALETTE["text_primary"]};
}}
QPushButton#sidebar_btn:checked {{
    background-color: rgba(16, 185, 129, 0.1); /* Low opacity electric mint */
    color: {NEON_PALETTE["success"]};
    border-left: 3px solid {NEON_PALETTE["success"]};
}}

/* Text Areas */
QTextEdit {{
    background-color: {NEON_PALETTE["sidebar_bg"]};
    border: 1px solid {NEON_PALETTE["border"]};
    border-radius: 8px;
    color: {NEON_PALETTE["text_primary"]};
}}
"""
