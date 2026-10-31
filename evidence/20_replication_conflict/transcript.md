# Experiment B: two-way replication, conflict and resolution

Run started: 2026-10-30T21:48:30+01:00

Configuration:
- Instance A http://127.0.0.1:5984 (replicator reaches it as http://couch-a:5984)
- Instance B http://127.0.0.1:5985 (replicator reaches it as http://couch-b:5984)
- Database `orders` on both, n=1. Continuous replication jobs in each instance's _replicator.
- Shared document: store01:order-shared

## B1. Continuous replication in both directions

### Step 1: Create job rep-a-to-b-1 in A's _replicator (A -> B)

_Credentials are needed to read the source and write the target. They are redacted in this output._

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /_replicator/rep-a-to-b-1
{
  "source": {
    "url": "http://couch-a:5984/orders",
    "auth": {
      "basic": {
        "username": "admin_a",
        "password": "***"
      }
    }
  },
  "target": {
    "url": "http://couch-b:5984/orders",
    "auth": {
      "basic": {
        "username": "admin_b",
        "password": "***"
      }
    }
  },
  "continuous": true
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "rep-a-to-b-1",
  "rev": "3-45d61c80a38621f8042decae7cfa608b"
}
```

- **PASS**: Job document rep-a-to-b-1 saved  
  expected: HTTP 201  
  observed: HTTP 201

### Step 2: Create job rep-b-to-a-1 in B's _replicator (B -> A)

_Credentials are needed to read the source and write the target. They are redacted in this output._

**Instance B** (`http://127.0.0.1:5985`)

```http
PUT /_replicator/rep-b-to-a-1
{
  "source": {
    "url": "http://couch-b:5984/orders",
    "auth": {
      "basic": {
        "username": "admin_b",
        "password": "***"
      }
    }
  },
  "target": {
    "url": "http://couch-a:5984/orders",
    "auth": {
      "basic": {
        "username": "admin_a",
        "password": "***"
      }
    }
  },
  "continuous": true
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "rep-b-to-a-1",
  "rev": "3-12c7d6d9933e23d2551f75f0fd79f4ec"
}
```

- **PASS**: Job document rep-b-to-a-1 saved  
  expected: HTTP 201  
  observed: HTTP 201

### Step 3: Wait until rep-a-to-b-1 is running (bounded: 60 s)

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /_scheduler/docs/_replicator/rep-a-to-b-1
```

Response: **HTTP 200 OK**

```json
{
  "database": "_replicator",
  "doc_id": "rep-a-to-b-1",
  "id": "341599bf8a551bbfa46d1930bce7cd91+continuous",
  "node": "nonode@nohost",
  "source": "http://couch-a:5984/orders/",
  "target": "http://couch-b:5984/orders/",
  "state": "running",
  "info": {
    "revisions_checked": 100,
    "missing_revisions_found": 100,
    "docs_read": 100,
    "docs_written": 100,
    "changes_pending": null,
    "doc_write_failures": 0,
    "bulk_get_docs": 100,
    "bulk_get_attempts": 100,
    "checkpointed_source_seq": "0",
    "source_seq": "100-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50SAXKMCeaJmYmJxsia4Yh_Y8FiDJ0ACk_kNNMQGbkpxqaZmaZISuJwsAlEIrrA",
    "through_seq": "100-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50SAXKMCeaJmYmJxsia4Yh_Y8FiDJ0ACk_kNNMQGbkpxqaZmaZISuJwsAlEIrrA"
  },
  "error_count": 0,
  "last_updated": "2026-10-30T20:50:07Z",
  "start_time": "2026-10-30T20:50:07Z",
  "source_proxy": null,
  "target_proxy": null
}
```

- **PASS**: rep-a-to-b-1 is running without errors  
  expected: state "running", no error in info  
  observed: state "running" after 0.02s, info={'revisions_checked': 100, 'missing_revisions_found': 100, 'docs_read': 100, 'docs_written': 100, 'changes_pending': None, 'doc_write_failures': 0, 'bulk_get_docs': 100, 'bulk_get_attempts': 100, 'checkpointed_source_seq': '0', 'source_seq': '100-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50SAXKMCeaJmYmJxsia4Yh_Y8FiDJ0ACk_kNNMQGbkpxqaZmaZISuJwsAlEIrrA', 'through_seq': '100-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50SAXKMCeaJmYmJxsia4Yh_Y8FiDJ0ACk_kNNMQGbkpxqaZmaZISuJwsAlEIrrA'}

### Step 4: Wait until rep-b-to-a-1 is running (bounded: 60 s)

**Instance B** (`http://127.0.0.1:5985`)

