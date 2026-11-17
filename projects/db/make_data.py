"""Generates synthetic CSV data for the BabsonAI Labs database (projects/db).

No third-party packages required -- only the standard library. Run it from
anywhere; it always writes into projects/db/data/, next to this file:

    python3 make_data.py

Writes: people.csv, projects.csv, assignments.csv, tasks.csv, expenses.csv

Rules followed (see README.md for the full scenario):
  - every person reports to at most one other person, who also works here
  - a budget is more than zero, and so is every expense
  - a task belongs to exactly one project, is assigned to at most one person,
    and is never completed before it was created
  - nobody commits more than 40 hours/week to a single project; every
    commitment is at least one hour
  - a project's status is one of planned, active, paused, done
  - a task is assigned only to somebody who works on its project, and never
    before that person's start date -- broken ON PURPOSE in exactly two
    tasks. `gen_tasks()` creates those cases, and `main()` prints their IDs
    and reasons so you can compare them with question 7.

Uses a fixed random seed so it writes the same files every time.
"""

# csv: writes each table's rows out as a .csv file, in write_csv() below.
import csv
# random: every "pick one of these" / "pick a date in this range" decision
# in this script goes through this module, seeded once below so the whole
# script is reproducible from run to run.
import random
# date/timedelta: every date in this file -- start dates, due dates,
# expense dates -- is built by adding/subtracting days from a date.
from datetime import date, timedelta
# Path: used once, to find this file's own folder on disk (DATA_DIR
# below), so the script writes into projects/db/data/ no matter what
# directory it's run from.
from pathlib import Path

# A fixed seed means random.choice/random.sample/random.random etc. all
# replay the exact same sequence of "random" values every time this
# script runs -- which is what makes the CSVs it writes identical from run
# to run.
SEED = 42
random.seed(SEED)

# The single reference date every other date in this file is measured
# against: "today," as far as the generated company is concerned.
# Changing this one constant shifts every generated date along with it.
AS_OF = date(2026, 11, 8)
# No person, project, task or expense predates this -- BabsonAI Labs
# "started" on this day.
FOUNDING_DATE = date(2024, 6, 1)
WINDOW_START = AS_OF - timedelta(days=365)  # the 12 months the data must cover

# Resolves to projects/db/data/, relative to *this file's own* location:
# __file__ is make_data.py's own path, .resolve() makes it absolute, and
# .parent is the projects/db/ folder it lives in -- so this script always
# writes into the right data/ folder regardless of the working directory
# it's launched from.
DATA_DIR = Path(__file__).resolve().parent / "data"

# ---------------------------------------------------------------- reference data
# Everything in this section is a fixed pool of realistic-looking values
# the gen_*() functions below draw from with random.choice/random.sample --
# none of it is computed, and none of it is unique to any one generated
# row.

# First and last names are combined, in gen_people() below, into 25
# distinct people; used_names there keeps any (first, last) pairing from
# repeating within one run.
FIRST_NAMES = [
    "Olivia", "Liam", "Emma", "Noah", "Ava", "Ethan", "Sophia", "Mason",
    "Isabella", "Lucas", "Mia", "Elijah", "Amelia", "James", "Harper",
    "Benjamin", "Evelyn", "Henry", "Abigail", "Alexander", "Emily", "Jack",
    "Ella", "Owen", "Scarlett", "Daniel", "Grace", "Matthew", "Chloe",
    "Samuel", "Victoria", "David", "Zoe", "Joseph", "Lily",
]
LAST_NAMES = [
    "Nguyen", "Smith", "Patel", "Garcia", "Chen", "Johnson", "Kim", "Brown",
    "Rodriguez", "Martinez", "Lee", "Walker", "Perez", "Hall", "Young",
    "Allen", "Sanchez", "Wright", "Torres", "Ramirez", "Collins", "Murphy",
    "Cook", "Rivera", "Bell", "Cooper", "Richardson", "Cox", "Howard",
    "Ward",
]

# The job-title ladder gen_people() builds the org chart from: exactly
# two founders (report to nobody), a handful of leads (each reports to a
# founder), and everyone else an individual contributor (reports to a
# founder or a lead).
FOUNDER_TITLES = ["Co-Founder & CEO", "Co-Founder & CTO"]
LEAD_TITLES = ["Engineering Lead", "Data Lead", "Product Lead", "Client Success Lead"]
IC_TITLES = [
    "AI Engineer", "Data Engineer", "ML Engineer", "Founding Engineer",
    "Data Scientist", "Product Designer", "QA Engineer", "Account Manager",
    "Business Analyst", "Customer Success Associate", "Software Engineer",
]

