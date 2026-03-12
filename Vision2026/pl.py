import torch

print("--- Verificando Hardware ---")
if torch.cuda.is_available():
    print(f"✅ GPU detectada: {torch.cuda.get_device_name(0)}")
    print(f"Memoria disponible: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
else:
    print("❌ El sistema sigue usando CPU. Revisa la instalación de CUDA.")