```http
GET /_scheduler/docs/_replicator/rep-b-to-a-1
```

Response: **HTTP 200 OK**

```json
{
  "database": "_replicator",
  "doc_id": "rep-b-to-a-1",
  "id": "34661d39863b8ac3d33f757b58727ff9+continuous",
  "node": "nonode@nohost",
  "source": "http://couch-b:5984/orders/",
  "target": "http://couch-a:5984/orders/",
  "state": "running",
  "info": {
    "revisions_checked": 100,
    "missing_revisions_found": 0,
    "docs_read": 0,
    "docs_written": 0,
    "changes_pending": null,
    "doc_write_failures": 0,
    "bulk_get_docs": 0,
    "bulk_get_attempts": 0,
    "checkpointed_source_seq": "0",
    "source_seq": "100-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50SAXKMCelmaQZGFmgq4Yh_Y8FiDJ0ACk_kNNMQGbYmJmZmZpkoauJwsAaGEqxw",
    "through_seq": "100-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50SAXKMCelmaQZGFmgq4Yh_Y8FiDJ0ACk_kNNMQGbYmJmZmZpkoauJwsAaGEqxw"
  },
  "error_count": 0,
  "last_updated": "2026-10-30T20:50:22Z",
  "start_time": "2026-10-30T20:50:22Z",
  "source_proxy": null,
  "target_proxy": null
}
```

- **PASS**: rep-b-to-a-1 is running without errors  
  expected: state "running", no error in info  
  observed: state "running" after 0.01s, info={'revisions_checked': 100, 'missing_revisions_found': 0, 'docs_read': 0, 'docs_written': 0, 'changes_pending': None, 'doc_write_failures': 0, 'bulk_get_docs': 0, 'bulk_get_attempts': 0, 'checkpointed_source_seq': '0', 'source_seq': '100-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50SAXKMCelmaQZGFmgq4Yh_Y8FiDJ0ACk_kNNMQGbYmJmZmZpkoauJwsAaGEqxw', 'through_seq': '100-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50SAXKMCelmaQZGFmgq4Yh_Y8FiDJ0ACk_kNNMQGbYmJmZmZpkoauJwsAaGEqxw'}

> Job settings saved to evidence/20_replication_conflict/replication_jobs.json (passwords redacted)

### Step 5: Wait until B has caught up with A's existing documents

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /orders
```

Response: **HTTP 200 OK**

```json
{
  "instance_start_time": "1793393310",
  "db_name": "orders",
  "purge_seq": "0-g1AAAABPeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCeexAEmGBiD1HwiyEhlwqEtkSKqHKMgCAIT2GV4",
  "update_seq": "100-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCeexAEmGBiD1HwiyMpgTTXKBAuzJqZaWqUlG6HpwmJLIkFQP1W4A1p5omZiYnGyJrjgLAEAYK6w",
  "sizes": {
    "file": 82316,
    "external": 44841,
    "active": 60558
  },
  "props": {},
  "doc_del_count": 0,
  "doc_count": 100,
  "disk_format_version": 8,
  "compact_running": false,
  "cluster": {
    "q": 2,
    "n": 1,
    "w": 1,
    "r": 1
  }
}
```

**Instance B** (`http://127.0.0.1:5985`)

```http
GET /orders
```

Response: **HTTP 200 OK**

```json
{
  "instance_start_time": "1793393310",
  "db_name": "orders",
  "purge_seq": "0-g1AAAABPeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCeexAEmGBiD1HwiyEhlwqEtkSKqHKMgCAIT2GV4",
  "update_seq": "100-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCeexAEmGBiD1HwiyMpgTTXKBAuwmZmZmliZp6HpwmJLIkFQP1W4A1p6WZpBkYWaCrjgLAAsjKsc",
  "sizes": {
    "file": 94604,
    "external": 44841,
    "active": 60550
  },
  "props": {},
  "doc_del_count": 0,
  "doc_count": 100,
  "disk_format_version": 8,
  "compact_running": false,
  "cluster": {
    "q": 2,
    "n": 1,
    "w": 1,
    "r": 1
  }
}
```

- **PASS**: B holds the same number of documents as A  
  expected: doc_count 100 on both  
  observed: B doc_count 100 after 0.0s

