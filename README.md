<h1 align="center">3D-ReVert: 3D Reconstruction of Vertebrae from a Single Radiograph for Minimally Invasive Spine Surgery
</h1>

<p  align="center">  
 
Intraoperative imaging in Minimally Invasive Spine Surgery (MISS) commonly uses C-arm fluoroscopy, which provides only 2D views without depth. Although preoperative CT scans offer 3D anatomical detail, their intraoperative use is limited by space and equipment constraints. To address the lack of real-time 3D context, we propose 3DReVert, a novel deep learning framework for reconstructing lumbar vertebra surfaces from 2D DRRs. The dataset required for training 3D-ReVert can be downloaded from: [3DReVert-Dataset](https://drive.google.com/drive/folders/1YBzQlRE8mZOfmKDpoc9omabz6GCIIJbH?usp=sharing) 
<h3 > <i>Index Terms</i> </h3> 

  :diamond_shape_with_a_dot_inside: Minimally Invasive Spine Surgery (MISS)
  :diamond_shape_with_a_dot_inside: Single view Surface Reconstruction(SVR)
  :diamond_shape_with_a_dot_inside: Digitally Reconstructed Radiograph (DRR) 
  :diamond_shape_with_a_dot_inside: Dynamic Graph CNNs
  :diamond_shape_with_a_dot_inside: Point Cloud 
  :diamond_shape_with_a_dot_inside: Mesh

</div>
<p align="center">
  <img src="Methodology.jpg">
</p>
<div align = "center">
  :small_orange_diamond: 3D-ReVert architecture consisting a ResNet-18 encoder and a DGCNN decoder
 </p>

</div>

</details>
<h2 align="center">Dataset</h2>
<details>
 
<summary><b>Details</b></summary>

You can download the dataset from the following link:  
🔗 <a href="https://drive.google.com/drive/folders/1YBzQlRE8mZOfmKDpoc9omabz6GCIIJbH?usp=sharing" target="_blank">3DReVert-Dataset</a>  

We present an open-source dataset for SVR of lumbar vertebrae comprising 475 unique mesh–DRR pairs.  
For each mesh, DRRs are rendered from 24 diverse viewpoints, resulting in an augmented dataset of 11,400 mesh–DRR pairs.

The 3DReVert-dataset is split into training, validation, and test sets in a 70:20:10 ratio.

**Sub-directory-based arrangement:**

```
DRR/
├── verse004_segment_20/
│  ├── rendering/
│    ├── 00.png
│    ├── 01.png
│    ├── 02.png
│    └── ...
├──verse005_segment_20/
│   ├── rendering/
│   │   ├── 00.png
│   │   ├── 01.png
│   │   ├── ...
│   │   └── 23.png
├── ...  
│   └── ...
Mesh/
├── verse004_segment_20.stl/..
├── verse005_segment_20.stl/..
├── ...
```
</details>



