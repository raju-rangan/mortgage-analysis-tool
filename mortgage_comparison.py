"""
Mortgage Comparison Module

This module provides functions for comparing multiple mortgage scenarios,
generating comparison tables, visualizing data, and exporting results.
"""

import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def compare_scenarios(scenarios):
    """
    Compare multiple mortgage scenarios and generate comparison metrics.
    
    Args:
        scenarios (list): List of MortgageScenario objects
        
    Returns:
        dict: Dictionary containing comparison metrics
    """
    if not scenarios:
        return {"error": "No scenarios provided"}
    
    comparison = {
        "scenarios": [],
        "metrics": {
            "monthly_payment": [],
            "total_interest": [],
            "total_cost": [],
            "equity_5yr": [],
            "equity_10yr": [],
            "equity_15yr": [],
            "break_even_point": []
        }
    }
    
    for scenario in scenarios:
        # Add scenario name
        comparison["scenarios"].append(scenario.name)
        
        # Calculate metrics
        monthly_payment = scenario.calculate_monthly_payment()
        total_interest = scenario.calculate_total_interest()
        total_cost = scenario.calculate_total_cost()
        equity_5yr = scenario.calculate_equity_at_year(5)
        equity_10yr = scenario.calculate_equity_at_year(10)
        equity_15yr = scenario.calculate_equity_at_year(15)
        break_even_point = scenario.calculate_break_even_point()
        
        # Add metrics to comparison
        comparison["metrics"]["monthly_payment"].append(monthly_payment)
        comparison["metrics"]["total_interest"].append(total_interest)
        comparison["metrics"]["total_cost"].append(total_cost)
        comparison["metrics"]["equity_5yr"].append(equity_5yr)
        comparison["metrics"]["equity_10yr"].append(equity_10yr)
        comparison["metrics"]["equity_15yr"].append(equity_15yr)
        comparison["metrics"]["break_even_point"].append(break_even_point)
    
    return comparison


def generate_comparison_table(comparison_data):
    """
    Generate a formatted comparison table for display.
    
    Args:
        comparison_data (dict): Comparison data from compare_scenarios()
        
    Returns:
        list: List of formatted table rows
    """
    if "error" in comparison_data:
        return [["Error", comparison_data["error"]]]
    
    # Create header row
    header = ["Metric"] + comparison_data["scenarios"]
    
    # Create rows for each metric
    rows = [header]
    
    # Format and add each metric
    rows.append(["Monthly Payment"] + [f"${payment:.2f}" for payment in comparison_data["metrics"]["monthly_payment"]])
    rows.append(["Total Interest"] + [f"${interest:.2f}" for interest in comparison_data["metrics"]["total_interest"]])
    rows.append(["Total Cost"] + [f"${cost:.2f}" for cost in comparison_data["metrics"]["total_cost"]])
    rows.append(["Equity (5 years)"] + [f"${equity:.2f}" for equity in comparison_data["metrics"]["equity_5yr"]])
    rows.append(["Equity (10 years)"] + [f"${equity:.2f}" for equity in comparison_data["metrics"]["equity_10yr"]])
    rows.append(["Equity (15 years)"] + [f"${equity:.2f}" for equity in comparison_data["metrics"]["equity_15yr"]])
    
    # Format break-even points
    break_even_row = ["Break-even Point"]
    for point in comparison_data["metrics"]["break_even_point"]:
        if point is None:
            break_even_row.append("N/A")
        else:
            years = int(point / 12)
            months = int(point % 12)
            break_even_row.append(f"{years}y {months}m")
    
    rows.append(break_even_row)
    
    return rows


