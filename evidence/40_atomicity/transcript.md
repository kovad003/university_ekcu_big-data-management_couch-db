# Experiment D: update conflicts and non-atomic bulk operations

Run started: 2026-10-30T21:58:37+01:00

Configuration:
- Instance A (http://127.0.0.1:5984), database `txn_test`: normal, n=1, no replication, recreated each run

## D1. Rejecting a stale document update

### Step 1: Create a document and save its initial _rev

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /txn_test/stock-SKU-KET-04
{
  "type": "stock",
  "sku": "SKU-KET-04",
  "on_hand": 10
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "stock-SKU-KET-04",
  "rev": "1-7d26bbf8399c4225c6da325d9a3b68ec"
}
```

- **PASS**: Created  
  expected: HTTP 201, rev 1-...  
  observed: HTTP 201, rev 1-7d26bbf8399c4225c6da325d9a3b68ec

### Step 2: Client 1 updates it (on_hand 10 -> 8) using rev 1

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /txn_test/stock-SKU-KET-04
{
  "_rev": "1-7d26bbf8399c4225c6da325d9a3b68ec",
  "type": "stock",
  "sku": "SKU-KET-04",
  "on_hand": 8
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "stock-SKU-KET-04",
  "rev": "2-a0b6810f5bc505b95ac74cfcfb36ceda"
}
```

- **PASS**: Update accepted  
  expected: HTTP 201, rev 2-...  
  observed: HTTP 201, rev 2-a0b6810f5bc505b95ac74cfcfb36ceda

### Step 3: Client 2 still holds rev 1 and tries to set on_hand 10 -> 9

_This is the lost-update case. CouchDB must refuse it._

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /txn_test/stock-SKU-KET-04
{
  "_rev": "1-7d26bbf8399c4225c6da325d9a3b68ec",
  "type": "stock",
  "sku": "SKU-KET-04",
  "on_hand": 9
}
```

Response: **HTTP 409 Conflict**

```json
{
  "error": "conflict",
  "reason": "Document update conflict."
}
```

- **PASS**: Stale update rejected with 409  
  expected: HTTP 409 {"error":"conflict"}  
  observed: HTTP 409 {'error': 'conflict', 'reason': 'Document update conflict.'}

### Step 4: Read: the successful update is untouched

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /txn_test/stock-SKU-KET-04
```

Response: **HTTP 200 OK**

```json
{
  "_id": "stock-SKU-KET-04",
  "_rev": "2-a0b6810f5bc505b95ac74cfcfb36ceda",
  "type": "stock",
  "sku": "SKU-KET-04",
  "on_hand": 8
}
```

- **PASS**: Document still holds client 1's value  
  expected: _rev 2-a0b6810f5bc505b95ac74cfcfb36ceda, on_hand 8  
  observed: _rev 2-a0b6810f5bc505b95ac74cfcfb36ceda, on_hand 8

## D2. Partial success in one _bulk_docs request

### Step 5: Create bulk-a and bulk-b, save their revisions

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /txn_test/bulk-a
{
  "value": "a-v1"
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "bulk-a",
  "rev": "1-cd062a7c1e8c247bdea80d0ceb1a9164"
}
```

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /txn_test/bulk-b
{
  "value": "b-v1"
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "bulk-b",
  "rev": "1-a79a0f7f8fc1d87beb1d2dfadec24502"
}
```

### Step 6: Update bulk-b once, so the saved revision of bulk-b becomes stale

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /txn_test/bulk-b
{
  "_rev": "1-a79a0f7f8fc1d87beb1d2dfadec24502",
  "value": "b-v2"
}
```

Response: **HTTP 201 Created**

```json
{
  "ok": true,
  "id": "bulk-b",
  "rev": "2-eb1a0a7636e239a81436c5e57ba585f1"
}
```

### Step 7: One _bulk_docs request: valid update of bulk-a + stale update of bulk-b

**Instance A** (`http://127.0.0.1:5984`)

```http
POST /txn_test/_bulk_docs
{
  "docs": [
    {
      "_id": "bulk-a",
      "_rev": "1-cd062a7c1e8c247bdea80d0ceb1a9164",
      "value": "a-v2"
    },
    {
      "_id": "bulk-b",
      "_rev": "1-a79a0f7f8fc1d87beb1d2dfadec24502",
      "value": "b-v3-from-stale-rev"
    }
  ]
}
```

Response: **HTTP 201 Created**

```json
[
  {
    "ok": true,
    "id": "bulk-a",
    "rev": "2-20910ce6dd5e495475420cee48427598"
  },
  {
    "id": "bulk-b",
    "error": "conflict",
    "reason": "Document update conflict."
  }
]
```

- **PASS**: The request as a whole reports success  
  expected: HTTP 201 (even though one item fails)  
  observed: HTTP 201

- **PASS**: Item bulk-a succeeded  
  expected: {"ok": true, "rev": "2-..."}  
  observed: {'ok': True, 'id': 'bulk-a', 'rev': '2-20910ce6dd5e495475420cee48427598'}

- **PASS**: Item bulk-b rejected  
  expected: {"error": "conflict"}  
  observed: {'id': 'bulk-b', 'error': 'conflict', 'reason': 'Document update conflict.'}

### Step 8: Read both documents

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /txn_test/bulk-a
```

Response: **HTTP 200 OK**

```json
{
  "_id": "bulk-a",
  "_rev": "2-20910ce6dd5e495475420cee48427598",
  "value": "a-v2"
}
```

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /txn_test/bulk-b
```

Response: **HTTP 200 OK**

```json
{
  "_id": "bulk-b",
  "_rev": "2-eb1a0a7636e239a81436c5e57ba585f1",
  "value": "b-v2"
}
```

- **PASS**: bulk-a holds the new value  
  expected: value a-v2  
  observed: value a-v2, _rev 2-20910ce6dd5e495475420cee48427598

- **PASS**: bulk-b keeps its previous valid value  
  expected: value b-v2, _rev 2-eb1a0a7636e239a81436c5e57ba585f1  
  observed: value b-v2, _rev 2-eb1a0a7636e239a81436c5e57ba585f1

## D3. What this means for the shop: order + stock are not atomic

> A checkout writes two documents: the new order and the decremented stock count. Here the stock revision is stale, because another checkout just changed it.

### Step 9: Send both writes in one _bulk_docs request, the stock update with a stale _rev

**Instance A** (`http://127.0.0.1:5984`)

```http
POST /txn_test/_bulk_docs
{
  "docs": [
    {
      "_id": "store01:order777",
      "type": "order",
      "sku": "SKU-KET-04",
      "qty": 1,
      "status": "paid"
    },
    {
      "_id": "stock-SKU-KET-04",
      "_rev": "2-a0b6810f5bc505b95ac74cfcfb36ceda",
      "type": "stock",
      "sku": "SKU-KET-04",
      "on_hand": 7
    }
  ]
}
```

Response: **HTTP 201 Created**

```json
[
  {
    "ok": true,
    "id": "store01:order777",
    "rev": "1-ae04e33c2c723585d6fed860a2d4ebfd"
  },
  {
    "id": "stock-SKU-KET-04",
    "error": "conflict",
    "reason": "Document update conflict."
  }
]
```

- **PASS**: Order written, stock update rejected  
  expected: order ok, stock conflict  
  observed: [{'ok': True, 'id': 'store01:order777', 'rev': '1-ae04e33c2c723585d6fed860a2d4ebfd'}, {'id': 'stock-SKU-KET-04', 'error': 'conflict', 'reason': 'Document update conflict.'}]

**Instance A** (`http://127.0.0.1:5984`)

```http
GET /txn_test/stock-SKU-KET-04
```

Response: **HTTP 200 OK**

```json
{
  "_id": "stock-SKU-KET-04",
  "_rev": "3-38ba3ef7293d855451a6cc6931ff6338",
  "type": "stock",
  "sku": "SKU-KET-04",
  "on_hand": 7
}
```

- **PASS**: Stock was NOT decremented for this order  
  expected: on_hand 7 (only the concurrent checkout counted)  
  observed: on_hand 7

> The application must detect the failed item and retry or compensate. A design that avoids the problem keeps each business event in ONE document (e.g. the order itself carries the reservation) and derives stock with a view.

