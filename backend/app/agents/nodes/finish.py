"""Turn tool results into what the user should study next."""

from collections import defaultdict

STUDY = {
    "Array": {
        "how": "Solve one-pass array problems before adding extra data structures.",
        "focus": "Keep one running value and finish the array in a single scan.",
        "problems": [
            ("Best Time to Buy and Sell Stock", "Easy", "One pass, one running minimum."),
            ("Maximum Subarray", "Medium", "Extend or restart the current sum."),
            ("Product of Array Except Self", "Medium", "Prefix and suffix without division."),
        ],
    },
    "Hash Table": {
        "how": "Store what you have already seen, then answer the current item in constant time.",
        "focus": "Write down the key before writing the loop.",
        "problems": [
            ("Two Sum", "Easy", "Store the complement as you scan."),
            ("Group Anagrams", "Medium", "Use the sorted word as the key."),
            ("Subarray Sum Equals K", "Medium", "Prefix sums in a map."),
        ],
    },
    "Two Pointers": {
        "how": "After each wrong answer, name which pointer should have moved.",
        "focus": "Move only the side that is still invalid.",
        "problems": [
            ("Container With Most Water", "Medium", "Move the shorter side."),
            ("3Sum", "Medium", "Sort, then skip duplicates."),
            ("Sort Colors", "Medium", "Three regions, one swap at a time."),
        ],
    },
    "Sliding Window": {
        "how": "Write the grow-and-shrink template once. Shrink only when the constraint breaks.",
        "focus": "The window only moves forward. Do not rescan.",
        "problems": [
            ("Longest Substring Without Repeating Characters", "Medium", "Shrink until the duplicate leaves."),
            ("Minimum Size Subarray Sum", "Medium", "Shrink while the sum is still enough."),
            ("Max Consecutive Ones III", "Medium", "The constraint is the number of zeros inside."),
        ],
    },
    "Binary Search": {
        "how": "Practice the lower-bound form on a sorted range, then search on the answer.",
        "focus": "Keep the invariant: the answer is still inside the range.",
        "problems": [
            ("Binary Search", "Easy", "Classic half-open range."),
            ("Search Insert Position", "Easy", "Return the lower bound."),
            ("Koko Eating Bananas", "Medium", "Search the speed, not the array index."),
        ],
    },
    "Stack": {
        "how": "Use a stack when the current item needs the nearest previous unmatched item.",
        "focus": "Pop while the top is finished, then push the current index.",
        "problems": [
            ("Valid Parentheses", "Easy", "Push opens, match closes."),
            ("Daily Temperatures", "Medium", "Store indexes, not just values."),
            ("Largest Rectangle in Histogram", "Hard", "Pop when the bar is shorter than the top."),
        ],
    },
    "Tree": {
        "how": "Name the recursive question for one node before coding the traversal.",
        "focus": "Return a value from the left and right, then combine them.",
        "problems": [
            ("Maximum Depth of Binary Tree", "Easy", "Depth is one plus the deeper child."),
            ("Invert Binary Tree", "Easy", "Swap, then recurse."),
            ("Binary Tree Level Order Traversal", "Medium", "Queue, one level at a time."),
        ],
    },
    "Graph": {
        "how": "Pick BFS for shortest path in an unweighted graph and DFS for reachability.",
        "focus": "Mark a node visited when you enqueue it, not when you dequeue it.",
        "problems": [
            ("Number of Islands", "Medium", "DFS or BFS from every land cell."),
            ("Clone Graph", "Medium", "Map old node to new node."),
            ("Course Schedule", "Medium", "Detect a cycle with indegrees."),
        ],
    },
    "Dynamic Programming": {
        "how": "Write the state in a sentence and two base cases before the loop.",
        "focus": "Fill the table in the order the recurrence reads.",
        "problems": [
            ("Climbing Stairs", "Easy", "Smallest take-or-skip recurrence."),
            ("House Robber", "Medium", "Skip the neighbor you just took."),
            ("Coin Change", "Medium", "Minimum coins to reach the amount."),
        ],
    },
    "Binary Tree": {
        "how": "Treat it as a tree problem: one node, then its children.",
        "focus": "Decide what the function returns before writing the recursion.",
        "problems": [
            ("Same Tree", "Easy", "Both null, or values match and children match."),
            ("Lowest Common Ancestor of a Binary Search Tree", "Medium", "Use the BST order to drop a side."),
            ("Validate Binary Search Tree", "Medium", "Pass an allowed range down."),
        ],
    },
}

CURRICULUM = list(STUDY)


def _solved_map(profile: dict) -> dict[str, int]:
    tags = profile.get("all_tags") or profile.get("tag_stats") or []
    return {tag["tag"]: int(tag["solved"]) for tag in tags}


def _curriculum_solved(solved: dict[str, int], tag: str) -> int:
    aliases = {
        "Graph": ("Graph", "Depth-First Search", "Breadth-First Search"),
        "Binary Tree": ("Binary Tree", "Tree", "Binary Search Tree"),
    }
    names = aliases.get(tag, (tag,))
    return max(solved.get(name, 0) for name in names)


def _gaps(solved: dict[str, int]) -> list[dict]:
    ranked = sorted(CURRICULUM, key=lambda tag: _curriculum_solved(solved, tag))
    gaps = []
    for index, tag in enumerate(ranked[:4]):
        count = _curriculum_solved(solved, tag)
        gaps.append(
            {
                "tag": tag,
                "solved": count,
                "severity": "high" if index < 2 else "medium",
                "how_to_study": STUDY[tag]["how"],
            }
        )
    return gaps


def _loops(submissions: list[dict]) -> list[dict]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in submissions:
        grouped[row["title"]].append(row["status"])

    loops = []
    for title, statuses in grouped.items():
        latest = statuses[0]
        if len(statuses) < 2 or latest == "Accepted":
            continue
        loops.append(
            {
                "title": title,
                "tag": "Recent submissions",
                "attempts": len(statuses),
                "last_status": latest,
                "note": f"{len(statuses)} recent tries, and the latest is still {latest}.",
            }
        )
    return loops[:3]


def build_facts(username: str, profile: dict, contest: dict | None, submissions: list[dict] | None) -> dict:
    """Measured inputs for the model. Contest scores stay as the tool returned them."""
    solved = _solved_map(profile)
    contest = contest or {}
    counts = profile["solved"]
    return {
        "username": username,
        "solved": counts,
        "acceptance_rate": profile.get("acceptance_rate"),
        "thinnest_topics": _gaps(solved),
        "recent_contests": contest.get("recent") or [],
        "contest_rating": contest.get("rating"),
        "contests_attended": contest.get("attended") or 0,
        "stuck_loops": _loops(submissions or []),
    }
