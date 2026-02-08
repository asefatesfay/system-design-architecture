# Data Redundancy

## Definition

**Data Redundancy** is the practice of storing multiple copies of data to protect against data loss, ensure high availability, and maintain system reliability even when failures occur.

## Types of Redundancy

### 1. Hardware Redundancy
```
RAID Arrays:
- RAID 1 (Mirroring): 2+ identical copies
- RAID 5: Parity for single disk failure
- RAID 6: Survives 2 disk failures
```

### 2. Database Redundancy
```
- Primary + Replicas
- Multi-region replication
- Backup databases
```

### 3. Geographic Redundancy
```
Data centers in multiple regions:
US-East, US-West, EU, Asia

Region failure? Other regions operational
```

### 4. Application-Level Redundancy
```
- Multiple application servers
- Load balanced
- Stateless (any server can handle  request)
```

## Real-World Examples

### AWS S3
**11 nines of durability (99.999999999%)**

```
Object stored → Automatically replicated to:
- Multiple devices
- Multiple facilities
- Within region

Losing 1 trillion objects → Expect to lose 1 object per 10,000 years!
```

### Google Cloud Storage
**Geo-redundant by default**

```
Multi-region bucket:
- Data replicated across continents
- Disaster recovery built-in
- Automatic failover
```

### Netflix
**Multi-region redundancy**

```
Chaos Monkey: Randomly kills servers
Chaos Kong: Simulates region failure

System handles failures gracefully:
- Multiple AZs within region
- Multiple regions worldwide
- Automated failover
```

### Databases (PostgreSQL, MySQL)
```
Primary database
↓
Replicas in multiple AZs
↓
Cross-region replicas
↓
Automated backups (point-in-time recovery)
```

## Redundancy Levels

### N+1 Redundancy
```
Need: N units to handle load
Have: N+1 units (1 extra)

Example: 3 servers needed → Deploy 4
One fails? Still operational ✅
```

### N+2 Redundancy
```
N+2 = Survives 2 simultaneous failures

Critical systems (financial, healthcare)
```

### 2N Redundancy
```
Double everything

Example: 10 servers needed → Deploy 20
50% can fail, still operational

Very expensive but highly available
```

## Redundancy vs Backup

```
Redundancy:
- Real-time copies
- Immediate failover
- HA (High Availability)

Backup:
- Point-in-time copies
- Manual/scheduled restore
- DR (Disaster Recovery)

Both needed! ✅
```

## Cost vs Benefit

```
1 copy: $100, 0% redundancy ❌
2 copies: $200, 1x redundancy ✅
3 copies: $300, 2x redundancy ✅✅
5 copies: $500, 4x redundancy? Overkill? 💸

Balance cost and reliability needs
```

## Best Practices

✅ **3-2-1 backup rule**
```
3 copies of data
2 different media types
1 offsite copy
```

✅ **Test failover regularly**
```
Netflix Chaos Engineering: Kill servers intentionally
Verify redundancy actually works
```

✅ **Monitor all copies**
```
Alert if replica falls behind
Alert if backup fails
```

✅ **Geographic diversity**
```
Don't put all copies in same data center!
Region-level redundancy for critical data
```

**Key Takeaway:** Data redundancy prevents data loss and enables high availability. Balance redundancy level with cost and business requirements!
