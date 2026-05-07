import subprocess
import json
import os
from pathlib import Path

def extract_metadata(file_path: str) -> dict:
    """Extract all metadata from a document using ExifTool."""
    try:
        # Run ExifTool on the file
        exiftool_path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))), "exiftool.exe")
        
        result = subprocess.run(
            [exiftool_path, "-j", "-all", file_path],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode != 0:
            return {"error": "ExifTool failed to process file"}
        
        metadata_list = json.loads(result.stdout)
        return metadata_list[0] if metadata_list else {}
    
    except Exception as e:
        return {"error": str(e)}


def analyze_metadata(file_path: str, file_format: str) -> dict:
    """
    Analyze document metadata and detect forensic anomalies.
    Returns a structured result with all findings.
    """
    metadata = extract_metadata(file_path)
    
    if "error" in metadata:
        return {
            "status": "error",
            "message": metadata["error"],
            "anomalies": [],
            "suspicion_flag": False,
            "completeness_score": 0
        }
    
    anomalies = []
    
    # ── Rule MD-01: Missing CreationDate ─────────────────────────────────
    creation_date = metadata.get("CreateDate") or metadata.get("CreationDate")
    if not creation_date:
        anomalies.append({
            "rule_id": "MD-01",
            "field": "CreationDate",
            "observed": "ABSENT",
            "expected": "Date present in authentic documents",
            "interpretation": "Creation date is missing. This may indicate deliberate metadata stripping (anti-forensics).",
            "severity": "HIGH"
        })
    
    # ── Rule MD-02: ModDate before CreationDate ───────────────────────────
    mod_date = metadata.get("ModifyDate") or metadata.get("ModDate")
    if creation_date and mod_date:
        try:
            if mod_date < creation_date:
                anomalies.append({
                    "rule_id": "MD-02",
                    "field": "ModifyDate vs CreateDate",
                    "observed": f"Modified: {mod_date} | Created: {creation_date}",
                    "expected": "ModDate must be equal to or later than CreationDate",
                    "interpretation": "Modification date is earlier than creation date. This is logically impossible and indicates metadata falsification.",
                    "severity": "CRITICAL"
                })
        except Exception:
            pass
    
    # ── Rule MD-03: Creator vs Producer mismatch ──────────────────────────
    creator = metadata.get("Creator") or metadata.get("Application")
    producer = metadata.get("Producer") or metadata.get("PDFProducer")
    
    if creator and producer:
        creator_lower = creator.lower()
        producer_lower = producer.lower()
        
        editing_tools = ["acrobat", "smallpdf", "ilovepdf", "pdfescape", 
                        "sejda", "pdf24", "pdfcandy", "foxit"]
        
        producer_is_editor = any(tool in producer_lower for tool in editing_tools)
        creator_is_office = any(app in creator_lower for app in ["word", "excel", "libreoffice", "openoffice"])
        
        if creator_is_office and producer_is_editor:
            anomalies.append({
                "rule_id": "MD-03",
                "field": "Creator vs Producer",
                "observed": f"Creator: {creator} | Producer: {producer}",
                "expected": "Creator and Producer should match for unmodified documents",
                "interpretation": "Document was created in one application and later edited in a PDF editor — a common pattern in altered documents.",
                "severity": "MEDIUM"
            })
    
    # ── Rule MD-04: Producer is a PDF editing tool ────────────────────────
    if producer:
        editing_tools = ["acrobat", "smallpdf", "ilovepdf", "pdfescape",
                        "sejda", "pdf24", "pdfcandy", "foxit"]
        if any(tool in producer.lower() for tool in editing_tools):
            anomalies.append({
                "rule_id": "MD-04",
                "field": "Producer",
                "observed": producer,
                "expected": "Original authoring application",
                "interpretation": f"Document was processed by a PDF editing tool ({producer}). Warrants closer examination.",
                "severity": "LOW"
            })
    
    # ── Rule MD-05: EXIF Software is an image editor ──────────────────────
    software = metadata.get("Software") or metadata.get("ProcessingSoftware")
    if software:
        image_editors = ["photoshop", "gimp", "canva", "paint.net", 
                        "lightroom", "illustrator", "inkscape"]
        if any(editor in software.lower() for editor in image_editors):
            anomalies.append({
                "rule_id": "MD-05",
                "field": "Software",
                "observed": software,
                "expected": "Camera or document software",
                "interpretation": f"Image was processed using {software} — an image editing application. This is presumptive evidence of pixel-level manipulation.",
                "severity": "HIGH"
            })
    
    # ── Rule MD-06: Complete metadata absence ─────────────────────────────
    important_fields = ["CreateDate", "CreationDate", "ModifyDate", 
                       "Creator", "Producer", "Software", "Author"]
    present_fields = [f for f in important_fields if metadata.get(f)]
    
    if len(present_fields) == 0:
        anomalies.append({
            "rule_id": "MD-06",
            "field": "All metadata fields",
            "observed": "COMPLETELY ABSENT",
            "expected": "Standard metadata fields present",
            "interpretation": "All metadata is absent. This strongly suggests deliberate metadata stripping to hide evidence of tampering.",
            "severity": "HIGH"
        })
    
    # ── Compute completeness score ─────────────────────────────────────────
    completeness_score = round((len(present_fields) / len(important_fields)) * 100)
    
    # ── Determine suspicion flag ───────────────────────────────────────────
    high_severity = ["CRITICAL", "HIGH"]
    suspicion_flag = any(a["severity"] in high_severity for a in anomalies)
    
    return {
        "status": "success",
        "metadata": metadata,
        "anomalies": anomalies,
        "anomaly_count": len(anomalies),
        "suspicion_flag": suspicion_flag,
        "completeness_score": completeness_score
    }