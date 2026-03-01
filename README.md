 I'm working on a wrapper for a terminal review tool

Review history exists at `~/Library/Application Support/reviews`.

Filenames are formatted like: `Reboarder_bda41a89_main_commits_20260301_151917_b4922528.json`

Which matches:
`[Project_name]_[Current commit hash]_[Branch name]_[Date]_[Time]_[Review ID].json`

Example content from a file:

```
{
  "id": "d8dc6bf5-2224-446a-b02c-4f691ff871e3",
  "version": "1.2",
  "repo_path": "/Users/martinbernstorff/Documents/life-lessons/.obsidian/plugins/Reboarder/",
  "branch_name": "main",
  "base_commit": "ce0eaacc7f826ff745b58b505591b6ece663590c",
  "diff_source": "commit_range",
  "commit_range": [
    "967a313451e0837ebcd5cd72f5894d393ff3af2d",
    "96bd5428671d6a0ba3368af09b68051cd80222c6",
    "ce0eaacc7f826ff745b58b505591b6ece663590c"
  ],
  "created_at": "2026-03-01T15:30:03.611Z",
  "updated_at": "2026-03-01T15:30:03.611Z",
  "files": {
    "src/View.tsx": {
      "path": "src/View.tsx",
      "reviewed": false,
      "status": "modified",
      "file_comments": [],
      "line_comments": {}
    },
    "src/ReboarderPlugin.tsx": {
      "path": "src/ReboarderPlugin.tsx",
      "reviewed": true,
      "status": "modified",
      "file_comments": [],
      "line_comments": {
        "122": [
          {
            "id": "08cfaa78-3b3a-4f20-9ff9-cb2bb7596c77",
            "content": "If no completed review is found for branch, ask the user if they'd like to set the current commit as \"reviewed\".",
            "comment_type": "note",
            "created_at": "2026-03-01T15:50:57.965716Z",
            "line_context": null,
            "side": "new",
            "line_range": null
          }
        ],
        "33": [
          {
            "id": "43791d14-41ec-4dbf-9f62-2ac2ec9990f8",
            "content": "Also replace these with pydantic rootmodels. created_at should be a datetime.",
            "comment_type": "note",
            "created_at": "2026-03-01T15:47:59.257264Z",
            "line_context": null,
            "side": "new",
            "line_range": {
              "start": 30,
              "end": 33
            }
          }
        ],
        "51": [
          {
            "id": "6d6e8382-157d-4ce4-a23a-617b157adc0e",
            "content": "Explain these args to me (not inline, just in your text output)",
            "comment_type": "note",
            "created_at": "2026-03-01T15:48:25.293648Z",
            "line_context": null,
            "side": "new",
            "line_range": {
              "start": 48,
              "end": 51
            }
          }
        ],
        "41": [
          {
            "id": "88dc3805-5684-4376-a5c7-9f6dbcaadb6e",
            "content": "Use a dataclass, so you don't need the __init__",
            "comment_type": "note",
            "created_at": "2026-03-01T15:48:10.163786Z",
            "line_context": null,
            "side": "new",
            "line_range": null
          }
        ]
      }
    },
  },
  "session_notes": null
}
```

I want to find the most recent _completed_ review for the current branch, and diff that against the current state of the branch (including unstaged changes). A review is completed if all files have `reviewed: true`. If the most recent review is not completed, ask the user whether they'd like to continue that review.

We're writing a Python wrapper that makes that happen. Use `typer` for the CLI.

To open the TUI, we invoke `tuicr --revisions 261c314aed6629bbbecb06da5c37058e735ecab6..HEAD` or similar.