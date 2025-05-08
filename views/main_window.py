"""
Main Window - The main application window with tabs for various features
"""
import os
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QLabel, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt

from models.company import Company
from views.project_view import ProjectView
from views.rooms_view import RoomsView
from views.scope_view import ScopeView
from views.dashboard_view import DashboardView
from views.export_view import ExportView
from views.rate_card_view import RateCardView

class MainWindow(QMainWindow):
    """Main window for the Interior Design Quote Tool application"""
    
    def __init__(self, project_controller, calculation_controller, 
                rate_card_controller, export_controller):
        """Initialize the main window with controllers"""
        super().__init__()
        
        # Store controllers
        self.project_controller = project_controller
        self.calculation_controller = calculation_controller
        self.rate_card_controller = rate_card_controller
        self.export_controller = export_controller
        
        # Set up the UI
        self.init_ui()
        
        # Set company theme
        self.set_company_theme()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Set window properties
        self.setWindowTitle("Home Project - Interior Design Quote Tool")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set window icon if logo file exists
        logo_path = Company.get_logo_path(compact=True)
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create header with company logo and title
        header_layout = QVBoxLayout()
        
        # Add logo
        logo_label = QLabel()
        logo_path = Company.get_logo_path(compact=False)
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            if not logo_pixmap.isNull():
                scaled_logo = logo_pixmap.scaled(250, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_logo)
                logo_label.setAlignment(Qt.AlignCenter)
                header_layout.addWidget(logo_label)
        
        # Add title
        header = QLabel("Interior Design Quote Tool")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet(f"color: {Company.HEADER_TEXT_COLOR}; padding: 5px;")
        header_layout.addWidget(header)
        
        # Add header layout to main layout
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        header_widget.setStyleSheet(f"background-color: {Company.HEADER_BG_COLOR};")
        main_layout.addWidget(header_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create and add tabs with views
        self.project_view = ProjectView(self.project_controller)
        self.rooms_view = RoomsView(self.project_controller)
        self.scope_view = ScopeView(
            self.project_controller, 
            self.calculation_controller,
            self.rate_card_controller
        )
        self.dashboard_view = DashboardView(
            self.project_controller, 
            self.calculation_controller
        )
        self.export_view = ExportView(
            self.project_controller,
            self.calculation_controller,
            self.export_controller
        )
        self.rate_card_view = RateCardView(self.rate_card_controller)
        
        # Add tabs to tab widget
        self.tabs.addTab(self.project_view, "Project Info")
        self.tabs.addTab(self.rooms_view, "Rooms")
        self.tabs.addTab(self.scope_view, "Scope of Work")
        self.tabs.addTab(self.dashboard_view, "Dashboard")
        self.tabs.addTab(self.export_view, "Export")
        self.tabs.addTab(self.rate_card_view, "Rate Card")
        
        # Set up status bar for notifications
        self.statusBar().showMessage("Ready - " + Company.COMPANY_NAME)
    
    def set_company_theme(self):
        """Set application-wide theme with company colors"""
        primary_color = Company.PRIMARY_COLOR
        
        self.setStyleSheet(f"""
            QMainWindow, QTabWidget, QWidget {{
                background-color: #2D2D2D;
                color: white;
            }}
            
            QTabWidget::pane {{ 
                border: 1px solid #444; 
                background-color: #2D2D2D;
            }}
            
            QTabBar::tab {{ 
                background-color: #3D3D3D; 
                color: #CCC; 
                padding: 8px 16px;
                border: 1px solid #555;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{ 
                background-color: {primary_color}; 
                color: white;
            }}
            
            QPushButton {{
                background-color: #444;
                color: white;
                border: 1px solid #555;
                padding: 5px 10px;
                border-radius: 3px;
            }}
            
            QPushButton:hover {{
                background-color: {primary_color};
            }}
            
            QTableWidget {{
                gridline-color: #444;
                color: white;
                background-color: #2D2D2D;
                selection-background-color: {primary_color};
            }}
            
            QHeaderView::section {{
                background-color: #3D3D3D;
                color: white;
                padding: 5px;
                border: 1px solid #444;
            }}
            
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
                background-color: #444;
                color: white;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 3px;
            }}
            
            QTreeWidget {{
                background-color: #2D2D2D;
                color: white;
                border: 1px solid #444;
            }}
            
            QTreeWidget::item:selected {{
                background-color: {primary_color};
            }}
            
            QDialog {{
                background-color: #2D2D2D;
                color: white;
            }}
            
            QLabel {{
                color: white;
            }}
            
            QSplitter::handle {{
                background-color: #444;
            }}
            
            QMessageBox {{
                background-color: #2D2D2D;
                color: white;
            }}
            
            QMessageBox QPushButton {{
                min-width: 80px;
            }}
            
            QToolBar {{
                background-color: #333;
                border: 1px solid #555;
                spacing: 3px;
            }}
            
            QToolBar QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 3px;
            }}
            
            QToolBar QToolButton:hover {{
                background-color: #444;
                border: 1px solid #666;
            }}
            
            QGroupBox {{
                border: 1px solid #555;
                border-radius: 3px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: white;
            }}
            
            QMenuBar {{
                background-color: #3D3D3D;
                color: white;
            }}
            
            QMenuBar::item {{
                background: transparent;
            }}
            
            QMenuBar::item:selected {{
                background: {primary_color};
            }}
            
            QMenu {{
                background-color: #3D3D3D;
                color: white;
                border: 1px solid #555;
            }}
            
            QMenu::item:selected {{
                background-color: {primary_color};
            }}
            
            QCheckBox {{
                color: white;
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {primary_color};
                border: 1px solid white;
            }}
            
            QRadioButton {{
                color: white;
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {primary_color};
                border: 1px solid white;
            }}
            
            QTextEdit {{
                background-color: #444;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
            }}
        """)
    
    def closeEvent(self, event):
        """Handle window close event - prompt to save project"""
        reply = QMessageBox.question(
            self, 'Exit Application',
            'Do you want to save your project before exiting?',
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )
        
        if reply == QMessageBox.Save:
            # Save project before exiting
            if self.project_controller.save_project(parent_widget=self):
                event.accept()
            else:
                # If save was cancelled, ask if user still wants to exit
                reply = QMessageBox.question(
                    self, 'Exit Application',
                    'Save cancelled. Exit anyway?',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    event.accept()
                else:
                    event.ignore()
        elif reply == QMessageBox.Discard:
            # Exit without saving
            event.accept()
        else:
            # Cancel exit
            event.ignore()