## B2. A document created on A reaches B, and one created on B reaches A

### Step 6: Create store02:order-from-a on A

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /orders/store02:order-from-a
{
  "type": "order",
  "tenant": "store02",
  "status": "open",
  "total": 25.0,
  "note": "created on A"
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "store02:order-from-a",
  "rev": "1-0416764192d5ae479ac6f38a24d60fb2"
}
```

### Step 7: Read store02:order-from-a on B (polling, bounded)

**Instance B** (`http://127.0.0.1:5985`)

```http
GET /orders/store02:order-from-a
```

Response: **HTTP 200 OK**

```json
{
  "_id": "store02:order-from-a",
  "_rev": "1-0416764192d5ae479ac6f38a24d60fb2",
  "type": "order",
  "tenant": "store02",
  "status": "open",
  "total": 25.0,
  "note": "created on A"
}
```

- **PASS**: A -> B replication works  
  expected: store02:order-from-a readable on B  
  observed: found=True after 0.0s

### Step 8: Create store03:order-from-b on B

**Instance B** (`http://127.0.0.1:5985`)

```http
PUT /orders/store03:order-from-b
{
  "type": "order",
  "tenant": "store03",
  "status": "open",
  "total": 31.5,
  "note": "created on B"
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "store03:order-from-b",
  "rev": "1-247349949ae332aa91fab24b0b6dffe4"
}
```

### Step 9: Read store03:order-from-b on A (polling, bounded)

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /orders/store03:order-from-b
```

Response: **HTTP 200 OK**

```json
{
  "_id": "store03:order-from-b",
  "_rev": "1-247349949ae332aa91fab24b0b6dffe4",
  "type": "order",
  "tenant": "store03",
  "status": "open",
  "total": 31.5,
  "note": "created on B"
}
```

- **PASS**: B -> A replication works  
  expected: store03:order-from-b readable on A  
  observed: found=True after 0.0s

## B3. Common starting state of the shared document

### Step 10: Create the shared order store01:order-shared on A

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /orders/store01:order-shared
{
  "type": "order",
  "tenant": "store01",
  "order_no": 901,
  "status": "open",
  "customer": {
    "name": "Shared Customer",
    "email": "shared@example.com"
  },
  "items": [
    {
      "sku": "SKU-COF-01",
      "name": "Coffee beans 1 kg",
      "qty": 3,
      "unit_price": 18.9
    }
  ],
  "total": 56.7,
  "currency": "EUR",
  "created_at": "2026-10-30T09:00:00Z",
  "delivery": {
    "city": "Szeged",
    "street": "Kossuth tér 3."
  }
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "store01:order-shared",
  "rev": "1-845cc458c4077f578aa02eb284f6a81a"
}
```

### Step 11: Wait until B has the same revision

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /orders/store01:order-shared
```

Response: **HTTP 200 OK**

```json
{
  "_id": "store01:order-shared",
  "_rev": "1-845cc458c4077f578aa02eb284f6a81a",
  "type": "order",
  "tenant": "store01",
  "order_no": 901,
  "status": "open",
  "customer": {
    "name": "Shared Customer",
    "email": "shared@example.com"
  },
  "items": [
    {
      "sku": "SKU-COF-01",
      "name": "Coffee beans 1 kg",
      "qty": 3,
      "unit_price": 18.9
    }
  ],
  "total": 56.7,
  "currency": "EUR",
  "created_at": "2026-10-30T09:00:00Z",
  "delivery": {
    "city": "Szeged",
    "street": "Kossuth tér 3."
  }
}
```

**Instance B** (`http://127.0.0.1:5985`)

```http
GET /orders/store01:order-shared
```

Response: **HTTP 200 OK**

```json
{
  "_id": "store01:order-shared",
  "_rev": "1-845cc458c4077f578aa02eb284f6a81a",
  "type": "order",
  "tenant": "store01",
  "order_no": 901,
  "status": "open",
  "customer": {
    "name": "Shared Customer",
    "email": "shared@example.com"
  },
  "items": [
    {
      "sku": "SKU-COF-01",
      "name": "Coffee beans 1 kg",
      "qty": 3,
      "unit_price": 18.9
    }
  ],
  "total": 56.7,
  "currency": "EUR",
  "created_at": "2026-10-30T09:00:00Z",
  "delivery": {
    "city": "Szeged",
    "street": "Kossuth tér 3."
  }
}
```

