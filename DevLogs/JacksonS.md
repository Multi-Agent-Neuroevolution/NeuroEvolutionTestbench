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


# Appended Git Commits by me.
commit a0bd046a10a3a1bdfe4bba7279074df690f55fd8
Author: JacksonSalyards <jacksonsalyards55@gmail.com>
Date:   Wed Apr 23 00:10:56 2025 -0400

    imporved breeding again

commit 6f8d52204e60da7a74dbba81b93f6f615228c2d1
Author: JacksonSalyards <jacksonsalyards55@gmail.com>
Date:   Thu Apr 17 02:12:53 2025 -0400

    revamp preys, fixed bugs, hyper neat still broken:(

commit 5ebf77f6d8958e7346e317c4b3b5c567a17baeef
Author: JacksonSalyards <jacksonsalyards55@gmail.com>
Date:   Thu Apr 3 09:27:25 2025 -0400

    added method to save initial genome state to json

commit 1b19f2f24572e4ea99dd1d15f7d2a3bbba77ea3c
Author: JacksonSalyards <jacksonsalyards55@gmail.com>
Date:   Thu Apr 3 09:17:02 2025 -0400

    adde viewer file that was low-key vibe coded :(

commit 1b63b3fb941919b973af45b8e787a903b5865a31
Author: JacksonSalyards <jacksonsalyards55@gmail.com>
Date:   Wed Apr 2 22:09:25 2025 -0400

    added progress bar, and estimated time to complete

commit 8f6793ce711b0fbff3c8f82aef4ab85bd42387f4
Author: JacksonSalyards <jacksonsalyards55@gmail.com>
Date:   Mon Mar 24 21:32:25 2025 -0400

    wip multi model and hyperneat

commit 7f6324f2b3e55bbeda23249649d96741e99e26a4
Author: JacksonSalyards <jacksonsalyards55@gmail.com>
Date:   Mon Mar 24 20:06:33 2025 -0400

    AHHHH

commit 6617f38af413fe345095b0c5297598371423e543
Author: JacksonSalyards <jacksonsalyards55@gmail.com>
Date:   Mon Mar 24 20:05:55 2025 -0400

    added misssing log dir for real this time

commit 22334c3f23eee5bd6558f26446e32c381a7f4f01
Author: JacksonSalyards <jacksonsalyards55@gmail.com>
Date:   Mon Mar 24 20:03:13 2025 -0400

    added misssing log dir, and ffixed bug causing agents to not update objects in sight

commit c620ddc93d3af34332523bef97047e27351e9a5c
Author: JacksonSalyards <jacksonsalyards55@gmail.com>
Date:   Mon Mar 24 19:35:52 2025 -0400

    fixed toml

commit a297807788f0bd04c3acd7a544ee8e1fb8444dcc
Merge: 1b24d6d fef51d8
Author: JacksonSalyards <95992718+CoolHackerMan27@users.noreply.github.com>
Date:   Tue Nov 5 14:27:14 2024 -0500

    Merge pull request #12 from Multi-Agent-Neuroevolution/feature-agent
    
    Feature agent

commit c89b8760b4d77c41c320a0a4b692efeb04cf6671
Merge: 0e7f96c eb8f75c
Author: JacksonSalyards <95992718+CoolHackerMan27@users.noreply.github.com>
Date:   Thu Oct 24 14:19:43 2024 -0400

    Merge pull request #4 from Multi-Agent-Neuroevolution/feature-rustgui-neural
    
    Feature rustgui neural. Has basic code for displaying the current  state of the neural network

commit 0e7f96ce074ce398a6de819ad1b5f58244b1262e
Merge: 96f3574 e681314
Author: JacksonSalyards <95992718+CoolHackerMan27@users.noreply.github.com>
Date:   Wed Oct 23 15:13:21 2024 -0400

    Merge pull request #3 from Multi-Agent-Neuroevolution/feature-rustgui-agentcontrolls
    
    Added agentview controlls and moved each view to its own struct for bΓÇª

commit 96f3574b687fcd143b11ff6296e0f466c2ea4c06
Merge: 893f4f0 8099519
Author: JacksonSalyards <95992718+CoolHackerMan27@users.noreply.github.com>
Date:   Thu Oct 17 21:19:30 2024 -0400

    Merge pull request #2 from Multi-Agent-Neuroevolution/feature-rustgui-neural
    
    added neural net object skeleton
commit b5a1c37cd50a4384c2c30be5cd734806b7ed33e8
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Wed Apr 23 12:24:40 2025 -0400

    more fixes

commit 1c50dedfda0a1957dfb874efc9c994373e0dcce7
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Apr 22 20:14:03 2025 -0400

    improved eating and agnt inputs

commit 5604fa09c70e48ce101addbbe10b6ba5a0ea0273
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Wed Apr 16 23:36:34 2025 -0400

    wip hyprneat features

commit c985d1aa30b68b946d5954f59eb239712bcca7ae
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Apr 15 22:21:05 2025 -0400

    added multiple configs for each sub type of agent

commit 59dffb2aabe60dc4bd18af0dc0d52b74c311e333
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Thu Apr 10 15:31:30 2025 -0400

    added agent type

commit 761eff2f926d1e15389588dd4a2ce2e6e6d0c572
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Apr 8 15:20:17 2025 -0400

    maybe fixed mutate function

commit 67d5c3966936a27eccb021f1db8e52d4a5c2ba18
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Apr 8 15:16:20 2025 -0400

    fixed sim_world

commit 5f5ca9e838ada5c5e898636858d0cbe2505cd6e6
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Apr 8 15:09:19 2025 -0400

    fixed some small buggs

commit 1e674734a72bad6496c22d95aa46ae8208827dea
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Apr 1 18:48:53 2025 -0400

    major bug fixes

commit dca63b2903fc9a0b5fc6b5daae13fdcc3f56f4bc
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Apr 1 12:46:59 2025 -0400

    massive speed improvements

commit c9992fb61aa9fc2c85ee15812de425f3bd0bb57f
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Mon Mar 31 16:35:27 2025 -0400

    rewrote get_nearby and get_inputs functions for more speed. Also disabled some logging as its slow

commit e30a55132e91a5f382fc244c7803025f0feed65d
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Mon Mar 31 15:21:29 2025 -0400

    more bugfixes and fixed breading for even more breading

commit 52c39cb1b7cdbc1b2327f8fc26341f9745931c80
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Mon Mar 31 12:24:31 2025 -0400

    bug fixes, multi-model working

commit 0b90b7357f14fc8b73a9f99e6d78b5124fa7c91d
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Mon Mar 31 12:12:06 2025 -0400

    multi-model breeding added

commit 30ac16b0e6fd2054cf7b14531cc10e9d118233e7
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Mar 25 15:09:00 2025 -0400

    wip multi model systems

commit 7286891df5f31976c513ad444472b0404b1568be
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Fri Feb 21 20:41:06 2025 -0500

    added env size scaler

commit 503c6d9ec6fddb90054f23e43897683076fae800
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Fri Feb 21 13:20:03 2025 -0500

    accedentally removed agents in last commit, fixed

commit a3848fe44d36b997bcfdef60d6e56c1f2ded3371
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Fri Feb 21 13:18:29 2025 -0500

    removed reduntand functions, sped up get_inputs, added several adjustible agent constants

commit 32d0a1e6f08f3ba46a4858a390670018977fecdb
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Thu Feb 20 15:31:58 2025 -0500

    fixed init_agents

commit 76353712ae534e98f4954bf12482b29ffe58c65c
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Thu Feb 20 14:39:43 2025 -0500

    moved checkbounds into agent class

commit b0a55b46050fcf33e93225bd170a5ece24d7e56d
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Feb 11 14:57:36 2025 -0500

    small changes

commit 7b84013fcea51e927832303a47d7d4b5401bd6dc
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Feb 4 12:50:40 2025 -0500

    fixed lol

commit 1335d0253143c63112e7f89d2c56a11d9f255465
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Thu Jan 30 16:01:28 2025 -0500

    food is removed when eaten and can respawn, rate mutable

commit 2396a504b36957b3d465fdc1911ac4c20ee1c738
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Thu Jan 30 15:43:33 2025 -0500

    ai

commit 833083ebe60abaa4865787bb3dc58de6fd9ddc62
Author: CoolHackerMan27 <SALYARDJ@my.erau.edu>
Date:   Wed Jan 29 16:32:40 2025 -0500

    AI blockchain llm gpt

commit e6ae4364fa8211742f77f8fad68c2507fd57a5fa
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Jan 28 18:32:39 2025 -0500

    added raton, prey food, more logging,and more

commit 2996886852556ad91d49a43c7c97642f10b8c2b9
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Jan 28 16:56:59 2025 -0500

    added mutation

commit 78349bf02e9c411417fa42dfdb913b56952aaebe
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Jan 28 15:20:54 2025 -0500

    added steps, and changable bounds

commit 7c237d124ae0814e929e2067f75a51580060630a
Author: CoolHackerMan27 <SALYARDJ@my.erau.edu>
Date:   Tue Jan 28 02:31:55 2025 -0500

    minor improvments

commit fd365957c6edeaf775acd9e9d4d41529aca3345b
Author: CoolHackerMan27 <SALYARDJ@my.erau.edu>
Date:   Tue Jan 28 02:00:14 2025 -0500

    AI working - no training

commit 84a98b6c90b22a3ec7cf2d1e2f3897e656489626
Author: CoolHackerMan27 <SALYARDJ@my.erau.edu>
Date:   Tue Jan 28 06:39:33 2025 -0500

    ai kinda working

commit 87547495b4670620de45deedde72677560a44da1
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Thu Jan 23 15:15:35 2025 -0500

    added imports

commit f2b29fb7da60493106c5215fedf9af00c1e856e5
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Thu Jan 23 15:07:40 2025 -0500

    added get_imputs

commit a48cfae25522278e51f99610baff92b4f8da9497
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Thu Jan 23 14:49:01 2025 -0500

    more ai

commit 2033ff4e82e35773e6905ce2f6078802596869ce
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Thu Jan 23 14:34:46 2025 -0500

    changed to .txt

commit ffc7ab23e6013e6d675a8c350501f231aa504460
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Thu Jan 23 14:33:03 2025 -0500

    changed to .txt

commit 4c9e32ab2f43df38ef69a27b6433b351e6d1a549
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Thu Jan 23 14:29:45 2025 -0500

    added a conf

commit d2fc16cdee7f00cdcaf678d17433b6a9a26d3f02
Author: CoolHackerMan27 <SALYARDJ@my.erau.edu>
Date:   Wed Jan 22 23:58:20 2025 -0500

    added some basic ai stuffs

commit 1bf81e5809b0eec224bd4c1313552448b7d66b35
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Jan 14 15:19:35 2025 -0500

    fixed gitignore

commit 7cce4957169511d810adc1d255a65c03a06910d8
Author: CoolHackerMan27 <SALYARDJ@my.erau.edu>
Date:   Fri Nov 22 01:35:58 2024 -0500

    imporved and sped up agent class. Gained about 100ms on large agent sizes

commit 9bb3f3dd70cad949126159535c69e64ae65f7be0
Author: CoolHackerMan27 <SALYARDJ@my.erau.edu>
Date:   Thu Nov 21 21:56:55 2024 -0500

    added multithreading and spacial grids for 2-10x speed increase

commit e733a8786c2b5e2ef4ae25575ffd0c7de2cf3e00
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Nov 19 15:08:50 2024 -0500

    fixed issue where took WAY to long. added enviroment-> json conversion

commit 4d2ffce2b13bf87752ff550b0e2ff252390ca5b3
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Tue Nov 19 11:30:36 2024 -0500

    minor bug fixes

commit 80bf91c622bd1a8720688750f69be2b0dd36136d
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Mon Nov 18 21:12:43 2024 -0500

    fixed display issues and add some more needed functionality

commit 496f872f15c7a0bf2cce78a44019040644c42ec3
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Mon Nov 18 13:09:08 2024 -0500

    added debug display and basic functionality

commit f06581e5642d48e151830b1d4005b5c4b5c6e505
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Thu Nov 14 15:09:59 2024 -0500

    added skeletons of all basic functions for agent and enviroment

commit 4eb14c19b84a8f5c099227e3202e775d5192b0a2
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Thu Nov 14 14:49:59 2024 -0500

    added super class for algents and obsticles and stuff

commit 77ff5eac80516c6d3a4a1fe2e710b5a5fc53922a
Author: CoolHackerMan27 <salyardj@my.erau.edu>
Date:   Thu Nov 14 14:31:30 2024 -0500

    Added basic code for simulation environment

commit a297807788f0bd04c3acd7a544ee8e1fb8444dcc
Merge: 1b24d6d fef51d8
Author: JacksonSalyards <95992718+CoolHackerMan27@users.noreply.github.com>
Date:   Tue Nov 5 14:27:14 2024 -0500

    Merge pull request #12 from Multi-Agent-Neuroevolution/feature-agent
    
    Feature agent

commit 91daa38f33a11f4958d2dbb5eca931aa56a24120
Author: CoolHackerMan27 <jacksonsalyards55@gmail.com>
Date:   Fri Nov 1 19:08:13 2024 -0400

     json parsing working, fixed bug preventing edges from having color mapped correctly, fixed attempting to unrwap None value for weights

commit 4e4cf8e514f801aea009cdeb69d7e29ab97eef30
Author: CoolHackerMan27 <jacksonsalyards55@gmail.com>
Date:   Wed Oct 30 14:30:26 2024 -0400

    added a nice demo of all the shapes and colors

commit 9e799efe83025f9eb75e00c36e5b89a4ff02a9be
Author: CoolHackerMan27 <jacksonsalyards55@gmail.com>
Date:   Wed Oct 30 14:04:13 2024 -0400

    added get_color func

commit 7719ec10ffd4561a73022b1706f5f63e50f9e05f
Author: CoolHackerMan27 <jacksonsalyards55@gmail.com>
Date:   Wed Oct 30 13:58:03 2024 -0400

    display working, but colors are always black

commit aee756f5bd2a2e672dd0380128cd761874dc7339
Author: CoolHackerMan27 <jacksonsalyards55@gmail.com>
Date:   Mon Oct 28 11:03:16 2024 -0400

    dots are displayed but position is wrong

commit 7344f42cf0b5785109adbbccd1b43f4d5300f6b0
Author: CoolHackerMan27 <SALYARDJ@my.erau.edu>
Date:   Fri Oct 25 00:40:46 2024 -0400

    Code compiles but shows nothing.

commit e1776973e02500f49e57118c150e078a684c721b
Author: CoolHackerMan27 <SALYARDJ@my.erau.edu>
Date:   Fri Oct 25 00:30:50 2024 -0400

    init

commit eef65203e8c69cf8126be49681f5fb94226904af
Author: CoolHackerMan27 <SALYARDJ@my.erau.edu>
Date:   Thu Oct 24 23:37:28 2024 -0400

    Example data structs for sending data to/from simulation

commit c89b8760b4d77c41c320a0a4b692efeb04cf6671
Merge: 0e7f96c eb8f75c
Author: JacksonSalyards <95992718+CoolHackerMan27@users.noreply.github.com>
Date:   Thu Oct 24 14:19:43 2024 -0400

    Merge pull request #4 from Multi-Agent-Neuroevolution/feature-rustgui-neural
    
    Feature rustgui neural. Has basic code for displaying the current  state of the neural network

commit 0e7f96ce074ce398a6de819ad1b5f58244b1262e
Merge: 96f3574 e681314
Author: JacksonSalyards <95992718+CoolHackerMan27@users.noreply.github.com>
Date:   Wed Oct 23 15:13:21 2024 -0400

    Merge pull request #3 from Multi-Agent-Neuroevolution/feature-rustgui-agentcontrolls
    
    Added agentview controlls and moved each view to its own struct for bΓÇª

commit e681314744a737a999bf44dce8e1718204a0a334
Author: CoolHackerMan27 <jacksonsalyards55@gmail.com>
Date:   Wed Oct 23 14:14:17 2024 -0400

    Added agentview controlls and moved each view to its own struct for better readability and modularity. These controlls/buttons are just placeholders currently.

commit 96f3574b687fcd143b11ff6296e0f466c2ea4c06
Merge: 893f4f0 8099519
Author: JacksonSalyards <95992718+CoolHackerMan27@users.noreply.github.com>
Date:   Thu Oct 17 21:19:30 2024 -0400

    Merge pull request #2 from Multi-Agent-Neuroevolution/feature-rustgui-neural
    
    added neural net object skeleton

commit 893f4f0b0101b4c6b4611c0a931a6c943fada7c8
Author: CoolHackerMan27 <SALYARDJ@my.erau.edu>
Date:   Tue Oct 8 19:46:21 2024 -0400

    basic UI wireframe created, ready for more development with other funtions and features

commit c2958245ad006e723e73623b8b42ec1d5058fed0
Author: CoolHackerMan27 <SALYARDJ@my.erau.edu>
Date:   Sun Oct 6 00:14:35 2024 -0400

    added basic skeleton for sim view nn view and agent view. This is very basic, but should be able to support the basic 2D graphuics required later on.

commit c20abc1eaf5e0b7eeb1d55458bdf9c42b99937b2
Author: CoolHackerMan27 <SALYARDJ@my.erau.edu>
Date:   Sat Oct 5 22:22:34 2024 -0400

    added basic rust gui and the gitignore

commit 3eaa49b38b62838c24fa17937a245b694bf317c2
Author: CoolHackerMan27 <jacksonsalyards55@gmail.com>
Date:   Fri Oct 4 11:00:27 2024 -0400

    added iced rust crate

