# Reference: Config Files

> The two JSON files that live alongside tag_fixer.py and control its behaviour.

## artist_genres.json — auto-generated cache

**Location:** `/Users/whofarted/Claude/Songs Download/artist_genres.json`
**Git:** Ignored (personal cache, not committed)

Maps lowercased artist names to genre strings. Built automatically as tracks are processed.
Once a genre is found for an artist, all future tracks by that artist use the cached value
without any API calls.

```json
{
  "jim noir": "Alternative",
  "radiohead": "Alternative Rock",
  "fink": "Folk"
}
```

**Edit manually to:**
- Seed genres before processing a new artist
- Fix incorrect genres from automated lookup
- Override what MusicBrainz or Wikipedia returned

## artist_groups.json — user-edited grouping map

**Location:** `/Users/whofarted/Claude/Songs Download/artist_groups.json`
**Git:** Committed

Maps artist names to a shared `ARTISTSORT` / `ALBUMARTISTSORT` key. This groups related
artists in iTunes/Apple Music without changing their display names.

```json
{
  "Grant-Lee Phillips": "Grant Lee Buffalo",
  "Grant Lee Phillips": "Grant Lee Buffalo"
}
```

Key = artist name exactly as it appears in the tag. Value = the sort key to use.

**Use case:** When a solo artist and their band should appear together in your library.
E.g., all Grant Lee Buffalo and Grant-Lee Phillips albums appear under one entry in Apple Music.

## Related

- [genre-pipeline.md](genre-pipeline.md) — how artist_genres.json is used
- [tag-fixer-pipeline.md](tag-fixer-pipeline.md) — step 9 (artist grouping)