# CATEGORIES / STATUSES_POOL / EXPENSE_CATEGORIES mirror the CHECK
# constraints in build.py exactly -- these are the only legal values the
# database will accept for projects.category, projects.status and
# expenses.category respectively. (STATUSES_POOL itself turns out unused
# below -- gen_projects() builds a specific status_plan list instead of
# drawing randomly from this pool; it's kept here as the authoritative
# list of the four legal status values.)
CATEGORIES = ["LLM app", "data pipeline", "internal tool"]
STATUSES_POOL = ["planned", "active", "paused", "done"]
EXPENSE_CATEGORIES = ["GPU cloud", "data labeling", "software", "travel"]

# The clients BabsonAI Labs' non-internal projects can belong to --
# gen_projects() samples from this list without replacement, so no two
# projects share a client by accident within one run.
CLIENT_NAMES = [
    "Riverside Dental", "Maple Street Bakery", "Chen Family Orthodontics",
    "Union Hardware", "Northside Veterinary", "Harbor Point Realty",
    "Glenwood Landscaping", "Third Avenue Bookshop", "Pinecrest Dental Group",
    "Lakeside Physical Therapy", "Summit Legal Partners", "Brightline Tutoring",
    "Coastal Coffee Roasters", "Maverick Auto Repair",
]

# One list of name templates per project category; gen_projects() formats
# "{client}" into whichever template it draws for a project's category, or
# uses the template as-is for "internal tool" projects (where client is
# None).
NAME_TEMPLATES = {
    "LLM app": [
        "{client} Support Chatbot", "{client} Sales Assistant",
        "{client} Intake Chatbot", "{client} Knowledge Base Copilot",
    ],
    "data pipeline": [
        "{client} Inventory Pipeline", "{client} Analytics Pipeline",
        "{client} CRM Data Sync", "{client} Reporting Pipeline",
    ],
    "internal tool": [
        "Internal Time Tracker", "Internal Hiring Dashboard",
        "Internal Expense Tool", "Internal Project Tracker",
        "Internal Client Health Dashboard", "Internal QA Dashboard",
        "Internal Billing Tool", "Internal Onboarding Portal",
    ],
}

# The job a person holds on one specific project (assignments.role) --
# independent of their company-wide title in people; drawn at random in
# gen_assignments().
ROLE_POOL = [
    "Lead Engineer", "ML Engineer", "Data Engineer", "Project Manager",
    "Account Lead", "QA", "Designer", "Analyst",
]

# What a task is, in plain English -- gen_tasks() picks one at random per
# task; the same description can recur across many unrelated tasks, same
# as a real company would reuse short task titles.
TASK_DESCRIPTIONS = [
    "Set up evaluation harness", "Write integration tests",
    "Draft client onboarding doc", "Label training examples",
    "Tune prompt templates", "Build ETL for client data",
    "Fix data pipeline bug", "Prepare weekly status report",
    "Review model outputs for quality", "Deploy to staging",
    "Set up monitoring dashboard", "Conduct user interview",
    "Write API documentation", "Refactor data ingestion script",
    "Create demo for client", "Clean duplicate records",
    "Set up CI pipeline", "Design database schema",
    "Implement authentication", "Optimize inference latency",
    "Scope follow-on phase", "Write unit tests for parser",
    "Sync with client stakeholders", "Benchmark model versions",
]

# A short, category-appropriate note for an expense; keyed by expense
# category so a "GPU cloud" expense never gets a "Conference travel"
# note, for example.
EXPENSE_NOTES = {
    "GPU cloud": ["Training run", "Inference hosting", "Fine-tuning job", "Batch eval run"],
    "data labeling": ["Annotation batch", "QA pass on labels", "Vendor labeling invoice"],
    "software": ["SaaS subscription", "API credits", "Dev tooling license"],
    "travel": ["Client site visit", "Conference travel", "Team offsite"],
}


