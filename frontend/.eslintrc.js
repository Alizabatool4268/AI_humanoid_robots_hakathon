{
  "extends": [
    "@docusaurus/eslint-config",
    "prettier"
  ],
  "plugins": [
    "markdown"
  ],
  "overrides": [
    {
      "files": ["**/*.md"],
      "processor": "markdown/markdown"
    }
  ]
}