- **PASS**: A and B have the same current revision  
  expected: _rev 1-845cc458c4077f578aa02eb284f6a81a on both  
  observed: A 1-845cc458c4077f578aa02eb284f6a81a, B 1-845cc458c4077f578aa02eb284f6a81a

## B4. Stop both replication jobs

### Step 12: Delete job document rep-a-to-b-1 on A, quoting its current _rev

**Instance A** (`http://127.0.0.1:5984`)

```http
DELETE /_replicator/rep-a-to-b-1?rev=3-45d61c80a38621f8042decae7cfa608b
```

Response: **HTTP 200 OK**

```json
{
  "ok": true,
  "id": "rep-a-to-b-1",
  "rev": "4-a5bc83bef1bb1d4b47bcc1a4d9e80b8a"
}
```

- **PASS**: rep-a-to-b-1 document deleted  
  expected: HTTP 200  
  observed: HTTP 200

### Step 13: Delete job document rep-b-to-a-1 on B, quoting its current _rev

**Instance B** (`http://127.0.0.1:5985`)

```http
DELETE /_replicator/rep-b-to-a-1?rev=3-12c7d6d9933e23d2551f75f0fd79f4ec
```

Response: **HTTP 200 OK**

```json
{
  "ok": true,
  "id": "rep-b-to-a-1",
  "rev": "4-07877a18afc2bdc6d6ac3aa9c5b16e27"
}
```

- **PASS**: rep-b-to-a-1 document deleted  
  expected: HTTP 200  
  observed: HTTP 200

### Step 14: Confirm rep-a-to-b-1 has stopped on A

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /_scheduler/jobs
```

Response: **HTTP 200 OK**

```json
{
  "total_rows": 0,
  "offset": 0,
  "jobs": []
}
```

- **PASS**: No running job for rep-a-to-b-1  
  expected: rep-a-to-b-1 absent from /_scheduler/jobs  
  observed: absent=True after 0.0s

### Step 15: Confirm rep-b-to-a-1 has stopped on B

**Instance B** (`http://127.0.0.1:5985`)

```http
GET /_scheduler/jobs
```

Response: **HTTP 200 OK**

```json
{
  "total_rows": 0,
  "offset": 0,
  "jobs": []
}
```

- **PASS**: No running job for rep-b-to-a-1  
  expected: rep-b-to-a-1 absent from /_scheduler/jobs  
  observed: absent=True after 0.0s

## B5. Edit the shared document independently on A and on B

### Step 16: On A (branch 1): mark the order paid

_Based on the common revision 1-845cc458c4077f578aa02eb284f6a81a._

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /orders/store01:order-shared
{
  "_id": "store01:order-shared",
  "_rev": "1-845cc458c4077f578aa02eb284f6a81a",
  "type": "order",
  "tenant": "store01",
  "order_no": 901,
  "status": "paid",
  "customer": {
    "name": "Shared Customer",
    "email": "shared@example.com"
  },
  "items": [
    {
      "sku": "SKU-COF-01",
      "name": "Coffee beans 1 kg",
      "qty": 3,
      "unit_price": 18.9
    }
  ],
  "total": 56.7,
  "currency": "EUR",
  "created_at": "2026-10-30T09:00:00Z",
  "delivery": {
    "city": "Szeged",
    "street": "Kossuth tér 3."
  },
  "payment": {
    "method": "card",
    "paid_at": "2026-10-30T10:15:00Z"
  }
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "store01:order-shared",
  "rev": "2-1f7d40c3ddc5854aa139802e059b188b"
}
```

- **PASS**: Edit accepted locally on A  
  expected: HTTP 201  
  observed: HTTP 201, rev 2-1f7d40c3ddc5854aa139802e059b188b

### Step 17: On B (branch 2): correct the delivery address

_Also based on 1-845cc458c4077f578aa02eb284f6a81a._

**Instance B** (`http://127.0.0.1:5985`)

```http
PUT /orders/store01:order-shared
{
  "_id": "store01:order-shared",
  "_rev": "1-845cc458c4077f578aa02eb284f6a81a",
  "type": "order",
  "tenant": "store01",
  "order_no": 901,
  "status": "open",
  "customer": {
    "name": "Shared Customer",
    "email": "shared@example.com"
  },
  "items": [
    {
      "sku": "SKU-COF-01",
      "name": "Coffee beans 1 kg",
      "qty": 3,
      "unit_price": 18.9
    }
  ],
  "total": 56.7,
  "currency": "EUR",
  "created_at": "2026-10-30T09:00:00Z",
  "delivery": {
    "city": "Szeged",
    "street": "Kárász utca 12."
  },
  "note": "Customer called: new delivery address"
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "store01:order-shared",
  "rev": "2-d520350d5b45912a18d482c3b8a236e6"
}
```

