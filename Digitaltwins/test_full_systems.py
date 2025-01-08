#!/usr/bin/env python3
# Load component framework

from utils import basic_component, system_configuration
import argparse
parser = argparse.ArgumentParser(description="Build system")
parser.add_argument(
    "--target-directory",
    type=str,
    default="build",
    help="Target directory to put the system in",
    metavar="PARAM",
)

parser.add_argument(
    "--system",
    type=str,
    default="Config/wiring.json",
    help="Wiring diagram json to build",
    metavar="PARAM",
)

args = parser.parse_args()

def bad_type_checker(type, x):
    "Doesn't do any type checking on the exchange types"
    return True

# We make classes for each component using a type checker
PhysicalTwin = basic_component.component_from_json(
    "PhysicalTwin/component_definition.json", bad_type_checker
)
DigitalTwin = basic_component.component_from_json(
    "DigitalTwin/component_definition.json", bad_type_checker
)
Discriminator = basic_component.component_from_json(
    "Discriminator/component_definition.json", bad_type_checker
)

# Dictionary used to interpret test_system.json
component_types = {
    "PhysicalTwin": PhysicalTwin,
    "DigitalTwin": DigitalTwin,
    "Discriminator": Discriminator 
}

# Read wiring diagram (lists components, links, and parameters)
# wiring_diagram = WiringDiagram.parse_file("test_system.json")
print("args.system :" , args.system)
wiring_diagram = system_configuration.WiringDiagram.parse_file(args.system)


# Generate runner config using wiring diagram and component types
# runner_config = generate_runner_config(wiring_diagram, component_types)
# with open("test_system_runner.json", "w") as f:

runner_config = system_configuration.generate_runner_config(wiring_diagram, component_types, target_directory=args.target_directory)
with open(f"{args.target_directory}/test_system_runner.json", "w") as f:
    f.write(runner_config.json(indent=2))
