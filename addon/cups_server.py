from flask import Flask, jsonify, request
import cups
import json
import tempfile
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch, mm, cm
from reportlab.pdfgen import canvas
import datetime

app = Flask(__name__)

CUPS_HOST = None
CUPS_PORT = None

try:
    with open("/data/options.json", "r") as f:
        options = json.load(f)
        CUPS_HOST = options.get("cups_host", "192.168.178.65")
        CUPS_PORT = options.get("cups_port", 631)
except Exception as e:
    print(e)

conn = cups.Connection(host=CUPS_HOST, port=CUPS_PORT)

@app.route("/printers", methods=["GET"])
def list_printers():
    printers = conn.getPrinters()
    printer_list = [{"name": name, "info": info.get("printer-info", "")} for name, info in printers.items()]
    return jsonify(printer_list)

@app.route("/print_test", methods=["POST"])
def print_test():
    data = request.json
    printer_name = data.get("printer")
    
    if not printer_name:
        return jsonify({"success": False, "error": "Printer not specified"}), 400
    
    try:
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            temp_file = f.name
        
        # Create PDF with colors
        c = canvas.Canvas(temp_file, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, height - 1*inch, "Printer Test Page")
        
        # Info section
        c.setFont("Helvetica", 10)
        y_pos = height - 1.5*inch
        c.drawString(1*inch, y_pos, f"Printer: {printer_name}")
        c.drawString(1*inch, y_pos - 0.2*inch, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(1*inch, y_pos - 0.4*inch, "Source: Home Assistant CUPS Add-on")
        
        # Color Test Section
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.black)
        y_pos = height - 2.5*inch
        c.drawString(1*inch, y_pos, "Color Test")
        
        # Define test colors
        test_colors = [
            ("Black", colors.black),
            ("Red", colors.red),
            ("Green", colors.green),
            ("Blue", colors.blue),
            ("Cyan", colors.cyan),
            ("Magenta", colors.magenta),
            ("Yellow", colors.yellow),
        ]
        
        # Color Bars Section
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.black)
        y_pos -= 0.5*inch
        c.drawString(1*inch, y_pos, "Color Bars")
        
        # Draw color bars
        y_pos -= 0.4*inch
        bar_width = (width - 5*inch) / len(test_colors)
        x_start = 1*inch
        
        for i, (color_name, color_obj) in enumerate(test_colors):
            c.setFillColor(color_obj)
            c.rect(x_start + i*bar_width, y_pos, bar_width, 0.3*inch, fill=1, stroke=0)
        
        # Footer message
        y_pos -= 1*inch
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, y_pos, 
            "If you can see all colors clearly, your printer is working correctly!")
        
        # Save PDF
        c.save()
        
        try:
            # Print the PDF file
            job_id = conn.printFile(printer_name, temp_file, "Color Test Page", {})
            return jsonify({
                "success": True, 
                "printer": printer_name,
                "job_id": job_id,
                "message": "Color test page sent to printer"
            })
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
                
    except cups.IPPError as e:
        return jsonify({
            "success": False, 
            "error": f"CUPS IPP Error: {str(e)}",
            "error_code": e.args[0] if e.args else None
        }), 500
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": str(e),
            "error_type": type(e).__name__
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)