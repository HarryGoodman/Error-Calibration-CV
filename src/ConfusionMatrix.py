import torch
from torch import Tensor

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

from typing import List
from pathlib import Path

class ConfusionMatrix:
    def __init__(
        self,
        predictions: Tensor,
        targets: Tensor,
        class_labels: List[str],
        save_path: str,
        save_png: bool = True,
    ) -> None:
        self.predictions = predictions
        self.targets = targets
        self.save_path = save_path
        self.class_labels = class_labels
        self.save_png = save_png

    def generate_conf_matrix(
        self,
    ) -> Tensor:
        classes_n = len(self.class_labels)
        self.conf_matrix = torch.zeros(classes_n, classes_n)

        for pred_class in range(classes_n):
            self.conf_matrix[pred_class] = torch.bincount(
                self.predictions[self.targets == pred_class], minlength=classes_n
            ).float()

        self.conf_matrix = pd.DataFrame(
            self.conf_matrix.numpy(),
            index=[i for i in self.class_labels],
            columns=[i for i in self.class_labels],
        )

    def plot_conf_matrix(self) -> None:
        self.generate_conf_matrix()
        with pd.option_context("display.max_rows", None, "display.max_columns", None):
            print("Confusion Matrix:\n")
            print(self.conf_matrix)

        Path(self.save_path).mkdir(parents=True, exist_ok=True)

        plt.clf()
        sns.set(rc={"figure.figsize": (15, 8)})

        conf_fig = sns.heatmap(
            self.conf_matrix,
            annot=True,
        ).set_title("Confusion Matrix")

        fig = conf_fig.get_figure()
        plt.tight_layout()
        if self.save_png:
            fig.savefig(self.save_path + "confusion_matrix.svg", dpi=400, format="svg")
        else:
            fig.show()

        plt.clf()

        