def random_date(start, end, weekday_bias=True):
    """A uniform random date in [start, end] -- except a first pass at this
    generator spread task/expense dates flat across all seven days of the
    week, which doesn't look like a real company (see 'A Look at the Data'
    in build.py). weekday_bias re-rolls weekend dates most of the time, so
    the week now looks like one a business actually runs."""
    # Callers aren't always careful about which of start/end is earlier;
    # swapping here means the rest of the function can safely assume
    # start <= end.
    if end < start:
        start, end = end, start
    # The number of days spanned by the range -- the upper bound for the
    # random offset drawn below.
    days = (end - start).days
    # Tries up to 8 times to land on a weekday (or win the 15% weekend
    # coin-flip below) before giving up and returning whatever the 8th try
    # was; 8 attempts makes landing on a weekend all 8 times astronomically
    # unlikely, so this loop effectively never falls through without an
    # early return.
    for _ in range(8):
        # max(days, 0) guards against a negative range (not expected to
        # happen given the swap above, but kept as a safety net); randint
        # is inclusive of both ends, so every day in [start, end] is
        # reachable.
        d = start + timedelta(days=random.randint(0, max(days, 0)))
        # Accepts this date if weekday bias is turned off, if it's already
        # a Monday-Friday (weekday() < 5), or -- about 15% of the time --
        # even though it's a weekend, so weekends aren't impossible, just
        # rarer.
        if not weekday_bias or d.weekday() < 5 or random.random() < 0.15:
            return d
    # Only reached if all 8 tries landed on a weekend and all 8 coin-flips
    # came up against it; returns that last weekend date rather than
    # looping forever.
    return d


def write_csv(path, fieldnames, rows):
    # Makes sure projects/db/data/ exists before writing into it;
    # exist_ok=True makes this a no-op if the folder is already there.
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # newline="" is the standard-library recommendation when a file is
    # opened for the csv module to write into -- it stops Python's own
    # newline translation from interfering with the line endings csv
    # writes itself.
    with open(path, "w", newline="") as f:
        # One CSV column per name in fieldnames, in that order -- not
        # whatever order each row dict's own keys happen to be in.
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        # Writes the header row, from fieldnames.
        writer.writeheader()
        for row in rows:
            # CSV has no native "this cell is empty" marker the way SQL
            # has NULL; writing None as the literal text "None" would
            # corrupt the column (e.g. people.manager_id,
            # tasks.assigned_to), so every None becomes an empty string
            # instead -- which build.py's loader (and DuckDB's
            # read_csv_auto) reads back as NULL/blank.
            writer.writerow({k: ("" if v is None else v) for k, v in row.items()})


# ---------------------------------------------------------------- people

def gen_people(n=25):
    # The final flat list of all n people, in the exact order they're
    # created -- founders first, then leads, then everyone else. Because
    # person_id is assigned as len(people) grows, this order is also
    # exactly increasing person_id order, which is what lets build.py's
    # "sort by person_id, then INSERT one row at a time" trick guarantee
    # every manager is already in the table before their first report is
    # inserted.
    people = []
    # Tracks every work_email already handed out, so make_person() can
    # detect a collision and disambiguate it.
    used_emails = set()
    # Tracks every (first, last) name pair already used, so no two people
    # in this run share an identical full name.
    used_names = set()

    def make_person(person_id, title, manager_id, start_date):
        # Keeps drawing a random first/last name pair until it finds one
        # that hasn't been used yet in this run, then reserves it.
        while True:
            first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
            if (first, last) not in used_names:
                used_names.add((first, last))
                break
        # The default email pattern: firstname.lastname@babsonailabs.com,
        # lower-cased.
        email = f"{first.lower()}.{last.lower()}@babsonailabs.com"
        suffix = 1
        base_email = email
        # In the rare case two different (first, last) pairs would still
        # produce the same email -- not actually possible here since names
        # are unique, but kept as a safety net -- appends a digit before
        # the @ (e.g. jane.smith2@...) until the email is unused, so
        # work_email's UNIQUE constraint in build.py is never at risk.
        while email in used_emails:
            suffix += 1
            email = base_email.replace("@", f"{suffix}@")
        used_emails.add(email)
        # One row of people, as a dict whose keys match the CSV's column
        # names exactly.
        return {
            "person_id": person_id,
            "first_name": first,
            "last_name": last,
            "work_email": email,
            "title": title,
            "start_date": start_date,
            "manager_id": manager_id,
        }

    # two founders, report to nobody
    # manager_id=None satisfies "the two founders report to nobody," and
    # both start on FOUNDING_DATE -- the earliest possible start_date
    # anywhere in this dataset.
    founders = []
    for i, title in enumerate(FOUNDER_TITLES, start=1):
        p = make_person(i, title, None, FOUNDING_DATE)
        founders.append(p)
        people.append(p)

    # a handful of leads, each reporting to a founder
    n_leads = len(LEAD_TITLES)  # computed but not read again below -- len(LEAD_TITLES) is used directly in the for loop's enumerate() instead
    leads = []
    # Leads pick up numbering right after the founders (ids 3, 4, 5, ...
    # for 2 founders).
    next_id = len(founders) + 1
    for i, title in enumerate(LEAD_TITLES):
        # Alternates leads between the two founders (i % len(founders)
        # cycles 0, 1, 0, 1, ...), so each founder ends up managing
        # roughly half the leads.
        manager = founders[i % len(founders)]
        # A lead starts sometime in the company's first 30-270 days --
        # always after the founder they report to (FOUNDING_DATE), and
        # always comfortably before AS_OF.
        start = random_date(FOUNDING_DATE + timedelta(days=30), FOUNDING_DATE + timedelta(days=270))
        p = make_person(next_id, title, manager["person_id"], start)
        leads.append(p)
        people.append(p)
        next_id += 1

    # Anyone who can manage somebody else: both founders and all leads.
    managers_pool = founders + leads

    # everybody else: individual contributors reporting to a founder or a lead
    # Keeps adding individual contributors until the full roster reaches n
    # people.
    while len(people) < n:
        # Picks any founder or lead at random to be this person's manager.
        manager = random.choice(managers_pool)
        # Never lets a report start less than 30 days after their manager
        # did -- a manager has to exist and be established before they
        # can have reports.
        earliest = manager["start_date"] + timedelta(days=30)
        # Never lets anyone start less than 10 days before AS_OF, so every
        # individual contributor has had at least a little time at the
        # company by AS_OF.
        latest = AS_OF - timedelta(days=10)
        start = random_date(earliest, latest)
        title = random.choice(IC_TITLES)
        p = make_person(next_id, title, manager["person_id"], start)
        people.append(p)
        next_id += 1

    return people


