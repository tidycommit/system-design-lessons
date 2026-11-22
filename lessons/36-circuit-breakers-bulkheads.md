# 36. Circuit breakers and bulkheads
_Sent 2026-11-06_

**The problem.** Lesson 30 was about protecting *your* service when *you* are overloaded. This one is about the other direction: a dependency is sick (payments, recommendations, a cache), and every call into it piles up threads, sockets, and retries until *your* healthy service falls over too. A circuit breaker stops calling a failing dependency for a while. A bulkhead limits how much of your capacity any one dependency can consume, so a fire in one cabin can't sink the ship.

**How a circuit breaker works.** Track recent outcomes for one dependency (or one endpoint of it). Three states:

- **Closed** (normal): calls go through. Count failures (timeouts, 5xx, connection errors, not every 4xx).
- **Open**: after the failure rate or consecutive-failure count crosses a threshold, short-circuit: fail fast locally, don't touch the dependency. Optionally serve a fallback (cached value, default, degraded UI).
- **Half-open**: after a cool-down, let a small probe of calls through. If they succeed, close; if they fail, open again.

```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open: failure threshold hit
    Open --> HalfOpen: cool-down expires
    HalfOpen --> Closed: probes succeed
    HalfOpen --> Open: probes fail
```

A **bulkhead** is the capacity fence around that call path: a dedicated thread pool, semaphore, or connection pool sized for that dependency alone. When the payments pool is full, new payment calls reject immediately, and search and cart keep their own pools and stay responsive.

**Real-world example.** Netflix's Hystrix (and its successors Resilience4j and the concurrency-limits work that followed) wrapped every call to a remote service with a circuit breaker plus a bulkhead. When a mid-tier recommendations service degraded, Hystrix opened the circuit and the UI fell back to a cached or default shelf instead of waiting on timeouts. The famous "fail whale" style cascades, one slow dependency saturating every Tomcat thread across the fleet, were exactly what the bulkhead was meant to stop: recommendations got 10 threads per host; checkout got its own 20; a stuck recommendations call could not eat checkout's threads. Amazon's Builders' Library and Google SRE make the same point with different words: isolate failure domains, and prefer a fast local failure over a slow remote one when the dependency's error budget is already burned.

**A second example: Envoy's outlier detection.** You don't always wrap each call in app code; a service mesh or proxy can break the circuit for you. Envoy's outlier detection ejects a bad backend from the load-balancing pool automatically, and its defaults are a useful reference point for tuning your own breakers: eject a host after **5 consecutive 5xx** responses, re-scan every **10 seconds**, keep it ejected for a base of **30 seconds** (growing with repeated ejections), and never eject more than **10%** of the pool at once. That last limit is the subtle, important one: it stops the breaker from pulling so many hosts that the survivors get overloaded and the "cure" becomes the outage. It's the per-host version of a circuit breaker, enforced at the load balancer (lesson 2) instead of inside each caller.

**Tradeoffs and failure modes.**
- **Open too eagerly and you amplify a blip into an outage.** A short timeout spike or a deploy rolling through instances can trip every breaker at once. Use a failure *rate* over a sliding window, require a minimum request volume, and stagger cool-downs (jitter) so the half-open stampede doesn't restart the fire.
- **Fail-open vs fail-closed.** For a non-critical path (recommendations), failing open to a fallback is fine. For authorization or payments, failing closed (deny / error) is usually safer than a silent allow.
- **Fallbacks that lie.** Serving a stale cart total or "in stock" from cache while the inventory service is down can create worse product bugs than an error page. Fallbacks need product sign-off, not just eng convenience.
- **Bulkheads that are too small look like the dependency is down.** Undersized pools reject under normal peak and trip the breaker on your own capacity mistake. Size from measured concurrency times latency (Little's Law, lesson 3), then load-test.
- **Ejecting too much.** As Envoy's 10% cap shows, pulling too many hosts at once overloads the rest. Bound how much of a pool any breaker can remove.
- **Retries bypass the breaker.** A client that retries three times against an open circuit (or against a half-open probe) undoes the protection. Retries belong *inside* the breaker's accounting, with a budget (lesson 30).
- **Health checks that hit the same sick dependency.** If your load balancer marks you unhealthy because a dependency timed out, you shed your own healthy capacity. Probe *your* liveness, not the whole dependency graph.

**When to use what.** Put a circuit breaker and a bulkhead around every call to a dependency that can fail independently of you, especially slow, flaky, or non-critical ones. Let a service mesh or proxy (Envoy-style outlier detection) handle host-level ejection for your internal fleet, and use in-process breakers (Resilience4j and friends) for finer control and fallbacks on specific calls. Fail open with a fallback for non-critical paths, fail closed for money and authorization, and always cap how much of a pool a breaker can remove so the cure doesn't cause the outage.

**Try this.** Your checkout service calls inventory (p99 40 ms), payments (p99 200 ms), and a fraud-score API (p99 800 ms, flaky). Under a fraud-vendor outage, checkout p99 jumps past 5 s and hosts start failing health checks. Design the breaker + bulkhead layout: which calls get breakers, which get fallbacks vs hard errors, how you size each bulkhead, and what you change so a fraud outage cannot take checkout out of the load balancer.
