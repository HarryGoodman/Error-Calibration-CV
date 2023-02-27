import torch
from torch import Tensor

from torchvision import models
from torchvision import datasets

from tqdm import tqdm
from typing import Tuple, List



class Inference:
    def __init__(self, data_path: str, model_size: str) -> None:
        # Model Size
        self.model_size = model_size.capitalize()

        # Data Transformation
        # Using the bespoke transformation of ConvNext
        self.data_transform = models.get_weight(
            f"ConvNeXt_{self.model_size}_Weights.DEFAULT"
        ).transforms

        # Data Loader
        # Using torchvison.models.ImageFolder
        self.dataset = datasets.ImageFolder(data_path, transform=self.data_transform())

        # Model
        # Accessing ConvNext from torchvision
        self.model = models.get_model(
            f"convnext_{self.model_size}", num_classes=len(self.dataset.classes)
        )
        self.model.eval()

        # Confindences, Predictions and Accuracy
        self.confidences = []
        self.predictions = []
        self.accuracies = []

    def _calibration_components_compute(
        self,
        preds: Tensor,
        target: Tensor
    ) -> Tuple[List[float], List[int], List[bool]]:
        confidence, prediction = preds.max(dim=1)
        accuracy = prediction.eq(target)
        return confidence.float(), prediction, accuracy

    def infer(self) -> None:


        for data, target in tqdm(self.dataset):
            data = data.unsqueeze(0)
            with torch.no_grad():
                output = self.model(data)
                softmax = torch.exp(output) / torch.sum(torch.exp(output))
                confidence, prediction, accuracy = self._calibration_components_compute(
                    preds=softmax,
                    target=target
                )

            self.confidences.append(confidence)
            self.predictions.append(prediction)
            self.accuracies.append(accuracy)

        self.confidences = torch.cat(self.confidences)
        self.predictions = torch.cat(self.predictions)
        self.accuracies = torch.cat(self.accuracies)


    def get_true_target(self) -> Tensor:
        """
        Get the target labels.
        Returns:
            The target labels (preserving order of inference)
        """
        return Tensor(self.dataset.targets)

    def get_predictions(self) -> Tensor:
        """
        Get the predicted labels.
        Returns:
            The predicted labels (preserving order of inference)
        """
        return self.predictions

    def get_confidences(self) -> Tensor:
        """
        Get the confidences of each prediction.
        Returns:
            The confidence levels (preserving order of inference)
        """
        return self.confidences

    def get_accuracies(self) -> Tensor:
        """
        Get the accuracy levels of each prediction.
        Returns:
            The confidence levels (preserving order of inference)
        """
        return self.confidences

    def get_class_labels(self) -> List[str]:
        """
        Get the class labels (produced by ImageFolder).
        Returns:
            List of the class labels (preserving order of index)
        """
        return self.dataset.classes

    def get_number_of_classes(self) -> int:
        """
        Get the number of classes (produced by ImageFolder).
        Returns:
            number of class labels
        """
        return len(self.dataset.classes)