# ---------------------------------------------------------------- projects

def _template_deck(templates):
    """Yields templates in shuffled order with no repeats until the list is
    exhausted, then reshuffles -- keeps project names from colliding."""
    # This is a generator function (it has a `yield` below), so calling
    # _template_deck(...) doesn't run this body yet -- it returns an
    # iterator that advances up to the next yield each time next() is
    # called on it, which is exactly what `next(name_decks[category])`
    # does in gen_projects() below.
    pool = []
    while True:
        # Refills and reshuffles once the deck runs out -- like a deck of
        # cards, every template gets used once before any repeats.
        if not pool:
            pool = list(templates)
            random.shuffle(pool)
        # Hands back (and removes) the last template in the shuffled pool
        # each time this generator is advanced.
        yield pool.pop()


def gen_projects(people, n=14):  # `people` isn't actually read below -- kept in the signature so the call site reads as "projects need to know who might staff them," even though no project field depends on it
    projects = []
    # a concrete, controlled mix of statuses instead of pure randomness
    # Builds the exact count of each status up front (3 planned, 6 active,
    # 2 paused, and whatever's left as done -- n - 11 of them, which is 3
    # when n=14) rather than rolling a random status per project and
    # hoping the mix looks reasonable; this is what guarantees "Answers
    # You Already Knew" (expect 3 planned, in build.py) always comes out
    # at exactly 3, regardless of the random seed.
    status_plan = (
        ["planned"] * 3
        + ["active"] * 6
        + ["paused"] * 2
        + ["done"] * (n - 11)
    )
    # Shuffles so which *project* gets which status is random, even though
    # the count of each status is fixed.
    random.shuffle(status_plan)

    # Samples without replacement, so (as long as there are at least n
    # clients) no client is reused by two different projects' round-robin
    # slot below; min(...) just protects against asking for more clients
    # than CLIENT_NAMES actually has.
    clients_used = random.sample(CLIENT_NAMES, k=min(len(CLIENT_NAMES), n))
    # One shuffled, no-repeats-until-exhausted "deck" of name templates per
    # category (see _template_deck above), so two projects in the same
    # category don't draw the same template back to back.
    name_decks = {cat: _template_deck(NAME_TEMPLATES[cat]) for cat in CATEGORIES}

    for i in range(1, n + 1):
        # status_plan is 0-indexed; project_id i is 1-indexed.
        status = status_plan[i - 1]
        category = random.choice(CATEGORIES)
        if category == "internal tool":
            # internal tool projects have no client (README: "internal
            # projects have none") -- client_name stays NULL in the
            # table.
            client_name = None
        else:
            # Cycles through the sampled clients round-robin (the modulo
            # wraps back to the start if there are more projects than
            # clients).
            client_name = clients_used[(i - 1) % len(clients_used)]

        # Pulls the next not-yet-reused template for this category and
        # fills in the client's name, if there is one.
        template = next(name_decks[category])
        name = template.format(client=client_name) if client_name else template

        if status == "planned":
            # hasn't kicked off yet -- starts after as_of, so it naturally
            # has no assignments, tasks or expenses yet
            # A planned project's start_date is deliberately placed in the
            # future (relative to AS_OF), which is exactly what makes it
            # have zero assignments/tasks/expenses later on -- nothing
            # else has to special-case "planned" projects, since nothing
            # can have happened yet on a project that hasn't started.
            start = AS_OF + timedelta(days=random.randint(7, 60))
        else:
            # Any non-planned project must have already started -- at
            # least 60 days after founding, and at least 21 days before
            # AS_OF (so it's had some time to accumulate activity).
            earliest = FOUNDING_DATE + timedelta(days=60)
            latest = AS_OF - timedelta(days=21)
            start = random_date(earliest, latest)

        if category == "internal tool":
            # Internal tools get a smaller budget range than client work.
            budget = round(random.uniform(10_000, 40_000), 2)
        else:
            budget = round(random.uniform(20_000, 150_000), 2)

        # One row of projects.
        projects.append({
            "project_id": i,
            "name": name,
            "client_name": client_name,
            "category": category,
            "budget": budget,
            "start_date": start,
            "status": status,
        })

    return projects


