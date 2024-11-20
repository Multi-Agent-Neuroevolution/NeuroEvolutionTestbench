# Jackson Salyards Dev Log

# Sprint 1

### 2024-09-26

  - Initial commit, and began research
  - Looked into the different types of AI and how they can be used in our simulation

### 2024-10-03

  - Found a github that had a similar project, and a good looking UI
  - We are using that GUI for inspiration
  - Here is the link

# Sprint 2

### 2024-10-4

  - Added the iced gui library to the project
  - Iced is a GUI library that is easy to use and looks good
  - Based on the dev branch that is based on main
  - Initially added basic layout for the GUI

### 2024-10-8

  - Basic wireframe done for the GUI
  - worked on JIRA documentation
  - worked on project presentation

# Sprint 3

  - created a new feature branch based on the current rust gui branch. This brannch is for the agent controlls feature.
  - Worked with jackson baker to define how data will be sent from GUI to the simulation
  - worked on project proposal
  - finished project presentation
  - worked with baker on creating code to view neural network in real time


### 2024-11-1
  - worked with baker to get gui to minimum viable state
  - running into issues reading from json and drawing neurons

### 2024-11-3
  - began to work on backend code, and presentation
  - worked with group members to design layout of simulation

### 2024-11-6
  - worked with kai to complete more documentation

# Spint 4
### 2024-11-12  
  - Worked on the backend simulation and encountered an issue where simulation steps progressively took longer to execute.  
  - Refactored older code to improve its efficiency and maintainability.  
  - Collaborated with Colton to create a Flask API for communication between the frontend and backend.  

### 2024-11-14  
  - Made progress in addressing the backend's slowness issues, but the simulation was still performing below acceptable speed.  
  - Developed a debugging viewer function to better analyze and identify potential bottlenecks in the simulation process.  
  
### 2024-11-16  
  - Expanded the functionality of individual agents by adding collision detection and response.  
  - Refactored the object system to streamline interactions and improve modularity in the simulation codebase.  

### 2024-11-19  
  - Resolved the issue with agents that was causing backend slowness, significantly improving performance. Simulation steps now execute in approximately 10ms.  
  - Focused on updating documentation and planning the next steps for further improvements and features.  
