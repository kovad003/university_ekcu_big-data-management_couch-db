# Part 2: Setup and readiness of instances A and B

Run started: 2026-10-30T21:48:03+01:00

Configuration:
- Instance A: http://127.0.0.1:5984 (inside Docker: http://couch-a:5984)
- Instance B: http://127.0.0.1:5985 (inside Docker: http://couch-b:5984)
- Image: couchdb:3.5.2 (Apache License 2.0), two containers, two named volumes

## Readiness

### Step 1: Wait until instance A answers (bounded: 60 s)

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /
```

Response: **HTTP 200 OK**

```json
{
  "couchdb": "Welcome",
  "version": "3.5.2",
  "git_sha": "5b4d92103",
  "uuid": "5d3dd91c706af3645cbd7afa7a5e68f6",
  "features": [
    "access-ready",
    "partitioned",
    "pluggable-storage-engines",
    "reshard",
    "scheduler"
  ],
  "vendor": {
    "name": "The Apache Software Foundation"
  }
}
```

- **PASS**: A runs CouchDB 3.5.x  
  expected: HTTP 200, version 3.5.x  
  observed: HTTP 200, version 3.5.2

### Step 2: Wait until instance B answers (bounded: 60 s)

**Instance B** (`http://127.0.0.1:5985`)

```http
GET /
```

Response: **HTTP 200 OK**

```json
{
  "couchdb": "Welcome",
  "version": "3.5.2",
  "git_sha": "5b4d92103",
  "uuid": "5106a0e51c646609f45f77ccf49fd98c",
  "features": [
    "access-ready",
    "partitioned",
    "pluggable-storage-engines",
    "reshard",
    "scheduler"
  ],
  "vendor": {
    "name": "The Apache Software Foundation"
  }
}
```

- **PASS**: B runs CouchDB 3.5.x  
  expected: HTTP 200, version 3.5.x  
  observed: HTTP 200, version 3.5.2

## Topology: two independent single nodes

### Step 3: Membership of A: which nodes does it know?

_A cluster would list both nodes. Independent instances list only themselves._

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /_membership
```

Response: **HTTP 200 OK**

```json
{
  "all_nodes": [
    "nonode@nohost"
  ],
  "cluster_nodes": [
    "nonode@nohost"
  ]
}
```

- **PASS**: A is a single-node instance  
  expected: cluster_nodes has exactly 1 entry  
  observed: ['nonode@nohost']

### Step 4: Membership of B: which nodes does it know?

_A cluster would list both nodes. Independent instances list only themselves._

**Instance B** (`http://127.0.0.1:5985`)

```http
GET /_membership
```

Response: **HTTP 200 OK**

```json
{
  "all_nodes": [
    "nonode@nohost"
  ],
  "cluster_nodes": [
    "nonode@nohost"
  ]
}
```

- **PASS**: B is a single-node instance  
  expected: cluster_nodes has exactly 1 entry  
  observed: ['nonode@nohost']

## Single-node setup

### Step 5: Set the default replica count n=1 on A

_One node can hold only one copy of each shard, so n=1 is the honest setting._

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /_node/_local/_config/cluster/n
"1"
```

Response: **HTTP 200 OK**

```json
""
```

- **PASS**: A accepted cluster/n=1  
  expected: HTTP 200  
  observed: HTTP 200

### Step 6: Create system database _users on A

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /_users?n=1
```

Response: **HTTP 412 Precondition Failed**

```json
{
  "error": "file_exists",
  "reason": "The database could not be created, the file already exists."
}
```

- **PASS**: _users exists on A  
  expected: HTTP 201 (created) or 412 (already exists)  
  observed: HTTP 412

### Step 7: Create system database _replicator on A

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /_replicator?n=1
```

Response: **HTTP 412 Precondition Failed**

```json
{
  "error": "file_exists",
  "reason": "The database could not be created, the file already exists."
}
```

- **PASS**: _replicator exists on A  
  expected: HTTP 201 (created) or 412 (already exists)  
  observed: HTTP 412

### Step 8: Health endpoint of A

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /_up
```

Response: **HTTP 200 OK**