# ---------------------------------------------------------------- assignments

def gen_assignments(people, projects):
    assignments = []
    # Planned projects haven't started, so nobody can be staffed on them
    # yet -- "staffable" means every other status.
    staffable_projects = [pr for pr in projects if pr["status"] != "planned"]
    # Only active projects count toward the "over 40 hours a week right
    # now" overload check (business question 3), so this subset is reused
    # below.
    active_projects = [pr for pr in projects if pr["status"] == "active"]
    # One set per project, tracking which person_ids are already staffed
    # on it -- every project starts with an empty set, including planned
    # ones (which simply stay empty, since nothing ever adds to them).
    staffed = {pr["project_id"]: set() for pr in projects}

    def add_assignment(person, pr, hours):
        # A person can only be paired with a given project once
        # (assignments' primary key is (person_id, project_id)) -- refuse
        # a second assignment to the same project.
        if person["person_id"] in staffed[pr["project_id"]]:
            return False
        # Nobody can join a project before both the project itself and
        # that person have started.
        earliest = max(pr["start_date"], person["start_date"])
        # If that earliest-possible join date is still in the future
        # (relative to AS_OF), there's no valid day left to assign them on
        # -- refuse.
        if earliest > AS_OF:
            return False
        # One row of assignments: this person, this project, a random
        # role, the hours/week the caller asked for, and a join date
        # somewhere between the earliest possible day and AS_OF.
        assignments.append({
            "person_id": person["person_id"],
            "project_id": pr["project_id"],
            "role": random.choice(ROLE_POOL),
            "hours_per_week": hours,
            "date_joined": random_date(earliest, AS_OF),
        })
        # Marks this pairing as taken, so a later call for the same
        # person+project is correctly refused above.
        staffed[pr["project_id"]].add(person["person_id"])
        return True

    # The normal case: every staffable project gets a small team.
    for pr in staffable_projects:
        # Each project gets a team of 2-7 people.
        team_size = random.randint(2, 7)
        # Only people who could realistically have joined by AS_OF are
        # eligible -- the same start-date logic add_assignment checks
        # itself, applied up front so random.sample doesn't have to retry.
        eligible = [p for p in people if max(pr["start_date"], p["start_date"]) <= AS_OF]
        # Picks the team without replacement (never the same person twice
        # for one project here); min(...) protects against asking for more
        # people than are actually eligible.
        team = random.sample(eligible, k=min(team_size, len(eligible)))
        for person in team:
            # Regular team members commit a modest 2-30 hours/week.
            add_assignment(person, pr, random.randint(2, 30))

    # deliberately overload a few people across two or more active projects
    # (each still <= 40 hrs/week on its own) so business question 3 --
    # "the people above 40 hours a week across all active projects" --
    # has real people to find
    # Picks up to 4 people at random to deliberately overcommit.
    for person in random.sample(people, k=min(4, len(people))):
        # Only active projects this person could already be on (or join)
        # count as candidates for the overload.
        candidates = [pr for pr in active_projects if max(pr["start_date"], person["start_date"]) <= AS_OF]
        random.shuffle(candidates)
        joined = 0
        for pr in candidates:
            # Stops once this person has 2 heavy commitments -- enough to
            # likely push them over 40 hours/week in total without
            # needing a third.
            if joined >= 2:
                break
            if person["person_id"] in staffed[pr["project_id"]]:
                # Already assigned to this project from the first loop
                # above (at 2-30 hrs/week) -- instead of adding a
                # duplicate row (which the composite primary key would
                # reject anyway), finds that existing assignment and
                # bumps its hours up into the heavy 22-32 range.
                for a in assignments:
                    if a["person_id"] == person["person_id"] and a["project_id"] == pr["project_id"]:
                        a["hours_per_week"] = random.randint(22, 32)
                joined += 1
            elif add_assignment(person, pr, random.randint(22, 32)):
                # Not yet on this project -- adds a brand-new heavy
                # assignment. add_assignment can still refuse (e.g. if
                # this person/project pairing fails the start-date check),
                # in which case joined doesn't increment and the loop
                # tries the next candidate project instead.
                joined += 1

    # Returns both the assignment rows themselves and the staffed lookup --
    # gen_tasks() below reuses `staffed` to know who's eligible to be
    # assigned a task on each project.
    return assignments, staffed


