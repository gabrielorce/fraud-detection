# Security Scanning

This repo intentionally contains a leaked secret in its git history
(commit <hash>, values.yaml, POSTGRES password) to demonstrate the
difference between:
- a secret present in the current working tree (visible immediately)
- a secret removed from HEAD but still recoverable via git history

Run    
`gitleaks detect --source . -v`   
or    
`trufflehog git file://.`   
to find it. This shows why deleting a file/line is NOT sufficient —
only history rewriting (git filter-repo) or rotation actually
remediates a leaked secret.

Real fix demonstrated in commit <hash>: moved secret to a gitignored
values-secret.yaml + added gitleaks pre-commit hook.