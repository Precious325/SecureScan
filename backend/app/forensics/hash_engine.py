import hashlib
from sqlalchemy.orm import Session
from app.models.hash_template import HashTemplate

def compute_sha256(file_path: str) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    
    return sha256.hexdigest()


def verify_hash(file_path: str, db: Session) -> dict:
    """
    Compute document hash and compare against reference database.
    Returns match status and matched template details if found.
    """
    try:
        # Step 1: Compute hash
        document_hash = compute_sha256(file_path)
        
        # Step 2: Query database
        template = db.query(HashTemplate).filter(
            HashTemplate.sha256_hash == document_hash
        ).first()
        
        # Step 3: Determine result
        if template:
            return {
                "status": "success",
                "sha256_hash": document_hash,
                "match_status": "MATCH",
                "matched_institution": template.institution_name,
                "matched_document_type": template.document_type,
                "matched_description": template.document_description,
                "suspicion_flag": False,
                "interpretation": f"Document matches authenticated template from {template.institution_name}. Strong indicator of authenticity."
            }
        else:
            # Check if any templates exist at all
            total_templates = db.query(HashTemplate).count()
            
            if total_templates == 0:
                return {
                    "status": "success",
                    "sha256_hash": document_hash,
                    "match_status": "NOT_IN_DATABASE",
                    "matched_institution": None,
                    "matched_document_type": None,
                    "suspicion_flag": False,
                    "interpretation": "No reference templates in database yet. Hash verification not applicable. Add authenticated templates via the admin interface."
                }
            else:
                return {
                    "status": "success",
                    "sha256_hash": document_hash,
                    "match_status": "NO_MATCH",
                    "matched_institution": None,
                    "matched_document_type": None,
                    "suspicion_flag": True,
                    "interpretation": "Document hash does not match any authenticated template in the database. This is a strong forensic indicator of modification."
                }
    
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "sha256_hash": None,
            "match_status": "ERROR",
            "suspicion_flag": False
        }