def boxes_needed(items, per_box):
    """How many boxes to pack `items`, each holding up to `per_box`.
    items >= 0, per_box >= 1. A partly-full box still counts as one box."""
    return (items + per_box - 1) // per_box
