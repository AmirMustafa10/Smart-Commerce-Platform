# Store Product Images in a Separate Model

## Status

Accepted

---

## Context

Products in the system can have multiple images to support different customer views, product galleries, and future integrations with external sales channels.

A design decision was required to determine how product images should be stored.

---

## Decision

Product images are stored in a dedicated `ProductImage` model with a one-to-many relationship to the `Product` model.

Each image references exactly one product, while a product may have any number of associated images.

Image uploads are validated before storage using:

- File extension validation
- File size validation
- Django `ImageField`
- Pillow image verification

---

## Alternatives Considered

### Option 1 — Single ImageField on Product

```python
image = models.ImageField(...)
```

#### Advantages

- Very simple implementation.
- Suitable for products that require only one image.

#### Disadvantages

- Does not support image galleries.
- Requires schema changes if multiple images become necessary.
- Poor scalability.

**Decision:** Rejected.

---

### Option 2 — Multiple Fixed Image Fields

```python
image1
image2
image3
...
```

#### Advantages

- Easy to understand initially.

#### Disadvantages

- Artificial limit on the number of images.
- Database schema must change whenever additional images are required.
- Produces repetitive code.
- Violates clean database design principles.

**Decision:** Rejected.

---

### Option 3 — Separate ProductImage Model

#### Advantages

- Supports unlimited images.
- Keeps the Product model clean.
- Scales naturally as the application grows.
- Simplifies image management.
- Makes future features easier, including:
  - Primary image selection
  - Image ordering
  - Image captions
  - Image optimization
  - Cloud storage integration

#### Disadvantages

- Requires an additional database table.
- Requires joins when retrieving product images.

**Decision:** Accepted.

---

## Consequences

### Positive

- Flexible image management.
- Better database normalization.
- Easier maintenance.
- Supports future business requirements without schema changes.
- Follows Django best practices for one-to-many relationships.

### Negative

- Slightly more complex queries.
- Additional relationship management in the application layer.

---

## Future Considerations

The dedicated image model allows future enhancements without modifying the Product model, including:

- Image ordering
- Featured image support
- Image compression
- Multiple image resolutions
- CDN integration
- Soft deletion of images