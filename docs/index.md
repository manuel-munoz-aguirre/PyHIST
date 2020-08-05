# PyHIST

PyHIST is a **H**istological **I**mage **S**egmentation **T**ool: a lightweight semi-automatic command-line tool to extract tiles from histopathology whole image slides. It is intended to be an easy-to-use tool to preprocess histological image data for usage in machine learning tasks.

<div align="center">
<img src="https://raw.githubusercontent.com/manuel-munoz-aguirre/PyHIST/master/docs/resources/workflow.png" alt="logo"></img>
</div>
<br>
<div align="center">
<img src="https://raw.githubusercontent.com/manuel-munoz-aguirre/PyHIST/master/docs/resources/tilecrossed_sample.png" alt="logo"></img>
</div>

Features:

*   Designed for Aperio's SVS/TIFF format (see experimental support for other formats).
*   Mask generation over regions with tissue content (foreground)
*   Generation of tiles based on the foreground
*   Quick overview of selected tiles
*   Several tile generation methods (graph-based, random sampling, Otsu and adaptive thresholding)
*   Ability to downsample from the original image
*   Log generation with information for all the tiles generated from an image