# Seed the demo database

Run started: 2026-10-30T21:48:30+01:00

Configuration:
- Dataset: 100 orders, 5 stores x 20, seed 42 (self-generated, see scripts/lib/data.py)
- Database `orders` on A and B, replica count n=1

### Step 1: Create database `orders` on A with n=1

**Instance A** (`http://127.0.0.1:5984`)

```http
PUT /orders?n=1
```

Response: **HTTP 201 Created**

```json
{
  "ok": true
}
```

- **PASS**: `orders` exists on A  
  expected: HTTP 201, or 412 if it already exists  
  observed: HTTP 201

### Step 2: Create database `orders` on B with n=1

**Instance B** (`http://127.0.0.1:5985`)

```http
PUT /orders?n=1
```

Response: **HTTP 201 Created**

```json
{
  "ok": true
}
```

- **PASS**: `orders` exists on B  
  expected: HTTP 201, or 412 if it already exists  
  observed: HTTP 201

### Step 3: Show one sample document before loading

_This is the data model (Part 3)._

> {"_id": "store01:order001", "type": "order", "tenant": "store01", "order_no": 1, "status": "open", "customer": {"name": "István Szabó", "email": "istvan.szabo1@example.com"}, "items": [{"sku": "SKU-COF-01", "name": "Coffee beans 1 kg", "qty": 3, "unit_price": 18.9}], "total": 56.7, "currency": "EUR", "created_at": "2026-09-21T15:36:00Z", "delivery": {"city": "Budapest", "street": "Dózsa György út 12."}}

### Step 4: Load 100 orders into A with one _bulk_docs request

**Instance A** (`http://127.0.0.1:5984`)

