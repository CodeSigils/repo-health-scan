Audit this repository before release. Before running repository probes,
identify and read any installed skill relevant to this request. Do not modify
files and do not use network access.

Follow the selected workflow exactly:

1. Emit the structured observed/inferred repository profile before selecting
   health dimensions. Include the core profile fields (`vcs`, `languages`,
   `package_managers`, `ci`, `shell_files`, `recent_commits`, `gitignore`,
   `version_sources`, `script_surface`, and `shipped_payload`). Include
   extended fields such as tags, base, workflow, release, and opt-in state when
   those probes apply. Use `null`, `false`, or `[]` when a known fact is
   absent; keep explanations out of scalar fields.
   Use this shape as a starting point before adding any prose:

   ```yaml
   observed:
     vcs: git
     languages: []
     package_managers: []
     ci: null
     shell_files: false
     recent_commits: false
     gitignore: false
     version_sources: []
     script_surface: ""
     shipped_payload: ""
     tags_present: false
     base_ref: null
     branch_commits_outside_base: null
     working_tree_dirty: false
     workflow_files: []
     release_files: []
     verify_refs: false
     verify_releases: false
   ```
2. Account for every candidate dimension defined by the workflow. Each active
   dimension must cite one or more exact profile paths in `activated_by`; each
   inactive dimension must have a concrete skip reason and `SKIP` status.
   Use the canonical activation paths from the skill (for example,
   `observed.vcs` for history, `observed.ci` for CI, and
   `inferred.release_model` only when it names concrete release evidence).
3. Report findings in blocking, warning, then informational order. Every
   finding must state concrete harm and remediation.

Return the final result using the supplied JSON schema. The fixture contains an
intentional repository-health defect, so do not return an empty findings list.
