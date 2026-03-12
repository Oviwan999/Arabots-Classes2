import torch
print(f"¿CUDA disponible?: {torch.cuda.is_available()}")
print(f"Versión de CUDA que usa Torch: {torch.version.cuda}")
print(f"Dispositivo: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'Ninguno'}")