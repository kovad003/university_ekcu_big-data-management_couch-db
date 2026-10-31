# Experiment A: CRUD and a Mango query

Run started: 2026-10-30T21:48:20+01:00

Configuration:
- Instance A (http://127.0.0.1:5984), database `orders` (n=1), seeded with 100 orders
- Test document id: store01:order900

## Create

### Step 1: Create a new order with a chosen _id

_PUT /db/<id> stores the document. CouchDB answers with the first revision, 1-<hash>._

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /orders/store01:order900
{
  "type": "order",
  "tenant": "store01",
  "order_no": 900,
  "status": "open",
  "customer": {
    "name": "Demo Customer",
    "email": "demo@example.com"
  },
  "items": [
    {
      "sku": "SKU-KET-04",
      "name": "Gooseneck kettle",
      "qty": 2,
      "unit_price": 72.0
    }
  ],
  "total": 144.0,
  "currency": "EUR",
  "created_at": "2026-10-30T12:00:00Z",
  "delivery": {
    "city": "Budapest",
    "street": "Fő utca 1."
  }
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "store01:order900",
  "rev": "1-623aba778c662412f193bc4687379cf7"
}
```

- **PASS**: Document created with revision 1  
  expected: HTTP 201, rev 1-...  
  observed: HTTP 201, rev 1-623aba778c662412f193bc4687379cf7

## Read

### Step 2: Read it back by _id

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /orders/store01:order900
```

Response: **HTTP 200 OK**

```json
{
  "_id": "store01:order900",
  "_rev": "1-623aba778c662412f193bc4687379cf7",
  "type": "order",
  "tenant": "store01",
  "order_no": 900,
  "status": "open",
  "customer": {
    "name": "Demo Customer",
    "email": "demo@example.com"
  },
  "items": [
    {
      "sku": "SKU-KET-04",
      "name": "Gooseneck kettle",
      "qty": 2,
      "unit_price": 72.0
    }
  ],
  "total": 144.0,
  "currency": "EUR",
  "created_at": "2026-10-30T12:00:00Z",
  "delivery": {
    "city": "Budapest",
    "street": "Fő utca 1."
  }
}
```

- **PASS**: Read returns the stored content and current _rev  
  expected: HTTP 200, _rev 1-623aba778c662412f193bc4687379cf7, status open  
  observed: HTTP 200, _rev 1-623aba778c662412f193bc4687379cf7, status open

## Update

### Step 3: Update: mark the order as paid, sending the current _rev

_An update replaces the whole document. Sending _rev proves which version we are changing._

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /orders/store01:order900
{
  "_id": "store01:order900",
  "_rev": "1-623aba778c662412f193bc4687379cf7",
  "type": "order",
  "tenant": "store01",
  "order_no": 900,
  "status": "paid",
  "customer": {
    "name": "Demo Customer",
    "email": "demo@example.com"
  },
  "items": [
    {
      "sku": "SKU-KET-04",
      "name": "Gooseneck kettle",
      "qty": 2,
      "unit_price": 72.0
    }
  ],
  "total": 144.0,
  "currency": "EUR",
  "created_at": "2026-10-30T12:00:00Z",
  "delivery": {
    "city": "Budapest",
    "street": "Fő utca 1."
  }
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "store01:order900",
  "rev": "2-7826c76f9c57a2271ad6e872e2a32712"
}
```

- **PASS**: Update accepted with a new revision 2  
  expected: HTTP 201, rev 2-...  
  observed: HTTP 201, rev 2-7826c76f9c57a2271ad6e872e2a32712

### Step 4: Verify the new state

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /orders/store01:order900
```

Response: **HTTP 200 OK**

```json
{
  "_id": "store01:order900",
  "_rev": "2-7826c76f9c57a2271ad6e872e2a32712",
  "type": "order",
  "tenant": "store01",
  "order_no": 900,
  "status": "paid",
  "customer": {
    "name": "Demo Customer",
    "email": "demo@example.com"
  },
  "items": [
    {
      "sku": "SKU-KET-04",
      "name": "Gooseneck kettle",
      "qty": 2,
      "unit_price": 72.0
    }
  ],
  "total": 144.0,
  "currency": "EUR",
  "created_at": "2026-10-30T12:00:00Z",
  "delivery": {
    "city": "Budapest",
    "street": "Fő utca 1."
  }
}
```

- **PASS**: Stored status is now paid  
  expected: status paid, _rev 2-7826c76f9c57a2271ad6e872e2a32712  
  observed: status paid, _rev 2-7826c76f9c57a2271ad6e872e2a32712

## Delete

### Step 5: Delete: DELETE with the current revision

_Deletion writes a new 'tombstone' revision, so replication can pass the delete on._

**Instance A** (`http://127.0.0.1:5984`)

```http
DELETE /orders/store01:order900?rev=2-7826c76f9c57a2271ad6e872e2a32712
```

Response: **HTTP 200 OK**

```json
{
  "ok": true,
  "id": "store01:order900",
  "rev": "3-11ad1671148a2236c25ff065cf0b89ac"
}
```

- **PASS**: Delete accepted (tombstone revision 3)  
  expected: HTTP 200, rev 3-...  
  observed: HTTP 200, rev 3-11ad1671148a2236c25ff065cf0b89ac

### Step 6: Verify the document is gone

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /orders/store01:order900
```

Response: **HTTP 404 Object Not Found**

```json
{
  "error": "not_found",
  "reason": "deleted"
}
```

- **PASS**: Read after delete returns 404 deleted  
  expected: HTTP 404 {"reason":"deleted"}  
  observed: HTTP 404 {'error': 'not_found', 'reason': 'deleted'}

## Mango query: open orders over 100 EUR for one store, newest first

### Step 7: Create a JSON index on (tenant, status, created_at)

_Equality on tenant and status, then created_at gives the sort order._

**Instance A** (`http://127.0.0.1:5984`)

```http
POST /orders/_index
{
  "index": {
    "fields": [
      "tenant",
      "status",
      "created_at"
    ]
  },
  "name": "tenant-status-created",
  "type": "json",
  "ddoc": "idx-tenant-status-created"
}
```

Response: **HTTP 200 OK**

```json
{
  "result": "created",
  "id": "_design/idx-tenant-status-created",
  "name": "tenant-status-created"
}
```

- **PASS**: Index exists  
  expected: result "created" (or "exists" on re-run)  
  observed: HTTP 200, result created

### Step 8: Ask CouchDB which index it will use (_explain)

**Instance A** (`http://127.0.0.1:5984`)

```http
POST /orders/_explain
{
  "selector": {
    "tenant": "store01",
    "status": "open",
    "total": {
      "$gt": 100
    }
  },
  "fields": [
    "_id",
    "customer.name",
    "total",
    "created_at"
  ],
  "sort": [
    {
      "tenant": "desc"
    },
    {
      "status": "desc"
    },
    {
      "created_at": "desc"
    }
  ],
  "limit": 50
}
```

Response: **HTTP 200 OK**

```json
{
  "dbname": "orders",
  "index": {
    "ddoc": "_design/idx-tenant-status-created",
    "name": "tenant-status-created",
    "type": "json",
    "partitioned": false,
    "def": {
      "fields": [
        {
          "tenant": "asc"
        },
        {
          "status": "asc"
        },
        {
          "created_at": "asc"
        }
      ]
    }
  },
  "partitioned": false,
  "selector": {
    "$and": [
      {
        "tenant": {
          "$eq": "store01"
        }
      },
      {
        "status": {
          "$eq": "open"
        }
      },
      {
        "total": {
          "$gt": 100
        }
      }
    ]
  },
  "opts": {
    "use_index": [],
    "bookmark": "nil",
    "limit": 50,
    "skip": 0,
    "sort": {
      "tenant": "desc",
      "status": "desc",
      "created_at": "desc"
    },
    "fields": [
      "_id",
      "customer.name",
      "total",
      "created_at"
    ],
    "partition": "",
    "r": 1,
    "conflicts": false,
    "stale": false,
    "update": true,
    "stable": false,
    "execution_stats": false,
    "allow_fallback": true
  },
  "limit": 50,
  "skip": 0,
  "fields": [
    "_id",
    "customer.name",
    "total",
    "created_at"
  ],
  "index_candidates": [
    {
      "index": {
        "ddoc": null,
        "name": "_all_docs",
        "type": "special",
        "def": {
          "fields": [
            {
              "_id": "asc"
            }
          ]
        }
      },
      "analysis": {
        "usable": false,
        "reasons": [
          {
            "name": "field_mismatch"
          }
        ],
        "ranking": 1,
        "covering": null
      }
    }
  ],
  "selector_hints": [
    {
      "type": "json",
      "indexable_fields": [
        "status",
        "tenant",
        "total"
      ],
      "unindexable_fields": []
    }
  ],
  "mrargs": {
    "include_docs": true,
    "view_type": "map",
    "reduce": false,
    "partition": null,
    "start_key": [
      "store01",
      "open",
      "<MAX>"
    ],
    "end_key": [
      "store01",
      "open"
    ],
    "direction": "rev",
    "stable": false,
    "update": true,
    "conflicts": "undefined"
  },
  "covering": false
}
```

- **PASS**: Query planner selects our index  
  expected: index tenant-status-created  
  observed: index tenant-status-created

### Step 9: Run the query

**Instance A** (`http://127.0.0.1:5984`)

```http
POST /orders/_find
{
  "selector": {
    "tenant": "store01",
    "status": "open",
    "total": {
      "$gt": 100
    }
  },
  "fields": [
    "_id",
    "customer.name",
    "total",
    "created_at"
  ],
  "sort": [
    {
      "tenant": "desc"
    },
    {
      "status": "desc"
    },
    {
      "created_at": "desc"
    }
  ],
  "limit": 50,
  "execution_stats": true
}
```

Response: **HTTP 200 OK**

```json
{
  "docs": [
    {
      "_id": "store01:order008",
      "customer": {
        "name": "István Kiss"
      },
      "total": 204.3,
      "created_at": "2026-10-24T10:44:00Z"
    },
    {
      "_id": "store01:order009",
      "customer": {
        "name": "Nóra Nagy"
      },
      "total": 220.1,
      "created_at": "2026-10-06T08:32:00Z"
    },
    {
      "_id": "store01:order007",
      "customer": {
        "name": "Kata Kiss"
      },
      "total": 150.0,
      "created_at": "2026-09-25T16:53:00Z"
    },
    {
      "_id": "store01:order018",
      "customer": {
        "name": "Eszter Kiss"
      },
      "total": 139.6,
      "created_at": "2026-09-18T00:50:00Z"
    },
    {
      "_id": "store01:order020",
      "customer": {
        "name": "Nóra Molnár"
      },
      "total": 225.6,
      "created_at": "2026-09-15T10:09:00Z"
    },
    {
      "_id": "store01:order003",
      "customer": {
        "name": "Gréta Varga"
      },
      "total": 133.8,
      "created_at": "2026-09-10T15:16:00Z"
    }
  ],
  "bookmark": "g1AAAABveJzLYWBgYMpgSmHgKy5JLCrJTq2MT8lPzkzJBYoLFJfkF6UaGFrlF6WkFhkYGIPUccDU5QBVMIOUsUOVgdgs-QWpeSCGiJGBkZmugaWuoUGIoamVoZmVgUFUVhYAjlkciw",
  "execution_stats": {
    "total_keys_examined": 10,
    "total_docs_examined": 10,
    "total_quorum_docs_examined": 0,
    "results_returned": 6,
    "execution_time_ms": 31.142
  }
}
```

- **PASS**: Result equals a client-side filter of all documents, in the same order  
  expected: 6 ids: ['store01:order008', 'store01:order009', 'store01:order007', 'store01:order018', 'store01:order020', 'store01:order003']  
  observed: 6 ids: ['store01:order008', 'store01:order009', 'store01:order007', 'store01:order018', 'store01:order020', 'store01:order003']

> execution_stats: {'total_keys_examined': 10, 'total_docs_examined': 10, 'total_quorum_docs_examined': 0, 'results_returned': 6, 'execution_time_ms': 31.142}

