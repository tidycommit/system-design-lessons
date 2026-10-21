# System Design Lessons

One daily system design lesson. Each lesson covers:

- **Concept**: the core idea, explained plainly
- **Diagram**: a Mermaid diagram (renders right on GitHub)
- **Real-world example**: how real systems use it
- **Tradeoffs**: what you gain and what you give up
- **Try this**: a question to test your understanding

A new lesson is added every day after 5 AM ET.

## Lessons

<!-- LESSONS:START -->

| # | Lesson | Sent |
|---:|---|---|
| 01 | [Caching patterns (cache-aside vs. write-through)](lessons/01-caching.md) | 2026-09-29 |
| 02 | [Load balancing](lessons/02-load-balancing.md) | 2026-09-30 |
| 03 | [Latency vs. throughput](lessons/03-latency-vs-throughput.md) | 2026-10-01 |
| 04 | [Vertical vs. horizontal scaling](lessons/04-vertical-vs-horizontal-scaling.md) | 2026-10-03 |
| 05 | [SQL vs. NoSQL, picking a data store](lessons/05-sql-vs-nosql.md) | 2026-10-04 |
| 06 | [Database replication — copies are easy, agreement is hard](lessons/06-replication.md) | 2026-10-05 |
| 07 | [Sharding, or splitting one database into many](lessons/07-sharding.md) | 2026-10-06 |
| 08 | [Consistency models, or what a read actually promises](lessons/08-consistency-models.md) | 2026-10-07 |
| 09 | [Message queues vs. event streams](lessons/09-queues-vs-streams.md) | 2026-10-08 |
| 10 | [Rate limiting](lessons/10-rate-limiting.md) | 2026-10-09 |
| 11 | [Idempotency, or how to make retries safe](lessons/11-idempotency.md) | 2026-10-10 |
| 12 | [CDNs, or moving your bytes closer to the user](lessons/12-cdns.md) | 2026-10-11 |
| 13 | [Consensus](lessons/13-consensus-raft.md) | 2026-10-12 |
| 14 | [Observability](lessons/14-observability.md) | 2026-10-13 |
| 15 | [Case study, designing a URL shortener](lessons/15-url-shortener.md) | 2026-10-14 |
| 16 | [Case study, designing a news feed](lessons/16-news-feed.md) | 2026-10-15 |
| 17 | [Case study: a chat app](lessons/17-chat-app.md) | 2026-10-16 |
| 18 | [Case study: ride-sharing](lessons/18-ride-sharing.md) | 2026-10-17 |
| 19 | [Case study: notification system](lessons/19-notification-system.md) | 2026-10-18 |
| 20 | [Case study: distributed cache](lessons/20-distributed-cache.md) | 2026-10-19 |
| 21 | [Case study: search typeahead](lessons/21-typeahead.md) | 2026-10-20 |
| 22 | [Case study: video streaming](lessons/22-video-streaming.md) | 2026-10-21 |

_22 lessons so far._

<!-- LESSONS:END -->

## Updating the index

After adding a new `lessons/NN-slug.md` file, regenerate the table above:

```sh
python3 scripts/build-index.py
```
