How do we handle if no review exists? Probably ask:
* Set current commit as "reviewed"
* Review since a given revision?

How do we do incremental reviews?
* E.g. some hunks look good, others do not
    * Can we just commit, and then review the next?
    * Or can we stage only some hunks?

* Handle being on another branch; we probably need to track the "trunk" branch and diff against that. Add an option for fetching the trunk branch.

* Can we handle the "staged changes" case? How does it track in which state the file has been reviewed?

* Can we add a Claude skill so the review is automatically piped into claude?

* Can we do top-down reviews in some way, so we do not review code that is about to be rewritten?

* Can we review in another tool? E.g. VSCode is much faster for symbol-navigation etc. What does Cursor do here?