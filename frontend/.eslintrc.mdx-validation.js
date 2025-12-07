module.exports = {
  extends: [
    '@docusaurus/eslint-config',
    'prettier'
  ],
  plugins: [
    'markdown',
    '@docusaurus'
  ],
  overrides: [
    {
      files: ["**/*.md", "**/*.mdx"],
      processor: "markdown/markdown",
      rules: {
        // Require specific frontmatter fields in documentation files
        '@docusaurus/no-untranslated-text': 'off', // Disable if causing issues
        // Additional rules for frontmatter validation would go here
      }
    },
    {
      files: ["**/*.mdx"],
      extends: [
        "plugin:@docusaurus/recommended"
      ]
    }
  ],
  // Global rules
  rules: {
    // Add any additional validation rules here
  }
};