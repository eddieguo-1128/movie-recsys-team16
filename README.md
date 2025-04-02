# Overfit-Club Group Project

## Env Setup

- Use Python=3.9

## Flow of creating and merge branch

```shell
# 1. Create and switch to a new branch
git checkout -b feature-branch

# 2. Work on your changes
# (Edit files)
git add .
git commit -m "Added new feature"

# 3. Push branch to remote
git push -u origin feature-branch

# 4. Update with latest main before creating the merge request
git checkout main
git pull origin main
git checkout feature-branch
git rebase main  # Reapply changes on top of latest main
git push --force-with-lease  # Push updated branch safely

# 5. Create a Merge Request on GitHub
# (Go to GitHub → Open a Pull Request → Merge when approved)

# 6. Clean up after merge
git checkout main
git pull origin main  # Get latest merged changes
git branch -d feature-branch  # Delete local branch
git push origin --delete feature-branch  # Delete remote branch

```