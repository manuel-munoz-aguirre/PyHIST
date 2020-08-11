This page contains an use case to demonstrate how PyHIST can be used to preprocess WSIs for usage in a machine learning application. The use case goal is to build a classifier at the tile level (which could be aggregated at the image level as well) that allows to determine the tissue of origin using the histological features contained in the tile. The classification will be performed using tiles generated from WSIs of The Cancer Genome Atlas (TCGA) from six different tissues: Brain, Breast, Colon, Kidney, Liver, and Skin. We have divided this use case in three parts:

## Part A: Processing the WSIs with PyHIST
In part A, we will download the WSIs from TCGA, segment them with PyHIST, examine the output, and set up the necessary data to construct a deep learning classifier. You can run this tutorial directly on a Google Colab notebook:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1VfTEUAxrwqX427wWUFe7nJEEo3Xa_RCl?usp=sharing)


### Part B: Training a CNN
We will fit a deep learning classifier (Resnet-152) using transfer learning in order to predict the tissue of origin for each tile generated in part A. You can run this tutorial directly on a Google Colab notebook:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1VeESYYDPNmU2-ndHitbwdjYUKp70xTvY?usp=sharing)


### Part C: Dimensionality reduction
Using the activations from the fully connected layer of the model trained in part B, we will perform dimensionality reduction over the feature vectors from each tile in order to see how the tiles cluster together with respect by their histological features. You can run this tutorial directly on a Google Colab notebook:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1JR5Hq8Ked1Fb9UIgmn65zg8P41qIBWhb?usp=sharing)
