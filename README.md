# Interpretable Control Competition

Repository for the [GECCO'26](https://gecco-2026.sigevo.org/HomePage) interpretable control competition.

## Install

Clone the repository and create the conda virtual environment with all needed packages.

```shell
git clone https://github.com/giorgia-nadizar/interpretable-control-competition.git
cd interpretable-control-competition
conda env create -f environment.yml
conda activate belugaenv
```

Alternatively, if you do not want to use conda, you can also directly create a virtual environment from the Python
version installed on your system (must be at least Python 3.12.12):

```shell
git clone https://github.com/giorgia-nadizar/interpretable-control-competition.git
cd interpretable-control-competition
python3 -m venv belugaenv
source belugaenv/bin/activate
pip3 install -r requirements.txt
```

## Control Task: Beluga

### Task details

For more details on the 'Pong' we refer to the official documentation on the ALE website:
[https://github.com/TUPLES-Trustworthy-AI/Beluga-AI-Challenge-Toolkit](https://github.com/TUPLES-Trustworthy-AI/Beluga-AI-Challenge-Toolkit).

### Repository content

The `pong` package contains two files:

- `controller.py` has a general controller class (which you can extend with your own implementation),
  and a random controller for testing purposes
- `example.py` shows the basic evaluation loop for the chosen environment, the `Pong-v4`

The competition's final evaluation will be performed with the same environment (`Pong-v4`).

_Note:_ in some cases running the `example.py` with `render_mode='human'` might result in a libGL error. One potential fix
is to run the following command in your conda environment.
```shell
conda install -c conda-forge libstdcxx-ng
```

## Competition rules

### Submissions

The goal is to provide an interpretable control policy that solves the task.

Each submission will have to include:

- **Control policy score, explanation, and pipeline description**: a document
    - containing the score obtained by the policy, an interpretability analysis of the policy (covering all
      relevant information deducible from it), and the pipeline used to obtain it
    - of up to 2 pages in the [Gecco format](https://gecco-2026.sigevo.org/Call-for-Papers), excluding references
- **Control policy and code**: for reproducibility and assessment purposes, we require
    - _updated environment file_ or _additional requirements_ needed to make the code work
    - _run file_, i.e., a Python script, from which the submitted policy can be assessed on the environment
    - _optimization file_, i.e., a Python script, from which the optimization process can be reproduced
    - _optimization log_ reporting the progression of the policies scores during the performed optimization

### Evaluation

Each submission will be evaluated according to two criteria:

- **Performance rank**, which will be evaluated by simulating the submitted policy
- **Interpretability rank**, which will be appraised by a panel of judges, who will consider:
    - Clarity of the pipeline
    - Readability of the model
    - Clarity of the explanation provided
    - Amount of processing required to derive the explanation from the raw policy

These two ranks will be combined using the geometric mean to compute the overall global rank for each competition entry.

### Prize

Winners will be awarded a **certificate**.