- **PASS**: Edit accepted locally on B  
  expected: HTTP 201  
  observed: HTTP 201, rev 2-d520350d5b45912a18d482c3b8a236e6

- **PASS**: The two branches now hold different revisions  
  expected: two different 2-... revisions  
  observed: A 2-1f7d40c3ddc5854aa139802e059b188b, B 2-d520350d5b45912a18d482c3b8a236e6

## B6. Restart replication and inspect the conflict

> New job documents with fresh ids, same connection settings, no old _rev or state fields.

### Step 18: Create job rep-a-to-b-2 in A's _replicator (A -> B)

_Credentials are needed to read the source and write the target. They are redacted in this output._

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /_replicator/rep-a-to-b-2
{
  "source": {
    "url": "http://couch-a:5984/orders",
    "auth": {
      "basic": {
        "username": "admin_a",
        "password": "***"
      }
    }
  },
  "target": {
    "url": "http://couch-b:5984/orders",
    "auth": {
      "basic": {
        "username": "admin_b",
        "password": "***"
      }
    }
  },
  "continuous": true
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "rep-a-to-b-2",
  "rev": "3-45d61c80a38621f8042decae7cfa608b"
}
```

- **PASS**: Job document rep-a-to-b-2 saved  
  expected: HTTP 201  
  observed: HTTP 201

### Step 19: Create job rep-b-to-a-2 in B's _replicator (B -> A)

_Credentials are needed to read the source and write the target. They are redacted in this output._

**Instance B** (`http://127.0.0.1:5985`)

```http
PUT /_replicator/rep-b-to-a-2
{
  "source": {
    "url": "http://couch-b:5984/orders",
    "auth": {
      "basic": {
        "username": "admin_b",
        "password": "***"
      }
    }
  },
  "target": {
    "url": "http://couch-a:5984/orders",
    "auth": {
      "basic": {
        "username": "admin_a",
        "password": "***"
      }
    }
  },
  "continuous": true
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "rep-b-to-a-2",
  "rev": "3-12c7d6d9933e23d2551f75f0fd79f4ec"
}
```

- **PASS**: Job document rep-b-to-a-2 saved  
  expected: HTTP 201  
  observed: HTTP 201

### Step 20: Wait until rep-a-to-b-2 is running (bounded: 60 s)

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /_scheduler/docs/_replicator/rep-a-to-b-2
```

Response: **HTTP 200 OK**

```json
{
  "database": "_replicator",
  "doc_id": "rep-a-to-b-2",
  "id": "341599bf8a551bbfa46d1930bce7cd91+continuous",
  "node": "nonode@nohost",
  "source": "http://couch-a:5984/orders/",
  "target": "http://couch-b:5984/orders/",
  "state": "running",
  "info": {
    "revisions_checked": 106,
    "missing_revisions_found": 103,
    "docs_read": 103,
    "docs_written": 103,
    "changes_pending": null,
    "doc_write_failures": 0,
    "bulk_get_docs": 103,
    "bulk_get_attempts": 103,
    "checkpointed_source_seq": "103-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50TAXKMCeaJmYmJxsia4Yh_Y8FiDJ0ACk_kNNMQObkpxqaZmaZISuJwsAlOIrrw",
    "source_seq": "105-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50TgXKMCeaJmYmJxsia4Yh_Y8FiDJ0ACk_kNNMQObkpxqaZmaZISuJwsAlaorsQ",
    "through_seq": "105-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50TgXKMCeaJmYmJxsia4Yh_Y8FiDJ0ACk_kNNMQObkpxqaZmaZISuJwsAlaorsQ"
  },
  "error_count": 0,
  "last_updated": "2026-10-30T20:51:06Z",
  "start_time": "2026-10-30T20:51:06Z",
  "source_proxy": null,
  "target_proxy": null
}
```

- **PASS**: rep-a-to-b-2 is running without errors  
  expected: state "running", no error in info  
  observed: state "running" after 0.01s, info={'revisions_checked': 106, 'missing_revisions_found': 103, 'docs_read': 103, 'docs_written': 103, 'changes_pending': None, 'doc_write_failures': 0, 'bulk_get_docs': 103, 'bulk_get_attempts': 103, 'checkpointed_source_seq': '103-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50TAXKMCeaJmYmJxsia4Yh_Y8FiDJ0ACk_kNNMQObkpxqaZmaZISuJwsAlOIrrw', 'source_seq': '105-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50TgXKMCeaJmYmJxsia4Yh_Y8FiDJ0ACk_kNNMQObkpxqaZmaZISuJwsAlaorsQ', 'through_seq': '105-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50TgXKMCeaJmYmJxsia4Yh_Y8FiDJ0ACk_kNNMQObkpxqaZmaZISuJwsAlaorsQ'}

### Step 21: Wait until rep-b-to-a-2 is running (bounded: 60 s)

**Instance B** (`http://127.0.0.1:5985`)

