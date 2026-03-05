import torch

print("allocated GB:", torch.cuda.memory_allocated(0) / 1024**3)
print("reserved  GB:", torch.cuda.memory_reserved(0) / 1024**3)
print("max alloc GB:", torch.cuda.max_memory_allocated(0) / 1024**3)
print("max reserv GB:", torch.cuda.max_memory_reserved(0) / 1024**3)
