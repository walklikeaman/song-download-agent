# Reference: FLAC Tag Fields

> All tags written, removed, or preserved by tag_fixer.py.

## Tags written

| Tag | Example value | Source | Rule |
|---|---|---|---|
| `albumartist` | `Radiohead` | iTunes `artistName` | Filled if empty; never "Various Artists" |
| `album` | `OK Computer` | iTunes `collectionName` | Filled if empty |
| `date` | `1997` | MusicBrainz ISRC → iTunes → Discogs | MusicBrainz is authoritative (original release year) |
| `tracknumber` | `1/12` | iTunes `trackNumber/trackCount` | Filled if empty |
| `discnumber` | `1/1` | iTunes `discNumber/discCount` | Filled if empty |
| `genre` | `Alternative Rock` | 5-source pipeline | Never left blank |
| `artistsort` | `Grant Lee Buffalo` | `artist_groups.json` | Only if artist is in the groups map |
| `albumartistsort` | `Grant Lee Buffalo` | `artist_groups.json` | Only if artist is in the groups map |
| `lyrics` | *(full text)* | 6-source lyrics chain | Never overwritten if already present |
| *(picture type 3)* | *(JPEG front cover)* | From file / iTunes fallback | Kept as-is; resized to ≤600×600 px if larger |

## Tags removed

| Tag | Condition |
|---|---|
| `encoder` | Always removed |
| `encoded_by` | Always removed |
| `comment` | Removed only if value matches: `lucida`, `downloaded`, `qobuz.com`, `amazon.com`, `tidal.com`, `deezer`, `ffmpeg`, `lavf` |

## Tags never touched

`title`, `artist`, `isrc`, `label`, `copyright`, `composer`, `performer`, `lyricist`, `rating`,
and any tag not listed above. These are preserved exactly as the download source set them.

## Tags never overwritten (once set)

| Tag | Rule |
|---|---|
| `title` | Never modified |
| `artist` | Never modified |
| `date` | Once set by MusicBrainz, never overwritten by iTunes/Discogs |
| `lyrics` | If already present in file, not touched |

## Related

- [tag-fixer-pipeline.md](tag-fixer-pipeline.md) — pipeline order
- [genre-pipeline.md](genre-pipeline.md) — genre tag detail
- [lyrics-pipeline.md](lyrics-pipeline.md) — lyrics tag detail