```http
GET /_scheduler/docs/_replicator/rep-b-to-a-2
```

Response: **HTTP 200 OK**

```json
{
  "database": "_replicator",
  "doc_id": "rep-b-to-a-2",
  "id": "34661d39863b8ac3d33f757b58727ff9+continuous",
  "node": "nonode@nohost",
  "source": "http://couch-b:5984/orders/",
  "target": "http://couch-a:5984/orders/",
  "state": "running",
  "info": {
    "revisions_checked": 105,
    "missing_revisions_found": 2,
    "docs_read": 2,
    "docs_written": 2,
    "changes_pending": null,
    "doc_write_failures": 0,
    "bulk_get_docs": 2,
    "bulk_get_attempts": 2,
    "checkpointed_source_seq": "103-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50TAXKMCelmaQZGFmgq4Yh_Y8FiDJ0ACk_kNNMQObYmJmZmZpkoauJwsAaQEqyg",
    "source_seq": "105-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50TgXKMCelmaQZGFmgq4Yh_Y8FiDJ0ACk_kNNMQObYmJmZmZpkoauJwsAackqzA",
    "through_seq": "105-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50TgXKMCelmaQZGFmgq4Yh_Y8FiDJ0ACk_kNNMQObYmJmZmZpkoauJwsAackqzA"
  },
  "error_count": 0,
  "last_updated": "2026-10-30T20:51:08Z",
  "start_time": "2026-10-30T20:51:08Z",
  "source_proxy": null,
  "target_proxy": null
}
```

- **PASS**: rep-b-to-a-2 is running without errors  
  expected: state "running", no error in info  
  observed: state "running" after 0.01s, info={'revisions_checked': 105, 'missing_revisions_found': 2, 'docs_read': 2, 'docs_written': 2, 'changes_pending': None, 'doc_write_failures': 0, 'bulk_get_docs': 2, 'bulk_get_attempts': 2, 'checkpointed_source_seq': '103-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50TAXKMCelmaQZGFmgq4Yh_Y8FiDJ0ACk_kNNMQObYmJmZmZpkoauJwsAaQEqyg', 'source_seq': '105-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50TgXKMCelmaQZGFmgq4Yh_Y8FiDJ0ACk_kNNMQObYmJmZmZpkoauJwsAackqzA', 'through_seq': '105-g1AAAACLeJzLYWBgYMpgTmHgzcvPy09JdcjLz8gvLskBCScyJNX___8_K4M50TgXKMCelmaQZGFmgq4Yh_Y8FiDJ0ACk_kNNMQObYmJmZmZpkoauJwsAackqzA'}

### Step 22: Wait until both instances know both revisions

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /orders/store01:order-shared?conflicts=true
```

Response: **HTTP 200 OK**

```json
{
  "_id": "store01:order-shared",
  "_rev": "2-d520350d5b45912a18d482c3b8a236e6",
  "type": "order",
  "tenant": "store01",
  "order_no": 901,
  "status": "open",
  "customer": {
    "name": "Shared Customer",
    "email": "shared@example.com"
  },
  "items": [
    {
      "sku": "SKU-COF-01",
      "name": "Coffee beans 1 kg",
      "qty": 3,
      "unit_price": 18.9
    }
  ],
  "total": 56.7,
  "currency": "EUR",
  "created_at": "2026-10-30T09:00:00Z",
  "delivery": {
    "city": "Szeged",
    "street": "Kárász utca 12."
  },
  "note": "Customer called: new delivery address",
  "_conflicts": [
    "2-1f7d40c3ddc5854aa139802e059b188b"
  ]
}
```

**Instance B** (`http://127.0.0.1:5985`)

