# 02. Load balancing

_Sent 2026-09-30_

Yesterday was caching, which keeps hot data close. Today's question: once you have more than one server, how do you spread traffic so no single machine becomes the bottleneck?

A load balancer sits in front of a pool of similar backends and picks which one handles each request. Clients talk to one address and the balancer spreads the work out. That gets you horizontal scaling, rolling deploys, and a way to quietly pull unhealthy instances out of rotation.

```mermaid
flowchart LR
  Clients --> LB[Load balancer]
  LB --> A[App server A]
  LB --> B[App server B]
  LB --> C[App server C]
  A --> DB[(Shared data store)]
  B --> DB
  C --> DB
```

**L4 vs. L7**
- **L4 (transport layer)** routes on IP, port, and TCP. It's fast and cheap but can't see anything about HTTP, so it's a good fit for raw throughput and simple TCP services.
- **L7 (application layer)** understands HTTP: paths, hosts, headers, cookies. It can do sticky sessions, path-based routing (`/api` vs. `/static`), and TLS termination. It costs a bit more CPU and gives you far more control.

**How it picks a backend**
- **Round-robin** just cycles through the list. That's fine when every request costs about the same.
- **Least connections** sends each request to whichever server is least busy. It works better when some connections are long-lived, like WebSockets or big uploads.
- **Power of two choices (P2C)** picks two backends at random and sends the request to the less busy one. It gets almost all the benefit of "least loaded" without scanning every server, which is why it's the modern default. Envoy's `LEAST_REQUEST` policy uses P2C with `choice_count` defaulting to 2.
- **Consistent hashing** sends the same key (a user id or cache key) to the same node almost every time. It's useful when backends hold local state, and when one node dies only its own keys move instead of the whole pool reshuffling.

Always pair routing with **health checks**. If a node fails and stays in the pool, one failure quickly spreads into many.

**In the real world:** AWS's ALB (L7) and NLB (L4), nginx, Envoy, or HAProxy in front of app fleets, Kubernetes Services and Ingress, and Cloudflare doing global load balancing at the edge. A common layout uses DNS or a CDN to route users by geography, then an L7 balancer in each region in front of autoscaled app servers.

**A second example: Google's Maglev** (NSDI 2016) is a software L4 load balancer that runs on ordinary Linux servers instead of special hardware. Routers spread packets across many Maglev machines with ECMP (equal-cost multipath), and each machine can saturate a 10 Gbps link with small packets by bypassing the kernel network stack. The clever bit is its consistent-hashing table (sized to a prime larger than 100x the backend count, for under 1% load imbalance) plus per-connection tracking, so a rolling upgrade or a flapping backend reshuffles very few existing connections. It has served Google's traffic since 2008.

**Tradeoffs and gotchas**
- The balancer is itself a single point of failure unless you run it highly available, across multiple zones or as a managed cloud service.
- Sticky sessions work against clean horizontal scaling, so use a shared session store when you can.
- Health checks that are too aggressive make instances flap in and out. Checks that are too slow keep sending traffic to dead servers.
- When the balancer terminates TLS, it sees plaintext unless you re-encrypt traffic to the backends, so know where your trust boundary is.
- A recovering node can get flooded the moment it rejoins and fall over again. Connection draining and slow-start fix this.
- **L4 balancing plus long-lived connections pins traffic.** Kubernetes' default Service balances per TCP connection, but gRPC multiplexes many calls over one long-lived HTTP/2 connection, so every call stays stuck on the first pod. You need L7 (request-level) balancing, like a client configured for round-robin on a headless Service, or an HTTP/2-aware proxy such as Envoy.

**When to use, when not.** Use L4 for raw TCP throughput, non-HTTP protocols, or when you want the balancer to stay dumb and fast. Use L7 when you need routing by path or header, TLS termination, or request-level balancing for HTTP/2 and gRPC. Consistent hashing earns its keep only when backends hold per-key local state; otherwise P2C or least connections spreads load more evenly.

**Try this:** You're putting a load balancer in front of 20 API servers. Most requests are short JSON GETs, but 5% open a WebSocket that stays connected for hours. Which algorithm do you pick, and do you keep the WebSockets in the same pool as the GETs or split them out? Why?
