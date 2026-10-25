"""
Generate synthetic demonstration medical reports and prescriptions using PyMuPDF.
Strictly synthetic demonstration data - NO real patient information.
"""
from pathlib import Path
import pymupdf


def generate_synthetic_samples():
    output_dir = Path(__file__).resolve().parent.parent / "data" / "sample_reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Synthetic Complete Blood Count (CBC) Report
    cbc_path = output_dir / "synthetic_cbc_report.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)  # A4 size
    cbc_text = (
        "METRO DIAGNOSTIC CLINICAL LABORATORIES\n"
        "SYNTHETIC DEMONSTRATION REPORT - NOT A REAL PATIENT\n"
        "--------------------------------------------------------------------------------\n"
        "Patient ID: DEMO-PATIENT-101          Date: 2026-10-24\n"
        "Age / Gender: 35 Y / M                Ref By: Dr. A. Demonstration, MD\n"
        "Specimen: Whole Blood EDTA            Collection Time: 08:30 AM\n"
        "--------------------------------------------------------------------------------\n"
        "TEST NAME                       RESULT    UNIT       REFERENCE RANGE    STATUS\n"
        "--------------------------------------------------------------------------------\n"
        "Hemoglobin                      13.5      g/dL       12.0 - 16.0        NORMAL\n"
        "WBC Count                       12.4      10^3/uL    4.5 - 11.0         HIGH\n"
        "Platelet Count                  240       10^3/uL    150 - 450          NORMAL\n"
        "RBC Count                       4.8       10^6/uL    4.3 - 5.9          NORMAL\n"
        "Hematocrit                      41.2      %          38.0 - 50.0        NORMAL\n"
        "--------------------------------------------------------------------------------\n"
        "End of Laboratory Report\n"
        "Educational Prototype Use Only."
    )
    page.insert_text((50, 70), cbc_text, fontsize=10, fontname="courier")
    doc.save(str(cbc_path))
    doc.close()
    print(f"Created: {cbc_path}")

    # 2. Synthetic Report with MISSING Reference Ranges (to verify requirement: missing ranges stay missing)
    missing_range_path = output_dir / "synthetic_missing_ranges_report.pdf"
    doc2 = pymupdf.open()
    page2 = doc2.new_page(width=595, height=842)
    missing_text = (
        "CITY OUTPATIENT LAB - SYNTHETIC DATA\n"
        "--------------------------------------------------------------------------------\n"
        "Patient ID: DEMO-PATIENT-202          Date: 2026-10-24\n"
        "--------------------------------------------------------------------------------\n"
        "TEST NAME                       RESULT    UNIT\n"
        "--------------------------------------------------------------------------------\n"
        "Serum Creatinine                1.4       mg/dL\n"
        "Fasting Blood Glucose           135       mg/dL\n"
        "Total Cholesterol               215       mg/dL\n"
        "--------------------------------------------------------------------------------\n"
        "Note: Reference ranges unavailable for this assay profile.\n"
    )
    page2.insert_text((50, 70), missing_text, fontsize=10, fontname="courier")
    doc2.save(str(missing_range_path))
    doc2.close()
    print(f"Created: {missing_range_path}")

    # 3. Synthetic Prescription
    presc_path = output_dir / "synthetic_prescription.pdf"
    doc3 = pymupdf.open()
    page3 = doc3.new_page(width=595, height=842)
    presc_text = (
        "HEALTHCARE MEDICAL CENTER\n"
        "PRESCRIPTION - SYNTHETIC DEMONSTRATION RECORD\n"
        "--------------------------------------------------------------------------------\n"
        "Prescriber: Dr. Elena Vance, MD       Date: 2026-10-24\n"
        "Patient: Synthetic Test Subject       Age: 40\n"
        "--------------------------------------------------------------------------------\n"
        "Rx:\n\n"
        "1. Tab Amoxicillin 500mg - 1 tablet TID for 7 days PO\n\n"
        "2. Paracetamol 650mg - 1 tablet as needed for fever PO\n\n"
        "3. UnknownMed? 10?? - Once daily\n\n"
        "--------------------------------------------------------------------------------\n"
        "Signature: Dr. E. Vance, MD\n"
    )
    page3.insert_text((50, 70), presc_text, fontsize=10, fontname="courier")
    doc3.save(str(presc_path))
    doc3.close()
    print(f"Created: {presc_path}")

    # 4. Synthetic PNG Image of CBC Report
    img_doc = pymupdf.open(str(cbc_path))
    img_page = img_doc[0]
    pix = img_page.get_pixmap(dpi=150)
    png_path = output_dir / "synthetic_cbc_image.png"
    pix.save(str(png_path))
    img_doc.close()
    print(f"Created: {png_path}")


if __name__ == "__main__":
    generate_synthetic_samples()
