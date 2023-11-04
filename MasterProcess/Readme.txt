It's "MasterProcess" folder.

It contains MasterProcess that recieves queries, and send response for them.

And there is 4 actions in MasterProcess.

(1) Successful Mining recording.
    - Each FullNode sends a message to MasterProcess as soon as solving mining puzzle.
    - Then, Verify and Print it.

(2) Snapshot myBC <ALL> or <Fi>.
    - When excute with '<ALL>', print longest chains that all the FullNodes thinks of as correct.
    - When excute with '<Fi>', print a longest chain that the specified FullNode think of as correct.
        -> 0 <= i <= N-1, when N FullNodes exist.
(3) Verify-transaction <Fi>
    - Print the last transaction in the most recent Block <Fi> tried to mine.
    - And also print the result of verification.

(4) Trace <Vid> <All or k>
    - When excute with '<ALL>', print all transactions for specified vehicle.
    - When excute with '<k>', print k transactions for specified vehicle from the first.