```mermaid
erDiagram
    TV_SHOW ||--|{ EPISODE : has
    EPISODE ||--|{ STAR : features
    EPISODE ||--|{ WRITER : credits
    TV_SHOW ||--|{ RATING : receives

    TV_SHOW {
        int show_id PK
    }

    EPISODE {
        int episode_id PK
        int show_id FK
    }

    STAR {
        int star_id PK
        string address
        int birth_year
        string image
    }

    WRITER {
        int writer_id PK
    }

    GENRE {
        int genre_id PK
    }

    RATING {
        int rating_id PK
        int show_id FK
    }
```

I interpreted the sketch's cardinalities as one TV show having many episodes and ratings, and one episode having many stars and writers. `GENRE` is listed in the sketch but has no relationship drawn. The sketch does not specify keys, so the `*_id` primary keys are placeholders. The Stars attributes are based on the notes for address, birth year, and images.
