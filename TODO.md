How do we handle if no review exists? Probably ask:
* Set current commit as "reviewed"
* Review since a given revision?

How do we do incremental reviews?
* E.g. some hunks look good, others do not
    * Can we just commit, and then review the next? 
    * Or can we stage only some hunks?

Refactor out the logic for tuicr