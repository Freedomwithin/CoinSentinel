## 2024-05-22 - Disabled State Clarity
**Learning:** Disabled buttons (like "Save Prediction") without tooltips confuse users about *why* they are disabled.
**Action:** Always add a tooltip explaining the requirement (e.g., "Run a prediction first") even on disabled elements to guide the user.

## 2024-05-22 - PyQt Accessibility Patterns
**Learning:** PyQt uses `setAccessibleName` and `setAccessibleDescription` instead of ARIA attributes. These map directly to OS-level accessibility APIs.
**Action:** Always use these methods for custom widgets or non-standard controls to ensure screen reader compatibility.

## 2024-05-22 - Neon-Sentinel UI Overhaul
**Learning:** Heavy blur effects (QGraphicsBlurEffect) are performance killers on Linux/X11. "Glassmorphism" can be simulated efficiently with semi-transparent backgrounds and borders.
**Action:** Use RGBA colors (e.g., `rgba(30, 32, 38, 0.7)`) for panel backgrounds instead of blur effects to ensure 60fps performance on all platforms.

## 2024-05-22 - Global Stylesheet Activation
**Learning:** Defining stylesheets inline within the main application file simplifies context but can lead to clutter. Using a dedicated dictionary for the palette (`NEON_PALETTE`) and f-strings for the stylesheet keeps it maintainable and allows easy color referencing in Python code (e.g., for conditional table cell coloring).
**Action:** Centralize theme definitions in a `PALETTE` constant and inject them into a `GLOBAL_STYLESHEET` string for consistency across QSS and Python logic.
