"""
Dashboard View - Handles the visualization and statistics dashboard
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSpinBox, QGroupBox, QFormLayout, QTreeWidget, 
                             QTreeWidgetItem, QTabWidget, QSplitter, QPushButton, 
                             QCheckBox, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPainter
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis

class DashboardView(QWidget):
    """View for project dashboard with visualizations and statistics"""
    
    def __init__(self, project_controller, calculation_controller):
        """Initialize with controllers"""
        super().__init__()
        
        self.project_controller = project_controller
        self.calculation_controller = calculation_controller
        
        self.init_ui()
        
        # Register for updates from the model (via controller)
        self.project_controller.register_view(self)
        
        # Load initial data
        self.update_from_model()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Add chart display
        charts_group = QGroupBox("Project Visualization")
        charts_layout = QVBoxLayout(charts_group)
        
        # Tab widget for different types of charts
        self.chart_tabs = QTabWidget()
        charts_layout.addWidget(self.chart_tabs)
        
        # Room cost distribution chart (pie chart)
        self.room_cost_view = QChartView()
        self.room_cost_view.setRenderHint(QPainter.Antialiasing)
        self.chart_tabs.addTab(self.room_cost_view, "Room Cost Distribution")
        
        # Item type distribution chart (bar chart)
        self.item_breakdown_view = QChartView()
        self.item_breakdown_view.setRenderHint(QPainter.Antialiasing)
        self.chart_tabs.addTab(self.item_breakdown_view, "Item Breakdown")
        
        # Add charts group to main layout
        layout.addWidget(charts_group)
        
        # Create a splitter for the bottom half
        bottom_splitter = QSplitter(Qt.Horizontal)
        
        # Summary panel (left side)
        summary_group = QGroupBox("Quote Summary")
        summary_layout = QFormLayout(summary_group)
        
        # Room-wise cost tree
        self.room_tree = QTreeWidget()
        self.room_tree.setHeaderLabels(["Room/Item", "Amount (₹)"])
        self.room_tree.setColumnWidth(0, 400)
        summary_layout.addRow(self.room_tree)
        
        # GST and Discount controls
        totals_layout = QHBoxLayout()
        
        self.subtotal_label = QLabel("₹0.00")
        self.subtotal_label.setFont(QFont("Arial", 10, QFont.Bold))
        totals_layout.addWidget(QLabel("Subtotal:"))
        totals_layout.addWidget(self.subtotal_label)
        
        # GST
        gst_layout = QHBoxLayout()
        gst_layout.addWidget(QLabel("GST (%):"))
        self.gst_spin = QSpinBox()
        self.gst_spin.setRange(0, 100)
        self.gst_spin.setValue(18)  # Default 18%
        self.gst_spin.valueChanged.connect(self.update_settings)
        gst_layout.addWidget(self.gst_spin)
        
        self.gst_amount_label = QLabel("₹0.00")
        gst_layout.addWidget(self.gst_amount_label)
        totals_layout.addLayout(gst_layout)
        
        # Discount
        discount_layout = QHBoxLayout()
        discount_layout.addWidget(QLabel("Discount (%):"))
        self.discount_spin = QSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.setValue(0)  # Default 0%
        self.discount_spin.valueChanged.connect(self.update_settings)
        discount_layout.addWidget(self.discount_spin)
        
        self.discount_amount_label = QLabel("₹0.00")
        discount_layout.addWidget(self.discount_amount_label)
        totals_layout.addLayout(discount_layout)
        
        summary_layout.addRow(totals_layout)
        
        # Grand Total
        grand_total_layout = QHBoxLayout()
        grand_total_layout.addWidget(QLabel("Grand Total:"))
        self.grand_total_label = QLabel("₹0.00")
        self.grand_total_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.grand_total_label.setStyleSheet("color: #C62828;")
        grand_total_layout.addWidget(self.grand_total_label)
        
        summary_layout.addRow(grand_total_layout)
        
        # Stats panel (right side)
        stats_group = QGroupBox("Project Statistics")
        stats_layout = QFormLayout(stats_group)
        
        # Overall project metrics
        self.total_rooms_label = QLabel("0")
        stats_layout.addRow("Total Rooms:", self.total_rooms_label)
        
        self.total_items_label = QLabel("0")
        stats_layout.addRow("Total Line Items:", self.total_items_label)
        
        self.avg_room_cost_label = QLabel("₹0.00")
        stats_layout.addRow("Average Room Cost:", self.avg_room_cost_label)
        
        self.avg_item_cost_label = QLabel("₹0.00")
        stats_layout.addRow("Average Item Cost:", self.avg_item_cost_label)
        
        self.highest_cost_room_label = QLabel("None")
        stats_layout.addRow("Highest Cost Room:", self.highest_cost_room_label)
        
        self.highest_cost_item_label = QLabel("None")
        stats_layout.addRow("Highest Cost Item:", self.highest_cost_item_label)
        
        # Add groups to splitter
        bottom_splitter.addWidget(summary_group)
        bottom_splitter.addWidget(stats_group)
        bottom_splitter.setSizes([600, 400])
        
        # Add splitter to main layout
        layout.addWidget(bottom_splitter)
        
        # Chart options
        chart_options_layout = QHBoxLayout()
        
        # Visualization options
        self.show_percentages = QCheckBox("Show Percentages")
        self.show_percentages.setChecked(True)
        self.show_percentages.stateChanged.connect(self.update_from_model)
        chart_options_layout.addWidget(self.show_percentages)
        
        # Chart sort
        chart_options_layout.addWidget(QLabel("Sort By:"))
        self.sort_type = QComboBox()
        self.sort_type.addItems(["Value (Descending)", "Value (Ascending)", "Name"])
        self.sort_type.currentIndexChanged.connect(self.update_from_model)
        chart_options_layout.addWidget(self.sort_type)
        
        # Add refresh button
        refresh_btn = QPushButton("Refresh Dashboard")
        refresh_btn.clicked.connect(self.update_from_model)
        chart_options_layout.addWidget(refresh_btn)
        
        layout.addLayout(chart_options_layout)
        
        # Add description at the bottom
        description = QLabel("This dashboard shows visualizations and statistics for your project.")
        description.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(description)
    
    def update_settings(self):
        """Update project settings (GST and discount)"""
        # Update settings in project controller
        self.project_controller.update_settings({
            "gst": self.gst_spin.value(),
            "discount": self.discount_spin.value()
        })
        
        # Update dashboard
        self.update_from_model()
    
    def update_from_model(self):
        """Update UI from model data via controller"""
        # Clear tree
        self.room_tree.clear()
        
        # Get line items
        line_items = self.project_controller.get_line_items()
        
        # Calculate room-wise totals
        room_totals = self.calculation_controller.calculate_room_totals()
        
        # Build tree structure
        subtotal = 0
        for room, total in room_totals.items():
            # Add room as parent
            room_item = QTreeWidgetItem([room, f"₹{total:.2f}"])
            self.room_tree.addTopLevelItem(room_item)
            
            # Add line items as children
            room_items = [item for item in line_items if item["room"] == room]
            for item in room_items:
                child = QTreeWidgetItem([item["item"], f"₹{item['amount']:.2f}"])
                room_item.addChild(child)
            
            # Expand by default
            room_item.setExpanded(True)
            
            # Add to subtotal
            subtotal += total
        
        # Update totals
        self.subtotal_label.setText(f"₹{subtotal:.2f}")
        
        # Get settings
        settings = self.project_controller.get_settings()
        gst_percent = settings.get("gst", 18)
        discount_percent = settings.get("discount", 0)
        
        # Set spin values without triggering signals
        self.gst_spin.blockSignals(True)
        self.gst_spin.setValue(gst_percent)
        self.gst_spin.blockSignals(False)
        
        self.discount_spin.blockSignals(True)
        self.discount_spin.setValue(discount_percent)
        self.discount_spin.blockSignals(False)
        
        # Calculate amounts
        gst_amount = self.calculation_controller.calculate_gst()
        self.gst_amount_label.setText(f"₹{gst_amount:.2f}")
        
        discount_amount = self.calculation_controller.calculate_discount()
        self.discount_amount_label.setText(f"₹{discount_amount:.2f}")
        
        grand_total = self.calculation_controller.calculate_grand_total()
        self.grand_total_label.setText(f"₹{grand_total:.2f}")
        
        # Update charts
        self.update_pie_chart(room_totals)
        self.update_bar_chart()
        
        # Update statistics
        self.update_statistics()
    
    def update_pie_chart(self, room_totals):
        """Update the room distribution pie chart"""
        # Create new pie series
        pie_series = QPieSeries()
        
        # Get sort option
        sort_option = self.sort_type.currentText()
        
        # Sort rooms based on selection
        items = list(room_totals.items())
        if sort_option == "Value (Descending)":
            items.sort(key=lambda x: x[1], reverse=True)
        elif sort_option == "Value (Ascending)":
            items.sort(key=lambda x: x[1])
        elif sort_option == "Name":
            items.sort(key=lambda x: x[0])
        
        # Add slices to the pie series
        total_sum = sum(room_totals.values())
        for room, amount in items:
            slice = pie_series.append(room, amount)
            
            # Calculate percentage
            percentage = (amount / total_sum) * 100 if total_sum > 0 else 0
            
            # Set slice label with percentage if enabled
            if self.show_percentages.isChecked():
                slice.setLabel(f"{room}: ₹{amount:.2f} ({percentage:.1f}%)")
            else:
                slice.setLabel(f"{room}: ₹{amount:.2f}")
            
            # Make slice exploded if it's the largest
            if amount == max(room_totals.values()):
                slice.setExploded(True)
                slice.setLabelVisible(True)
        
        # Create the chart
        chart = QChart()
        chart.addSeries(pie_series)
        chart.setTitle("Room Cost Distribution")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        # Set style
        chart.setTheme(QChart.ChartThemeDark)
        
        # Set the chart on the view
        self.room_cost_view.setChart(chart)
    
    def update_bar_chart(self):
        """Update the item breakdown bar chart"""
        # Get breakdown by UOM (or other categorization)
        breakdown = self.calculation_controller.get_item_breakdown_by_type()
        
        # Get sort option
        sort_option = self.sort_type.currentText()
        
        # Sort categories based on selection
        items = list(breakdown.items())
        if sort_option == "Value (Descending)":
            items.sort(key=lambda x: x[1], reverse=True)
        elif sort_option == "Value (Ascending)":
            items.sort(key=lambda x: x[1])
        elif sort_option == "Name":
            items.sort(key=lambda x: x[0])
        
        # Create bar set
        bar_set = QBarSet("Amount (₹)")
        
        # Add values to bar set
        for _, amount in items:
            bar_set.append(amount)
        
        # Create bar series
        bar_series = QBarSeries()
        bar_series.append(bar_set)
        
        # Create chart
        chart = QChart()
        chart.addSeries(bar_series)
        chart.setTitle("Item Category Breakdown")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Create axes
        axis_x = QBarCategoryAxis()
        categories = [item[0] for item in items]
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        bar_series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("Amount (₹)")
        chart.addAxis(axis_y, Qt.AlignLeft)
        bar_series.attachAxis(axis_y)
        
        # Set style
        chart.setTheme(QChart.ChartThemeDark)
        chart.legend().setVisible(False)
        
        # Set the chart on the view
        self.item_breakdown_view.setChart(chart)
    
    def update_statistics(self):
        """Update project statistics"""
        # Get project statistics from calculation controller
        stats = self.calculation_controller.calculate_project_statistics()
        
        # Update labels
        self.total_rooms_label.setText(str(stats["total_rooms"]))
        self.total_items_label.setText(str(stats["total_items"]))
        
        self.avg_room_cost_label.setText(f"₹{stats['avg_room_cost']:.2f}")
        self.avg_item_cost_label.setText(f"₹{stats['avg_item_cost']:.2f}")
        
        highest_room = stats["highest_cost_room"]
        if highest_room["name"] != "None":
            self.highest_cost_room_label.setText(f"{highest_room['name']} (₹{highest_room['amount']:.2f})")
        else:
            self.highest_cost_room_label.setText("None")
        
        highest_item = stats["highest_cost_item"]
        if highest_item["name"] != "None":
            self.highest_cost_item_label.setText(
                f"{highest_item['name']} in {highest_item['room']} (₹{highest_item['amount']:.2f})"
            )
        else:
            self.highest_cost_item_label.setText("None")