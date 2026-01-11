# Mars Explorer – Multi-Agent Planning System
## Authors
Laia Barcenilla Mañá, Núria Cardona Vilar, Natalia Muñoz Moruno and Helena Sánchez Ulloa
## Overview
Mars Explorer is a **multi-agent planning system** designed for autonomous Martian exploration. Built using CrewAI, the platform coordinates rovers, drones, and satellites to generate optimized mission plans while respecting environmental hazards and operational constraints.

The system decomposes complex mission objectives into specialized agent crews that collaborate autonomously, ensuring safe, efficient, and robust exploration strategies. Full technical details and methodology are described in the accompanying report.

## Installation

Clone the repository:
```bash
git clone <https://github.com/hsanchezulloa/IMAS.git>
cd IMAS/mars_explorer/src/mars_explorer  
```
Install dependencies:
```bash
pip install -r requirements.txt
```
## Execution
Run the complete pipeline:
```bash
python main.py
```
This executes:
- Mission analysis
- Parallel planning (rovers, drones, satellites)
- Automatic validation loop
- Final mission integration
- Markdown report generation

## Results

The best execution results are stored inside the results/ folder:
```bash
results/
├── hazards/
│   ├── routes_drone.json
│   ├── routes_rover.json
│   ├── routes_satellite.json
│   └── ...
└── non-hazards/
    ├── routes_drone.json
    ├── routes_rover.json
    ├── routes_satellite.json
    └── ...
```
Since hazards may or may not occur, two execution scenarios are provided:

Hazards ON (hazards/)
 - Routes strictly avoid unstable, radioactive and storm-affected nodes.

Hazards OFF (non-hazards/)
  - Optimized routes assuming ideal environmental conditions.

This dual execution provides a robust contingency plan, ensuring mission readiness under uncertain Martian conditions.

