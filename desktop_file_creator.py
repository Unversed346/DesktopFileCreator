#!/usr/bin/env python3
"""
.desktop File Creator
A PySide6 GUI tool for creating XDG .desktop launcher files.
"""

import sys
import os
import subprocess
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QPushButton, QComboBox, QCheckBox,
    QRadioButton, QButtonGroup, QFileDialog, QLabel, QGroupBox,
    QMessageBox, QFrame, QScrollArea, QSizePolicy, QStackedWidget,
    QTextEdit, QToolButton,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_system_app_dirs() -> list[str]:
    """Return standard XDG application directories."""
    dirs = ["/usr/share/applications", "/usr/local/share/applications"]
    xdg_data_dirs = os.environ.get("XDG_DATA_DIRS", "")
    for d in xdg_data_dirs.split(":"):
        if d:
            dirs.append(os.path.join(d, "applications"))
    return dirs


def get_user_app_dir() -> str:
    xdg_data_home = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    return os.path.join(xdg_data_home, "applications")


# ---------------------------------------------------------------------------
# Styled sub-widgets
# ---------------------------------------------------------------------------

class SectionTitle(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.setFont(font)
        self.setStyleSheet("color: #5294e2; margin-top: 6px;")


class HRule(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setStyleSheet("color: #3c4252;")


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class DesktopFileCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(".desktop File Creator")
        self.setMinimumWidth(620)
        self.setMinimumHeight(700)
        self._apply_dark_theme()
        self._build_ui()

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def _apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e2230;
                color: #d8dee9;
                font-family: 'Segoe UI', 'Noto Sans', sans-serif;
                font-size: 10pt;
            }
            QGroupBox {
                border: 1px solid #3c4252;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                color: #81a1c1;
                font-weight: bold;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #252a3a;
                border: 1px solid #3c4252;
                border-radius: 4px;
                padding: 4px 8px;
                color: #d8dee9;
                selection-background-color: #5294e2;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #5294e2;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #81a1c1;
                margin-right: 6px;
            }
            QComboBox QAbstractItemView {
                background-color: #252a3a;
                border: 1px solid #3c4252;
                selection-background-color: #5294e2;
            }
            QPushButton {
                background-color: #3b4261;
                border: 1px solid #4a5270;
                border-radius: 5px;
                padding: 6px 16px;
                color: #d8dee9;
            }
            QPushButton:hover {
                background-color: #4a5270;
                border-color: #5294e2;
            }
            QPushButton:pressed {
                background-color: #2e3450;
            }
            QPushButton#primaryBtn {
                background-color: #5294e2;
                border: 1px solid #6ba8f0;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton#primaryBtn:hover {
                background-color: #6ba8f0;
            }
            QPushButton#primaryBtn:pressed {
                background-color: #3a7acf;
            }
            QPushButton#dangerBtn {
                background-color: #bf616a;
                border: 1px solid #d0717a;
                color: #ffffff;
            }
            QPushButton#dangerBtn:hover {
                background-color: #d0717a;
            }
            QCheckBox, QRadioButton {
                spacing: 8px;
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {
                border: 2px solid #4a5270;
                border-radius: 3px;
                background: #252a3a;
            }
            QRadioButton::indicator:unchecked {
                border-radius: 8px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #5294e2;
                border-radius: 3px;
                background: #5294e2;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #5294e2;
                border-radius: 8px;
                background: #5294e2;
            }
            QScrollArea {
                border: none;
            }
            QLabel#iconPreview {
                border: 1px dashed #4a5270;
                border-radius: 4px;
                background-color: #252a3a;
            }
            QTextEdit#preview {
                font-family: 'Courier New', monospace;
                font-size: 9pt;
                background-color: #141824;
                color: #a3be8c;
                border: 1px solid #3c4252;
                border-radius: 4px;
            }
        """)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(10)

        # Header
        header = QLabel(".desktop File Creator")
        hfont = QFont()
        hfont.setPointSize(14)
        hfont.setBold(True)
        header.setFont(hfont)
        header.setStyleSheet("color: #81a1c1;")
        root.addWidget(header)

        sub = QLabel("Generate XDG application launcher files for Linux desktops")
        sub.setStyleSheet("color: #616e88; font-size: 9pt;")
        root.addWidget(sub)
        root.addWidget(HRule())

        # Scrollable form area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(0, 4, 0, 4)

        # ── Scope ──────────────────────────────────────────────────────
        scope_group = QGroupBox("Installation Scope")
        scope_inner = QHBoxLayout(scope_group)
        self.rb_user = QRadioButton("Personal (current user only)")
        self.rb_system = QRadioButton("System-wide (all users, requires root)")
        self.rb_user.setChecked(True)
        self._scope_group = QButtonGroup()
        self._scope_group.addButton(self.rb_user)
        self._scope_group.addButton(self.rb_system)
        scope_inner.addWidget(self.rb_user)
        scope_inner.addWidget(self.rb_system)
        scope_inner.addStretch()
        form_layout.addWidget(scope_group)

        # ── Basic Info ─────────────────────────────────────────────────
        info_group = QGroupBox("Basic Information")
        info_form = QFormLayout(info_group)
        info_form.setLabelAlignment(Qt.AlignRight)
        info_form.setHorizontalSpacing(12)
        info_form.setVerticalSpacing(8)

        self.le_name = QLineEdit()
        self.le_name.setPlaceholderText("My Application")
        info_form.addRow("Name *", self.le_name)

        self.le_generic_name = QLineEdit()
        self.le_generic_name.setPlaceholderText("e.g. Text Editor  (optional)")
        info_form.addRow("Generic Name", self.le_generic_name)

        self.le_comment = QLineEdit()
        self.le_comment.setPlaceholderText("Short description shown in tooltip")
        info_form.addRow("Comment", self.le_comment)

        self.le_categories = QLineEdit()
        self.le_categories.setPlaceholderText("e.g. Utility;TextEditor;  (semicolon-separated)")
        info_form.addRow("Categories", self.le_categories)

        self.le_keywords = QLineEdit()
        self.le_keywords.setPlaceholderText("e.g. editor;text;  (semicolon-separated, optional)")
        info_form.addRow("Keywords", self.le_keywords)

        form_layout.addWidget(info_group)

        # ── Type ───────────────────────────────────────────────────────
        type_group = QGroupBox("Entry Type")
        type_inner = QHBoxLayout(type_group)
        self.cb_type = QComboBox()
        self.cb_type.addItems(["Application", "Link", "Directory"])
        self.cb_type.setFixedWidth(180)
        type_inner.addWidget(QLabel("Type:"))
        type_inner.addWidget(self.cb_type)
        type_inner.addStretch()
        form_layout.addWidget(type_group)

        # ── Exec / URL ─────────────────────────────────────────────────
        exec_group = QGroupBox("Command / Execution")
        exec_v = QVBoxLayout(exec_group)
        exec_v.setSpacing(8)

        # Radio: file vs command
        exec_radio_row = QHBoxLayout()
        self.rb_exec_file = QRadioButton("Execute a file / binary")
        self.rb_exec_cmd = QRadioButton("Execute a shell command")
        self.rb_exec_file.setChecked(True)
        self._exec_mode_group = QButtonGroup()
        self._exec_mode_group.addButton(self.rb_exec_file)
        self._exec_mode_group.addButton(self.rb_exec_cmd)
        exec_radio_row.addWidget(self.rb_exec_file)
        exec_radio_row.addWidget(self.rb_exec_cmd)
        exec_radio_row.addStretch()
        exec_v.addLayout(exec_radio_row)

        # Stacked pages: file picker  /  command line edit
        self.exec_stack = QStackedWidget()

        # Page 0: file picker
        page_file = QWidget()
        pf_layout = QHBoxLayout(page_file)
        pf_layout.setContentsMargins(0, 0, 0, 0)
        self.le_exec_file = QLineEdit()
        self.le_exec_file.setPlaceholderText("/usr/bin/my-app")
        btn_browse_exec = QPushButton("Browse…")
        btn_browse_exec.setFixedWidth(90)
        btn_browse_exec.clicked.connect(self._browse_exec)
        pf_layout.addWidget(self.le_exec_file)
        pf_layout.addWidget(btn_browse_exec)

        # Page 1: command text
        page_cmd = QWidget()
        pc_layout = QHBoxLayout(page_cmd)
        pc_layout.setContentsMargins(0, 0, 0, 0)
        self.le_exec_cmd = QLineEdit()
        self.le_exec_cmd.setPlaceholderText("bash -c 'echo hello && read'")
        pc_layout.addWidget(self.le_exec_cmd)

        self.exec_stack.addWidget(page_file)
        self.exec_stack.addWidget(page_cmd)
        exec_v.addWidget(self.exec_stack)

        # Path field
        path_row = QHBoxLayout()
        path_label = QLabel("Working Dir:")
        path_label.setFixedWidth(90)
        self.le_path = QLineEdit()
        self.le_path.setPlaceholderText("/home/user  (optional)")
        btn_browse_path = QPushButton("Browse…")
        btn_browse_path.setFixedWidth(90)
        btn_browse_path.clicked.connect(self._browse_path)
        path_row.addWidget(path_label)
        path_row.addWidget(self.le_path)
        path_row.addWidget(btn_browse_path)
        exec_v.addLayout(path_row)

        # Exec flags
        flags_row = QHBoxLayout()
        self.chk_terminal = QCheckBox("Run in terminal")
        self.chk_startup_notify = QCheckBox("Startup notification")
        self.chk_no_display = QCheckBox("Hide from menus (NoDisplay)")
        flags_row.addWidget(self.chk_terminal)
        flags_row.addWidget(self.chk_startup_notify)
        flags_row.addWidget(self.chk_no_display)
        flags_row.addStretch()
        exec_v.addLayout(flags_row)

        form_layout.addWidget(exec_group)

        # Connect exec mode radios
        self.rb_exec_file.toggled.connect(lambda checked: self.exec_stack.setCurrentIndex(0) if checked else None)
        self.rb_exec_cmd.toggled.connect(lambda checked: self.exec_stack.setCurrentIndex(1) if checked else None)

        # ── Icon ───────────────────────────────────────────────────────
        icon_group = QGroupBox("Icon")
        icon_h = QHBoxLayout(icon_group)

        self.icon_preview = QLabel()
        self.icon_preview.setObjectName("iconPreview")
        self.icon_preview.setFixedSize(56, 56)
        self.icon_preview.setAlignment(Qt.AlignCenter)
        self.icon_preview.setText("?")
        self.icon_preview.setStyleSheet(
            "QLabel#iconPreview { border: 1px dashed #4a5270; border-radius:4px;"
            " background:#252a3a; font-size:20pt; color:#4a5270; }"
        )
        icon_h.addWidget(self.icon_preview)

        icon_right = QVBoxLayout()
        icon_input_row = QHBoxLayout()
        self.le_icon = QLineEdit()
        self.le_icon.setPlaceholderText("Icon name or /path/to/icon.png")
        self.le_icon.textChanged.connect(self._update_icon_preview)
        btn_browse_icon = QPushButton("Browse…")
        btn_browse_icon.setFixedWidth(90)
        btn_browse_icon.clicked.connect(self._browse_icon)
        icon_input_row.addWidget(self.le_icon)
        icon_input_row.addWidget(btn_browse_icon)
        icon_right.addLayout(icon_input_row)
        icon_hint = QLabel("Use a theme icon name (e.g. <i>utilities-terminal</i>) or an absolute path.")
        icon_hint.setWordWrap(True)
        icon_hint.setStyleSheet("color: #616e88; font-size: 8pt;")
        icon_right.addWidget(icon_hint)
        icon_right.addStretch()
        icon_h.addLayout(icon_right)
        form_layout.addWidget(icon_group)

        # ── MIME types ─────────────────────────────────────────────────
        mime_group = QGroupBox("MIME Types  (optional)")
        mime_v = QVBoxLayout(mime_group)
        self.le_mime = QLineEdit()
        self.le_mime.setPlaceholderText("e.g. text/plain;image/png;  (semicolon-separated)")
        mime_v.addWidget(self.le_mime)
        form_layout.addWidget(mime_group)

        # ── Live preview ───────────────────────────────────────────────
        preview_group = QGroupBox("Live Preview")
        prev_v = QVBoxLayout(preview_group)
        self.preview_text = QTextEdit()
        self.preview_text.setObjectName("preview")
        self.preview_text.setReadOnly(True)
        self.preview_text.setFixedHeight(160)
        prev_v.addWidget(self.preview_text)
        form_layout.addWidget(preview_group)

        form_layout.addStretch()
        scroll.setWidget(form_widget)
        root.addWidget(scroll)

        # ── Buttons ────────────────────────────────────────────────────
        root.addWidget(HRule())
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_preview = QPushButton("⟳  Refresh Preview")
        btn_preview.clicked.connect(self._refresh_preview)

        btn_validate = QPushButton("✓  Validate")
        btn_validate.clicked.connect(self._validate)

        btn_save = QPushButton("💾  Save .desktop File")
        btn_save.setObjectName("primaryBtn")
        btn_save.clicked.connect(self._save)

        btn_clear = QPushButton("✕  Clear")
        btn_clear.setObjectName("dangerBtn")
        btn_clear.clicked.connect(self._clear)

        btn_row.addWidget(btn_preview)
        btn_row.addWidget(btn_validate)
        btn_row.addStretch()
        btn_row.addWidget(btn_clear)
        btn_row.addWidget(btn_save)
        root.addLayout(btn_row)

        # Connect live-update signals
        for widget in [
            self.le_name, self.le_generic_name, self.le_comment,
            self.le_categories, self.le_keywords, self.le_exec_file,
            self.le_exec_cmd, self.le_path, self.le_icon, self.le_mime,
        ]:
            widget.textChanged.connect(self._refresh_preview)
        for cb in [self.chk_terminal, self.chk_startup_notify, self.chk_no_display]:
            cb.stateChanged.connect(self._refresh_preview)
        self.cb_type.currentIndexChanged.connect(self._refresh_preview)
        self.rb_exec_file.toggled.connect(self._refresh_preview)
        self.rb_user.toggled.connect(self._refresh_preview)

        self._refresh_preview()

    # ------------------------------------------------------------------
    # Browse helpers
    # ------------------------------------------------------------------

    def _browse_exec(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Executable", os.path.expanduser("~"))
        if path:
            self.le_exec_file.setText(path)

    def _browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Working Directory", os.path.expanduser("~"))
        if path:
            self.le_path.setText(path)

    def _browse_icon(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Icon",
            os.path.expanduser("~"),
            "Images (*.png *.svg *.xpm *.ico *.jpg);;All Files (*)"
        )
        if path:
            self.le_icon.setText(path)

    def _update_icon_preview(self, text: str):
        text = text.strip()
        if os.path.isabs(text) and os.path.isfile(text):
            pix = QPixmap(text)
            if not pix.isNull():
                self.icon_preview.setPixmap(pix.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.icon_preview.setText("")
                return
        self.icon_preview.clear()
        self.icon_preview.setText(text[:2] if text else "?")

    # ------------------------------------------------------------------
    # Build the file content
    # ------------------------------------------------------------------

    def _build_content(self) -> str:
        entry_type = self.cb_type.currentText()
        lines = [
            "[Desktop Entry]",
            f"Version=1.0",
            f"Type={entry_type}",
        ]

        def add(key, value):
            if value:
                lines.append(f"{key}={value}")

        add("Name", self.le_name.text().strip())
        add("GenericName", self.le_generic_name.text().strip())
        add("Comment", self.le_comment.text().strip())
        add("Icon", self.le_icon.text().strip())

        if entry_type == "Application":
            if self.rb_exec_file.isChecked():
                exec_val = self.le_exec_file.text().strip()
            else:
                exec_val = self.le_exec_cmd.text().strip()
            add("Exec", exec_val)
            add("Path", self.le_path.text().strip())
            lines.append(f"Terminal={'true' if self.chk_terminal.isChecked() else 'false'}")
            if self.chk_startup_notify.isChecked():
                lines.append("StartupNotify=true")
        elif entry_type == "Link":
            add("URL", self.le_exec_file.text().strip() if self.rb_exec_file.isChecked() else self.le_exec_cmd.text().strip())

        add("Categories", self.le_categories.text().strip())
        add("Keywords", self.le_keywords.text().strip())
        add("MimeType", self.le_mime.text().strip())
        if self.chk_no_display.isChecked():
            lines.append("NoDisplay=true")

        scope = "user" if self.rb_user.isChecked() else "system"
        lines.append(f"# Scope: {scope}")
        return "\n".join(lines) + "\n"

    def _refresh_preview(self):
        self.preview_text.setPlainText(self._build_content())

    # ------------------------------------------------------------------
    # Validate
    # ------------------------------------------------------------------

    def _validate(self) -> bool:
        errors = []

        if not self.le_name.text().strip():
            errors.append("• Name is required.")

        entry_type = self.cb_type.currentText()
        if entry_type in ("Application", "Link"):
            exec_val = (self.le_exec_file.text() if self.rb_exec_file.isChecked() else self.le_exec_cmd.text()).strip()
            if not exec_val:
                errors.append("• Exec / URL is required for Application and Link types.")
            if self.rb_exec_file.isChecked() and entry_type == "Application":
                bin_path = exec_val.split()[0] if exec_val else ""
                if bin_path and not os.path.exists(bin_path):
                    errors.append(f"• Executable not found: {bin_path}")

        icon = self.le_icon.text().strip()
        if icon and os.path.isabs(icon) and not os.path.isfile(icon):
            errors.append(f"• Icon file not found: {icon}")

        if errors:
            QMessageBox.warning(self, "Validation Errors", "\n".join(errors))
            return False

        QMessageBox.information(self, "Validation", "✓ All fields look good!")
        return True

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _save(self):
        name = self.le_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a Name before saving.")
            return

        safe_name = name.lower().replace(" ", "-")
        default_filename = f"{safe_name}.desktop"

        if self.rb_user.isChecked():
            default_dir = get_user_app_dir()
            os.makedirs(default_dir, exist_ok=True)
        else:
            default_dir = "/usr/local/share/applications"

        default_path = os.path.join(default_dir, default_filename)

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save .desktop File",
            default_path,
            "Desktop Entry (*.desktop);;All Files (*)"
        )
        if not path:
            return

        content = self._build_content()
        # Strip the scope comment line before writing
        content_clean = "\n".join(
            l for l in content.splitlines() if not l.startswith("# Scope:")
        ) + "\n"

        try:
            if self.rb_system.isChecked() and not os.access(os.path.dirname(path) or ".", os.W_OK):
                # Try via pkexec / sudo
                import tempfile
                with tempfile.NamedTemporaryFile("w", suffix=".desktop", delete=False) as tmp:
                    tmp.write(content_clean)
                    tmp_path = tmp.name
                result = subprocess.run(
                    ["pkexec", "cp", tmp_path, path],
                    capture_output=True
                )
                os.unlink(tmp_path)
                if result.returncode != 0:
                    raise PermissionError(result.stderr.decode())
            else:
                with open(path, "w") as f:
                    f.write(content_clean)
            os.chmod(path, 0o644)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save file:\n{e}")
            return

        # Optionally update desktop database
        try:
            subprocess.run(
                ["update-desktop-database", os.path.dirname(path)],
                capture_output=True, timeout=5
            )
        except Exception:
            pass

        QMessageBox.information(
            self, "Saved",
            f"File saved to:\n{path}\n\nYou may need to log out and back in for the\nlauncher to appear in your application menu."
        )

    # ------------------------------------------------------------------
    # Clear
    # ------------------------------------------------------------------

    def _clear(self):
        reply = QMessageBox.question(
            self, "Clear Form",
            "Clear all fields?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        for le in [
            self.le_name, self.le_generic_name, self.le_comment,
            self.le_categories, self.le_keywords, self.le_exec_file,
            self.le_exec_cmd, self.le_path, self.le_icon, self.le_mime,
        ]:
            le.clear()
        self.chk_terminal.setChecked(False)
        self.chk_startup_notify.setChecked(False)
        self.chk_no_display.setChecked(False)
        self.rb_user.setChecked(True)
        self.rb_exec_file.setChecked(True)
        self.cb_type.setCurrentIndex(0)
        self.icon_preview.clear()
        self.icon_preview.setText("?")
        self._refresh_preview()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Desktop File Creator")
    app.setApplicationVersion("1.0")
    window = DesktopFileCreator()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
