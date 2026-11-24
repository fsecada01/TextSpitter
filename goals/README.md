# Goals

Each `*.md` file here is one goal contract for the factory engine. The
file name (without `.md`) is the goal id, and the SHA-256 of the
committed file is the contract id.

- Add a goal: `factory-engine goal new <id> --title "..."`, fill it in,
  check it with `factory-engine goal check`, then commit it to the
  target branch. Merging the file is the approval to build it.
- Change a goal: edit and commit. Work in flight for the old text is
  discarded and the goal is built again from the new text.
- Withdraw a goal: delete the file.

Files starting with `_` and this README are ignored by the engine.
