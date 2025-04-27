import torch
import torchvision.models as models  # or your custom model definition
from PIL import Image
import torchvision.transforms as transforms

import torch
import torchvision.models as models

def load_model(model_path):
    model = models.resnet18()
    num_ftrs = model.fc.in_features
    model.fc = torch.nn.Linear(num_ftrs, 1)

    checkpoint = torch.load(model_path, map_location='cpu')

    # Check if model is wrapped inside the checkpoint
    if isinstance(checkpoint, dict) and 'model' in checkpoint:
        state_dict = checkpoint['model']
    else:
        state_dict = checkpoint

    model.load_state_dict(state_dict, strict=False)
    model.eval()
    return model



def predict(image_path, model):
    image = Image.open(image_path).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    image_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        output = model(image_tensor)

    return output.tolist()
