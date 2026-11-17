# The Scenario

BabsonAI Labs is a startup founded by Babson students that builds AI tools for small businesses. It has about 25 people and today tracks its work across spreadsheets and chat threads. This database gives the founders one place to see who works on what, where the money goes, and who is overloaded.

What it keeps today:

- **People** — first name, last name, work email, title, start date, and the person they report to. The two founders report to nobody. A person's work email changes whenever their title changes.
- **Projects** — name, client name (internal projects have none), category (LLM app, data pipeline, or internal tool), budget, start date, and status (planned, active, paused, or done).
- **Who works on which project** — a person can work on several projects, and a project has several people. For each pairing: the person's role on that project, the hours a week they commit to it, and the date they joined it.
- **Tasks** — each belongs to one project: a description, the date it was created, the person it's assigned to (a new task may be unassigned), the due date, and the date it was completed, which stays empty until it is.
- **Expenses** — each belongs to one project: the date, the amount, the category (GPU cloud, data labeling, software, or travel), and a short note.

The rules it works by:

- Every person reports to at most one other person, who also works here.
- A budget is more than zero, and so is every expense.
- A task belongs to exactly one project and is assigned to at most one person. It cannot be completed before it was created.
- Nobody commits more than 40 hours a week to a single project, and every commitment is at least one hour.
- A project's status is one of planned, active, paused, or done.
- A task is assigned only to somebody who works on its project, and never before that person's start date.

# The ERD

```mermaid
erDiagram
  PEOPLE |o--o{ PEOPLE : manages
  PROJECTS ||--o{ TASKS : contains
  PROJECTS ||--o{ EXPENSES : incurs
  PEOPLE ||--o{ ASSIGNMENTS : "is assigned via"
  PROJECTS ||--o{ ASSIGNMENTS : "is staffed via"
  PEOPLE |o--o{ TASKS : "is assigned to"

  PEOPLE {
    int person_id PK
    string first_name
    string last_name
    string work_email
    string title
    date start_date
    int manager_id FK
  }
  PROJECTS {
    int project_id PK
    string name
    string client_name
    string category
    decimal budget
    date start_date
    string status
  }
  ASSIGNMENTS {
    int person_id PK, FK
    int project_id PK, FK
    string role
    decimal hours_per_week
    date date_joined
  }
  TASKS {
    int task_id PK
    int project_id FK
    string description
    date created_date
    int assigned_to FK
    date due_date
    date completed_date
  }
  EXPENSES {
    int expense_id PK
    int project_id FK
    date expense_date
    decimal amount
    string category
    string note
  }
```

# What One Row Means

- One row of **people** represents one person who works at BabsonAI Labs.
- One row of **projects** represents one BabsonAI Labs project, whether it is being planned, is running, has paused, or has finished.
- One row of **assignments** represents one person's commitment to one project (their role on it, the hours a week they give it, and the day they joined).
- One row of **tasks** represents one piece of work on one project, assigned to at most one person.
- One row of **expenses** represents one dated expense against one project.

# Design Choices
