# Data Model: AI-Native Textbook

## Entities

### Chapter
- **Description**: Represents a single unit of content within the AI-Native Textbook.
- **Attributes**:
    - `id`: Unique identifier (derived from file path/slug).
    - `title`: Display title of the chapter (from Markdown frontmatter).
    - `content`: The full Markdown content of the chapter.
    - `slug`: URL-friendly identifier for the chapter.
    - `module_id`: Reference to the parent module.
    - `order`: Numeric order within its module.
    - `metadata`: (Optional) Additional frontmatter fields like `description`, `keywords`, etc.

### Module
- **Description**: A logical grouping of related chapters.
- **Attributes**:
    - `id`: Unique identifier (derived from directory name).
    - `title`: Display title of the module (from directory/index file).
    - `chapters`: A collection of `Chapter` entities belonging to this module.
    - `order`: Numeric order within the overall textbook structure.

## Relationships

- A `Module` contains many `Chapters`.
- A `Chapter` belongs to one `Module`.

## Validation Rules

- Chapter `title` and `content` must be present.
- Chapter `slug` must be unique within its module.
- Chapter `order` must be unique within its module.
- Module `title` must be present.
- All Markdown files (chapters) must adhere to Docusaurus-compatible Markdown and frontmatter conventions.
