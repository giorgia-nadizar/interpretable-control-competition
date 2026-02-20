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

## Control Task: Beluga Logistic Planning

### Description

The control task of this year is based on the one proposed in the [Beluga AI Challenge](https://github.com/TUPLES-Trustworthy-AI/Beluga-AI-Challenge). The **Use Case Description** is presented in the official repository of Beluga AI Challenge. Below, we provide a brief overview of the main components of the system and the high-level operational task.

The problem originates from a logistics scenario proposed by Airbus SE. It concerns the transportation and management of aircraft components carried by the Airbus Beluga XL, a specialized cargo aircraft used to move large aircraft parts between production sites.

### System Overview

Several Beluga aircraft operate between sites. When a Beluga lands at a production facility, the cargo it carries must be unloaded and stored in a rack system. Conversely, before departure, the aircraft must be loaded with empty jigs that need to be transported elsewhere.

The main physical components involved are:

Beluga: Aircrafts transporting large cargoes and components. They need to be unloaded when landing at a production site and then loaded with empty jigs before departing again.

Jigs: Support structures used to hold and transport aircraft parts. A jig can be either full (carrying a part) or empty. The space a jig occupies may differ depending on whether it is full or empty. Each jig has a type, which determines its size characteristics (empty and full).

Racks: Storage units where jigs are placed in sequence. Racks behave as bidirectional queues. Only the jigs located at the two ends (Beluga side or factory side) can be removed. Jigs located inside a rack may require rearrangement operations to become accessible.

Trailers: Mobile rack elements that connect the Beluga and the fixed rack system, or the rack system and the hangars. Jigs slide onto and off trailers during transfers.

Hangars: Intermediate locations where parts are removed from jigs before being sent to production lines. After unloading, jigs become empty and must be returned to the rack system.

### Operational Phases

The logistics process can be divided into two main contexts: operations during a Beluga visit and operations between flights.

1. When a Beluga lands two high-level tasks must be completed. First, unload full jigs from the Beluga and store them in the rack system. Here, individual jig identities matter: the specific jigs carried by the aircraft must be handled explicitly. Load empty jigs onto the Beluga before departure. In this case, only jig types and required quantities matter. Any empty jig matching the required type can be selected; specific jig identities are irrelevant.

2. Between two Beluga flights three types of activities may take place. Send parts to production lines, when full jigs are removed from racks (when accessible) and transported via trailers to hangars. Parts are removed in the hangars and sent to production. Then, return empty jigs to racks. Basically, after unloading, empty jigs are sent back from hangars and stored in the rack system. If needed, jigs at rack edges may be moved between racks to free access to jigs located inside. These operations improve accessibility and prepare the system for future loading or unloading tasks.

### Key Planning Challenges

The control problem arises from several structural constraints.

Limited accessibility: only edge jigs can be directly removed.

Variable space occupation depending on jig state (full vs. empty).

Coordination between unloading, loading, production supply, and rack reorganisation.

Distinction between operations requiring exact jig identities (incoming full jigs) and operations requiring only jig types (outgoing empty jigs).

The objective is to control these operations efficiently while respecting structural and temporal constraints of the system.

### Toolkit and Benchmark

The official Beluga AI Challenge repository also links the full code for the challenge at [Beluga AI Challenge Toolkit](https://github.com/TUPLES-Trustworthy-AI/Beluga-AI-Challenge-Toolkit), with examples of problem instances at [Beluga AI Challenge Benchmark](https://github.com/TUPLES-Trustworthy-AI/Beluga-AI-Challenge-Benchmarks). Refer to them, along with the official Beluga AI Challenge repository, for any in-depth details. Moreover, the code of the challenge employs the library **scikit-decide**, whose documentation is available at [Scikit-Decide Docs](https://airbus.github.io/scikit-decide/). Scikit-decide is an AI framework for Reinforcement Learning, Automated Planning and Scheduling. It has been initiated at Airbus AI Research and notably received contributions through the ANITI and TUPLES projects, and also from ANU.

### Repository Content

The `beluga` package includes selected files and folders copied from the Beluga AI Challenge Toolkit for convenience. Our control task focuses on a specific domain of the original challenge. Below is an overview of the main components of this repository and how they should be used.

---

#### `problems/`

This folder contains JSON files representing problem instances.

- You may generate your own instances and split them into training and testing sets.
- We provide example instances with different difficulty levels that you may use directly.
- Currently, the folder includes an example file (`example.json`), which can be generated with:

```bash
./generate_json_problem_instance.sh 2026 50.0 0 150 example.json
```

---

#### `generate_json_problem_instance.sh`

This bash script generates a JSON problem instance inside the `problems/` folder.

Internally, it runs `generate_instance.py` with:
- verbose mode enabled (`-v`)
- probabilistic mode enabled (`-pp`)
- probabilistic mode set to arrivals (`-pm arrivals`)
- output folder fixed to `problems/`

The parameters you can configure through this script are:
- random seed  
- occupancy rate  
- type  
- number of flights  
- problem name  

All other parameters remain at their default values.

Importantly, this script always produces **probabilistic instances with stochastic flight arrivals** (e.g., possible delays). This reflects the evaluation setting. During the final evaluation, your policy will be tested on probabilistic instances of this type that will **not** be published, to prevent overfitting or bias.

For a full description of available parameters, refer to the help documentation of `generate_instance.py` (also available in the Toolkit repository README).

In the simulation script, JSON problem instances will be used to encode the problem by using the classical PDDL (Planning Domain Description Language) formalism.

---

#### `controller.py`

This file contains:

- A general `Controller` base class (which you must extend).
- A `RandomController` for testing purposes.
- A dummy deterministic controller that always selects the median action among the available ones.

Each controller exposes a method:

```python
control(state: skd_domains.skd_base_domain.State) -> skd_domains.skd_base_domain.Action
```

- `State` represents the current observation of the environment.
- `Action` represents the action chosen by the controller.
- Available actions for a given state can be obtained via `get_available_actions`.

Your task is to implement your own policy by modifying the `CustomController` class in this file. The `control` method must return a valid action.

---

#### `simulation.py`

This script runs a simulation of a controller on the competition environment.

- The simulation is based on `SkdSPDDLDomain`, a probabilistic RL domain.
- This is the same domain that will be used during evaluation.
- Your policy must work with this exact domain and simulation loop.

The script accepts command-line arguments specifying:
- domain seed  
- controller seed  
- maximum simulation steps  
- problem name  
- controller name  

Optionally, the final reward can be saved in a `.txt` file inside the `final_rewards/` folder.

You must:
- Modify `CustomController` in `controller.py`.
- If necessary, extend the `CustomController` constructor to accept additional parameters.

If you modify the constructor, you may update the corresponding call in `simulation.py`, but:

- **You must not modify the domain, environment, simulation loop, or evaluation setting.**
- Your controller must operate within the exact environment provided.

During evaluation:
- Only the **final reward** will be considered for performance.
- Interpretability of the policy and clarity of the pipeline will be assessed separately.

---

### Evaluation Constraints

- The final evaluation will use the same RL environment, domain, simulation loop, and setting defined in `simulation.py`.
- You must submit **one single concrete implementation** of the `Controller` class, i.e., the CustomController modified properly.
- That implementation will be used directly in the provided simulation script.
- Multiple controller implementations or modifications to the RL environment/simulation loop may result in rejection.

You do **not** need to provide dependencies required for training.  
You only need to provide:
- either a conda environment file, or  
- a `requirements.txt`  

containing the dependencies strictly necessary to execute your controller during evaluation.

---

## Competition Rules

### Submissions

The goal is to provide an **interpretable control policy** that performs as well as possible on the task.

Each submission must include:

---

### 1. Control Policy Score, Explanation, and Pipeline Description

A document:

- Reporting the score obtained by the policy.
- Providing an interpretability analysis covering all relevant aspects of the policy.
- Describing the full pipeline used to obtain the policy.
- Limited to **2 pages** in the [GECCO format](https://gecco-2026.sigevo.org/Call-for-Papers), excluding references.

---

### 2. Control Policy and Code

For reproducibility and evaluation, you must provide:

- **Updated conda environment file or requirements.txt**  
  Only those dependencies that are strictly necessary to execute your `CustomController` during evaluation (training dependencies are not required).

- **Updated `controller.py`**  
  Including your implementation of `CustomController`, with all required imports you need from external libraries and/or your own code.

- **Updated `simulation.py` (if needed)**  
  Only to pass additional parameters to the `CustomController` constructor, if required.

  ⚠️ No other modifications are allowed:
  - Do not modify the domain.
  - Do not modify the simulation loop.
  - Do not modify the RL environment or evaluation setting.

  If your controller is stochastic:
  - You may use the provided seed parameter.
  - During evaluation, we may test multiple random seeds.
  
  If your controller is not stochastic, ignore the seed parameter we provide. As regards the other, eventual parameters of your controller, when submitting, you must choose **one** set of parameters for your controller and we are going to test your controller with the provided set of parameters.

- **Optimization log**  
  Reporting the progression of policy scores during the optimization process.

---

Failure to comply with these structural and implementation constraints may result in rejection of the submission.

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


