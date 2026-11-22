# 04. Vertical vs. horizontal scaling

_Sent 2026-10-03_

Your app is getting popular and one machine can't keep up. You can make that machine bigger, or you can add more machines. Those solve different problems, and mixing them up is a classic mistake in interviews and in production.

**Vertical scaling (scaling up)** means giving one server more CPU, RAM, or faster disks. It's simple: no code changes and none of the headaches that come with distributed systems. But the ceiling is hard. There's a biggest machine you can buy, and when it fails, everything fails with it. That ceiling is higher than people think: AWS's u7in-32tb instance offers 896 vCPUs and 32 TiB of RAM, enough to hold a very large database entirely in memory. So "scale up" is a real strategy for a while, not just a stopgap.

**Horizontal scaling (scaling out)** means running many smaller instances behind a load balancer and spreading traffic across them. Capacity grows as you add instances, and one machine dying is usually fine. The catch is that your design has to allow it.

```mermaid
flowchart TB
  subgraph Vertical [Scale up]
    U1[Users] --> Big[One big server]
    Big --> DB1[(Database)]
  end
  subgraph Horizontal [Scale out]
    U2[Users] --> LB[Load balancer]
    LB --> A[App 1]
    LB --> B[App 2]
    LB --> C[App 3]
    A --> DB2[(Shared data store)]
    B --> DB2
    C --> DB2
  end
```

What makes horizontal scaling possible is **stateless app servers**. Any instance can handle any request because sessions and other lasting state live in Redis, a database, or object storage, not in the server's own memory. Sticky sessions, which pin each user to one server, are a temporary crutch: they make failover and autoscaling awkward.

**In the real world:** early Twitter was famous for the "fail whale" error page, because its tightly coupled monolith couldn't absorb traffic spikes. The rebuild split it into many independent services that scale out separately. Netflix runs the same idea at huge scale, with thousands of identical instances that come and go with demand while state lives in databases and caches.

**A second example: how far one box can go.** In January 2012 WhatsApp reported sustaining 2,277,845 open TCP connections on a *single* FreeBSD server running Erlang, with CPU and memory to spare. The work wasn't buying a bigger box; it was removing lock contention in the VM and kernel (especially around timers) and tuning socket and file-descriptor limits. The lesson cuts against reflexive scaling out: for the right workload, careful single-node engineering can beat a sprawling cluster, and it's far simpler to operate. The counterpoint is availability, since that one box is still a single point of failure.

**Tradeoffs and gotchas**
- Vertical scaling is quick to adopt and easy to reason about, until you hit the hardware ceiling or one machine's outage takes everything down.
- Horizontal scaling needs a load balancer, health checks, and shared state. That's more moving parts, plus distributed failure modes like partial outages and request floods when new instances come up.
- Scaling the app tier doesn't help if the database is still one overloaded primary. That's when you reach for read replicas (lesson 6), sharding (lesson 7), or caching (lesson 1).
- Cost isn't always linear. Many small instances can beat one giant machine on both price and availability, but only if your deployment and operations tooling is solid. Going the other way, the very largest instances often carry a price premium per unit of CPU or RAM.
- Autoscaling has lag. New instances take time to boot, warm caches, and open connection pools, so a sudden spike can outrun your scale-out before capacity arrives. Keep headroom.

**When to use which.** Scale up first when the bottleneck is a single stateful component that's hard to split (a primary database, an in-memory index) and you're not yet near the hardware ceiling. Scale out when the work is parallelizable, when you need to survive single-machine failure, or when demand is spiky and you want to add and remove capacity. In practice most systems do both: stateless tiers scale out, a few stubborn stateful cores scale up until they must be sharded.

**Try this:** An API handles about 2,000 requests per second, each user's session takes about 50 MB in the server's memory, and p99 latency keeps climbing under load. Do you scale up first, scale out first, or change the design before adding capacity? What's the one change that sets you up best long term?
