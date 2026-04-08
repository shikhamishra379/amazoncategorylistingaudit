# Amazon Listing Field Reference

A quick reference for required and recommended fields by Amazon category.

## Universal Required Fields (All Categories)
| Field | Max Length | Notes |
|-------|-----------|-------|
| `item_name` (Title) | 200 chars | No ALL CAPS, no special characters |
| `brand_name` | 50 chars | Must match brand registry name |
| `bullet_point1` | 255 chars | Start with a benefit, not a feature |
| `product_description` | 2000 chars | Use HTML tags for formatting |
| `main_image_url` | — | Pure white background, product fills 85%+ |

## Health & Beauty
| Field | Required? |
|-------|----------|
| `ingredients` | Required |
| `directions` | Required |
| `warnings` | Required |
| `aplus_content` | Strongly recommended |
| Min 3 bullet points | Required |
| Min 3 images | Required |

## Grocery
| Field | Required? |
|-------|----------|
| `ingredients` | Required |
| `allergen_information` | Required |
| `net_content` | Required |

## Electronics
| Field | Required? |
|-------|----------|
| `wattage` | Required |
| `batteries_required` | Required |
| Min 4 images | Required |

## Scoring
| Score | Status | Action |
|-------|--------|--------|
| 80-100 | PASS | Minor improvements only |
| 60-79 | WARNING | Address before next review |
| 0-59 | FAIL | Critical fields missing |