# ---------------------------------------------------------------- tasks

def gen_tasks(people, projects, staffed, n=280):
    # Quick id -> row lookups, used throughout this function instead of
    # scanning the full list every time.
    person_by_id = {p["person_id"]: p for p in people}
    project_by_id = {pr["project_id"]: pr for pr in projects}
    # Anything that isn't still "planned" can have tasks (same reasoning
    # as staffable_projects in gen_assignments).
    active_projects = [pr for pr in projects if pr["status"] != "planned"]

    # weight task volume toward active/done projects
    # Builds a pool where each project_id appears multiple times -- more
    # copies means more likely to be drawn by random.choice(pool) below.
    # Active projects get the most tasks, done projects a bit fewer, and
    # paused projects the fewest, reflecting that work mostly happens on
    # live projects -- "planned" projects aren't in active_projects at
    # all, so they get zero tasks, which is correct: nothing can have
    # happened yet on a project that hasn't started.
    weights = {"active": 4, "paused": 2, "done": 3}
    pool = []
    for pr in active_projects:
        pool.extend([pr["project_id"]] * weights[pr["status"]])

    tasks = []
    for task_id in range(1, n + 1):
        # Draws a project_id from the weighted pool -- a project with
        # weight 4 is twice as likely to be picked as one with weight 2.
        project_id = random.choice(pool)
        pr = project_by_id[project_id]
        # A task can't be created before its own project started.
        created = random_date(pr["start_date"], AS_OF)

        # Only people already staffed on this project, who had also
        # already started at the company by this task's created_date, are
        # eligible to be assigned it -- this is exactly the rule business
        # question 7 checks, enforced here so the vast majority of
        # generated tasks obey it (the two exceptions are added on
        # purpose further down).
        team = [pid for pid in staffed[project_id] if person_by_id[pid]["start_date"] <= created]
        assigned_to = None
        # About 12% of tasks are left unassigned (README: "a new task may
        # be unassigned") -- but only if there's actually a team to assign
        # from; an empty team always leaves assigned_to as None.
        if team and random.random() > 0.12:
            assigned_to = random.choice(team)

        # Due 5-30 days after creation.
        due = created + timedelta(days=random.randint(5, 30))

        # The chance this task ends up completed depends on the project's
        # status and whether the task is already overdue: a finished
        # project should have nearly all its tasks done (95%); a task
        # that's already past its due_date is likely (but not certain) to
        # have been finished late (75%); anything else -- not yet due, on
        # a project that's still active or paused -- is unlikely to be
        # done yet (10%), leaving plenty of open tasks for business
        # question 2 ("tasks past due and not completed") to find.
        if pr["status"] == "done":
            complete_chance = 0.95
        elif due < AS_OF:
            complete_chance = 0.75
        else:
            complete_chance = 0.10

        completed = None
        if random.random() < complete_chance:
            # A completed task finishes sometime between its creation and
            # 10 days after its due date (or its creation date, if that's
            # later -- max(...) handles a due date that somehow landed
            # before creation) -- but never after AS_OF, since nothing in
            # this dataset happens "in the future."
            window_end = max(due, created) + timedelta(days=10)
            window_end = min(window_end, AS_OF)
            completed = random_date(created, window_end)

        # One row of tasks.
        tasks.append({
            "task_id": task_id,
            "project_id": project_id,
            "description": random.choice(TASK_DESCRIPTIONS),
            "created_date": created,
            "assigned_to": assigned_to,
            "due_date": due,
            "completed_date": completed,
        })

    # --------- deliberately break the rule in exactly two rows ----------
    # Rule: "a task is assigned only to somebody who works on its project,
    # and never before that person's start date."
    # This is the one rule in the whole scenario that a CHECK constraint
    # can't hold -- it reaches into both people and assignments, not just
    # the tasks row itself -- so build.py can't refuse these two rows at
    # load time, and business question 7's query has to be what catches
    # them instead. `broken` records exactly which two tasks and why, so
    # this section doubles as the write-up the README's "The Data" section
    # points back to.
    broken = []

    # Row A: assign to someone who is NOT staffed on that task's project.
    # Reuses the very first generated task...
    task_a = tasks[0]
    project_id_a = task_a["project_id"]
    # ...and finds the first person in the whole company who is *not* in
    # that project's staffed set -- guaranteed to exist, since each
    # staffed set only ever holds a handful of the 25 people.
    outsider = next(
        p["person_id"] for p in people if p["person_id"] not in staffed[project_id_a]
    )
    # Overwrites this task's assigned_to with that outsider -- now this
    # task is assigned to somebody who has never worked on its project at
    # all.
    task_a["assigned_to"] = outsider
    broken.append(("A", task_a["task_id"], "assigned_to is not staffed on the task's project"))

    # Row B: assign to someone staffed on the project, but back-date the
    # task's created_date to before that person's start_date.
    # Reuses the second generated task...
    task_b = tasks[1]
    project_id_b = task_b["project_id"]
    # ...and grabs any one person who genuinely is staffed on its project
    # (next(iter(...)) just takes an arbitrary element out of that set).
    insider = next(iter(staffed[project_id_b]))
    task_b["assigned_to"] = insider
    # Moves this task's created_date to 30 days *before* that person's
    # start_date -- so even though they really do work on this project,
    # the task predates them joining the company at all.
    task_b["created_date"] = person_by_id[insider]["start_date"] - timedelta(days=30)
    # Keeps the row internally consistent despite the back-dating: a
    # due_date or completed_date that ended up earlier than the new
    # created_date would trip the *other* CHECK constraint on tasks
    # (completed_date >= created_date) and would make no logical sense, so
    # both get nudged forward if needed. This keeps the row broken in
    # exactly the one way business question 7 is meant to catch, and not
    # broken in some other, unintended way too.
    if task_b["due_date"] < task_b["created_date"]:
        task_b["due_date"] = task_b["created_date"] + timedelta(days=14)
    if task_b["completed_date"] is not None and task_b["completed_date"] < task_b["created_date"]:
        task_b["completed_date"] = task_b["created_date"] + timedelta(days=5)
    broken.append(("B", task_b["task_id"], "created_date is before assigned_to's start_date"))

    # Returns the full task list (including the two broken rows, mixed in
    # with everything else) plus `broken`, the answer key main() prints
    # out below and the README documents.
    return tasks, broken


