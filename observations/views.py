import os
import sys
import tempfile
import torch
import numpy as np
from PIL import Image
from django.shortcuts import render
from django.http import FileResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Load YOLO model
def load_model():
    import pathlib
    import platform
    if platform.system() == 'Windows':
        pathlib.PosixPath = pathlib.WindowsPath

    model_path = os.path.join(settings.BASE_DIR, 'models', 'weapon.pt')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at: {model_path}")

    sys.path.append(os.path.join(settings.BASE_DIR, 'yolov5'))
    from models.common import DetectMultiBackend
    model = DetectMultiBackend(model_path, device='cpu')
    model.eval()
    return model

# Render upload page
def index(request):
    return render(request, 'observations/index.html')

# Generate PDF with user info and image only
@csrf_exempt
def generate_report(request):
    if request.method == 'POST':
        images = request.FILES.getlist('image')
        if len(images) != 1:
            return render(request, 'observations/index.html', {'error': 'Please upload exactly one image.'})

        image_file = images[0]

        # Collect user input
        authority = request.POST.get('authority', '')
        crime = request.POST.get('crime', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')

        # Load model
        model = load_model()
        stride = model.stride if isinstance(model.stride, int) else int(max(model.stride))
        imgsz = 640

        # Create PDF
        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        c = canvas.Canvas(pdf_file.name, pagesize=A4)
        width, height = A4

        # Add user info to PDF
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 800, "Crime Scene Observation Report")
        c.setFont("Helvetica", 12)
        y_offset = 770
        for line in [
            f"Official Authority: {authority}",
            f"Crime Type: {crime}",
            f"First Name: {first_name}",
            f"Last Name: {last_name}",
            f"Email: {email}"
        ]:
            c.drawString(100, y_offset, line)
            y_offset -= 20
        y_offset -= 10

        # Image processing
        img = Image.open(image_file).convert('RGB')
        img_np = np.array(img)

        from utils.augmentations import letterbox
        from utils.general import non_max_suppression, scale_boxes
        from utils.plots import Annotator

        img_resized = letterbox(img_np, new_shape=imgsz, stride=stride)[0]
        img_resized = img_resized.transpose((2, 0, 1))
        img_resized = np.ascontiguousarray(img_resized)

        img_tensor = torch.from_numpy(img_resized).float() / 255.0
        if img_tensor.ndimension() == 3:
            img_tensor = img_tensor.unsqueeze(0)

        with torch.no_grad():
            pred = model(img_tensor)
            pred = non_max_suppression(pred, conf_thres=0.25, iou_thres=0.45)

        annotator = Annotator(img_np.copy(), line_width=2)
        det = pred[0]

        if det is not None and len(det):
            det[:, :4] = scale_boxes(img_tensor.shape[2:], det[:, :4], img_np.shape).round()
            for *xyxy, conf, cls in det:
                label = f'{model.names[int(cls)]}'
                annotator.box_label(xyxy, f'{label} {conf:.2f}')

        # Save annotated image
        annotated_img = annotator.result()
        annotated_img_pil = Image.fromarray(annotated_img)
        temp_img_path = os.path.join(tempfile.gettempdir(), f"processed_{image_file.name}")
        annotated_img_pil.save(temp_img_path)

        # Add image to PDF
        c.drawImage(temp_img_path, 40, 100, width=500, preserveAspectRatio=True)
        c.save()

        return FileResponse(open(pdf_file.name, 'rb'), as_attachment=True, filename='CrimeScene_ImageReport.pdf')

    return render(request, 'observations/index.html')