```json
{
  "seeds": {},
  "status": "ok"
}
```

- **PASS**: A reports status ok  
  expected: HTTP 200 {"status":"ok"}  
  observed: HTTP 200 {'seeds': {}, 'status': 'ok'}

### Step 9: Set the default replica count n=1 on B

_One node can hold only one copy of each shard, so n=1 is the honest setting._

**Instance B** (`http://127.0.0.1:5985`)

```http
PUT /_node/_local/_config/cluster/n
"1"
```

Response: **HTTP 200 OK**

```json
""
```

- **PASS**: B accepted cluster/n=1  
  expected: HTTP 200  
  observed: HTTP 200

### Step 10: Create system database _users on B

**Instance B** (`http://127.0.0.1:5985`)

```http
PUT /_users?n=1
```

Response: **HTTP 412 Precondition Failed**

```json
{
  "error": "file_exists",
  "reason": "The database could not be created, the file already exists."
}
```

- **PASS**: _users exists on B  
  expected: HTTP 201 (created) or 412 (already exists)  
  observed: HTTP 412

### Step 11: Create system database _replicator on B

**Instance B** (`http://127.0.0.1:5985`)

```http
PUT /_replicator?n=1
```

Response: **HTTP 412 Precondition Failed**

```json
{
  "error": "file_exists",
  "reason": "The database could not be created, the file already exists."
}
```

- **PASS**: _replicator exists on B  
  expected: HTTP 201 (created) or 412 (already exists)  
  observed: HTTP 412

### Step 12: Health endpoint of B

**Instance B** (`http://127.0.0.1:5985`)

```http
GET /_up
```

Response: **HTTP 200 OK**

```json
{
  "seeds": {},
  "status": "ok"
}
```

- **PASS**: B reports status ok  
  expected: HTTP 200 {"status":"ok"}  
  observed: HTTP 200 {'seeds': {}, 'status': 'ok'}

## Test write and read

### Step 13: Write then read a test document on A

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /setup_check?n=1
```

Response: **HTTP 201 Created**

```json
{
  "ok": true
}
```

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /setup_check/hello
{
  "written_by": "01_setup.py"
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "hello",
  "rev": "1-84ac4920de61ee02d324b54e0bb66d7e"
}
```

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /setup_check/hello
```

Response: **HTTP 200 OK**

```json
{
  "_id": "hello",
  "_rev": "1-84ac4920de61ee02d324b54e0bb66d7e",
  "written_by": "01_setup.py"
}
```

- **PASS**: Read-back on A matches the write  
  expected: HTTP 201 then HTTP 200 with the same content  
  observed: HTTP 201 then HTTP 200, written_by=01_setup.py

**Instance A** (`http://127.0.0.1:5984`)

```http
DELETE /setup_check
```

Response: **HTTP 200 OK**

```json
{
  "ok": true
}
```

### Step 14: Write then read a test document on B

**Instance B** (`http://127.0.0.1:5985`)

```http
PUT /setup_check?n=1
```

Response: **HTTP 201 Created**

```json
{
  "ok": true
}
```

**Instance B** (`http://127.0.0.1:5985`)

```http
PUT /setup_check/hello
{
  "written_by": "01_setup.py"
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "hello",
  "rev": "1-84ac4920de61ee02d324b54e0bb66d7e"
}
```

**Instance B** (`http://127.0.0.1:5985`)

```http
GET /setup_check/hello
```

Response: **HTTP 200 OK**

```json
{
  "_id": "hello",
  "_rev": "1-84ac4920de61ee02d324b54e0bb66d7e",
  "written_by": "01_setup.py"
}
```

- **PASS**: Read-back on B matches the write  
  expected: HTTP 201 then HTTP 200 with the same content  
  observed: HTTP 201 then HTTP 200, written_by=01_setup.py

**Instance B** (`http://127.0.0.1:5985`)

```http
DELETE /setup_check
```

Response: **HTTP 200 OK**

```json
{
  "ok": true
}
```

## Versions and container state (best effort)

### Step 15: Record image digest and container state for the README

> Saved to evidence/00_setup/versions.txt

