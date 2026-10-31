import torch 
import torchvision.models as models
from PIL import Image
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader
from torchvision.transforms import InterpolationMode
import os
import pandas as pd
import numpy as np
import torchvision.transforms.functional as functional

#-----------------
#| DATASET CLASS |
#-----------------

# Custom image dataset class as defined in https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html
class CustomImageDataset(Dataset):
    def __init__(self, annotations_file, img_dir, transform=None, target_transform=None):
        self.img_labels = pd.read_csv(annotations_file)
        self.img_dir = img_dir
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.img_labels)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.img_labels.iloc[idx, 0])

        image = Image.open(img_path).convert("RGB")
        label = self.img_labels.iloc[idx, 1]

        if self.transform:
            image = self.transform(image)
        if self.target_transform:
            label = self.target_transform(label)
        
        return image, label

#--------------------
#| HELPER FUNCTIONS |
#--------------------

class PadToSquare:
    def __call__(self, img):
        w, h = img.size
        new_size = max(w, h)
        # background estimate from the border pixels
        pixels_arr = np.asarray(img)
        border = np.concatenate([pixels_arr[0], pixels_arr[-1], pixels_arr[:, 0], pixels_arr[:, -1]])
        # Average 
        padding_fill = tuple(int(v) for v in np.median(border, axis=0))

        pl, pt = (new_size - w) // 2, (new_size - h) // 2
        return functional.pad(img, [pl, pt, new_size - w - pl, new_size - h - pt], fill=padding_fill)

#--------------------
#| ALEXNET TRAINING |
#--------------------

def train_alexnet(
    train_dir,
    val_dir,
    num_classes=7,
    batch_size=1,
    num_epochs=5,
    learning_rate=0.0001,
    translate_value = 0.08,
    color_jitter_value = 0.3,
):
    # Image processing for AlexNet Input
    preprocess_val = transforms.Compose([
        PadToSquare(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    preprocess_train = transforms.Compose([
        # Transforms into ALexNet expected input size
        PadToSquare(),
        transforms.Resize((224, 224)),
        # Data augmentation
        transforms.RandomAffine(
            degrees=0,
            translate=(translate_value, translate_value),
            #scale=(0.85, 1.1),
            interpolation=InterpolationMode.BILINEAR
            fill=255
        ),
        transforms.ColorJitter(brightness=color_jitter_value, contrast=color_jitter_value),
        #transforms.RandomApply([transforms.GaussianBlur(5, sigma=(0.1, 1.5))], p=0.3),
        # Appropriates image for Pytorch
        transforms.ToTensor(),
        # Appropriates image for AlexNet pre-trained weights
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),

    ])

    # Datasets
    train_data = CustomImageDataset(
        annotations_file = os.path.join(train_dir, "labels.csv"),
        img_dir = train_dir,
        transform = preprocess_train
    )

    val_data = CustomImageDataset(
        annotations_file = os.path.join(val_dir, "labels.csv"),
        img_dir = val_dir,
        transform = preprocess_val
    )

    # DataLoaders
    train_dataloader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
    val_dataloader = DataLoader(val_data, batch_size=batch_size, shuffle=False)

    # Load AlexNet
    alexnet = models.alexnet(weights=models.AlexNet_Weights.IMAGENET1K_V1)

    # Resize of output layer as defined in https://deploy-preview-646--pytorch-tutorials-preview.netlify.app/beginner/finetuning_torchvision_models_tutorial
    alexnet.classifier[6] = torch.nn.Linear(
        alexnet.classifier[6].in_features,
        num_classes
    )

    # Loss function
    criterion = torch.nn.CrossEntropyLoss()

    # Optimizer function 
    optimizer = torch.optim.Adam(
        alexnet.parameters(),
        lr=learning_rate
    )

    # Select the device
    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    alexnet.to(device)

    # Results
    results = {
        "train_loss": [],
        "train_accuracy": [],
        "val_loss": [],
        "val_accuracy": []
    }

    # Epoch Loop
    for epoch in range(num_epochs):
        #Training
        alexnet.train()

        running_loss = 0.0
        train_correct = 0
        total = 0

        for images, labels in train_dataloader:

            images = images.to(device)
            labels = labels.to(device, dtype=torch.long)

            # Zero the parameter gradients
            optimizer.zero_grad()

            # Forward pass
            outputs = alexnet(images)

            # Calculate the loss
            loss = criterion(outputs, labels)

            # Backpropagation
            loss.backward()

            # Update the model weights
            optimizer.step()

            running_loss += loss.item()

            # Calculate training accuracy
            predictions = outputs.argmax(dim=1)

            train_correct += (predictions == labels).sum().item()
            total += labels.size(0)

        train_loss = running_loss / len(train_dataloader)
        train_accuracy = train_correct / total

        #Validation
        alexnet.eval()

        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():

            for images, labels in val_dataloader:

                images = images.to(device)
                labels = labels.to(device, dtype=torch.long)

                outputs = alexnet(images)

                loss = criterion(outputs, labels)

                val_loss += loss.item()

                predictions = outputs.argmax(dim=1)

                val_correct += (predictions == labels).sum().item()
                val_total += labels.size(0)

        avg_val_loss = val_loss / len(val_dataloader)
        val_accuracy = val_correct / val_total

        # Results
        results["train_loss"].append(train_loss)
        results["train_accuracy"].append(train_accuracy)
        results["val_loss"].append(avg_val_loss)
        results["val_accuracy"].append(val_accuracy)


        # Print Results

        print(f"\nEpoch [{epoch + 1}/{num_epochs}]")

        print(f"Training Loss: {train_loss:.4f}")
        print(f"Training Accuracy: {train_accuracy:.4f}")

        print(f"Validation Loss: {avg_val_loss:.4f}")
        print(f"Validation Accuracy: {val_accuracy:.4f}")

    return alexnet, results