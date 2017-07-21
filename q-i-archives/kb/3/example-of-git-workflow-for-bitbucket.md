
---
slug: 3/example-of-git-workflow-for-bitbucket
title: Example of Git Workflow for BitBucket
author: admin
date: 1496496001104

tags: 
categories: Knowledge Base

link: https://quantum-integration.org/topic/3/example-of-git-workflow-for-bitbucket
---

# Branching strategy

## Master branch

There is a *master* branch which holds current state of the project. master branch must provide a working state of the code all the time.

If master is broken - development and merges to master branch are blocked until situation is resolved.

To keep master in a working state, direct pushes to master branch are disabled. Every change to master branch must come from a pull-requests which passes tests and gets approval from code reviewers.


## Feature branch

Every change is developed in a dedicated feature branch *feature/<TASK-ID>-some-meaningful-description*.

```txt
    ---- A ---- B ---- C ---- D ----  master
          \
           \
            \
             E ---- F ----            feature/TASK-123-add-gradle-scripts
```

Feature branch is merged to master via pull-request.

## Release branch

Release branch is created manually from a certain "good enough" point on a master branch and must be named *release/<version>*.

Release candidate is built from release branch.

Direct push to release branch is forbidden. Changes to release branch come via pull-requests from bugfix-branches.

Once release is deployed to production, release branch needs to be merged back to master.

## Bugfix branch

*bugfix*-branches for *release/smth* are the same as *feature*-branches for *master*.

bugfix branch created from branch *release/X.Y.Z* can only be merged to the same *release/X.Y.Z* branch.

Never merge it to master, feature-branch or any other release branch.

# Tips and Tricks

## Always create feature branch from master

Never create a branch from another feature branch.

Wrong:

```txt
    ---- A ---- B ---- C ---- D ----  master
          \
           \
            \
             E ---- F ----            feature/TASK-123-add-gradle-scripts
                     \
                      \
                       \
                        G ----        feature/TASK-345-add-functionality-XYZ
```

Correct:

```txt
                    G ----            feature/TASK-345-add-functionality-XYZ
                   /
                  /
                 /
    ---- A ---- B ---- C ---- D ----  master
          \
           \
            \
             E ---- F ----            feature/TASK-123-add-gradle-scripts
```

The main goal of this rule is that we need to avoid merges and keep history as linear as possible. With merges you can no longer see the linear history of the changes, and can not navigate with them easily.

There might be the case when you have part one of a feature implemented in a branch and it is ready to merge as it is. But while it is still on review, you want to keep working on this new codebase.

In the ideal world you should wait till the feature branch is merged. The idea is that you start additional improvements and refactoring of the code only when it is already accepted to the mainline and you can be sure that there will be no new changes. While code is on review, it might be that you will need to change it, which then will cause rewriting of all the new code you have written so far.

If it is impossible (the review is pending but you *need* to keep working on the feature), the other option would be:

### Step 1. Create new branch for next part of the feature
```txt
    ---- A ---- B ----             master
          \
           \
            \
             E ---- F                 feature/TASK-123-part-1
                     \
                      \
                       \
                        G ----        feature/TASK-123-part-2
```

### Step 2. Create pull-request for feature/TASK-123-part-1 (the F commit) and keep working in the branch feature/TASK-123-part-2 (commit G)

### Step 3. Once feature/TASK-123-part-1 is accepted, rebase feature/TASK-123-part-2 on master

```txt
    ---- A ---- B ---(merge-commit)- C ---- D ----            master
          \             /                    \
           \           /                      \
            \         /                        \
             E ---- F                           G ----        feature/TASK-123-part-2
```

### Step 4. Keep working on feature/TASK-123-part-2 as an independent feature branch.

The third step is very important as it will eliminate the complexity in the merge of feature/TASK-123-part-2 to master later on.

## Use small independent commits

If you can split the task into series of independent commits, create independent feature-branches for each of them.

The smaller your feature branch is - the easier it is for review and testing. Ideally, every feature branch should contain just one atomic commit. And it should be merged to master as soon as commit is ready and passed test and review.

Ok:

```txt
    ---- A -- B -- C -- merge ---- D ----  master
          \              /
           \            /
            \          /
             E ------ F                    feature/TASK-123-add-gradle-scripts-and-clean-env.yaml
```

But better:

```txt
                              F               feature/TASK-123-clean-environment.yml
                             / \
                            /   \
                           /     \
    ---- A - B - merge -- C -- merge -- D --  master
          \     /
           \   /
            \ /
             E                                feature/TASK-123-add-gradle-scripts

```

Do not wait for the end of the sprint or for full feature implementation to merge the working code.

## Never merge to feature-branch, rebase

Merges bring complexity and increase amount of work required to track changes and manage branches. Avoid them and use rebase instead.

Rebase reapplies your changes in the same order you did them on top of the master branch, thus it keeps history straightforward.

Good:
```txt
    ---- A ---- B ---- C ---- D ----  master
          \
           \
            \
             E ---- F ----            feature/TASK-123-add-gradle-scripts


    $ git checkout feature/TASK-123-add-gradle-scripts
    $ git rebase master


    ---- A ---- B ---- C ---- D ----  master
                               \
                                \
                                 \
                                  E'---- F'----  feature/TASK-123-add-gradle-scripts
```

## Rebase often

The smaller the footprint of your change is, the easier it is to handle. The earlier you spot the merge conflict, the easier it is to resolve.

Rebase your branch onto master at least once per day.

## Use push --force

`git push --force` is a dangerous command as it rewrites history of the branch.

It is strictly forbidden to do `push --force` for master and release branches, as these branches are used for collaboration, and their history is critically important and must be kept consistent.

But for feature branches `git push --force` is recommended. It is, in fact, required for rebase to work.

Feature branch is independent and short-living branch and owned by one developer. So one can alter its history without affecting anyone else's work. More to that, it is critically important to keep history of feature branch clean and readable, as it is targeted for review.

Thus, while you are working on a yet unmerged feature branch, use interactive rebase, squashing and amending technics to clean the history, modify comments and adjust their order. And then use `git push --force` for this branch to publish it to Bitbucket.

If you create pull-request from a feature branch, and then change and update the branch with `push --force`, Bitbucket will automatically update the pull-request for you.