# ---------------------------------------------------------------- expenses

def gen_expenses(projects, n=170):
    # Only a project that has actually started can have incurred an
    # expense.
    fundable = [pr for pr in projects if pr["status"] != "planned"]
    # force at least one non-planned project to have zero expenses on purpose
    # Picks out the single cheapest non-planned project (by budget) to
    # guarantee it ends up with zero expense rows -- business question 5
    # ("the projects with no expenses at all") needs at least one real
    # example to find, and leaving this to pure chance could fail to
    # produce one.
    zero_expense_project = min(fundable, key=lambda pr: pr["budget"])
    # Removes that project from the pool expenses get drawn from, so it's
    # guaranteed to end the run with no expense rows pointing at it.
    fundable = [pr for pr in fundable if pr["project_id"] != zero_expense_project["project_id"]]

    # Same weighting idea as gen_tasks(): active projects draw the most
    # expenses, done projects somewhat fewer, paused projects the fewest.
    weights = {"active": 4, "paused": 2, "done": 3}
    pool = []
    for pr in fundable:
        # Note: unlike gen_tasks' pool (which stores project_ids), this
        # pool stores the project dict itself -- so `pr` below is already
        # the full row, with no project_by_id[...] lookup needed.
        pool.extend([pr] * weights[pr["status"]])

    # The realistic dollar range for an expense, by category -- a GPU
    # bill can run much higher than a software subscription, for
    # instance.
    category_ranges = {
        "GPU cloud": (200, 3000),
        "data labeling": (100, 2000),
        "software": (20, 500),
        "travel": (150, 1200),
    }
    # Which expense categories are plausible for which *project* category,
    # with repeats used as weights (e.g. an LLM app project draws "GPU
    # cloud" twice as often as "software," because GPU cloud appears
    # twice in its list) -- an internal tool project, notably, never
    # generates a "data labeling" or "GPU cloud" expense at all, since
    # neither category appears in its list.
    category_weight = {
        "LLM app": ["GPU cloud", "GPU cloud", "data labeling", "software", "travel"],
        "data pipeline": ["GPU cloud", "data labeling", "data labeling", "software", "travel"],
        "internal tool": ["software", "software", "travel"],
    }

    expenses = []
    for expense_id in range(1, n + 1):
        # Draws a project from the weighted pool (zero_expense_project was
        # already excluded from `fundable` above, so it can never be drawn
        # here).
        pr = random.choice(pool)
        # Picks a category that makes sense for this project's own
        # category.
        category = random.choice(category_weight[pr["category"]])
        low, high = category_ranges[category]
        amount = round(random.uniform(low, high), 2)
        # An expense can't predate its own project.
        expense_date = random_date(pr["start_date"], AS_OF)
        # One row of expenses.
        expenses.append({
            "expense_id": expense_id,
            "project_id": pr["project_id"],
            "expense_date": expense_date,
            "amount": amount,
            "category": category,
            "note": random.choice(EXPENSE_NOTES[category]),
        })

    # Returns the expense rows plus the id of the project deliberately
    # left with none, so main() can report it below.
    return expenses, zero_expense_project["project_id"]


