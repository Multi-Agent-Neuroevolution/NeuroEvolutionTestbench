Jackson Salyards Dev Log

# Sprint 1
2024-09-26
Initial commit, and began research
Looked into the different types of AI and how they can be used in our simulation
2024-10-03
Found a github that had a similar project, and a good looking UI
We are using that GUI for inspiration
Here is the link

# Sprint 2
2024-10-04
Added the iced gui library to the project
Iced is a GUI library that is easy to use and looks good
Based on the dev branch that is based on main
Initially added basic layout for the GUI
2024-10-08
Basic wireframe done for the GUI
worked on JIRA documentation
worked on project presentation

# Sprint 3
created a new feature branch based on the current rust gui branch. This brannch is for the agent controlls feature.
Worked with jackson baker to define how data will be sent from GUI to the simulation
worked on project proposal
finished project presentation
worked with baker on creating code to view neural network in real time
2024-10-17
Merge pull request #2 from Multi-Agent-Neuroevolution/feature-rustgui-neural
added neural net object skeleton
2024-10-23
Merge pull request #3 from Multi-Agent-Neuroevolution/feature-rustgui-agentcontrolls
Added agentview controlls and moved each view to its own struct
2024-10-24
Merge pull request #4 from Multi-Agent-Neuroevolution/feature-rustgui-neural
Feature rustgui neural. Has basic code for displaying the current state of the neural network
2024-11-01
worked with baker to get gui to minimum viable state
running into issues reading from json and drawing neurons
2024-11-03
began to work on backend code, and presentation
worked with group members to design layout of simulation
2024-11-05
Merge pull request #12 from Multi-Agent-Neuroevolution/feature-agent
Feature agent
2024-11-06
worked with kai to complete more documentation

# Sprint 4
2024-11-12
Worked on the backend simulation and encountered an issue where simulation steps progressively took longer to execute.
Refactored older code to improve its efficiency and maintainability.
Collaborated with Colton to create a Flask API for communication between the frontend and backend.
2024-11-14
Made progress in addressing the backend's slowness issues, but the simulation was still performing below acceptable speed.
Developed a debugging viewer function to better analyze and identify potential bottlenecks in the simulation process.
2024-11-16
Expanded the functionality of individual agents by adding collision detection and response.
Refactored the object system to streamline interactions and improve modularity in the simulation codebase.
2024-11-19
Resolved the issue with agents that was causing backend slowness,
significantly improving performance. Simulation steps now execute in
approximately 10ms.
Focused on updating documentation and planning the next steps for further improvements and features.
2024-11-21
Added multithreading and spatial grids for 2-10x speed increase
Added ability to display agents dynamically. Current JSON 500 agent demo
WIP on feature-simulation-backend: fixed issue where it took WAY too long. Added environment-> JSON conversion
Index on feature-simulation-backend: fixed issue where it took WAY too long. Added environment-> JSON conversion
2024-11-22
Improved and sped up agent class. Gained about 100ms on large agent sizes

# Sprint 5
2024-12-03
Merge pull request #13 from Multi-Agent-Neuroevolution/feature-simulation-backend (Jackson Baker)

# Sprint 6
2025-01-14
fixed gitignore
2025-01-22
added some basic ai stuffs
2025-01-23
added a conf
2025-01-23
changed to .txt
2025-01-23
changed to .txt
2025-01-23
more ai
2025-01-23
added get_imputs
2025-01-23
added imports
2025-01-28
ai kinda working
2025-01-28
AI working - no training
2025-01-28
minor improvments
2025-01-28
added steps, and changable bounds
2025-01-28
added mutation
2025-01-28
added raton, prey food, more logging,and more
2025-01-29
AI blockchain llm gpt
2025-01-30
ai
2025-01-30
food is removed when eaten and can respawn, rate mutable

# Sprint 7
2025-02-04
fixed lol
2025-02-11
small changes
2025-02-20
moved checkbounds into agent class
2025-02-20
fixed init_agents
2025-02-21
removed reduntand functions, sped up get_inputs, added several adjustible agent constants
2025-02-21
accedentally removed agents in last commit, fixed
2025-02-21
added env size scaler

# Sprint 8
2025-03-24
fixed toml
2025-03-24
added misssing log dir, and ffixed bug causing agents to not update objects in sight
2025-03-24
added misssing log dir for real this time
2025-03-24
AHHHH
2025-03-24
wip multi model and hyperneat
2025-03-25
wip multi model systems
2025-03-31
multi-model breeding added
2025-03-31
bug fixes, multi-model working
2025-03-31
more bugfixes and fixed breading for even more breading
2025-03-31
rewrote get_nearby and get_inputs functions for more speed. Also disabled some logging as its slow

# Sprint 9
2025-04-01
massive speed improvements
2025-04-01
major bug fixes
2025-04-02
added progress bar, and estimated time to complete
2025-04-03
adde viewer file that was low-key vibe coded :(
2025-04-03
added method to save initial genome state to json
2025-04-08
fixed some small buggs
2025-04-08
fixed sim_world
2025-04-08
maybe fixed mutate function
2025-04-10
added agent type

# Sprint 10
2025-04-15
added multiple configs for each sub type of agent
2025-04-16
wip hyprneat features
2025-04-17
revamp preys, fixed bugs, hyper neat still broken:(
2025-04-22
improved eating and agnt inputs
2025-04-23
more fixes
2025-04-23
imporved breeding again