```http
POST /orders/_bulk_docs
{
  "docs": [
    {
      "_id": "store01:order001",
      "type": "order",
      "tenant": "store01",
      "order_no": 1,
      "status": "open",
      "customer": {
        "name": "István Szabó",
        "email": "istvan.szabo1@example.com"
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
      "created_at": "2026-09-21T15:36:00Z",
      "delivery": {
        "city": "Budapest",
        "street": "Dózsa György út 12."
      }
    },
    {
      "_id": "store01:order002",
      "type": "order",
      "tenant": "store01",
      "order_no": 2,
      "status": "paid",
      "customer": {
        "name": "Gréta Kiss",
        "email": "greta.kiss2@example.com"
      },
      "items": [
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 1,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 3,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 3,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 1,
          "unit_price": 9.5
        }
      ],
      "total": 185.3,
      "currency": "EUR",
      "created_at": "2026-09-21T09:33:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Fő utca 98."
      }
    },
    {
      "_id": "store01:order003",
      "type": "order",
      "tenant": "store01",
      "order_no": 3,
      "status": "open",
      "customer": {
        "name": "Gréta Varga",
        "email": "greta.varga3@example.com"
      },
      "items": [
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 2,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 1,
          "unit_price": 54.0
        }
      ],
      "total": 133.8,
      "currency": "EUR",
      "created_at": "2026-09-10T15:16:00Z",
      "delivery": {
        "city": "Budapest",
        "street": "Petőfi utca 109."
      }
    },
    {
      "_id": "store01:order004",
      "type": "order",
      "tenant": "store01",
      "order_no": 4,
      "status": "paid",
      "customer": {
        "name": "Dániel Kiss",
        "email": "daniel.kiss4@example.com"
      },
      "items": [
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 3,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 2,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 3,
          "unit_price": 18.9
        }
      ],
      "total": 155.1,
      "currency": "EUR",
      "created_at": "2026-09-08T12:08:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Dózsa György út 114."
      }
    },
    {
      "_id": "store01:order005",
      "type": "order",
      "tenant": "store01",
      "order_no": 5,
      "status": "shipped",
      "customer": {
        "name": "Júlia Nagy",
        "email": "julia.nagy5@example.com"
      },
      "items": [
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 1,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 3,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 1,
          "unit_price": 18.9
        }
      ],
      "total": 162.9,
      "currency": "EUR",
      "created_at": "2026-09-22T12:32:00Z",
      "delivery": {
        "city": "Pécs",
        "street": "Petőfi utca 59."
      }
    },
    {
      "_id": "store01:order006",
      "type": "order",
      "tenant": "store01",
      "order_no": 6,
      "status": "shipped",
      "customer": {
        "name": "Csilla Tóth",
        "email": "csilla.toth6@example.com"
      },
      "items": [
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 1,
          "unit_price": 54.0
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 3,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 2,
          "unit_price": 39.9
        }
      ],
      "total": 171.0,
      "currency": "EUR",
      "created_at": "2026-10-19T22:50:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Rákóczi út 49."
      }
    },
    {
      "_id": "store01:order007",
      "type": "order",
      "tenant": "store01",
      "order_no": 7,
      "status": "open",
      "customer": {
        "name": "Kata Kiss",
        "email": "kata.kiss7@example.com"
      },
      "items": [
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 1,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 1,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 1,
          "unit_price": 54.0
        }
      ],
      "total": 150.0,
      "currency": "EUR",
      "created_at": "2026-09-25T16:53:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Petőfi utca 28."
      }
    },
    {
      "_id": "store01:order008",
      "type": "order",
      "tenant": "store01",
      "order_no": 8,
      "status": "open",
      "customer": {
        "name": "István Kiss",
        "email": "istvan.kiss8@example.com"
      },
      "items": [
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 2,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 1,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 1,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 3,
          "unit_price": 9.5
        }
      ],
      "total": 204.3,
      "currency": "EUR",
      "created_at": "2026-10-24T10:44:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Kossuth tér 66."
      }
    },
    {
      "_id": "store01:order009",
      "type": "order",
      "tenant": "store01",
      "order_no": 9,
      "status": "open",
      "customer": {
        "name": "Nóra Nagy",
        "email": "nora.nagy9@example.com"
      },
      "items": [
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 1,
          "unit_price": 9.5
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 3,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 1,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 3,
          "unit_price": 24.0
        }
      ],
      "total": 220.1,
      "currency": "EUR",
      "created_at": "2026-10-06T08:32:00Z",
      "delivery": {
        "city": "Pécs",
        "street": "Dózsa György út 33."
      }
    },
    {
      "_id": "store01:order010",
      "type": "order",
      "tenant": "store01",
      "order_no": 10,
      "status": "open",
      "customer": {
        "name": "István Varga",
        "email": "istvan.varga10@example.com"
      },
      "items": [
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 3,
          "unit_price": 9.5
        }
      ],
      "total": 28.5,
      "currency": "EUR",
      "created_at": "2026-09-11T11:41:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Rákóczi út 1."
      }
    },
    {
      "_id": "store01:order011",
      "type": "order",
      "tenant": "store01",
      "order_no": 11,
      "status": "shipped",
      "customer": {
        "name": "Gréta Tóth",
        "email": "greta.toth11@example.com"
      },
      "items": [
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 3,
          "unit_price": 54.0
        },
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 2,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 3,
          "unit_price": 18.9
        }
      ],
      "total": 231.1,
      "currency": "EUR",
      "created_at": "2026-10-05T08:49:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Dózsa György út 118."
      }
    },
    {
      "_id": "store01:order012",
      "type": "order",
      "tenant": "store01",
      "order_no": 12,
      "status": "shipped",
      "customer": {
        "name": "Anna Nagy",
        "email": "anna.nagy12@example.com"
      },
      "items": [
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 2,
          "unit_price": 24.0
        }
      ],
      "total": 48.0,
      "currency": "EUR",
      "created_at": "2026-10-04T08:56:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Kossuth tér 8."
      }
    },
    {
      "_id": "store01:order013",
      "type": "order",
      "tenant": "store01",
      "order_no": 13,
      "status": "shipped",
      "customer": {
        "name": "Csilla Tóth",
        "email": "csilla.toth13@example.com"
      },
      "items": [
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 3,
          "unit_price": 9.5
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 2,
          "unit_price": 18.9
        }
      ],
      "total": 66.3,
      "currency": "EUR",
      "created_at": "2026-09-13T00:28:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Kossuth tér 34."
      }
    },
    {
      "_id": "store01:order014",
      "type": "order",
      "tenant": "store01",
      "order_no": 14,
      "status": "paid",
      "customer": {
        "name": "László Molnár",
        "email": "laszlo.molnar14@example.com"
      },
      "items": [
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 3,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 2,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 2,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 3,
          "unit_price": 9.5
        }
      ],
      "total": 304.9,
      "currency": "EUR",
      "created_at": "2026-10-18T10:39:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Kossuth tér 9."
      }
    },
    {
      "_id": "store01:order015",
      "type": "order",
      "tenant": "store01",
      "order_no": 15,
      "status": "open",
      "customer": {
        "name": "Anna Nagy",
        "email": "anna.nagy15@example.com"
      },
      "items": [
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 1,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 3,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 1,
          "unit_price": 39.9
        }
      ],
      "total": 77.4,
      "currency": "EUR",
      "created_at": "2026-09-06T16:36:00Z",
      "delivery": {
        "city": "Budapest",
        "street": "Petőfi utca 10."
      }
    },
    {
      "_id": "store01:order016",
      "type": "order",
      "tenant": "store01",
      "order_no": 16,
      "status": "shipped",
      "customer": {
        "name": "Eszter Molnár",
        "email": "eszter.molnar16@example.com"
      },
      "items": [
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 2,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 1,
          "unit_price": 24.0
        }
      ],
      "total": 36.4,
      "currency": "EUR",
      "created_at": "2026-09-23T10:50:00Z",
      "delivery": {
        "city": "Pécs",
        "street": "Kossuth tér 13."
      }
    },
    {
      "_id": "store01:order017",
      "type": "order",
      "tenant": "store01",
      "order_no": 17,
      "status": "shipped",
      "customer": {
        "name": "Nóra Kiss",
        "email": "nora.kiss17@example.com"
      },
      "items": [
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 2,
          "unit_price": 39.9
        }
      ],
      "total": 79.8,
      "currency": "EUR",
      "created_at": "2026-10-13T20:13:00Z",
      "delivery": {
        "city": "Budapest",
        "street": "Fő utca 8."
      }
    },
    {
      "_id": "store01:order018",
      "type": "order",
      "tenant": "store01",
      "order_no": 18,
      "status": "open",
      "customer": {
        "name": "Eszter Kiss",
        "email": "eszter.kiss18@example.com"
      },
      "items": [
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 1,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 1,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 3,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 2,
          "unit_price": 9.5
        }
      ],
      "total": 139.6,
      "currency": "EUR",
      "created_at": "2026-09-18T00:50:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Fő utca 57."
      }
    },
    {
      "_id": "store01:order019",
      "type": "order",
      "tenant": "store01",
      "order_no": 19,
      "status": "open",
      "customer": {
        "name": "Anna Nagy",
        "email": "anna.nagy19@example.com"
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
      "created_at": "2026-09-22T20:22:00Z",
      "delivery": {
        "city": "Pécs",
        "street": "Rákóczi út 28."
      }
    },
    {
      "_id": "store01:order020",
      "type": "order",
      "tenant": "store01",
      "order_no": 20,
      "status": "open",
      "customer": {
        "name": "Nóra Molnár",
        "email": "nora.molnar20@example.com"
      },
      "items": [
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 2,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 2,
          "unit_price": 9.5
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 2,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 2,
          "unit_price": 12.4
        }
      ],
      "total": 225.6,
      "currency": "EUR",
      "created_at": "2026-09-15T10:09:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Fő utca 75."
      }
    },
    {
      "_id": "store02:order001",
      "type": "order",
      "tenant": "store02",
      "order_no": 1,
      "status": "cancelled",
      "customer": {
        "name": "Bence Molnár",
        "email": "bence.molnar1@example.com"
      },
      "items": [
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 1,
          "unit_price": 24.0
        }
      ],
      "total": 24.0,
      "currency": "EUR",
      "created_at": "2026-10-17T02:29:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Kossuth tér 8."
      }
    },
    {
      "_id": "store02:order002",
      "type": "order",
      "tenant": "store02",
      "order_no": 2,
      "status": "open",
      "customer": {
        "name": "Csilla Szabó",
        "email": "csilla.szabo2@example.com"
      },
      "items": [
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 1,
          "unit_price": 54.0
        }
      ],
      "total": 54.0,
      "currency": "EUR",
      "created_at": "2026-10-08T02:03:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Kossuth tér 75."
      }
    },
    {
      "_id": "store02:order003",
      "type": "order",
      "tenant": "store02",
      "order_no": 3,
      "status": "shipped",
      "customer": {
        "name": "Kata Horváth",
        "email": "kata.horvath3@example.com"
      },
      "items": [
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 2,
          "unit_price": 9.5
        }
      ],
      "total": 19.0,
      "currency": "EUR",
      "created_at": "2026-09-19T22:12:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Kossuth tér 34."
      }
    },
    {
      "_id": "store02:order004",
      "type": "order",
      "tenant": "store02",
      "order_no": 4,
      "status": "paid",
      "customer": {
        "name": "Olivér Nagy",
        "email": "oliver.nagy4@example.com"
      },
      "items": [
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 2,
          "unit_price": 54.0
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 2,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 1,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 1,
          "unit_price": 12.4
        }
      ],
      "total": 208.3,
      "currency": "EUR",
      "created_at": "2026-09-08T00:02:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Petőfi utca 17."
      }
    },
    {
      "_id": "store02:order005",
      "type": "order",
      "tenant": "store02",
      "order_no": 5,
      "status": "open",
      "customer": {
        "name": "Júlia Kovács",
        "email": "julia.kovacs5@example.com"
      },
      "items": [
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 2,
          "unit_price": 9.5
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 1,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 2,
          "unit_price": 54.0
        }
      ],
      "total": 139.4,
      "currency": "EUR",
      "created_at": "2026-10-21T19:32:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Fő utca 113."
      }
    },
    {
      "_id": "store02:order006",
      "type": "order",
      "tenant": "store02",
      "order_no": 6,
      "status": "paid",
      "customer": {
        "name": "Eszter Horváth",
        "email": "eszter.horvath6@example.com"
      },
      "items": [
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 1,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 3,
          "unit_price": 18.9
        }
      ],
      "total": 62.9,
      "currency": "EUR",
      "created_at": "2026-09-26T23:30:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Petőfi utca 27."
      }
    },
    {
      "_id": "store02:order007",
      "type": "order",
      "tenant": "store02",
      "order_no": 7,
      "status": "open",
      "customer": {
        "name": "István Kovács",
        "email": "istvan.kovacs7@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 1,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 3,
          "unit_price": 54.0
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 2,
          "unit_price": 18.9
        }
      ],
      "total": 212.2,
      "currency": "EUR",
      "created_at": "2026-09-01T15:44:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Petőfi utca 21."
      }
    },
    {
      "_id": "store02:order008",
      "type": "order",
      "tenant": "store02",
      "order_no": 8,
      "status": "paid",
      "customer": {
        "name": "Bence Varga",
        "email": "bence.varga8@example.com"
      },
      "items": [
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 1,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 3,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 1,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 3,
          "unit_price": 24.0
        }
      ],
      "total": 149.4,
      "currency": "EUR",
      "created_at": "2026-10-24T08:30:00Z",
      "delivery": {
        "city": "Pécs",
        "street": "Kossuth tér 6."
      }
    },
    {
      "_id": "store02:order009",
      "type": "order",
      "tenant": "store02",
      "order_no": 9,
      "status": "shipped",
      "customer": {
        "name": "Hanna Nagy",
        "email": "hanna.nagy9@example.com"
      },
      "items": [
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 2,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 1,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 3,
          "unit_price": 18.9
        }
      ],
      "total": 144.6,
      "currency": "EUR",
      "created_at": "2026-10-03T12:37:00Z",
      "delivery": {
        "city": "Pécs",
        "street": "Dózsa György út 96."
      }
    },
    {
      "_id": "store02:order010",
      "type": "order",
      "tenant": "store02",
      "order_no": 10,
      "status": "shipped",
      "customer": {
        "name": "Nóra Kovács",
        "email": "nora.kovacs10@example.com"
      },
      "items": [
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 1,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 1,
          "unit_price": 39.9
        }
      ],
      "total": 111.9,
      "currency": "EUR",
      "created_at": "2026-09-17T15:49:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Rákóczi út 103."
      }
    },
    {
      "_id": "store02:order011",
      "type": "order",
      "tenant": "store02",
      "order_no": 11,
      "status": "open",
      "customer": {
        "name": "Márk Kovács",
        "email": "mark.kovacs11@example.com"
      },
      "items": [
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 3,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 1,
          "unit_price": 9.5
        }
      ],
      "total": 28.1,
      "currency": "EUR",
      "created_at": "2026-10-14T04:14:00Z",
      "delivery": {
        "city": "Pécs",
        "street": "Petőfi utca 40."
      }
    },
    {
      "_id": "store02:order012",
      "type": "order",
      "tenant": "store02",
      "order_no": 12,
      "status": "shipped",
      "customer": {
        "name": "Márk Varga",
        "email": "mark.varga12@example.com"
      },
      "items": [
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 3,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 1,
          "unit_price": 18.9
        }
      ],
      "total": 234.9,
      "currency": "EUR",
      "created_at": "2026-09-26T16:37:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Petőfi utca 83."
      }
    },
    {
      "_id": "store02:order013",
      "type": "order",
      "tenant": "store02",
      "order_no": 13,
      "status": "shipped",
      "customer": {
        "name": "Dániel Kiss",
        "email": "daniel.kiss13@example.com"
      },
      "items": [
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 1,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 3,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 2,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 1,
          "unit_price": 54.0
        }
      ],
      "total": 214.5,
      "currency": "EUR",
      "created_at": "2026-10-02T19:09:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Rákóczi út 78."
      }
    },
    {
      "_id": "store02:order014",
      "type": "order",
      "tenant": "store02",
      "order_no": 14,
      "status": "shipped",
      "customer": {
        "name": "Gréta Horváth",
        "email": "greta.horvath14@example.com"
      },
      "items": [
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 3,
          "unit_price": 39.9
        }
      ],
      "total": 119.7,
      "currency": "EUR",
      "created_at": "2026-09-05T08:57:00Z",
      "delivery": {
        "city": "Budapest",
        "street": "Dózsa György út 119."
      }
    },
    {
      "_id": "store02:order015",
      "type": "order",
      "tenant": "store02",
      "order_no": 15,
      "status": "shipped",
      "customer": {
        "name": "Kata Varga",
        "email": "kata.varga15@example.com"
      },
      "items": [
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 1,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 3,
          "unit_price": 72.0
        }
      ],
      "total": 240.0,
      "currency": "EUR",
      "created_at": "2026-09-12T16:14:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Dózsa György út 40."
      }
    },
    {
      "_id": "store02:order016",
      "type": "order",
      "tenant": "store02",
      "order_no": 16,
      "status": "open",
      "customer": {
        "name": "Márk Tóth",
        "email": "mark.toth16@example.com"
      },
      "items": [
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 3,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 1,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 1,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 2,
          "unit_price": 54.0
        }
      ],
      "total": 264.4,
      "currency": "EUR",
      "created_at": "2026-10-23T03:13:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Fő utca 39."
      }
    },
    {
      "_id": "store02:order017",
      "type": "order",
      "tenant": "store02",
      "order_no": 17,
      "status": "shipped",
      "customer": {
        "name": "Olivér Molnár",
        "email": "oliver.molnar17@example.com"
      },
      "items": [
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 3,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 3,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 2,
          "unit_price": 6.2
        }
      ],
      "total": 265.6,
      "currency": "EUR",
      "created_at": "2026-10-11T13:54:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Rákóczi út 102."
      }
    },
    {
      "_id": "store02:order018",
      "type": "order",
      "tenant": "store02",
      "order_no": 18,
      "status": "shipped",
      "customer": {
        "name": "Kata Nagy",
        "email": "kata.nagy18@example.com"
      },
      "items": [
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 3,
          "unit_price": 9.5
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 3,
          "unit_price": 54.0
        }
      ],
      "total": 190.5,
      "currency": "EUR",
      "created_at": "2026-09-22T17:04:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Kossuth tér 19."
      }
    },
    {
      "_id": "store02:order019",
      "type": "order",
      "tenant": "store02",
      "order_no": 19,
      "status": "paid",
      "customer": {
        "name": "Petra Nagy",
        "email": "petra.nagy19@example.com"
      },
      "items": [
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 1,
          "unit_price": 18.9
        }
      ],
      "total": 18.9,
      "currency": "EUR",
      "created_at": "2026-10-12T18:52:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Dózsa György út 25."
      }
    },
    {
      "_id": "store02:order020",
      "type": "order",
      "tenant": "store02",
      "order_no": 20,
      "status": "shipped",
      "customer": {
        "name": "Nóra Szabó",
        "email": "nora.szabo20@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 3,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 3,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 1,
          "unit_price": 9.5
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 1,
          "unit_price": 24.0
        }
      ],
      "total": 286.7,
      "currency": "EUR",
      "created_at": "2026-09-17T08:13:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Dózsa György út 60."
      }
    },
    {
      "_id": "store03:order001",
      "type": "order",
      "tenant": "store03",
      "order_no": 1,
      "status": "shipped",
      "customer": {
        "name": "Olivér Tóth",
        "email": "oliver.toth1@example.com"
      },
      "items": [
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 1,
          "unit_price": 72.0
        }
      ],
      "total": 72.0,
      "currency": "EUR",
      "created_at": "2026-10-13T15:01:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Dózsa György út 41."
      }
    },
    {
      "_id": "store03:order002",
      "type": "order",
      "tenant": "store03",
      "order_no": 2,
      "status": "shipped",
      "customer": {
        "name": "István Szabó",
        "email": "istvan.szabo2@example.com"
      },
      "items": [
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 1,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 3,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 2,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 2,
          "unit_price": 72.0
        }
      ],
      "total": 233.5,
      "currency": "EUR",
      "created_at": "2026-09-26T13:47:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Rákóczi út 81."
      }
    },
    {
      "_id": "store03:order003",
      "type": "order",
      "tenant": "store03",
      "order_no": 3,
      "status": "open",
      "customer": {
        "name": "Júlia Szabó",
        "email": "julia.szabo3@example.com"
      },
      "items": [
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 1,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 3,
          "unit_price": 72.0
        }
      ],
      "total": 222.2,
      "currency": "EUR",
      "created_at": "2026-09-26T01:34:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Fő utca 18."
      }
    },
    {
      "_id": "store03:order004",
      "type": "order",
      "tenant": "store03",
      "order_no": 4,
      "status": "paid",
      "customer": {
        "name": "Gréta Nagy",
        "email": "greta.nagy4@example.com"
      },
      "items": [
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 3,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 1,
          "unit_price": 12.4
        }
      ],
      "total": 228.4,
      "currency": "EUR",
      "created_at": "2026-10-09T02:17:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Rákóczi út 54."
      }
    },
    {
      "_id": "store03:order005",
      "type": "order",
      "tenant": "store03",
      "order_no": 5,
      "status": "open",
      "customer": {
        "name": "Márk Kovács",
        "email": "mark.kovacs5@example.com"
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
      "created_at": "2026-10-23T17:36:00Z",
      "delivery": {
        "city": "Budapest",
        "street": "Petőfi utca 39."
      }
    },
    {
      "_id": "store03:order006",
      "type": "order",
      "tenant": "store03",
      "order_no": 6,
      "status": "open",
      "customer": {
        "name": "István Kiss",
        "email": "istvan.kiss6@example.com"
      },
      "items": [
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 3,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 1,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 2,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 1,
          "unit_price": 12.4
        }
      ],
      "total": 186.3,
      "currency": "EUR",
      "created_at": "2026-10-15T12:54:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Rákóczi út 93."
      }
    },
    {
      "_id": "store03:order007",
      "type": "order",
      "tenant": "store03",
      "order_no": 7,
      "status": "paid",
      "customer": {
        "name": "Anna Kiss",
        "email": "anna.kiss7@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 3,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 3,
          "unit_price": 9.5
        }
      ],
      "total": 65.7,
      "currency": "EUR",
      "created_at": "2026-10-25T05:00:00Z",
      "delivery": {
        "city": "Budapest",
        "street": "Fő utca 83."
      }
    },
    {
      "_id": "store03:order008",
      "type": "order",
      "tenant": "store03",
      "order_no": 8,
      "status": "open",
      "customer": {
        "name": "Gréta Molnár",
        "email": "greta.molnar8@example.com"
      },
      "items": [
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 1,
          "unit_price": 54.0
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 2,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 2,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 2,
          "unit_price": 9.5
        }
      ],
      "total": 296.8,
      "currency": "EUR",
      "created_at": "2026-10-01T02:00:00Z",
      "delivery": {
        "city": "Pécs",
        "street": "Petőfi utca 97."
      }
    },
    {
      "_id": "store03:order009",
      "type": "order",
      "tenant": "store03",
      "order_no": 9,
      "status": "shipped",
      "customer": {
        "name": "László Szabó",
        "email": "laszlo.szabo9@example.com"
      },
      "items": [
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 1,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 3,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 3,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 1,
          "unit_price": 72.0
        }
      ],
      "total": 254.6,
      "currency": "EUR",
      "created_at": "2026-09-07T13:53:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Fő utca 97."
      }
    },
    {
      "_id": "store03:order010",
      "type": "order",
      "tenant": "store03",
      "order_no": 10,
      "status": "open",
      "customer": {
        "name": "Anna Tóth",
        "email": "anna.toth10@example.com"
      },
      "items": [
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 1,
          "unit_price": 72.0
        }
      ],
      "total": 72.0,
      "currency": "EUR",
      "created_at": "2026-09-23T01:06:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Fő utca 73."
      }
    },
    {
      "_id": "store03:order011",
      "type": "order",
      "tenant": "store03",
      "order_no": 11,
      "status": "cancelled",
      "customer": {
        "name": "Ferenc Nagy",
        "email": "ferenc.nagy11@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 2,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 2,
          "unit_price": 24.0
        }
      ],
      "total": 72.8,
      "currency": "EUR",
      "created_at": "2026-09-16T05:45:00Z",
      "delivery": {
        "city": "Budapest",
        "street": "Dózsa György út 4."
      }
    },
    {
      "_id": "store03:order012",
      "type": "order",
      "tenant": "store03",
      "order_no": 12,
      "status": "shipped",
      "customer": {
        "name": "Hanna Nagy",
        "email": "hanna.nagy12@example.com"
      },
      "items": [
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 1,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 1,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 3,
          "unit_price": 24.0
        }
      ],
      "total": 183.9,
      "currency": "EUR",
      "created_at": "2026-09-28T18:49:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Fő utca 102."
      }
    },
    {
      "_id": "store03:order013",
      "type": "order",
      "tenant": "store03",
      "order_no": 13,
      "status": "paid",
      "customer": {
        "name": "Nóra Varga",
        "email": "nora.varga13@example.com"
      },
      "items": [
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 3,
          "unit_price": 24.0
        }
      ],
      "total": 72.0,
      "currency": "EUR",
      "created_at": "2026-09-07T14:38:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Fő utca 109."
      }
    },
    {
      "_id": "store03:order014",
      "type": "order",
      "tenant": "store03",
      "order_no": 14,
      "status": "cancelled",
      "customer": {
        "name": "Nóra Tóth",
        "email": "nora.toth14@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 3,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 2,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 3,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 1,
          "unit_price": 54.0
        }
      ],
      "total": 345.0,
      "currency": "EUR",
      "created_at": "2026-10-18T19:46:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Dózsa György út 104."
      }
    },
    {
      "_id": "store03:order015",
      "type": "order",
      "tenant": "store03",
      "order_no": 15,
      "status": "shipped",
      "customer": {
        "name": "István Molnár",
        "email": "istvan.molnar15@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 2,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 2,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 1,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 1,
          "unit_price": 6.2
        }
      ],
      "total": 199.0,
      "currency": "EUR",
      "created_at": "2026-09-23T12:43:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Dózsa György út 86."
      }
    },
    {
      "_id": "store03:order016",
      "type": "order",
      "tenant": "store03",
      "order_no": 16,
      "status": "shipped",
      "customer": {
        "name": "István Varga",
        "email": "istvan.varga16@example.com"
      },
      "items": [
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 1,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 2,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 1,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 2,
          "unit_price": 54.0
        }
      ],
      "total": 241.8,
      "currency": "EUR",
      "created_at": "2026-09-26T18:55:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Petőfi utca 72."
      }
    },
    {
      "_id": "store03:order017",
      "type": "order",
      "tenant": "store03",
      "order_no": 17,
      "status": "paid",
      "customer": {
        "name": "Hanna Kiss",
        "email": "hanna.kiss17@example.com"
      },
      "items": [
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 1,
          "unit_price": 72.0
        }
      ],
      "total": 72.0,
      "currency": "EUR",
      "created_at": "2026-10-15T19:18:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Rákóczi út 83."
      }
    },
    {
      "_id": "store03:order018",
      "type": "order",
      "tenant": "store03",
      "order_no": 18,
      "status": "open",
      "customer": {
        "name": "Hanna Horváth",
        "email": "hanna.horvath18@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 2,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 1,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 2,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 3,
          "unit_price": 24.0
        }
      ],
      "total": 174.5,
      "currency": "EUR",
      "created_at": "2026-10-24T06:25:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Dózsa György út 45."
      }
    },
    {
      "_id": "store03:order019",
      "type": "order",
      "tenant": "store03",
      "order_no": 19,
      "status": "open",
      "customer": {
        "name": "Dániel Szabó",
        "email": "daniel.szabo19@example.com"
      },
      "items": [
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 2,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 2,
          "unit_price": 54.0
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 2,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 1,
          "unit_price": 72.0
        }
      ],
      "total": 252.8,
      "currency": "EUR",
      "created_at": "2026-09-30T01:19:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Kossuth tér 25."
      }
    },
    {
      "_id": "store03:order020",
      "type": "order",
      "tenant": "store03",
      "order_no": 20,
      "status": "open",
      "customer": {
        "name": "Júlia Nagy",
        "email": "julia.nagy20@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 3,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 3,
          "unit_price": 54.0
        }
      ],
      "total": 199.2,
      "currency": "EUR",
      "created_at": "2026-09-19T00:03:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Kossuth tér 39."
      }
    },
    {
      "_id": "store04:order001",
      "type": "order",
      "tenant": "store04",
      "order_no": 1,
      "status": "open",
      "customer": {
        "name": "Bence Kovács",
        "email": "bence.kovacs1@example.com"
      },
      "items": [
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 2,
          "unit_price": 54.0
        }
      ],
      "total": 108.0,
      "currency": "EUR",
      "created_at": "2026-10-21T16:49:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Rákóczi út 14."
      }
    },
    {
      "_id": "store04:order002",
      "type": "order",
      "tenant": "store04",
      "order_no": 2,
      "status": "open",
      "customer": {
        "name": "Petra Molnár",
        "email": "petra.molnar2@example.com"
      },
      "items": [
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 2,
          "unit_price": 6.2
        }
      ],
      "total": 12.4,
      "currency": "EUR",
      "created_at": "2026-10-02T08:17:00Z",
      "delivery": {
        "city": "Budapest",
        "street": "Petőfi utca 111."
      }
    },
    {
      "_id": "store04:order003",
      "type": "order",
      "tenant": "store04",
      "order_no": 3,
      "status": "shipped",
      "customer": {
        "name": "Bence Tóth",
        "email": "bence.toth3@example.com"
      },
      "items": [
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 2,
          "unit_price": 9.5
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 1,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 3,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 3,
          "unit_price": 72.0
        }
      ],
      "total": 331.6,
      "currency": "EUR",
      "created_at": "2026-09-14T21:55:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Fő utca 32."
      }
    },
    {
      "_id": "store04:order004",
      "type": "order",
      "tenant": "store04",
      "order_no": 4,
      "status": "cancelled",
      "customer": {
        "name": "Hanna Kiss",
        "email": "hanna.kiss4@example.com"
      },
      "items": [
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 3,
          "unit_price": 39.9
        }
      ],
      "total": 119.7,
      "currency": "EUR",
      "created_at": "2026-10-12T08:09:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Dózsa György út 55."
      }
    },
    {
      "_id": "store04:order005",
      "type": "order",
      "tenant": "store04",
      "order_no": 5,
      "status": "open",
      "customer": {
        "name": "Gréta Horváth",
        "email": "greta.horvath5@example.com"
      },
      "items": [
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 1,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 1,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 3,
          "unit_price": 24.0
        }
      ],
      "total": 97.1,
      "currency": "EUR",
      "created_at": "2026-09-08T17:21:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Dózsa György út 10."
      }
    },
    {
      "_id": "store04:order006",
      "type": "order",
      "tenant": "store04",
      "order_no": 6,
      "status": "open",
      "customer": {
        "name": "Petra Horváth",
        "email": "petra.horvath6@example.com"
      },
      "items": [
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 2,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 3,
          "unit_price": 72.0
        }
      ],
      "total": 253.8,
      "currency": "EUR",
      "created_at": "2026-09-04T07:18:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Petőfi utca 90."
      }
    },
    {
      "_id": "store04:order007",
      "type": "order",
      "tenant": "store04",
      "order_no": 7,
      "status": "open",
      "customer": {
        "name": "Nóra Nagy",
        "email": "nora.nagy7@example.com"
      },
      "items": [
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 3,
          "unit_price": 9.5
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 3,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 3,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 1,
          "unit_price": 54.0
        }
      ],
      "total": 191.7,
      "currency": "EUR",
      "created_at": "2026-10-20T21:36:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Petőfi utca 106."
      }
    },
    {
      "_id": "store04:order008",
      "type": "order",
      "tenant": "store04",
      "order_no": 8,
      "status": "paid",
      "customer": {
        "name": "Júlia Molnár",
        "email": "julia.molnar8@example.com"
      },
      "items": [
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 1,
          "unit_price": 9.5
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 2,
          "unit_price": 18.9
        }
      ],
      "total": 47.3,
      "currency": "EUR",
      "created_at": "2026-09-12T15:39:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Rákóczi út 35."
      }
    },
    {
      "_id": "store04:order009",
      "type": "order",
      "tenant": "store04",
      "order_no": 9,
      "status": "open",
      "customer": {
        "name": "István Kovács",
        "email": "istvan.kovacs9@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 2,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 3,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 2,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 3,
          "unit_price": 39.9
        }
      ],
      "total": 213.6,
      "currency": "EUR",
      "created_at": "2026-09-09T15:30:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Dózsa György út 76."
      }
    },
    {
      "_id": "store04:order010",
      "type": "order",
      "tenant": "store04",
      "order_no": 10,
      "status": "paid",
      "customer": {
        "name": "Bence Tóth",
        "email": "bence.toth10@example.com"
      },
      "items": [
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 3,
          "unit_price": 6.2
        }
      ],
      "total": 18.6,
      "currency": "EUR",
      "created_at": "2026-10-14T03:49:00Z",
      "delivery": {
        "city": "Pécs",
        "street": "Petőfi utca 24."
      }
    },
    {
      "_id": "store04:order011",
      "type": "order",
      "tenant": "store04",
      "order_no": 11,
      "status": "paid",
      "customer": {
        "name": "Dániel Tóth",
        "email": "daniel.toth11@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 2,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 2,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 2,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 3,
          "unit_price": 54.0
        }
      ],
      "total": 368.6,
      "currency": "EUR",
      "created_at": "2026-10-01T08:28:00Z",
      "delivery": {
        "city": "Pécs",
        "street": "Petőfi utca 85."
      }
    },
    {
      "_id": "store04:order012",
      "type": "order",
      "tenant": "store04",
      "order_no": 12,
      "status": "open",
      "customer": {
        "name": "Anna Molnár",
        "email": "anna.molnar12@example.com"
      },
      "items": [
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 2,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 2,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 1,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 2,
          "unit_price": 54.0
        }
      ],
      "total": 302.2,
      "currency": "EUR",
      "created_at": "2026-10-08T22:45:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Petőfi utca 80."
      }
    },
    {
      "_id": "store04:order013",
      "type": "order",
      "tenant": "store04",
      "order_no": 13,
      "status": "open",
      "customer": {
        "name": "Olivér Molnár",
        "email": "oliver.molnar13@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 2,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 3,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 1,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 2,
          "unit_price": 9.5
        }
      ],
      "total": 182.4,
      "currency": "EUR",
      "created_at": "2026-09-12T09:15:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Dózsa György út 103."
      }
    },
    {
      "_id": "store04:order014",
      "type": "order",
      "tenant": "store04",
      "order_no": 14,
      "status": "cancelled",
      "customer": {
        "name": "Nóra Nagy",
        "email": "nora.nagy14@example.com"
      },
      "items": [
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 3,
          "unit_price": 54.0
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 1,
          "unit_price": 12.4
        }
      ],
      "total": 174.4,
      "currency": "EUR",
      "created_at": "2026-09-21T18:51:00Z",
      "delivery": {
        "city": "Budapest",
        "street": "Rákóczi út 16."
      }
    },
    {
      "_id": "store04:order015",
      "type": "order",
      "tenant": "store04",
      "order_no": 15,
      "status": "cancelled",
      "customer": {
        "name": "István Kiss",
        "email": "istvan.kiss15@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 2,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 3,
          "unit_price": 24.0
        }
      ],
      "total": 96.8,
      "currency": "EUR",
      "created_at": "2026-10-15T06:02:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Rákóczi út 71."
      }
    },
    {
      "_id": "store04:order016",
      "type": "order",
      "tenant": "store04",
      "order_no": 16,
      "status": "shipped",
      "customer": {
        "name": "Eszter Nagy",
        "email": "eszter.nagy16@example.com"
      },
      "items": [
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 3,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 3,
          "unit_price": 9.5
        }
      ],
      "total": 148.2,
      "currency": "EUR",
      "created_at": "2026-09-26T11:28:00Z",
      "delivery": {
        "city": "Pécs",
        "street": "Petőfi utca 120."
      }
    },
    {
      "_id": "store04:order017",
      "type": "order",
      "tenant": "store04",
      "order_no": 17,
      "status": "paid",
      "customer": {
        "name": "Petra Tóth",
        "email": "petra.toth17@example.com"
      },
      "items": [
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 2,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 3,
          "unit_price": 54.0
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 3,
          "unit_price": 24.0
        }
      ],
      "total": 271.8,
      "currency": "EUR",
      "created_at": "2026-10-11T23:29:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Petőfi utca 71."
      }
    },
    {
      "_id": "store04:order018",
      "type": "order",
      "tenant": "store04",
      "order_no": 18,
      "status": "shipped",
      "customer": {
        "name": "Bence Varga",
        "email": "bence.varga18@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 3,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 2,
          "unit_price": 54.0
        },
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 1,
          "unit_price": 9.5
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 2,
          "unit_price": 24.0
        }
      ],
      "total": 202.7,
      "currency": "EUR",
      "created_at": "2026-10-14T09:13:00Z",
      "delivery": {
        "city": "Pécs",
        "street": "Rákóczi út 85."
      }
    },
    {
      "_id": "store04:order019",
      "type": "order",
      "tenant": "store04",
      "order_no": 19,
      "status": "open",
      "customer": {
        "name": "Kata Nagy",
        "email": "kata.nagy19@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 1,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 3,
          "unit_price": 18.9
        }
      ],
      "total": 69.1,
      "currency": "EUR",
      "created_at": "2026-10-11T09:51:00Z",
      "delivery": {
        "city": "Pécs",
        "street": "Fő utca 93."
      }
    },
    {
      "_id": "store04:order020",
      "type": "order",
      "tenant": "store04",
      "order_no": 20,
      "status": "open",
      "customer": {
        "name": "Csilla Molnár",
        "email": "csilla.molnar20@example.com"
      },
      "items": [
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 3,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 1,
          "unit_price": 12.4
        }
      ],
      "total": 132.1,
      "currency": "EUR",
      "created_at": "2026-09-25T10:57:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Rákóczi út 84."
      }
    },
    {
      "_id": "store05:order001",
      "type": "order",
      "tenant": "store05",
      "order_no": 1,
      "status": "shipped",
      "customer": {
        "name": "Márk Varga",
        "email": "mark.varga1@example.com"
      },
      "items": [
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 3,
          "unit_price": 24.0
        }
      ],
      "total": 72.0,
      "currency": "EUR",
      "created_at": "2026-10-15T17:56:00Z",
      "delivery": {
        "city": "Budapest",
        "street": "Dózsa György út 9."
      }
    },
    {
      "_id": "store05:order002",
      "type": "order",
      "tenant": "store05",
      "order_no": 2,
      "status": "paid",
      "customer": {
        "name": "Nóra Nagy",
        "email": "nora.nagy2@example.com"
      },
      "items": [
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 3,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 1,
          "unit_price": 9.5
        }
      ],
      "total": 28.1,
      "currency": "EUR",
      "created_at": "2026-09-10T11:33:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Petőfi utca 116."
      }
    },
    {
      "_id": "store05:order003",
      "type": "order",
      "tenant": "store05",
      "order_no": 3,
      "status": "open",
      "customer": {
        "name": "Bence Horváth",
        "email": "bence.horvath3@example.com"
      },
      "items": [
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 2,
          "unit_price": 18.9
        }
      ],
      "total": 37.8,
      "currency": "EUR",
      "created_at": "2026-10-03T23:04:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Kossuth tér 68."
      }
    },
    {
      "_id": "store05:order004",
      "type": "order",
      "tenant": "store05",
      "order_no": 4,
      "status": "open",
      "customer": {
        "name": "Hanna Molnár",
        "email": "hanna.molnar4@example.com"
      },
      "items": [
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 3,
          "unit_price": 54.0
        },
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 2,
          "unit_price": 9.5
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 3,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 3,
          "unit_price": 18.9
        }
      ],
      "total": 357.4,
      "currency": "EUR",
      "created_at": "2026-10-24T09:55:00Z",
      "delivery": {
        "city": "Pécs",
        "street": "Petőfi utca 59."
      }
    },
    {
      "_id": "store05:order005",
      "type": "order",
      "tenant": "store05",
      "order_no": 5,
      "status": "cancelled",
      "customer": {
        "name": "Ferenc Nagy",
        "email": "ferenc.nagy5@example.com"
      },
      "items": [
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 2,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 3,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 3,
          "unit_price": 72.0
        }
      ],
      "total": 373.5,
      "currency": "EUR",
      "created_at": "2026-10-11T12:58:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Petőfi utca 82."
      }
    },
    {
      "_id": "store05:order006",
      "type": "order",
      "tenant": "store05",
      "order_no": 6,
      "status": "open",
      "customer": {
        "name": "Márk Varga",
        "email": "mark.varga6@example.com"
      },
      "items": [
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 2,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 2,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 1,
          "unit_price": 54.0
        },
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 1,
          "unit_price": 9.5
        }
      ],
      "total": 219.9,
      "currency": "EUR",
      "created_at": "2026-10-23T15:41:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Petőfi utca 3."
      }
    },
    {
      "_id": "store05:order007",
      "type": "order",
      "tenant": "store05",
      "order_no": 7,
      "status": "paid",
      "customer": {
        "name": "Hanna Varga",
        "email": "hanna.varga7@example.com"
      },
      "items": [
        {
          "sku": "SKU-FIL-05",
          "name": "Paper filters x100",
          "qty": 3,
          "unit_price": 6.2
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 3,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 2,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 2,
          "unit_price": 39.9
        }
      ],
      "total": 179.9,
      "currency": "EUR",
      "created_at": "2026-09-21T06:25:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Petőfi utca 87."
      }
    },
    {
      "_id": "store05:order008",
      "type": "order",
      "tenant": "store05",
      "order_no": 8,
      "status": "paid",
      "customer": {
        "name": "Júlia Molnár",
        "email": "julia.molnar8@example.com"
      },
      "items": [
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 3,
          "unit_price": 9.5
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 1,
          "unit_price": 24.0
        }
      ],
      "total": 52.5,
      "currency": "EUR",
      "created_at": "2026-09-04T08:53:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Kossuth tér 12."
      }
    },
    {
      "_id": "store05:order009",
      "type": "order",
      "tenant": "store05",
      "order_no": 9,
      "status": "open",
      "customer": {
        "name": "László Horváth",
        "email": "laszlo.horvath9@example.com"
      },
      "items": [
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 1,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 1,
          "unit_price": 12.4
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 1,
          "unit_price": 72.0
        }
      ],
      "total": 108.4,
      "currency": "EUR",
      "created_at": "2026-09-16T07:27:00Z",
      "delivery": {
        "city": "Pécs",
        "street": "Petőfi utca 96."
      }
    },
    {
      "_id": "store05:order010",
      "type": "order",
      "tenant": "store05",
      "order_no": 10,
      "status": "shipped",
      "customer": {
        "name": "Márk Varga",
        "email": "mark.varga10@example.com"
      },
      "items": [
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 1,
          "unit_price": 9.5
        },
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 1,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 3,
          "unit_price": 18.9
        }
      ],
      "total": 138.2,
      "currency": "EUR",
      "created_at": "2026-09-09T13:16:00Z",
      "delivery": {
        "city": "Budapest",
        "street": "Petőfi utca 69."
      }
    },
    {
      "_id": "store05:order011",
      "type": "order",
      "tenant": "store05",
      "order_no": 11,
      "status": "open",
      "customer": {
        "name": "István Kiss",
        "email": "istvan.kiss11@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 2,
          "unit_price": 12.4
        }
      ],
      "total": 24.8,
      "currency": "EUR",
      "created_at": "2026-10-05T03:29:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Rákóczi út 4."
      }
    },
    {
      "_id": "store05:order012",
      "type": "order",
      "tenant": "store05",
      "order_no": 12,
      "status": "open",
      "customer": {
        "name": "Júlia Kiss",
        "email": "julia.kiss12@example.com"
      },
      "items": [
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 3,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 2,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 3,
          "unit_price": 18.9
        }
      ],
      "total": 320.7,
      "currency": "EUR",
      "created_at": "2026-09-11T22:52:00Z",
      "delivery": {
        "city": "Budapest",
        "street": "Petőfi utca 64."
      }
    },
    {
      "_id": "store05:order013",
      "type": "order",
      "tenant": "store05",
      "order_no": 13,
      "status": "open",
      "customer": {
        "name": "Eszter Kiss",
        "email": "eszter.kiss13@example.com"
      },
      "items": [
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 1,
          "unit_price": 9.5
        }
      ],
      "total": 9.5,
      "currency": "EUR",
      "created_at": "2026-10-12T14:59:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Dózsa György út 54."
      }
    },
    {
      "_id": "store05:order014",
      "type": "order",
      "tenant": "store05",
      "order_no": 14,
      "status": "shipped",
      "customer": {
        "name": "Nóra Horváth",
        "email": "nora.horvath14@example.com"
      },
      "items": [
        {
          "sku": "SKU-SCL-07",
          "name": "Coffee scale",
          "qty": 1,
          "unit_price": 39.9
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 2,
          "unit_price": 24.0
        }
      ],
      "total": 87.9,
      "currency": "EUR",
      "created_at": "2026-09-04T07:28:00Z",
      "delivery": {
        "city": "Debrecen",
        "street": "Rákóczi út 57."
      }
    },
    {
      "_id": "store05:order015",
      "type": "order",
      "tenant": "store05",
      "order_no": 15,
      "status": "open",
      "customer": {
        "name": "László Kovács",
        "email": "laszlo.kovacs15@example.com"
      },
      "items": [
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 3,
          "unit_price": 24.0
        },
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 2,
          "unit_price": 18.9
        }
      ],
      "total": 109.8,
      "currency": "EUR",
      "created_at": "2026-10-07T13:44:00Z",
      "delivery": {
        "city": "Budapest",
        "street": "Rákóczi út 12."
      }
    },
    {
      "_id": "store05:order016",
      "type": "order",
      "tenant": "store05",
      "order_no": 16,
      "status": "shipped",
      "customer": {
        "name": "Eszter Szabó",
        "email": "eszter.szabo16@example.com"
      },
      "items": [
        {
          "sku": "SKU-COF-01",
          "name": "Coffee beans 1 kg",
          "qty": 2,
          "unit_price": 18.9
        },
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 1,
          "unit_price": 12.4
        }
      ],
      "total": 50.2,
      "currency": "EUR",
      "created_at": "2026-09-07T13:52:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Kossuth tér 76."
      }
    },
    {
      "_id": "store05:order017",
      "type": "order",
      "tenant": "store05",
      "order_no": 17,
      "status": "cancelled",
      "customer": {
        "name": "Anna Horváth",
        "email": "anna.horvath17@example.com"
      },
      "items": [
        {
          "sku": "SKU-KET-04",
          "name": "Gooseneck kettle",
          "qty": 1,
          "unit_price": 72.0
        },
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 3,
          "unit_price": 54.0
        }
      ],
      "total": 234.0,
      "currency": "EUR",
      "created_at": "2026-09-14T12:04:00Z",
      "delivery": {
        "city": "Győr",
        "street": "Petőfi utca 103."
      }
    },
    {
      "_id": "store05:order018",
      "type": "order",
      "tenant": "store05",
      "order_no": 18,
      "status": "paid",
      "customer": {
        "name": "Anna Varga",
        "email": "anna.varga18@example.com"
      },
      "items": [
        {
          "sku": "SKU-MUG-02",
          "name": "Ceramic mug",
          "qty": 1,
          "unit_price": 9.5
        },
        {
          "sku": "SKU-DRP-06",
          "name": "Pour-over dripper",
          "qty": 1,
          "unit_price": 24.0
        }
      ],
      "total": 33.5,
      "currency": "EUR",
      "created_at": "2026-09-22T23:46:00Z",
      "delivery": {
        "city": "Budapest",
        "street": "Kossuth tér 34."
      }
    },
    {
      "_id": "store05:order019",
      "type": "order",
      "tenant": "store05",
      "order_no": 19,
      "status": "paid",
      "customer": {
        "name": "Nóra Nagy",
        "email": "nora.nagy19@example.com"
      },
      "items": [
        {
          "sku": "SKU-GRN-03",
          "name": "Hand grinder",
          "qty": 3,
          "unit_price": 54.0
        }
      ],
      "total": 162.0,
      "currency": "EUR",
      "created_at": "2026-09-07T02:50:00Z",
      "delivery": {
        "city": "Szeged",
        "street": "Dózsa György út 76."
      }
    },
    {
      "_id": "store05:order020",
      "type": "order",
      "tenant": "store05",
      "order_no": 20,
      "status": "open",
      "customer": {
        "name": "Hanna Kovács",
        "email": "hanna.kovacs20@example.com"
      },
      "items": [
        {
          "sku": "SKU-TEA-08",
          "name": "Green tea 250 g",
          "qty": 3,
          "unit_price": 12.4
        }
      ],
      "total": 37.2,
      "currency": "EUR",
      "created_at": "2026-10-18T19:07:00Z",
      "delivery": {
        "city": "Miskolc",
        "street": "Fő utca 8."
      }
    }
  ]
}
```

