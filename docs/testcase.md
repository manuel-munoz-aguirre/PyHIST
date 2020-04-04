To demonstrate how PyHIST can be used to preprocess WSIs for usage in a machine learning application, we downloaded 5 WSIs from each of the following tissues hosted in The Cancer Genome Atlas (TCGA): Brain, Breast, Colon, Kidney, Liver, and Skin. The use case goal is to build a classifier at the tile level (which can be aggregated at the image level as well) that allows to determine the tissue of origin. We have divided the tutorial in three parts:

## Part A: Processing the WSIs with PyHIST
In part A, we will download the WSIs from TCGA, segment them with PyHIST, examine the output, and set up the necessary data to construct a deep learning classifier.

Clone the repository if you haven't yet, and move to the `use_case` directory.
```
git clone https://github.com/manuel-munoz-aguirre/PyHIST.git
cd use_case
```

Jupyter is needed to open the tutorial part A notebook: if you are using the provided conda environment, you can install jupyter with:
```
conda install jupyter
```

And then launch the notebook:
```
jupyter notebook Test_case_part_A_Data_cleaning.ipynb
```

### Part B: Training a CNN
We will fit a deep learning classifier (Resnet-152) using transfer learning in order to predict the tissue of origin for each tile generated in part A. You can run this tutorial directly on a Google Colab notebook:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1d5HmAYTod6Zk-hxL0tum2JwfTGRpz8rH)


### Part C: Dimensionality reduction
Using the activations from the fully connected layer of the model trained in part B, we will perform dimensionality reduction over the feature vectors from each tile in order to see how the tiles cluster together with respect by their histological features. You can run this tutorial directly on a Google Colab notebook:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Q4HAU98gxg32okcUBU4C-Qb6g33ySuCH)

