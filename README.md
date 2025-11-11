# image-processing

Internal Python package used for UHDT's image processing

## Installation Instructions

1. Create a virtual environment with your environment manager of choice (e.g., conda, uv, venv, virtualenv).Python 3.10.12 is the recommended version as of 9/26/25.  

   - **If using conda**, run:  

     ```bash
     conda create -n <env_name> python=<version>
     ```

2. Activate the target virtual environment.  

   - **If using conda**, run:  

     ```bash
     conda activate <env_name>
     ```

3. Install all packages with the following command:  

   ```bash
   pip install -r requirements-<platform>.txt
   ```

4. Install the image-processing package in editable mode.

```bash
pip install -e .
```

## Building Documentation w/ Sphinx
1. Install `sphinx` and its associated support packages. The requirements.txt file for your platform include these packages.

```bash
pip install sphinx sphinx-autoapi sphinx-code-tabs sphinx-rtd-theme
```

2. Change directory into `docs`.

```bash
cd docs
```

3. Use `make` to generate the HTML documentation. The home page of the documentation can be accessed at `docs/_build/html/index.html`.

```bash
make html
```
  
## Installing Pytorch

Download Pytorch using the command provided on Pytorch's *Get Started* page using the appropriate hardware configuration options. If the computer does not have a GPU, select *CPU* for the *Compute Platform*. For Mac computers, select *Source* for the *Compute Platform*.

### Installing CUDA 12.8 Toolkit (Linux/Windows Systems with Nvidia GPUs)

This is only applicable to systems that have an Nvidia GPU. It is strongly recommended that you install CUDA 12.8 drivers for stable performance and support across development environments. Download the driver corresponding to your development platform at [https://developer.nvidia.com/cuda-12-8-0-download-archive](https://developer.nvidia.com/cuda-12-8-0-download-archive).

### Installing ROCm Drivers (Linux/Windows Systems with AMD GPUs)

ROCm drivers have not been tested for model training.

