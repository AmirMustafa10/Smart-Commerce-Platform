# ADR-005: Store Product Images in a Separate Model

## Status

Accepted

---

## Context

Products in the platform may require multiple images to support different customer views, product galleries, and future integrations with external sales channels.

A design decision was required to determine whether images should be stored directly inside the Product model or represented as a separate entity.

The chosen design should support scalability, clean database structure, and future image-related features.

---

## Decision

Product images are stored in a dedicated `ProductImage` model with a one-to-many relationship to the `Product` model.

Each image belongs to exactly one product, while a product can have multiple associated images.

Relationship:

```text id="pimg71"
Product

   |

   └── ProductImage
```

Image uploads are validated before storage using:

- File extension validation
- File size validation
- Django `ImageField`
- Pillow image verification

Product images are managed through Django Admin using `ProductImageInline`, allowing image management directly from the Product administration page.

---

## Alternatives Considered

### Option 1 — Single ImageField on Product

```python
image = models.ImageField(...)
```

#### Advantages

- Very simple implementation.
- Suitable for products requiring only one image.

#### Disadvantages

- Does not support product galleries.
- Requires schema changes when multiple images become necessary.
- Limits future expansion.

**Decision:** Rejected.

---

### Option 2 — Multiple Fixed Image Fields

```python
image1
image2
image3
```

#### Advantages

- Easy initial implementation.

#### Disadvantages

- Creates an artificial image limit.
- Requires database changes when more images are needed.
- Produces repetitive code.
- Does not follow scalable database design.

**Decision:** Rejected.

---

### Option 3 — Separate ProductImage Model

#### Advantages

- Supports unlimited images.
- Keeps Product model focused on product data.
- Provides better database normalization.
- Simplifies image management.
- Supports future features such as:
  - Primary image selection
  - Image ordering
  - Image captions
  - Image optimization
  - Cloud storage integration

#### Disadvantages

- Requires an additional database table.
- May require additional joins when retrieving images.

**Decision:** Accepted.

---

## Consequences

### Positive

- Flexible image management.
- Better database normalization.
- Cleaner Product model.
- Easier maintenance.
- Supports future business requirements without changing Product schema.
- Aligns with Django's one-to-many relationship patterns.

### Negative

- Slightly more complex queries.
- Additional relationship management in the application layer.
- Additional model administration.

---

## Future Considerations

The dedicated image model allows future enhancements without modifying the Product model, including:

- Image ordering
- Featured image support
- Image compression
- Multiple image resolutions
- CDN integration
- Soft deletion of images

---

## Related Documentation

- `Database/product-model.md`
- `ADR/ADR-003-product-images.md`
- `Architecture/product-management.md`
