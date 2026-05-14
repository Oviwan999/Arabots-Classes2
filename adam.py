import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, utils
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np

# 1. Configuración del Entorno y Dispositivo (CUDA para tu 4070)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Usando dispositivo: {device}")

# 2. Preparación de Datos (MNIST)
# Normalizamos a (-1, 1) para que coincida con la activación Tanh del generador
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

train_data = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
train_loader = DataLoader(train_data, batch_size=128, shuffle=True)


# 3. Arquitectura del Modelo
class Generator(nn.Module):
    def __init__(self, z_dim, img_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(z_dim, 256),
            nn.LeakyReLU(0.2),  # LeakyReLU ayuda a evitar gradientes moribundos
            nn.Linear(256, 512),
            nn.LeakyReLU(0.2),
            nn.Linear(512, img_dim),
            nn.Tanh()  # Salida en rango [-1, 1]
        )

    def forward(self, x):
        return self.net(x).view(-1, 1, 28, 28)


class Discriminator(nn.Module):
    def __init__(self, img_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(img_dim, 512),
            nn.LeakyReLU(0.2),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 1),
            nn.Sigmoid()  # Salida de probabilidad [0, 1]
        )

    def forward(self, x):
        return self.net(x.view(-1, 28 * 28))


# 4. Hiperparámetros e Inicialización
z_dim = 100
image_dim = 28 * 28 * 1
lr = 0.0002

G = Generator(z_dim, image_dim).to(device)
D = Discriminator(image_dim).to(device)

criterion = nn.BCELoss()  # Binary Cross Entropy Loss
opt_G = optim.Adam(G.parameters(), lr=lr)
opt_D = optim.Adam(D.parameters(), lr=lr)

# 5. Bucle de Entrenamiento
losses_G = []
losses_D = []
epochs = 20  # Puedes aumentarlo para mejores resultados

print("Iniciando entrenamiento...")
for epoch in range(epochs):
    for i, (real, _) in enumerate(train_loader):
        real = real.to(device)
        batch_size = real.size(0)

        # Etiquetas
        label_real = torch.ones(batch_size, 1).to(device)
        label_fake = torch.zeros(batch_size, 1).to(device)

        # --- Entrenar Discriminador ---
        opt_D.zero_grad()

        # Pérdida con imágenes reales
        pred_real = D(real)
        loss_real = criterion(pred_real, label_real)

        # Pérdida con imágenes falsas
        noise = torch.randn(batch_size, z_dim).to(device)
        fake = G(noise)
        pred_fake = D(fake.detach())  # .detach() para no afectar gradientes de G
        loss_fake = criterion(pred_fake, label_fake)

        loss_D = loss_real + loss_fake
        loss_D.backward()
        opt_D.step()

        # --- Entrenar Generador ---
        opt_G.zero_grad()

        # Queremos que D crea que las fakes son reales
        output = D(fake)
        loss_G = criterion(output, label_real)

        loss_G.backward()
        opt_G.step()

    # Guardar pérdidas por época
    losses_D.append(loss_D.item())
    losses_G.append(loss_G.item())
    print(f'Epoch [{epoch + 1}/{epochs}] - Loss D: {loss_D.item():.4f}, Loss G: {loss_G.item():.4f}')


# 6. Evaluación y Visualización
def show_samples(generator, n_samples=16):
    generator.eval()
    with torch.no_grad():
        noise = torch.randn(n_samples, z_dim).to(device)
        samples = generator(noise).cpu()
        grid = utils.make_grid(samples, nrow=4, normalize=True)
        plt.figure(figsize=(6, 6))
        plt.imshow(np.transpose(grid, (1, 2, 0)))
        plt.axis('off')
        plt.title("Imágenes Generadas")
        plt.show()


# Mostrar resultados finales
show_samples(G)

# Gráfica de Pérdidas
plt.figure(figsize=(10, 5))
plt.plot(losses_D, label='Discriminator Loss')
plt.plot(losses_G, label='Generator Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.title('Curvas de Pérdida GAN')
plt.show()