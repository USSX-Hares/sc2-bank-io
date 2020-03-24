# StarCraft II Bank IO
An implementation of two-side data-channel between StarCraft II and the outer world
based on the game data banks.

See Documentation:
 - [Protocol Description](docs/protocol.md)

### Try It Yourself!
1. Open the [Test Map](test-map/Bank%20IO%20Test%20Map.SC2Map) in the Galaxy Editor
2. Launch StarCraft via "Test Document"
3. Post any of these to the chat:
   * `-event request ping`
   * `-event request allocate-unit user1 . ThorAP:any`
   * `-event request allocate-unit user1 . Marine:any`
4. Open the created bank file with the text editor, write the event and save

### Going Deeper: Python API
1. Download & install Python of version 3.6 or higher
from the [official website](https://www.python.org/downloads/)
2. Install dependencies:

    For Windows:
    ```batch
    python -m venv .venv
    .venv\Scripts\activate
    python -m pip install -e .
    ```
    
    For Linux & MacOS:
    ```bash
    python -m venv .venv
    .venv/bin/activate
    python -m pip install -e .
    ```

3. Run example script:
    ```
    python -m starcraft_io.example
    ```
    
    It dumps & removes all responses written by StarCraft
    and sends new Ping Request.
    
    You can repeat the process any number of times.

### TODOs - StarCraft
 - [x] Split Test Map and the Mode
 - [x] Session KeepAlive support
 - [x] Wipe out bank on start and fill meta correctly
 - [ ] Basic support of all events
 - [ ] Extended support of all events ("understand what user means not what he types")
 - [ ] Add grammar, hints & labels for all triggers & functions

### Useful Links:
 - [Python Homepage](https://www.python.org/)
 - [Video: StarCraft 2 Editor Tutorial - Bank Basics](https://www.youtube.com/watch?v=6d_VU-krxOg)
 - [Article: Twitch/StarCraft Integration](https://www.maguro.one/2020/01/fluffy-chatbot.html)
