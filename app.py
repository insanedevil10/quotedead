"""
Interior Design Quote Tool - Main Application

This module sets up the application with MVC architecture and runs the main window.
"""
import sys
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

# Import models
from models.project import Project
from models.rate_card import RateCard
from models.company import Company

# Import controllers
from controllers.project_controller import ProjectController
from controllers.calculation_controller import CalculationController
from controllers.rate_card_controller import RateCardController
from controllers.export_controller import ExportController

# Import views
from views.main_window import MainWindow

def check_assets():
    """Check if required assets are available"""
    assets_status = Company.check_logo_files()
    
    if not (assets_status["full_logo_exists"] and assets_status["compact_logo_exists"]):
        # Show warning message
        message = (
            "Some logo files are missing. Running in logo-less mode.\n\n"
            f"Full Logo Path: {assets_status['full_logo_path']}\n"
            f"Compact Logo Path: {assets_status['compact_logo_path']}\n\n"
            "The application will continue without logo files."
        )
        QMessageBox.warning(None, "Missing Assets", message)
        return False
    
    return True

def main():
    """Main application entry point"""
    # Create application
    app = QApplication(sys.argv)
    
    # Check for required assets
    assets_available = check_assets()
    
    # Show splash screen with logo if available
    if assets_available:
        splash_pixmap = QPixmap(Company.get_logo_path())
    else:
        # Use fallback if logo can't be loaded
        splash_pixmap = QPixmap(400, 200)
        splash_pixmap.fill(Qt.white)
    
    splash = QSplashScreen(splash_pixmap)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
    splash.show()
    # Use dark text on white background
    splash.showMessage(f"Loading {Company.COMPANY_NAME} Quote Tool...", 
                       Qt.AlignBottom | Qt.AlignCenter, Qt.black)
                       
    # Process events to show the splash screen
    app.processEvents()
    
    # ---- Initialize Models ----
    project_model = Project()
    rate_card_model = RateCard()
    
    # ---- Initialize Controllers ----
    project_controller = ProjectController(project_model)
    calculation_controller = CalculationController(project_model)
    rate_card_controller = RateCardController(rate_card_model)
    export_controller = ExportController(project_model, calculation_controller)
    
    # ---- Initialize Main Window ----
    window = MainWindow(
        project_controller,
        calculation_controller,
        rate_card_controller,
        export_controller
    )
    
    # Close splash screen and show main window after a delay
    QTimer.singleShot(1500, splash.close)
    QTimer.singleShot(1500, window.show)
    
    # Run application
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())