```http
GET /orders/store01:order-shared?conflicts=true
```

Response: **HTTP 200 OK**

```json
{
  "_id": "store01:order-shared",
  "_rev": "2-d520350d5b45912a18d482c3b8a236e6",
  "type": "order",
  "tenant": "store01",
  "order_no": 901,
  "status": "open",
  "customer": {
    "name": "Shared Customer",
    "email": "shared@example.com"
  },
  "items": [
    {
      "sku": "SKU-COF-01",
      "name": "Coffee beans 1 kg",
      "qty": 3,
      "unit_price": 18.9
    }
  ],
  "total": 56.7,
  "currency": "EUR",
  "created_at": "2026-10-30T09:00:00Z",
  "delivery": {
    "city": "Szeged",
    "street": "Kárász utca 12."
  },
  "note": "Customer called: new delivery address",
  "_conflicts": [
    "2-1f7d40c3ddc5854aa139802e059b188b"
  ]
}
```

- **PASS**: Both instances report a conflict  
  expected: _conflicts present on A and B  
  observed: A after 0.0s: True, B after 0.0s: True

- **PASS**: Both instances pick the same winning revision  
  expected: same _rev and same _conflicts on A and B  
  observed: A 2-d520350d5b45912a18d482c3b8a236e6 / ['2-1f7d40c3ddc5854aa139802e059b188b']; B 2-d520350d5b45912a18d482c3b8a236e6 / ['2-1f7d40c3ddc5854aa139802e059b188b']

- **PASS**: Winner follows the documented deterministic rule  
  expected: equal revision depth, so the higher revision id wins: 2-d520350d5b45912a18d482c3b8a236e6  
  observed: 2-d520350d5b45912a18d482c3b8a236e6

### Step 23: Fetch the losing revision by its revision id

_It is not lost, just hidden from ordinary reads._

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /orders/store01:order-shared?rev=2-1f7d40c3ddc5854aa139802e059b188b
```

Response: **HTTP 200 OK**

```json
{
  "_id": "store01:order-shared",
  "_rev": "2-1f7d40c3ddc5854aa139802e059b188b",
  "type": "order",
  "tenant": "store01",
  "order_no": 901,
  "status": "paid",
  "customer": {
    "name": "Shared Customer",
    "email": "shared@example.com"
  },
  "items": [
    {
      "sku": "SKU-COF-01",
      "name": "Coffee beans 1 kg",
      "qty": 3,
      "unit_price": 18.9
    }
  ],
  "total": 56.7,
  "currency": "EUR",
  "created_at": "2026-10-30T09:00:00Z",
  "delivery": {
    "city": "Szeged",
    "street": "Kossuth tér 3."
  },
  "payment": {
    "method": "card",
    "paid_at": "2026-10-30T10:15:00Z"
  }
}
```

- **PASS**: Losing revision is still readable  
  expected: HTTP 200, _rev 2-1f7d40c3ddc5854aa139802e059b188b  
  observed: HTTP 200, _rev 2-1f7d40c3ddc5854aa139802e059b188b

> Winning revision status=open street=Kárász utca 12.; losing revision status=paid street=Kossuth tér 3.. CouchDB did not merge them.

## B7. Resolve the conflict with an explicit merge rule

> Rule: three-way merge per top-level field against the common start. A field changed on only one side takes that side's value. A field changed differently on both sides keeps the winner's value and is recorded in merge_notes.

### Step 24: Save the merged content as a new revision of the WINNING branch

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /orders/store01:order-shared
{
  "created_at": "2026-10-30T09:00:00Z",
  "currency": "EUR",
  "customer": {
    "name": "Shared Customer",
    "email": "shared@example.com"
  },
  "delivery": {
    "city": "Szeged",
    "street": "Kárász utca 12."
  },
  "items": [
    {
      "sku": "SKU-COF-01",
      "name": "Coffee beans 1 kg",
      "qty": 3,
      "unit_price": 18.9
    }
  ],
  "note": "Customer called: new delivery address",
  "order_no": 901,
  "payment": {
    "method": "card",
    "paid_at": "2026-10-30T10:15:00Z"
  },
  "status": "paid",
  "tenant": "store01",
  "total": 56.7,
  "type": "order",
  "merge_notes": [
    "no overlapping field changes"
  ],
  "_id": "store01:order-shared",
  "_rev": "2-d520350d5b45912a18d482c3b8a236e6"
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "store01:order-shared",
  "rev": "3-8fc0650d59560c8a809451b7b2330f55"
}
```