def generate_payment_chart(scenarios, save_path=None):
    """
    Generate a chart showing payment breakdown over time for multiple scenarios.
    
    Args:
        scenarios (list): List of MortgageScenario objects
        save_path (str, optional): Path to save the chart image
        
    Returns:
        str or None: Path to the saved chart image, or None if display only
    """
    if not scenarios:
        return None
    
    # Create figure and axis
    plt.figure(figsize=(12, 8))
    
    # Plot each scenario
    for scenario in scenarios:
        # Generate amortization schedule
        rate = scenario.reduced_rate if scenario.reduced_rate is not None else scenario.interest_rate
        from mortgage_calculator import generate_amortization_schedule
        schedule = generate_amortization_schedule(scenario.loan_amount, rate, scenario.term_years)
        
        # Extract data for plotting
        payments = range(1, len(schedule) + 1)
        principal_payments = [payment["principal"] for payment in schedule]
        interest_payments = [payment["interest"] for payment in schedule]
        
        # Plot principal and interest over time
        plt.plot(payments, principal_payments, label=f"{scenario.name} - Principal")
        plt.plot(payments, interest_payments, linestyle='--', label=f"{scenario.name} - Interest")
    
    # Add labels and legend
    plt.title("Payment Breakdown Over Time")
    plt.xlabel("Payment Number")
    plt.ylabel("Amount ($)")
    plt.legend()
    plt.grid(True)
    
    # Save or display
    if save_path:
        plt.savefig(save_path)
        plt.close()
        return save_path
    else:
        plt.show()
        return None


def export_to_csv(comparison_data, filename):
    """
    Export comparison data to a CSV file.
    
    Args:
        comparison_data (dict): Comparison data from compare_scenarios()
        filename (str): Path to save the CSV file
        
    Returns:
        str: Path to the saved file
    """
    if "error" in comparison_data:
        return None
    
    # Generate table rows
    rows = generate_comparison_table(comparison_data)
    
    # Write to CSV
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in rows:
            writer.writerow(row)
    
    return filename


def export_to_pdf(comparison_data, scenarios, filename):
    """
    Export comparison data to a PDF file.
    
    Args:
        comparison_data (dict): Comparison data from compare_scenarios()
        scenarios (list): List of MortgageScenario objects
        filename (str): Path to save the PDF file
        
    Returns:
        str: Path to the saved file
    """
    if "error" in comparison_data:
        return None
    
    # Create PDF document
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Add title
    elements.append(Paragraph("Mortgage Comparison Report", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 24))
    
    # Add scenario details
    elements.append(Paragraph("Scenario Details", subtitle_style))
    elements.append(Spacer(1, 12))
    
    for scenario in scenarios:
        elements.append(Paragraph(f"<b>{scenario.name}</b>", normal_style))
        elements.append(Paragraph(f"Loan Amount: ${scenario.loan_amount:,.2f}", normal_style))
        elements.append(Paragraph(f"Interest Rate: {scenario.interest_rate:.2f}%", normal_style))
        elements.append(Paragraph(f"Term: {scenario.term_years} years", normal_style))
        elements.append(Paragraph(f"Down Payment: ${scenario.down_payment:,.2f}", normal_style))
        if scenario.points_paid > 0:
            elements.append(Paragraph(f"Points Paid: {scenario.points_paid:.2f}", normal_style))
            elements.append(Paragraph(f"Reduced Rate: {scenario.reduced_rate:.2f}%", normal_style))
        elements.append(Spacer(1, 12))
    
    elements.append(Spacer(1, 12))
    
    # Add comparison table
    elements.append(Paragraph("Comparison Table", subtitle_style))
    elements.append(Spacer(1, 12))
    
    # Generate table data
    table_data = generate_comparison_table(comparison_data)
    
    # Create table
    table = Table(table_data)
    
    # Style the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    table.setStyle(style)
    elements.append(table)
    elements.append(Spacer(1, 24))
    
    # Generate and add chart
    chart_path = os.path.join(os.path.dirname(filename), "payment_chart.png")
    generate_payment_chart(scenarios, chart_path)
    
    # Add chart to PDF
    elements.append(Paragraph("Payment Breakdown Chart", subtitle_style))
    elements.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(elements)
    
    # Clean up temporary chart file
    if os.path.exists(chart_path):
        os.remove(chart_path)
    
    return filename