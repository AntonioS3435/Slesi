import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, random_split
import copy
import random
import numpy as np

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

# Establecer la semilla global para garantizar la reproducibilidad
set_seed(42)

class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        # Capa 1: Entrada 3 canales (RGB), salida 32 filtros. Imagen 32x32 -> 16x16 tras pooling
        self.layer1 = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        # Capa 2: Entrada 32, salida 64. Imagen 16x16 -> 8x8 tras pooling
        self.layer2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        # Capa 3: Entrada 64, salida 64. Imagen 8x8 -> 4x4 tras pooling
        self.layer3 = nn.Sequential(
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        # Clasificador: 64 filtros de 4x4 = 1024 neuronas de entrada
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 4 * 4, 512),
            nn.ReLU(),
            nn.Linear(512, 10) # 10 clases de CIFAR-10
        )

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.fc(x)
        return x

# 1. Definición del Hardware (Esto define 'device')
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 2. Carga de CIFAR-10 y creación de Dataloaders (Esto define 'testloader' y 'client_loaders')
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.4914, 0.4822, 0.4465], std=[0.2023, 0.1994, 0.201])
])

trainset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
testset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=transform)
testloader = DataLoader(testset, batch_size=100, shuffle=False)

# 3. Partición de datos para 5 clientes
num_clients = 5
partition_size = len(trainset) // num_clients
partitions = random_split(trainset, [partition_size] * num_clients)
# Cada client loader tiene una partición disjunta de los datos.
client_loaders = [DataLoader(part, batch_size=64, shuffle=True) for part in partitions]

# 4. Instanciación de Modelos (Esto define 'global_model' y 'local_models')
# Asegúrate de haber ejecutado la celda de la clase SimpleCNN antes que esta
global_model = SimpleCNN().to(device)
local_models = [SimpleCNN().to(device) for _ in range(num_clients)]

print(f"Entorno listo en {device}. Datos cargados y modelos instanciados.")
client_loaders = [DataLoader(part, batch_size=64, shuffle=True) for part in partitions]

def train_local(model, train_loader, epochs=1, lr=0.01):
    model.train()
    criterion = nn.CrossEntropyLoss()
    # Importante: Usamos SGD local para cada cliente
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9)
    
    for epoch in range(epochs):
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
    
    # Devolvemos el estado del modelo (pesos)
    return model.state_dict()

def federated_averaging(local_weights):
    # Usamos el primer cliente como base para la estructura del dict
    avg_weights = copy.deepcopy(local_weights[0])
    
    for key in avg_weights.keys():
        for i in range(1, len(local_weights)):
            avg_weights[key] += local_weights[i][key]
        # Promedio simple ya que las particiones son IID y del mismo tamaño
        avg_weights[key] = torch.div(avg_weights[key], len(local_weights))
    
    return avg_weights

def evaluate_model(model, test_loader):
    model.eval() # Ponemos el modelo en modo evaluación (desactiva Dropout/BatchNorm)
    correct = 0
    total = 0
    
    # Desactivamos el cálculo de gradientes para ahorrar memoria y tiempo
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
    accuracy = 100 * correct / total
    return accuracy