- **PASS**: Merged revision saved on the winning branch  
  expected: HTTP 201, rev 3-... (child of 2-d520350d5b45912a18d482c3b8a236e6)  
  observed: HTTP 201, rev 3-8fc0650d59560c8a809451b7b2330f55

### Step 25: Delete the LOSING leaf, using the loser's own revision id

_Not the new merged revision: that would delete the resolved document._

**Instance A** (`http://127.0.0.1:5984`)

```http
DELETE /orders/store01:order-shared?rev=2-1f7d40c3ddc5854aa139802e059b188b
```

Response: **HTTP 200 OK**

```json
{
  "ok": true,
  "id": "store01:order-shared",
  "rev": "3-03c970a37b339a258c3477557a4c35a5"
}
```

- **PASS**: Losing leaf marked deleted  
  expected: HTTP 200  
  observed: HTTP 200

### Step 26: Wait until the resolution has replicated to B

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /orders/store01:order-shared?conflicts=true&deleted_conflicts=true
```

Response: **HTTP 200 OK**

```json
{
  "_id": "store01:order-shared",
  "_rev": "3-8fc0650d59560c8a809451b7b2330f55",
  "created_at": "2026-10-30T09:00:00Z",
  "currency": "EUR",
  "customer": {
    "name": "Shared Customer",
    "email": "shared@example.com"
  },
  "delivery": {
    "city": "Szeged",
    "street": "Kárász utca 12."
  },
  "items": [
    {
      "sku": "SKU-COF-01",
      "name": "Coffee beans 1 kg",
      "qty": 3,
      "unit_price": 18.9
    }
  ],
  "note": "Customer called: new delivery address",
  "order_no": 901,
  "payment": {
    "method": "card",
    "paid_at": "2026-10-30T10:15:00Z"
  },
  "status": "paid",
  "tenant": "store01",
  "total": 56.7,
  "type": "order",
  "merge_notes": [
    "no overlapping field changes"
  ],
  "_deleted_conflicts": [
    "3-03c970a37b339a258c3477557a4c35a5"
  ]
}
```

**Instance B** (`http://127.0.0.1:5985`)

```http
GET /orders/store01:order-shared?conflicts=true&deleted_conflicts=true
```

Response: **HTTP 200 OK**

```json
{
  "_id": "store01:order-shared",
  "_rev": "3-8fc0650d59560c8a809451b7b2330f55",
  "created_at": "2026-10-30T09:00:00Z",
  "currency": "EUR",
  "customer": {
    "name": "Shared Customer",
    "email": "shared@example.com"
  },
  "delivery": {
    "city": "Szeged",
    "street": "Kárász utca 12."
  },
  "items": [
    {
      "sku": "SKU-COF-01",
      "name": "Coffee beans 1 kg",
      "qty": 3,
      "unit_price": 18.9
    }
  ],
  "note": "Customer called: new delivery address",
  "order_no": 901,
  "payment": {
    "method": "card",
    "paid_at": "2026-10-30T10:15:00Z"
  },
  "status": "paid",
  "tenant": "store01",
  "total": 56.7,
  "type": "order",
  "merge_notes": [
    "no overlapping field changes"
  ],
  "_deleted_conflicts": [
    "3-03c970a37b339a258c3477557a4c35a5"
  ]
}
```

- **PASS**: A: merged data, no live conflicts  
  expected: _rev 3-8fc0650d59560c8a809451b7b2330f55, no _conflicts, status paid, street Kárász utca 12.  
  observed: _rev 3-8fc0650d59560c8a809451b7b2330f55, _conflicts None, status paid, street Kárász utca 12., _deleted_conflicts ['3-03c970a37b339a258c3477557a4c35a5']

- **PASS**: B: merged data, no live conflicts  
  expected: _rev 3-8fc0650d59560c8a809451b7b2330f55, no _conflicts, status paid, street Kárász utca 12.  
  observed: _rev 3-8fc0650d59560c8a809451b7b2330f55, _conflicts None, status paid, street Kárász utca 12., _deleted_conflicts ['3-03c970a37b339a258c3477557a4c35a5']

> The two jobs from step B6 keep running. 90_reset.py stops them.

