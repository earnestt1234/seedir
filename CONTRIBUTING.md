
# Contributing to seedir

This document describes ways that you can contribute to seedir, progressing in increasing levels of involvement.

## Use it

Simply using this package is helpful!  It is rewarding for me to see more people using it, and makes me want to keep working on it.  Having the code be used in more real world settings is great for detecting use cases and missing features.  Maybe you are already using it if you are reading this... but if not, please give it a try.

## Share it

If you liked seedir or found it useful, sharing it with others is a good way to help the package grow.  Moreover, the package maintainer is basically just me - so sharing the project may be helpful for growing a maintenance community and fostering stable development in the long term.

## Report a bug / request a feature

Please use the [issues page](https://github.com/earnestt1234/seedir/issues) to formally log any sort of suggestion to improve the package.  This can be a bug report, a feature request, documentation improvements, etc.  These are extremely helpful as they can give me a sense of what people are actually doing with the package, and what its drawbacks are.

Note that proposed changes will be implemented at the discretion of the maintainers.

There currently is no formal structure needed for posting an issue.  But some general guidelines:

- If sharing a bug, include a minimally reproducible example - something that I will be able to demonstrate and debug on my own machine.
- Please share code where possible (as plaintext, not as pictures)
- Please be courteous : )

## Contribute code

We welcome anyone who wants to contribute code to seedir!  Expanding the maintainers would be great for the longterm stability of the package.

This has not happened much so far, so the guidelines may evolve over time.   But the general steps should be:

1. Open an issue (or comment on an existing issue) indicating the changes you plan to implement.  Discuss with a maintainer to agree on a general course of action for the proposed changes.
2. [Fork the seedir repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo), and make sure you have the most up-to-date changes from the `dev` branch.
3. Create a branch stemming from the `dev` branch.  Name it whatever you like, but ideally something related to the feature/bug you plan to tackle.
4. Implement your changes, making one or more commits to your created branch.   **Note:** We currently do not have an opposition to generative AI tools (e.g. ChatGPT, Claude, Copilot, etc) being used for aiding with seedir development.  But we ask that you inform us if you have used AI tools for any code slated to be contributed to the seedir codebase.
5. Run the test suite to make sure they still pass.  Add any additional tests needed to cover your changes - or edit existing tests if they are no longer valid following your changes.
6. Add to the [`CHANGELOG.md`](https://github.com/earnestt1234/seedir/blob/master/CHANGELOG.md) to document any changes that occurred.  You can add a header for "DEV" rather than assigning them to a specific version.
7. Create a pull request into the main branch, with a brief summary of what you did.
8. A maintainer should then approve your changes and merge them into `dev`, which will then be merged into `master` at the next version release.

Please raise an issue if these steps are unclear or seem incorrect.   If you are more familiar with this process and have suggestions, please let us know!

