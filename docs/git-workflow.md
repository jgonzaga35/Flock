# Typical git workflow

Git's hard, especially at the beginning, but it's super useful. Figured I'd help out with what I got.

## Updating your branch after a merge request (MR) has been merged on gitlab

```bash
$ # you've been doing some work on the awesome-feature branch
$ # a MR has been merged on gitlab!
$ git checkout master                # go on the master branch
$ git pull                           # get updates from gitlab
$ git checkout awesome-feature       # go back on your branch
$ git merge master                   # merge master into your branch
$ # go back to working on your branch
```

## Submitting/updating a merge request

Short version (to update a MR):

```bash
$ # write code
$ # commit
$ pytest
👍 All tests passing. 👊
$ git push
```

Longer version:

```bash
$ # you've been doing some work on aweome-feature, and you want to submit a MR
$ # update your branch with the latest master (see above)
$ pytest
👍 All tests passing. 👊
$ git push

$ # go on gitlab, and create a MR for your branch

$ # your teammate reviewed your MR and found a bug in your code!

$ # fix the bug
$ # commit your changes
$ pytest
👍 All tests passing. 👊
$ git push
$ # your "fix bug" commit now shows up in your MR

$ # your team's been a bit confused about some of the code you wrote half asleep.
$ # you decide you want to add a small comment to clear it up for your team and
  # your future self

$ # write the comment
$ # commit changes
$ pytest
👍 All tests passing. 👊
$ git push

$ # easy as that
```

## The whole story, with more comments

```bash
$ git branch                        # you are on the master branch
  some
  other
* master
  branch
  es

$ git checkout -b awesome-feature   # branch off (creates a new branch) to go
                                    # work on your feature

$ git branch                        # now you're on awesome-feature
  some
  other
  master
  branch
  es
* awesome-feature

$ # do some work, commit stuff on your branch

$ # group's been working hard, a merge request (MR) has been merged into master
$ # (on gitlab)

$ # so we have update our master branch

$ git checkout master                # go on master

$ git pull                           # get latest update from gitlab

$ git checkout awesome-feature       # go back on your branch

$ git merge master                   # merge master into your branch
                                     #
                                     # this way, you solve the conflicts between
                                     # master and your branch on your computer
                                     # (local), when conflicts are still small
                                     # (relatively), rather than at the end when
                                     # everything's diverged like crazy (and you
                                     # get crazy conflicts)

$ # keep working

$ # now you reckon it's good to be merged into master

$ # you check gitlab, no merge request has been merged into master since you
  # last updated it, good to go

$ git push                           # push your branch up to gitlab

$ # you go on gitlab, find your branch, and create a merge request

$ # damn, one of your teammates saw a bug you forgot to patch up in your code

$ # what do you do? It's easy:

$ # fix the bug

$ git add a.py

$ git commit -m "fix bug <description> in a.py" -m "Cheers to <name> for catching that"
                         # first -m: commit title. later -m: commit description

$ pytest                              # make sure all your tests still pass

$ git push                            # push your update back up to gitlab

$ # oops... in the meantime someone's merged another MR into master. You have
  # to update your your branch again. You know the drill now:

$ git checkout master
$ git pull
$ git checkout awesome-feature
$ git merge master

$ pytest                              # just to make sure nothing broke

$ git push                            # push latest version of your branch on gitlab

$ # your new commits shows up on your merge request! (on gitlab)

$ # your teammate sees it, and drops a big fat LGTM.

$ # you smash that merge button.

$ git checkout master                 # go on master
$ git pull                            # get the latest version of master (with your MR!)
$ git checkout -b awesome-feature-2   # branch off to go work on the next feature

$ # and you know the rest ;)
```