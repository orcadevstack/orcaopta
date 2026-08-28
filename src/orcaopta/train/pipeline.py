from orcaopta.utils.device import device
import torch

def train(model, dataloader, optimizer, epochs=10):
    model = model.to(device)

    for epoch in range(epochs):
        for batch in dataloader:
            batch = batch.to(device)

            optimizer.zero_grad()
            output = model(batch)
            loss = output.sum()
            loss.backward()
            optimizer.step()

        print(f"Epoch {epoch+1}/{epochs} — Loss: {loss.item()}")

    print(f"Training completed on device: {device}")