# ---------------------------------------------------------------- main

def main():
    # Builds every table in dependency order: people first (depends on
    # nothing), then projects (also depends on nothing, but logically
    # comes next), then assignments (needs both people and projects to
    # exist), then tasks (needs assignments' `staffed` lookup), then
    # expenses (needs only projects).
    people = gen_people(25)
    projects = gen_projects(people, 14)
    assignments, staffed = gen_assignments(people, projects)
    tasks, broken = gen_tasks(people, projects, staffed, 280)
    expenses, zero_expense_project_id = gen_expenses(projects, 170)

    # Each write_csv call's fieldnames list fixes that CSV's column order --
    # build.py's INSERT statements list columns in this same order when
    # bulk-loading projects/assignments/tasks/expenses (people is loaded
    # one row at a time instead, by column name, so its CSV's column
    # order doesn't have to match as strictly).
    write_csv(
        DATA_DIR / "people.csv",
        ["person_id", "first_name", "last_name", "work_email", "title", "start_date", "manager_id"],
        people,
    )
    write_csv(
        DATA_DIR / "projects.csv",
        ["project_id", "name", "client_name", "category", "budget", "start_date", "status"],
        projects,
    )
    write_csv(
        DATA_DIR / "assignments.csv",
        ["person_id", "project_id", "role", "hours_per_week", "date_joined"],
        assignments,
    )
    write_csv(
        DATA_DIR / "tasks.csv",
        ["task_id", "project_id", "description", "created_date", "assigned_to", "due_date", "completed_date"],
        tasks,
    )
    write_csv(
        DATA_DIR / "expenses.csv",
        ["expense_id", "project_id", "expense_date", "amount", "category", "note"],
        expenses,
    )

    # A plain-text summary printed to the terminal every time this script
    # runs -- not written to any file -- so whoever runs `python3
    # make_data.py` can immediately see the row counts and, crucially,
    # exactly which two rows were broken on purpose and why, without
    # having to query the database first.
    print(f"as_of date: {AS_OF}")
    print(f"people: {len(people)}")
    print(f"projects: {len(projects)}")
    print(f"assignments: {len(assignments)}")
    print(f"tasks: {len(tasks)}")
    print(f"expenses: {len(expenses)}")
    print(f"project with zero expenses on purpose: project_id={zero_expense_project_id}")
    print("Rows that break the 'assignee works on project' rule on purpose:")
    for label, task_id, reason in broken:
        print(f"  {label}: task_id={task_id} ({reason})")


# Only runs main() when this file is executed directly (`python3
# make_data.py`) -- not when build.py or anything else imports names out
# of this module instead.
if __name__ == "__main__":
    main()
