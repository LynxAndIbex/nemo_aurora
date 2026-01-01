from openwakeword import train_custom_verifier
import os

positive_folder = "training_data/aurora"
negative_folder = "training_data/not_aurora"
output_model = "models/aurora.tflite"


os.makedirs("models", exist_ok=True)

train_custom_verifier(
    positive_reference_clips=positive_folder,
    negative_reference_clips=negative_folder,
    output_path=output_model,
    model_name="aurora",
    epochs=50  #consider reducing
)

print(f"Training complete! Model saved to {output_model}")
