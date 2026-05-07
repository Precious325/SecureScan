from PIL import Image, ImageChops, ImageEnhance
import io
import os
import uuid


def perform_ela(file_path: str, reports_dir: str = "reports") -> dict:
    """
    Perform Error Level Analysis using only Pillow.
    No NumPy or OpenCV required.
    """
    try:
        original = Image.open(file_path).convert("RGB")

        # Re-compress at quality 90
        buffer = io.BytesIO()
        original.save(buffer, format="JPEG", quality=90)
        buffer.seek(0)
        recompressed = Image.open(buffer).convert("RGB")

        # Compute pixel difference
        diff = ImageChops.difference(original, recompressed)

        # Amplify by factor 15
        amplified = diff.point(lambda p: min(p * 15, 255))

        # Compute ELA score from histogram
        histogram = amplified.histogram()
        total_pixels = original.width * original.height * 3
        weighted_sum = sum(i * histogram[i] for i in range(256))
        ela_score = float(weighted_sum / (total_pixels * 255))

        # Enhance brightness for better visualization
        enhancer = ImageEnhance.Brightness(amplified)
        ela_enhanced = enhancer.enhance(2.0)

        # Save heatmap
        os.makedirs(reports_dir, exist_ok=True)
        heatmap_filename = f"ela_{uuid.uuid4().hex}.jpg"
        heatmap_path = os.path.join(reports_dir, heatmap_filename)
        ela_enhanced.save(heatmap_path, "JPEG", quality=95)

        suspicion_flag = ela_score > 0.15
        high_confidence = ela_score > 0.30

        return {
            "status": "success",
            "ela_score": round(ela_score, 4),
            "suspicion_flag": suspicion_flag,
            "high_confidence_manipulation": high_confidence,
            "heatmap_path": heatmap_path,
            "interpretation": get_ela_interpretation(ela_score)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "ela_score": 0.0,
            "suspicion_flag": False,
            "heatmap_path": None
        }


def perform_ela_on_pdf(file_path: str, reports_dir: str = "reports") -> dict:
    """Extract images from PDF and perform ELA on each."""
    try:
        import fitz

        doc = fitz.open(file_path)
        results = []

        for page_num in range(min(len(doc), 3)):
            page = doc[page_num]
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                os.makedirs("reports", exist_ok=True)
                temp_path = f"reports/temp_{uuid.uuid4().hex}.jpg"

                with open(temp_path, "wb") as f:
                    f.write(image_bytes)

                result = perform_ela(temp_path, reports_dir)
                result["page"] = page_num + 1
                result["image_index"] = img_index + 1
                results.append(result)
                os.remove(temp_path)

        doc.close()

        if not results:
            return {
                "status": "no_images",
                "message": "No embedded images found in PDF",
                "ela_score": 0.0,
                "suspicion_flag": False,
                "heatmap_path": None
            }

        return max(results, key=lambda x: x.get("ela_score", 0))

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "ela_score": 0.0,
            "suspicion_flag": False,
            "heatmap_path": None
        }


def get_ela_interpretation(score: float) -> str:
    if score < 0.05:
        return "Very low error level. Image appears unmodified."
    elif score < 0.15:
        return "Low error level. No strong indicators of manipulation detected."
    elif score < 0.30:
        return "Moderate error level detected. Possible manipulation in some regions."
    else:
        return "High error level detected. Strong indicators of pixel-level manipulation present."