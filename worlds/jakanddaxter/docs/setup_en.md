# Jak And Daxter (ArchipelaGOAL) Setup Guide

## Required Software

- A legally purchased copy of *Jak And Daxter: The Precursor Legacy.*
- [The OpenGOAL Mod Launcher](https://jakmods.dev/)
- [The Jak and Daxter .APWORLD package](https://github.com/ArchipelaGOAL/Archipelago/releases)

At this time, this method of setup works on Windows only, but Linux support is a strong likelihood in the near future. 
(OpenGOAL itself supports Linux, and the mod launcher is runnable with Python.)

## Preparations

- Dump your copy of the game as an ISO file to your PC.
- Install the Mod Launcher.
- If you are prompted by the Mod Launcher at any time during setup, provide the path to your ISO file.

## Installation

***OpenGOAL Mod Launcher***

- Run the Mod Launcher and click `ArchipelaGOAL` in the mod list.
- Click `Install` and wait for it to complete.
  - If you have yet to be prompted for the ISO, click Re-Extract and provide the path to your ISO file.
- Click `Recompile`. This may take between 30-60 seconds. It should run to 100% completion. If it does not, see the Troubleshooting section.
- Click `View Folder`. 
  - In the new file explorer window, take note of the current path. It should contain `gk.exe` and `goalc.exe`.

***Archipelago Launcher***

- Copy the `jakanddaxter.apworld` file into your `Archipelago/lib/worlds` directory.
  - Reminder: the default installation location for Archipelago is `C:\ProgramData\Archipelago`.
- Run the Archipelago Launcher.
- From the left-most list, click `Open host.yaml`. In this file, search for `jakanddaxter_options`.
  - If the entry exists, modify the value of `root_directory` and replace it with the path 
    that appeared when you clicked View Folder in the Mod Launcher.
  - If the entry does not exist, you will need to add it to the bottom of this file. It should look like this:
```
jakanddaxter_options:
  # Path to folder containing the ArchipelaGOAL mod executables (gk.exe and goalc.exe).
  root_directory: "C:\Users\<YourName>\AppData\Roaming\OpenGOAL-Mods\archipelagoal"
```
  - And don't forget you will need to modify the value of `root_directory` as mentioned above!
  - Save and close the file.

## Starting a Game

- Run the Archipelago Launcher.
- From the right-most list, find and click `Jak and Daxter Client`.
- 4 new windows should appear:
  - A powershell window will open to run the OpenGOAL compiler. It should take about 30 seconds to compile the game.
    - As before, it should run to 100% completion, and you should hear a musical cue to indicate it is done. 
      If it does not run to 100%, or you do not hear the musical cue, see the Troubleshooting section.
  - Another powershell window will open to run the game.
  - The game window itself will launch, and Jak will be standing outside Samos's Hut.
  - Finally, the Archipelago text client will open.
    - You should see several messages appear after the compiler has run to 100% completion. 
      If you see `The REPL is ready!` and `The Memory Reader is ready!` then that should indicate a successful startup.
- You can *minimize* the 2 powershell windows, **BUT DO NOT CLOSE THEM.** 
  They are required for Archipelago and the game to communicate with each other.
- Now, like many other Archipelago text clients, you can connect to the Archipelago server and start the game!

## Troubleshooting

***Installation Failure***

- If you encounter errors during extraction or compilation of the game when using the Mod Launcher, you may see errors like this:
```
-- Compilation Error! -- 
Input file iso_data/jak1/MUS/TWEAKVAL.MUS does not exist.
```
  - If this occurs, you may need to copy the extracted data to the mod folder manually.
    - From a location like this: `C:\Users\<YourName>\AppData\Roaming\OpenGOAL-Mods\_iso_data`
    - To a location like this: `C:\Users\<YourName>\AppData\Roaming\OpenGOAL-Mods\archipelagoal\iso_data`
    - Then try clicking `Recompile` in the Mod Launcher (ensure you have selected the right mod first!)

***Game Failure***

- If at any point the text client says `The <gk/goalc> process has died`, you will need to restart the appropriate 
  application:
  - Open a new powershell window.
  - Navigating to the directory containing `gk.exe` and `goalc.exe` using `cd`.
  - Run the command corresponding to the dead process:
    - `.\gk.exe --game jak1 -- -v -boot -fakeiso -debug`
    - `.\goalc.exe --game jak1`
  - Then enter the following commands into the text client to reconnect everything to the game.
    - `/repl connect`
    - `/memr connect`
  - Once these are done, you can enter `/repl status` and `/memr status` to verify.
- If the game freezes by replaying the same two frames over and over, but the music still runs in the background,
  you may have accidentally interacted with the powershell windows in the background - they halt the game if you:
  scroll up in them, highlight text in them, etc.
  - To unfreeze the game, scroll to the very bottom of the log output and right click. That will release powershell from
    your control and allow the game to continue.
  - It is recommended to keep these windows minimized and out of your way.

### Known Issues

- The game needs to run in debug mode in order to allow the repl to connect to it. At some point I want to make sure it can run in retail mode, or at least hide the debug text on screen and play the game's introductory cutscenes properly.
- The client is currently not very robust and doesn't handle failures gracefully. This may result in items not being delivered to the game, or location checks not being delivered to the server.
- The game relates tasks and power cells closely but separately. Some issues may result from custom code to add distinct items to the game (like the Fisherman's Boat, the Pontoons, or the Gondola).
- 