Response: **HTTP 201 Created**

```json
[
  {
    "ok": true,
    "id": "store01:order001",
    "rev": "1-2d37e26a73818960522c212db135250b"
  },
  {
    "ok": true,
    "id": "store01:order002",
    "rev": "1-13ca29c6ca8365538821509e281c31e3"
  },
  {
    "ok": true,
    "id": "store01:order003",
    "rev": "1-4b89a08089b01c765ecbae40912ddfde"
  },
  {
    "ok": true,
    "id": "store01:order004",
    "rev": "1-dbd4a697e0422dd8a05165341233add1"
  },
  {
    "ok": true,
    "id": "store01:order005",
    "rev": "1-7f872a617ed051ba29cc656e4e351c7c"
  },
  {
    "ok": true,
    "id": "store01:order006",
    "rev": "1-9d4c6699500d741471a36c2d13e2d940"
  },
  {
    "ok": true,
    "id": "store01:order007",
    "rev": "1-1035ebee9a66806e2146a9be35daa30a"
  },
  {
    "ok": true,
    "id": "store01:order008",
    "rev": "1-136b297b7252175b70c2ff46be317d1e"
  },
  {
    "ok": true,
    "id": "store01:order009",
    "rev": "1-982651d6d3a4d1a0a8e9d991ef1f9105"
  },
  {
    "ok": true,
    "id": "store01:order010",
    "rev": "1-dceb2c5de85b5d32a67ec3d13b53d187"
  },
  {
    "ok": true,
    "id": "store01:order011",
    "rev": "1-9a966af863735b1eeabc3f2f11946b07"
  },
  {
    "ok": true,
    "id": "store01:order012",
    "rev": "1-92f38b4c42d752232daa21779a81da5c"
  },
  {
    "ok": true,
    "id": "store01:order013",
    "rev": "1-aa8ae0cbee8ad677d39fc89d2088bb13"
  },
  {
    "ok": true,
    "id": "store01:order014",
    "rev": "1-bd08bb207141d1d4d0e0f3afb3521288"
  },
  {
    "ok": true,
    "id": "store01:order015",
    "rev": "1-c51061daa8847a12a9aa57935f393d91"
  },
  {
    "ok": true,
    "id": "store01:order016",
    "rev": "1-fb8fdbc0f0f2261b40dd9565d773f486"
  },
  {
    "ok": true,
    "id": "store01:order017",
    "rev": "1-d2a42742e5c4fff02bc6d92465c9bfc8"
  },
  {
    "ok": true,
    "id": "store01:order018",
    "rev": "1-f397352bec6a41491742ba69fc22a6bb"
  },
  {
    "ok": true,
    "id": "store01:order019",
    "rev": "1-e886308877722e5fbbdcc5275a07fef2"
  },
  {
    "ok": true,
    "id": "store01:order020",
    "rev": "1-0a7a186cbefb3061f1b5c3da064b2708"
  },
  {
    "ok": true,
    "id": "store02:order001",
    "rev": "1-c0ef7dac576a6e8a8f500ba23e9cf454"
  },
  {
    "ok": true,
    "id": "store02:order002",
    "rev": "1-709011b883f68d63a4a23a82d7869783"
  },
  {
    "ok": true,
    "id": "store02:order003",
    "rev": "1-6a9cdf44e7b670c6c5fd928f653894f8"
  },
  {
    "ok": true,
    "id": "store02:order004",
    "rev": "1-a4bf8e809bc751856f1c16b47d3e19ff"
  },
  {
    "ok": true,
    "id": "store02:order005",
    "rev": "1-c6d18e9fa015a4f22f4c1135b50b2cda"
  },
  {
    "ok": true,
    "id": "store02:order006",
    "rev": "1-34aa2afaf0073f9bc9946174a467a88c"
  },
  {
    "ok": true,
    "id": "store02:order007",
    "rev": "1-63b591a4d3aaaee0d4f323e4010baf8b"
  },
  {
    "ok": true,
    "id": "store02:order008",
    "rev": "1-0ee1c6aaf56f88486d0ea204478e9ae2"
  },
  {
    "ok": true,
    "id": "store02:order009",
    "rev": "1-f9b6d8d52855a404acbbb233f3351747"
  },
  {
    "ok": true,
    "id": "store02:order010",
    "rev": "1-5aa764c3b4163ebb521611322974c8de"
  },
  {
    "ok": true,
    "id": "store02:order011",
    "rev": "1-ab4bc3c799d0ee076fff7e8edf106ac7"
  },
  {
    "ok": true,
    "id": "store02:order012",
    "rev": "1-bad7d2a86e817b0532447a8321efa17a"
  },
  {
    "ok": true,
    "id": "store02:order013",
    "rev": "1-f938c5dc265756fec030fe8f0176ff8d"
  },
  {
    "ok": true,
    "id": "store02:order014",
    "rev": "1-574588508bf4e81e244ff783b557fb68"
  },
  {
    "ok": true,
    "id": "store02:order015",
    "rev": "1-84bd01d518d8fbda4f621d45f2b483bb"
  },
  {
    "ok": true,
    "id": "store02:order016",
    "rev": "1-0f848bf7d81e6dddb823e3d595316ba4"
  },
  {
    "ok": true,
    "id": "store02:order017",
    "rev": "1-b375e0e86db59273d0fd7b0a342d10d8"
  },
  {
    "ok": true,
    "id": "store02:order018",
    "rev": "1-39bfaede56d3de1e42bb9b5b777d3546"
  },
  {
    "ok": true,
    "id": "store02:order019",
    "rev": "1-c0d410c2a7e8cccae536f4e4229deeea"
  },
  {
    "ok": true,
    "id": "store02:order020",
    "rev": "1-a4cc2b908cb35b4362eadf1641fb09a7"
  },
  {
    "ok": true,
    "id": "store03:order001",
    "rev": "1-0ace681a439c50cac5c5abacadf418ea"
  },
  {
    "ok": true,
    "id": "store03:order002",
    "rev": "1-6e59cac6835643dd691c2b9b2ef1493d"
  },
  {
    "ok": true,
    "id": "store03:order003",
    "rev": "1-ab11449ceed41fd032d7745f4aa7221f"
  },
  {
    "ok": true,
    "id": "store03:order004",
    "rev": "1-c0097574aa31b0a3f0b24cbdcebc0f4c"
  },
  {
    "ok": true,
    "id": "store03:order005",
    "rev": "1-d0889ce3e5c666fd68ebe1b89b523015"
  },
  {
    "ok": true,
    "id": "store03:order006",
    "rev": "1-adbec1c2173a0a980a5b968f7c5d7ef7"
  },
  {
    "ok": true,
    "id": "store03:order007",
    "rev": "1-b8a3f9af2e3c5c48bc8508e64a8da2f6"
  },
  {
    "ok": true,
    "id": "store03:order008",
    "rev": "1-069b8f050acd16857cc3615018d94b1a"
  },
  {
    "ok": true,
    "id": "store03:order009",
    "rev": "1-779bda2ea3bcd05a538005a982b789d5"
  },
  {
    "ok": true,
    "id": "store03:order010",
    "rev": "1-7607d32e0a3b22296430828c21c54f32"
  },
  {
    "ok": true,
    "id": "store03:order011",
    "rev": "1-e648f376e611d0f5d15f1b4c7f1d4bf8"
  },
  {
    "ok": true,
    "id": "store03:order012",
    "rev": "1-1bc9e0b56472e8f8862d9c59b5c9e050"
  },
  {
    "ok": true,
    "id": "store03:order013",
    "rev": "1-e19b054ded76ef64043a77aa2367214d"
  },
  {
    "ok": true,
    "id": "store03:order014",
    "rev": "1-1a696392e14df1234e754122d4b66c9d"
  },
  {
    "ok": true,
    "id": "store03:order015",
    "rev": "1-d4b037d6fc074990f981c930b80b09eb"
  },
  {
    "ok": true,
    "id": "store03:order016",
    "rev": "1-0fd4f317fd8358a6db6c2c2142c7cc31"
  },
  {
    "ok": true,
    "id": "store03:order017",
    "rev": "1-ec11601b51b802f6477b5c0ea84140fb"
  },
  {
    "ok": true,
    "id": "store03:order018",
    "rev": "1-e3d132bd16a3480bcac3c2b0701914b6"
  },
  {
    "ok": true,
    "id": "store03:order019",
    "rev": "1-caa8b1ce050ce80c1da9caa9b57207e7"
  },
  {
    "ok": true,
    "id": "store03:order020",
    "rev": "1-9a71eb9d4b2a6d6e2280a6a8909ceb83"
  },
  {
    "ok": true,
    "id": "store04:order001",
    "rev": "1-4799818507b8bbaaee39490d53eb4ad3"
  },
  {
    "ok": true,
    "id": "store04:order002",
    "rev": "1-f677d00027dabc749b0c407aad2dab04"
  },
  {
    "ok": true,
    "id": "store04:order003",
    "rev": "1-b32da0f6ce9e93daf86efd207810143a"
  },
  {
    "ok": true,
    "id": "store04:order004",
    "rev": "1-8cb726ae5e8c9bd8dd1f98bf3253f752"
  },
  {
    "ok": true,
    "id": "store04:order005",
    "rev": "1-24e53a601fdbd2e32b22d85613b9de4e"
  },
  {
    "ok": true,
    "id": "store04:order006",
    "rev": "1-9c6a9c63c3f99c7acf5706fc31767074"
  },
  {
    "ok": true,
    "id": "store04:order007",
    "rev": "1-c5ac044b69a027300649459288cf0ed0"
  },
  {
    "ok": true,
    "id": "store04:order008",
    "rev": "1-7d309a76173966bddd88588cc6d48eaa"
  },
  {
    "ok": true,
    "id": "store04:order009",
    "rev": "1-7ecf857a263423657f8c07274eba62f1"
  },
  {
    "ok": true,
    "id": "store04:order010",
    "rev": "1-69014d150d5cbab33244fcce4ae90e9a"
  },
  {
    "ok": true,
    "id": "store04:order011",
    "rev": "1-f2c3c5b685cd272760af8311ee4fbc0c"
  },
  {
    "ok": true,
    "id": "store04:order012",
    "rev": "1-c6f867071a21743dc22983d4caef6ee3"
  },
  {
    "ok": true,
    "id": "store04:order013",
    "rev": "1-582676e5400567bbefde2057fedb3ed8"
  },
  {
    "ok": true,
    "id": "store04:order014",
    "rev": "1-76521f72221901088daf4780a7a30aa0"
  },
  {
    "ok": true,
    "id": "store04:order015",
    "rev": "1-e7c749811cea6bf0a8bd80fdf62f9371"
  },
  {
    "ok": true,
    "id": "store04:order016",
    "rev": "1-4691da02b4c4acb0663708cadf033940"
  },
  {
    "ok": true,
    "id": "store04:order017",
    "rev": "1-c8678d3350e2d4915ae02172031c0c7c"
  },
  {
    "ok": true,
    "id": "store04:order018",
    "rev": "1-d052e0973df6dbe5233fd7e8929674ec"
  },
  {
    "ok": true,
    "id": "store04:order019",
    "rev": "1-f87080fe558c0c7922bb70a76e1d4393"
  },
  {
    "ok": true,
    "id": "store04:order020",
    "rev": "1-217fc81ab86629caa16c5c7d8e07071a"
  },
  {
    "ok": true,
    "id": "store05:order001",
    "rev": "1-02104f0bd8f14e259a2b4d845247222e"
  },
  {
    "ok": true,
    "id": "store05:order002",
    "rev": "1-d6441baf0c72e7c9c44a1bfcb2b2640d"
  },
  {
    "ok": true,
    "id": "store05:order003",
    "rev": "1-258db82800262e6efafdbfbed9a38f47"
  },
  {
    "ok": true,
    "id": "store05:order004",
    "rev": "1-b472f5b2fb580a414d5881a3828893cd"
  },
  {
    "ok": true,
    "id": "store05:order005",
    "rev": "1-0da2a07fd2a971a584093476f7e74143"
  },
  {
    "ok": true,
    "id": "store05:order006",
    "rev": "1-e74e4880fec17d6e64f4fb3d4f46948f"
  },
  {
    "ok": true,
    "id": "store05:order007",
    "rev": "1-9028cb165ae75e03d30aa700296255ef"
  },
  {
    "ok": true,
    "id": "store05:order008",
    "rev": "1-d24e53a33a924cea06b4e9c73d62b6be"
  },
  {
    "ok": true,
    "id": "store05:order009",
    "rev": "1-448e5803498b28de0c7494fa06d048c6"
  },
  {
    "ok": true,
    "id": "store05:order010",
    "rev": "1-e10a016d69e5c5129c095f0c9eb83ff1"
  },
  {
    "ok": true,
    "id": "store05:order011",
    "rev": "1-64ceec465efaf73934008deeee91f37d"
  },
  {
    "ok": true,
    "id": "store05:order012",
    "rev": "1-3d29b412d4a4787239b3e9f0fa6cf2cb"
  },
  {
    "ok": true,
    "id": "store05:order013",
    "rev": "1-a4106686f81b0a898573dc283ef4de17"
  },
  {
    "ok": true,
    "id": "store05:order014",
    "rev": "1-aa118f3366e4c64f95f32bcfb19c1b1f"
  },
  {
    "ok": true,
    "id": "store05:order015",
    "rev": "1-a40901eae1e2a1afb5b1efcff2ddd0f3"
  },
  {
    "ok": true,
    "id": "store05:order016",
    "rev": "1-7e766ca9a9f2968cf8e9c09d4c254b1d"
  },
  {
    "ok": true,
    "id": "store05:order017",
    "rev": "1-e2e8d089944c18934aba0e54c367f376"
  },
  {
    "ok": true,
    "id": "store05:order018",
    "rev": "1-995310c1a56eefc2a5ffdf2bbd03d04d"
  },
  {
    "ok": true,
    "id": "store05:order019",
    "rev": "1-35b8038b320cb8d27c7ccefebb4d5786"
  },
  {
    "ok": true,
    "id": "store05:order020",
    "rev": "1-7670463b10054200a8f9c79e77ee23c9"
  }
]
```

- **PASS**: Every order is stored on A (new or already present)  
  expected: HTTP 201 and 100 items ok or already present  
  observed: HTTP 201, 100 created, 0 already present

### Step 5: Database info on A

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

- **PASS**: Document count on A  
  expected: >= 100 documents  
  observed: 100 documents

