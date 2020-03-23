# StarCraft II Bank IO
An implementation of two-side data-channel between StarCraft II and the outer world
based on the game data banks.

See Documentation:
 - [Protocol Description](docs/protocol.md)

### Try It Yourself!
1. Open the [Test Map](test-map/Bank%20IO%20Test%20Map.SC2Map) in the Galaxy Editor
2. Launch StarCraft via "Test Document"
3. Post any of these to the chat:
   * `-event request allocate-unit user1 . ThorAP:any`
   * `-event request allocate-unit user1 . Marine:any`
4. Open the created bank file with the text editor, write the event and save

### TODOs - StarCraft
 - [ ] Split Test Map and the Mode
 - [ ] Session KeepAlive support
 - [ ] Wipe out bank on start and fill meta correctly
 - [ ] Basic support of all events
 - [ ] Extended support of all events ("understand what user means not what he types")
