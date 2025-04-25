Kai Sniadach Dev Log

## Sprint 1

    Initial commits, GitHub and Jira integration
    Looked through research papers to start our planning for the rest of the sprints
    Found a github that had a good looking UI for inspiration, and were given other repos for agent setup as well as their implementations of NEAT and hyperNEAT models.
    Set up initial backlog items and planned out who will take on what type of tasks (documentation, frontend, backend), this also involved planning items for later in the semester, as well as our long and short term goals.

## Sprint 2

    Set up items for each member of the team, as well as planned who will take on what tasks.
    Designed the simulation control and metric format. This involved planning tasks for rendering of the simulation, which needed to be coordinated with the work with both Jackson Salyards and Jackson Baker for their work in the GUI.
    This also involved looking through research papers to model what metrics we needed to measure fitness by (time alive, how quick a goal was achieved, etc.)
    The hurricane really ripped through us this sprint and as a result we had been set back a bit.

## Sprint 3

    ### 10/15/2024
    Made tasks for documentation, splitting into subtasks for the SRS document, and assigning tasks based on team strengths.
    Finished the presentation slides for the update presentation assignment that was pushed from last sprint.
    
    ### 10/17/2024
    Planning for the backend layout of generating new agents and passing weights and nodes of the network to the NN(neural network) view

    ### 10/24/2024
    Worked on a python file that will take in data from a neural network and convert it to a JSON in order to send data to our rust GUI. Also discussed with other members some possible methods for passing the JSON via websocket to the simulation display.

## Sprint 4
    10/29 - 11/07

    ### 10/29/2024
        set up backlog items for sprint 4
        planned who was going to tackle what tasks (Colton and Jackson S. on websocket)
        worked on setting up presentation 2 

    ### 10/31/2024
        did not work because it was halloween !

    ### 11/05/2024
        did some research and planned with Jackson S our backend implementation for setting up NEAT, like how we will connect it to the simulation and what parameters will be needed.
    
    ### 10/17/2024
    Planning 

## Sprint 5
    11/12 - 11/21

    ### 11/12/2024
        Made tasks for everyone this sprint, including things for SDD
        Worked on the simulation backend, Adrian had also started to do some research on NEAT and so we combined our work for the backend into one file.

    ### 11/14/2024
        NEAT implemented in backend, just need to get the websockets working for outputs and inputs into the model.

    ### 11/19/2024
        Poster first draft made, substantial progress on this

    ### 11/21/2024
        Revisions to poster draft based on feedback from Dr. Akbas

## Sprint 6
    11/26 - 12/05

    ### 11/26/2024
        Made tasks for documentation, worked a lot on SRS v2 and met with team to determine what will be done by who. Worked in call with Jackson S in order to finish a few sections in time for submission.
        Finishing touches on the SRS v2

    ### 11/28/2024
        Thanksgiving, so no work done. 

    ### 12/3/2024
        Worked on the 10 minute presentation
        Picked up poster from being printed
        SPENT MONEY on the poster board ;(
        
    ### 12/4/2024
        10 minute video presentation finished and recorded

    ### 12/5/2024
        Test plan v1 finished - filled out introduction section, testing approach, and system overview, and helped out with some other sections

## Sprint 7
    1/14 - 1/23

    ### 01/14/2025
        Set initial tasks for start of semester sprint.
    ### 01/16/2025
        Set up goals for the next sprints, and came up with an outline of the minimum viable product that needs to be delivered by the end of the semester.
    ### 01/21/2025
        Discussed some of the bottlenecks in the simulation runtime with Jackson Salyards, worked on some parts of simulation.

## Sprint 8
    01/28 - 02/06

    ### 01/28/2025
        Worked on the SRS document, filling in some of the group sections and then my own section (global impact).
    ### 01/30/2025
        Went over the current NEAT implementation with Jackson Salyards and suggested code reviews.
    ### 02/04/2025
        Did a lot of work and the final touches of the SRS with Jackson Salyards.
        
## Sprint 9
    02/11 - 02/20

    ### 02/11/2025
        Set up sprint goals and backlog for the sprint, focus was on fixing some of the performance issues with simulation runtime.
    ### 02/13/2025
        Investigated the use of SHAP for some explainable AI, and for looking at the logging that we already do.
    ### 02/18/2025
        Worked through some functions in agent.py to try and remove redundancies and set up some methods to make hyperNEAT easier to implement.
    ### 02/20/2025
        Started to set up tasks for next sprint in order to get HyperNEAT working. Talked with Jackson Baker and Salyards about what steps we need to take.

## Sprint 10
    02/25 - 03/06

    ### 02/25/2025
        Started breaking down the requirements for the SRS document. Coordinated with the team to delegate who would be filling out which sections and made sure everyone was clear on expectations and deadlines.

    ### 02/27/2025
        Focused on initial integration work for HyperNEAT. Looked over relevant documentation and prior NEAT implementation to figure out how best to incorporate the additional complexity HyperNEAT introduces (indirect encoding, CPPN structure, etc.).

    ### 03/04/2025
        Worked on the abstract for submission to AIAA.

    ### 03/06/2025
        Sent the abstract to Professor Akbas for revision.

## Sprint 11
    03/18 - 04/03

    ### 03/18/2025
        Started on the sprint goals, getting out of the spring break so just trying to get everyone back on track with work and transitioning smoothly back into working on the project.
    
    ### 03/21/2025
        Reviewed our current agent architecture with Jackson S. to ensure it could support multiple agent types at once. Sat down with Salyards to plan this out and start prototyping.

    ### 03/25/2025
        Worked on getting multiple different agent types working in a simulation environment at once (for example NEAT and non-neat)

## Sprint 12
    04/08 - 04/24

    ### 04/08/2025
        Kicked off the sprint by initializing the final set of goals for the semester and an outline for revisions to the STP (software test plan). Worked with the team to ensure all edge cases for multiple agent types were included in our testing scenarios.

    ### 04/10/2025
        Focused on implementing core elements of HyperNEAT in the backend. 

    ### 04/15/2025
        Helped with the structure and design of our final poster. Went through previous logs and documentation to pull together highlights of our technical contributions and project milestones. Talked to Professor Akbas about possible revisions.

    ### 04/17/2025
        Worked on the final presentation, revising based on the previous final presentation slides, updating with the added content worked on this semester. SRS helped with this.

    ### 04/22/2025
        Picked up the poster from printing after making final revisions.

    ### 04/24/2025
        Poster presentation day, finished the peer evaluations and finished recording the presentation.