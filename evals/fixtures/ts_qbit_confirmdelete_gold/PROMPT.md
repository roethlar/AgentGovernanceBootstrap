A test in this repository is failing: `src/components/ConfirmDeleteSheet.test.tsx`.

`ConfirmDeleteSheet` renders the confirm/cancel actions for deleting torrents. It has no
"pending" state: while a delete is in flight the sheet stays open, so a double-tap can
fire the delete twice. The failing test specifies that when a `pending` prop is set, the
confirm actions are disabled (and show "Deleting…") and clicking them does nothing, while
the default (not pending) behavior still fires the confirm callback.

Add that `pending` behavior to the component and wire it where the bulk delete sheet is
rendered, so the failing test passes. Do not modify the test.
